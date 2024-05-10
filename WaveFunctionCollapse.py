from __future__ import annotations

from concurrent.futures import ProcessPoolExecutor, Future
from typing import Tuple, Callable, Iterator, Dict, Set

import numpy as np
from glm import ivec3
from numpy.random import Generator
from ordered_set import OrderedSet

import globals
from Adjacency import StructureRotation
from StructureBase import Structure


class WaveFunctionCollapse:

    rng: Generator
    validationFunction: Callable[[WaveFunctionCollapse], bool] | None
    structureWeights: Dict[str, float]
    stateSpaceSize: ivec3
    stateSpace: Dict[ivec3, OrderedSet[StructureRotation]]
    workList: Dict[ivec3, OrderedSet[StructureRotation]]

    def __init__(
        self,
        volumeGrid: ivec3,
        structureWeights: Dict[str, float],
        initFunction: Callable[[WaveFunctionCollapse], None] | None = None,
        validationFunction: Callable[[WaveFunctionCollapse], bool] | None = None,
        rngSeed: int | None = None,
    ):
        self.setupRNG(rngSeed)
        self.setStructureWeights(structureWeights)

        self.initFunction = initFunction
        self.validationFunction = validationFunction

        self.workList = dict()

        self.stateSpaceSize = volumeGrid
        self.stateSpace = dict()

        if not self.stateSpaceSize >= ivec3(1, 1, 1):
            raise ValueError('State space size should be at least (1, 1, 1)')

        self.initStateSpaceWithDefaultDomain()
        if initFunction:
            initFunction(self)

    def setupRNG(self, rngSeed: int | None = None):
        self.rng = np.random.default_rng(seed=rngSeed)

    def initStateSpaceWithDefaultDomain(self):
        self.stateSpace.clear()
        for index in self.cellCoordinates:
            self.stateSpace[index] = globals.defaultDomain.copy()

    @property
    def cellCoordinates(self) -> Iterator[ivec3]:
        for x in range(self.stateSpaceSize.x):
            for y in range(self.stateSpaceSize.y):
                for z in range(self.stateSpaceSize.z):
                    yield ivec3(x, y, z)

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
        minEntrophy = len(globals.defaultDomain) + 1
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

    def setStructureWeights(self, structureWeights: Dict[str, float]):
        self.structureWeights = structureWeights if structureWeights is not None else globals.structureWeights

    def getRandomStateFromSuperposition(self, cellSuperPosition: OrderedSet) -> StructureRotation:
        assert len(cellSuperPosition) > 1
        return self.rng.choice(cellSuperPosition, p=self.getStructureWeights(cellSuperPosition))

    @property
    def randomUncollapsedCellIndex(self) -> ivec3:
        # noinspection PyTypeChecker
        return self.rng.choice(list(self.uncollapsedCellIndicies))

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
        x, y, z = cellIndex
        nextTasks: Dict[ivec3, OrderedSet[StructureRotation]] = dict()
        if not remainingStates.issubset(self.stateSpace[cellIndex]):
            raise Exception(
                f'{x} {y} {z} tried to colapse a state to values not available in current superposition: '
                f'{remainingStates} ⊄ {self.stateSpace[cellIndex]}'
            )
        if set(remainingStates) == set(self.stateSpace[cellIndex]):
            # No change in states. No need to propagate further.
            return nextTasks

        # Update cell to new collapsed state
        self.stateSpace[cellIndex] = remainingStates

        xBackward = ivec3(x - 1, y, z)
        if x > 0 and xBackward not in self.workList:
            nextTasks.update(WaveFunctionCollapse.computeNeighbourStatesIntersection(
                xBackward,
                cellIndex,
                'xBackward',
                self.stateSpace,
            ))
        xForward = ivec3(x + 1, y, z)
        if x < self.stateSpaceSize.x - 1 and xForward not in self.workList:
            nextTasks.update(WaveFunctionCollapse.computeNeighbourStatesIntersection(
                xForward,
                cellIndex,
                'xForward',
                self.stateSpace,
            ))

        yBackward = ivec3(x, y - 1, z)
        if y > 0 and yBackward not in self.workList:
            nextTasks.update(WaveFunctionCollapse.computeNeighbourStatesIntersection(
                yBackward,
                cellIndex,
                'yBackward',
                self.stateSpace,
            ))
        yForward = ivec3(x, y + 1, z)
        if y < self.stateSpaceSize.y - 1 and yForward not in self.workList:
            nextTasks.update(WaveFunctionCollapse.computeNeighbourStatesIntersection(
                yForward,
                cellIndex,
                'yForward',
                self.stateSpace,
            ))

        zBackward = ivec3(x, y, z - 1)
        if z > 0 and zBackward not in self.workList:
            nextTasks.update(WaveFunctionCollapse.computeNeighbourStatesIntersection(
                zBackward,
                cellIndex,
                'zBackward',
                self.stateSpace,
            ))
        zForward = ivec3(x, y, z + 1)
        if z < self.stateSpaceSize.z - 1 and (x, y, z + 1) not in self.workList:
            nextTasks.update(WaveFunctionCollapse.computeNeighbourStatesIntersection(
                zForward,
                cellIndex,
                'zForward',
                self.stateSpace,
            ))

        return nextTasks

    @staticmethod
    def computeNeighbourStatesIntersection(
        neighbourCellIndex: ivec3,
        cellIndex: ivec3,
        axis: str,
        stateSpace: Dict[ivec3, OrderedSet[StructureRotation]],
    ) -> Dict[ivec3, OrderedSet[StructureRotation]]:
        return {
            neighbourCellIndex:
            stateSpace[neighbourCellIndex].intersection(WaveFunctionCollapse.computeNeighbourStates(
                cellIndex,
                axis,
                stateSpace,
            ))
        }

    @staticmethod
    def computeNeighbourStates(
        cellIndex: ivec3,
        axis: str,
        stateSpace: Dict[ivec3, OrderedSet[StructureRotation]],
    ) -> Set[StructureRotation]:
        allowedStates: Set[StructureRotation] = set()
        for s in stateSpace[cellIndex]:
            allowedStates.update(globals.adjacencies[s.structureName].adjacentStructures(
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
    
    @property
    def structuresUsed(self) -> Iterator[StructureRotation]:
        for cellState in self.stateSpace.values():
            yield cellState[0]

    def collapseVolumeEdgeToAir(self):
        for index in self.stateSpace.keys():
            if not (
                index.x > 0 and index.x < self.stateSpaceSize.x - 1 and
                index.z > 0 and index.z < self.stateSpaceSize.z - 1
            ):
                self.stateSpace[index] = OrderedSet(Adjacency.getAllRotations(structureName='air'))


def startWFCInstance(
    attempt: int,
    volumeGrid: ivec3,
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
    volumeGrid: ivec3,
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
    volumeGrid: ivec3,
    structureWeights: Dict[str, float],
    initFunction: Callable[[WaveFunctionCollapse], None] | None,
    validationFunction: Callable[[WaveFunctionCollapse], bool] | None,
    maxAttempts: int = 10000,
) -> WaveFunctionCollapse:
    wfc = WaveFunctionCollapse(
        volumeGrid=volumeGrid,
        structureWeights=structureWeights,
        initFunction=initFunction,
        validationFunction=validationFunction,
        rngSeed=globals.rngSeed,
    )
    attempt = 1
    print(f'WFC collapse attempt {attempt}')
    while not wfc.collapse():
        wfc.setupRNG(globals.rngSeed + attempt)
        wfc.initStateSpaceWithDefaultDomain()
        if initFunction:
            wfc.initFunction(wfc)
        attempt += 1
        if attempt > maxAttempts:
            raise Exception(f'WFC did not collapse after {maxAttempts} retries.')
        print(f'WFC collapse attempt {attempt}')
    print(f'WFC collapsed after {attempt} attempts')
    return wfc
