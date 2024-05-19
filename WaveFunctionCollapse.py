from __future__ import annotations

import itertools
from concurrent.futures import ProcessPoolExecutor, Future
from copy import deepcopy
from typing import Tuple, Callable, Iterator, Dict, Set, List, Optional

import numpy as np
from glm import ivec3
from numpy.random import Generator
from ordered_set import OrderedSet

import globals
import Adjacency
import vectorTools
from Adjacency import StructureRotation, StructureAdjacency
from StructureBase import Structure
from gdpc.src.gdpc import Box


class WaveFunctionCollapse:

    stateSpace: Dict[ivec3, OrderedSet[StructureRotation]]
    structureWeights: Dict[str, float]
    defaultAdjacencies: Dict[str, StructureAdjacency]
    defaultDomain: OrderedSet[StructureRotation]
    rng: Generator
    validationFunction: Callable[[WaveFunctionCollapse], bool] | None
    workList: Dict[ivec3, OrderedSet[StructureRotation]]

    def __init__(
        self,
        volumeGrid: Box,
        structureWeights: Dict[str, float],
        stateSpace: Optional[Dict[ivec3, OrderedSet[StructureRotation]]] = None,
        initFunction: Callable[[WaveFunctionCollapse], None] | None = None,
        validationFunction: Callable[[WaveFunctionCollapse], bool] | None = None,
        rngSeed: int | None = None,
    ):

        self.stateSpaceBox = volumeGrid
        if not volumeGrid.size >= ivec3(1, 1, 1):
            raise ValueError('State space size should be at least (1, 1, 1)')

        self.stateSpace = dict() if stateSpace is None else stateSpace

        self.structureWeights = structureWeights

        # Setup default list of adjacencies and cell domain
        self.defaultAdjacencies = self.createDefaultAdjacencies()
        self.defaultDomain = self.createDefaultDomain()

        self.setupRNG(rngSeed)

        self.initFunction = initFunction
        self.validationFunction = validationFunction

        self.workList = dict()

        self.initStateSpaceWithDefaultDomain()
        if initFunction:
            initFunction(self)

    def setupRNG(self, rngSeed: int | None = None):
        self.rng = np.random.default_rng(seed=rngSeed)

    def createDefaultAdjacencies(self) -> Dict[str, StructureAdjacency]:
        return Adjacency.omitAdjacenciesWithZeroWeight(
            globals.defaultAdjacencies,
            self.structureWeights
        )

    def createDefaultDomain(self) -> OrderedSet[StructureRotation]:
        return OrderedSet(
            Adjacency.StructureRotation(structureName, rotation)
            for structureName, rotation in itertools.product(self.defaultAdjacencies.keys(), range(4))
        )

    def initStateSpaceWithDefaultDomain(self):
        for index in self.cellCoordinates:
            self.stateSpace[index] = deepcopy(self.defaultDomain)

    @property
    def cellCoordinates(self) -> Iterator[ivec3]:
        return vectorTools.boxPositions(self.stateSpaceBox)

    @property
    def uncollapsedCellIndicies(self) -> Iterator[ivec3]:
        for cellIndex, cellState in self.stateSpace.items():
            if len(cellState) > 1:
                yield cellIndex

    def getCellIndicesWithEntropy(self, entropy: int = 1) -> Iterator[ivec3]:
        for cellIndex, cellState in self.stateSpace.items():
            if len(cellState) == entropy:
                yield cellIndex

    @property
    def lowestEntropy(self) -> int:
        minEntrophy = len(self.defaultDomain) + 1
        for cellState in self.stateSpace.values():
            entrophySize = len(cellState)
            if entrophySize == 0:
                return entrophySize
            if entrophySize < minEntrophy and entrophySize != 1:
                minEntrophy = entrophySize
        return minEntrophy

    def getStructureWeights(self, structureRotations: OrderedSet[StructureRotation]):
        structureWeights = np.array([
            self.structureWeights[structureRotation.structureName] for structureRotation in structureRotations
        ], dtype=float)
        return structureWeights / sum(structureWeights)

    def getRandomStateFromSuperposition(self, cellSuperPosition: OrderedSet[StructureRotation]) -> StructureRotation:
        assert len(cellSuperPosition) > 1
        # noinspection PyTypeChecker
        return self.rng.choice(cellSuperPosition, p=self.getStructureWeights(cellSuperPosition))

    @property
    def randomUncollapsedCellIndex(self) -> ivec3:
        # noinspection PyTypeChecker
        return ivec3(self.rng.choice(list(self.uncollapsedCellIndicies)))

    @property
    def randomCollapsedCellIndex(self) -> ivec3:
        # noinspection PyTypeChecker
        return ivec3(self.rng.choice(list(self.getCellIndicesWithEntropy(entropy=1))))

    @property
    def isCollapsed(self) -> bool:
        return len(list(self.getCellIndicesWithEntropy(entropy=1))) == len(self.stateSpace)

    def collapse(self) -> bool:
        while not self.isCollapsed:
            minEntropy = self.lowestEntropy
            if minEntropy == 0:
                return False
            nextCellsToCollapse = list(self.getCellIndicesWithEntropy(minEntropy))
            assert len(nextCellsToCollapse) > 0

            # noinspection PyTypeChecker
            nextCellIndex = ivec3(self.rng.choice(nextCellsToCollapse))

            nextCellState = self.stateSpace[nextCellIndex]
            collapsedState = self.getRandomStateFromSuperposition(nextCellState)
            self.collapseCellToState(nextCellIndex, collapsedState)

        if self.validationFunction:
            return self.validationFunction(self)
        return True

    def collapseCellToState(self, cellIndex: ivec3, structureToCollapse: StructureRotation):
        if cellIndex not in self.workList:
            self.workList[cellIndex] = OrderedSet([structureToCollapse])
        while len(self.workList) > 0:
            taskCellIndex, remainingStates = self.workList.popitem()
            newTasks = self.propagate(
                cellIndex=taskCellIndex,
                remainingStates=remainingStates,
            )
            self.workList.update(newTasks)

        assert self.stateSpace[cellIndex] in (OrderedSet(), OrderedSet([structureToCollapse])), \
            f'Cell should have been set to {structureToCollapse} or {OrderedSet()} but is {self.stateSpace[cellIndex]}'

    def propagate(
        self,
        cellIndex: ivec3,
        remainingStates: OrderedSet[StructureRotation],
    ) -> Dict[ivec3, OrderedSet[StructureRotation]]:
        nextTasks: Dict[ivec3, OrderedSet[StructureRotation]] = dict()
        if not remainingStates.issubset(self.stateSpace[cellIndex]):
            raise Exception(
                f'{cellIndex} tried to colapse a state to values not available in current superposition: '
                f'{remainingStates} ⊄ {self.stateSpace[cellIndex]}'
            )
        if set(remainingStates) == set(self.stateSpace[cellIndex]):
            # No change in states. No need to propagate further.
            return nextTasks

        # Update cell to new collapsed state
        self.stateSpace[cellIndex] = remainingStates

        xBackward, axis = Adjacency.getPositionFromAxis('xBackward', cellIndex)
        if cellIndex.x > self.stateSpaceBox.begin.x and xBackward not in self.workList:
            nextTasks.update(self.computeNeighbourStatesIntersection(
                xBackward,
                cellIndex,
                axis,
            ))
        xForward, axis = Adjacency.getPositionFromAxis('xForward', cellIndex)
        if cellIndex.x < self.stateSpaceBox.last.x and xForward not in self.workList:
            nextTasks.update(self.computeNeighbourStatesIntersection(
                xForward,
                cellIndex,
                axis,
            ))

        yBackward, axis = Adjacency.getPositionFromAxis('yBackward', cellIndex)
        if cellIndex.y > self.stateSpaceBox.begin.y and yBackward not in self.workList:
            nextTasks.update(self.computeNeighbourStatesIntersection(
                yBackward,
                cellIndex,
                axis,
            ))
        yForward, axis = Adjacency.getPositionFromAxis('yForward', cellIndex)
        if cellIndex.y < self.stateSpaceBox.last.y and yForward not in self.workList:
            nextTasks.update(self.computeNeighbourStatesIntersection(
                yForward,
                cellIndex,
                axis,
            ))

        zBackward, axis = Adjacency.getPositionFromAxis('zBackward', cellIndex)
        if cellIndex.z > self.stateSpaceBox.begin.z and zBackward not in self.workList:
            nextTasks.update(self.computeNeighbourStatesIntersection(
                zBackward,
                cellIndex,
                axis,
            ))
        zForward, axis = Adjacency.getPositionFromAxis('zForward', cellIndex)
        if cellIndex.z < self.stateSpaceBox.last.z and zForward not in self.workList:
            nextTasks.update(self.computeNeighbourStatesIntersection(
                zForward,
                cellIndex,
                axis,
            ))

        return nextTasks

    def computeNeighbourStatesIntersection(
        self,
        neighbourCellIndex: ivec3,
        cellIndex: ivec3,
        axis: str,
    ) -> Dict[ivec3, OrderedSet[StructureRotation]]:
        return {
            neighbourCellIndex:
            self.stateSpace[neighbourCellIndex].intersection(self.computeNeighbourStates(
                cellIndex,
                axis,
            ))
        }

    def computeNeighbourStates(
        self,
        cellIndex: ivec3,
        axis: str,
    ) -> Set[StructureRotation]:
        allowedStates: Set[StructureRotation] = set()
        for s in self.stateSpace[cellIndex]:
            allowedStates.update(self.defaultAdjacencies[s.structureName].adjacentStructures(
                axis,
                s.rotation
            ))
        return allowedStates

    def getCollapsedState(self, buildVolumeOffset: ivec3 = ivec3(0, 0, 0)) -> Iterator[Structure]:
        if not self.isCollapsed:
            raise Exception('WFC is not fully collapsed yet! Therefore the state cannot yet be extracted.')
        for cellIndex in self.stateSpace:
            cellState: StructureRotation = self.stateSpace[cellIndex][0]
            if cellState.structureName not in globals.structureFolders:
                raise Exception(f'Structure file {cellState.structureName} not found in {globals.structureFolders}')
            structureFolder = globals.structureFolders[cellState.structureName]
            structureInstance: Structure = structureFolder.structureClass(
                withRotation=cellState.rotation,
                tile=ivec3(*cellIndex),
                offset=buildVolumeOffset,
            )
            yield structureInstance

    def scanForBuildings(self) -> List[Set[ivec3]]:
        if not self.isCollapsed:
            raise Exception('WFC is not fully collapsed yet! Therefore volume cannot be scanned yet.')
        buildings: List[Set[ivec3]] = []
        newBuilding: Set[ivec3] = set()
        cellsVisited: Set[ivec3] = set()

        while len(cellsVisited) != len(self.stateSpace):
            randomIndex = self.randomCollapsedCellIndex
            if randomIndex in cellsVisited:
                continue

            if self.stateSpace[randomIndex][0].structureName.endswith('air'):
                cellsVisited.add(randomIndex)
                continue

            scanWorkList: List[ivec3] = [randomIndex]
            while len(scanWorkList) > 0:
                cellIndex = scanWorkList.pop()
                if cellIndex in cellsVisited:
                    continue

                cellState: StructureRotation = self.stateSpace[cellIndex][0]
                if cellState.structureName.endswith('air'):
                    raise Exception(f'Wall leak found in building {newBuilding}')

                openPositions: Set[ivec3] = self.defaultAdjacencies[cellState.structureName].getNonWallPositions(
                    cellState.rotation,
                    cellIndex,
                    self.stateSpaceBox,
                )
                newBuilding.add(cellIndex)
                newBuilding.update(openPositions)
                scanWorkList.extend(openPositions)
                cellsVisited.add(cellIndex)
            buildings.append(newBuilding.copy())
            newBuilding.clear()

        return buildings

    def removeOrphanedBuildings(self):
        buildings = self.scanForBuildings()
        print(f'Found {len(buildings)} distinct buildings, removing orphaned buildings…')
        largestBuilding = max(buildings, key=lambda x: len(x))
        for building in buildings:
            if building != largestBuilding:
                for pos in building:
                    self.stateSpace[pos] = OrderedSet({StructureRotation(structureName='air', rotation=0)})

    @property
    def structuresUsed(self) -> Iterator[StructureRotation]:
        for cellState in self.stateSpace.values():
            if cellState[0].structureName not in globals.structureFolders:
                raise Exception(f'Structure file {cellState[0].structureName} not found in {globals.structureFolders}')
            yield cellState[0]


def startWFCInstance(
    attempt: int,
    volumeGrid: Box,
    structureWeights: Dict[str, float],
    initFunction: Callable[[WaveFunctionCollapse], None] | None,
    validationFunction: Callable[[WaveFunctionCollapse], bool] | None,
) -> Tuple[bool, WaveFunctionCollapse, int]:
    rngSeed = (globals.rngSeed + attempt) if globals.rngSeed is not None else None
    wfc = WaveFunctionCollapse(
        volumeGrid=volumeGrid,
        initFunction=initFunction,
        validationFunction=validationFunction,
        rngSeed=rngSeed,
        structureWeights=structureWeights,
    )
    print(f'Starting WFC collapse attempt {attempt}')
    isCollapsed = wfc.collapse()
    return isCollapsed, wfc, attempt


def startMultiThreadedWFC(
    volumeGrid: Box,
    structureWeights: Dict[str, float],
    initFunction: Callable[[WaveFunctionCollapse], None] | None,
    validationFunction: Callable[[WaveFunctionCollapse], bool] | None,
    maxAttempts: int = 1000,
) -> WaveFunctionCollapse:
    with ProcessPoolExecutor() as executor:
        wfcResult: WaveFunctionCollapse | None = None

        def futureCallback(f: Future):
            nonlocal wfcResult
            if wfcResult:
                f.cancel()
                return
            newWfcResult = f.result()
            if newWfcResult[0]:
                executor.shutdown(wait=False, cancel_futures=True)
                wfcResult = newWfcResult[1]
                print(f'WFC attempt {newWfcResult[2]} HAS collapsed!')
                return
            if newWfcResult[2] >= maxAttempts:
                raise Exception(f'WFC did not collapse after {maxAttempts} retries.')
            print(f'WFC attempt {newWfcResult[2]} did NOT collapse')

        for attempt in range(maxAttempts):
            if wfcResult is None:
                future: Future = executor.submit(
                    startWFCInstance,
                    attempt,
                    volumeGrid,
                    structureWeights,
                    initFunction,
                    validationFunction
                )
                future.add_done_callback(futureCallback)

    return wfcResult


def startSingleThreadedWFC(
    volumeGrid: Box,
    structureWeights: Dict[str, float],
    initFunction: Callable[[WaveFunctionCollapse], None] | None,
    validationFunction: Callable[[WaveFunctionCollapse], bool] | None,
    maxAttempts: int = 10000,
) -> WaveFunctionCollapse:
    attempt = 1
    isCollapsed = False
    wfc = None
    while not isCollapsed:
        isCollapsed, wfc, _ = startWFCInstance(
            attempt=attempt,
            volumeGrid=volumeGrid,
            structureWeights=structureWeights,
            initFunction=initFunction,
            validationFunction=validationFunction,
        )
        attempt += 1
        if attempt > maxAttempts:
            raise Exception(f'WFC did not collapse after {maxAttempts} retries.')
    print(f'WFC collapsed after {attempt} attempts')
    return wfc
