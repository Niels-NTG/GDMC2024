from __future__ import annotations

import itertools
import os
from concurrent.futures import ProcessPoolExecutor, Future
from copy import deepcopy
from typing import Tuple, Callable, Iterator, Dict, Set

import numpy as np
from glm import ivec3
from numpy.random import Generator
from ordered_set import OrderedSet

import Adjacency
import globals
import vectorTools
from Adjacency import StructureRotation, StructureAdjacency
from gdpc.src.gdpc import Box


class WaveFunctionCollapse:

    stateSpace: Dict[ivec3, OrderedSet[StructureRotation]]
    lockedTiles: Dict[ivec3, bool]
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
        initFunction: Callable[[WaveFunctionCollapse], None] | None = None,
        validationFunction: Callable[[WaveFunctionCollapse], bool] | None = None,
        rngSeed: int | None = None,
    ):
        self.stateSpaceBox = volumeGrid
        if not volumeGrid.size >= ivec3(1, 1, 1):
            raise ValueError('State space size should be at least (1, 1, 1)')

        self.stateSpace = dict()
        self.lockedTiles = dict()

        self.structureWeights = structureWeights

        # Setup default list of adjacencies and cell domain
        self.defaultAdjacencies = self.createDefaultAdjacencies()
        self.defaultDomain = self.createDefaultDomain()

        self.setupRNG(rngSeed)

        self.initFunction = initFunction
        self.validationFunction = validationFunction

        self.workList = dict()
        self.firstPositions = set()

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
            self.lockedTiles[index] = False

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

            if len(self.firstPositions) > 0:
                nextCellIndex = self.firstPositions.pop()
                if len(self.stateSpace[nextCellIndex]) == 1:
                    continue

            nextCellState = self.stateSpace[nextCellIndex]
            collapsedState = self.getRandomStateFromSuperposition(nextCellState)

            self.collapseCellToState(nextCellIndex, collapsedState)

        if self.validationFunction:
            return self.validationFunction(self)
        return True

    def collapseRandomCell(self):
        cellCellIndex = self.randomUncollapsedCellIndex
        nextCellState = self.stateSpace[cellCellIndex]
        collapsedState = self.getRandomStateFromSuperposition(nextCellState)
        self.collapseCellToState(cellCellIndex, collapsedState)

    def collapseCellToState(self, cellIndex: ivec3, structureToCollapse: StructureRotation):
        self.workList[cellIndex] = OrderedSet([structureToCollapse])
        while len(self.workList) > 0:
            if self.lowestEntropy == 0:
                self.workList.clear()
                break
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

        if not self.lockedTiles[cellIndex]:
            # Update cell to new collapsed state
            self.stateSpace[cellIndex] = remainingStates

        xForward, axis = Adjacency.getPositionFromAxis('xForward', cellIndex)
        if cellIndex.x < self.stateSpaceBox.last.x and xForward not in self.workList:
            nextTasks.update(self.computeNeighbourStatesIntersection(
                xForward,
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

        xBackward, axis = Adjacency.getPositionFromAxis('xBackward', cellIndex)
        if cellIndex.x > self.stateSpaceBox.begin.x and xBackward not in self.workList:
            nextTasks.update(self.computeNeighbourStatesIntersection(
                xBackward,
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

        return nextTasks

    def computeNeighbourStatesIntersection(
        self,
        neighbourCellIndex: ivec3,
        cellIndex: ivec3,
        axis: str,
    ) -> Dict[ivec3, OrderedSet[StructureRotation]]:
        return {
            neighbourCellIndex: self.stateSpace[neighbourCellIndex].intersection(self.computeNeighbourStates(
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
    onResolve: Callable[[WaveFunctionCollapse], None],
    maxAttempts: int = 1000,
) -> WaveFunctionCollapse:
    executor = ProcessPoolExecutor()
    wfcResult: WaveFunctionCollapse | None = None
    attempt = 1

    def createFuture():
        nonlocal attempt
        if attempt >= maxAttempts:
            executor.shutdown(wait=False, cancel_futures=True)
            raise Exception(f'WFC did not collapse after {maxAttempts} retries.')
        try:
            future: Future = executor.submit(
                startWFCInstance,
                attempt,
                volumeGrid,
                structureWeights,
                initFunction,
                validationFunction,
            )
            future.add_done_callback(futureCallback)
            attempt += 1
        except RuntimeError:
            print('Shutting down remaining attempts…')

    def futureCallback(f: Future):
        nonlocal wfcResult
        if wfcResult:
            f.cancel()
            return
        newWfcResultIsCollapsed, wfc, lastAttempt = f.result()
        if newWfcResultIsCollapsed:
            executor.shutdown(wait=False, cancel_futures=True)
            wfcResult = wfc
            print(f'WFC attempt {lastAttempt} HAS collapsed!')
            onResolve(wfc)
            return
        print(f'WFC attempt {lastAttempt} did NOT collapse')
        # Create a new future after a previous future has not resulted in a collapsed state.
        createFuture()

    for initialAttempt in range(1, min(maxAttempts, os.cpu_count() + 1)):
        createFuture()
    while wfcResult is None:
        pass

    return wfcResult


def startSingleThreadedWFC(
    volumeGrid: Box,
    structureWeights: Dict[str, float],
    initFunction: Callable[[WaveFunctionCollapse], None] | None,
    validationFunction: Callable[[WaveFunctionCollapse], bool] | None,
    onResolve: Callable[[WaveFunctionCollapse], None],
    maxAttempts: int = 10000,
) -> WaveFunctionCollapse:
    attempt = 0
    isCollapsed = False
    wfc = None
    while not isCollapsed:
        attempt += 1
        isCollapsed, wfc, _ = startWFCInstance(
            attempt=attempt,
            volumeGrid=volumeGrid,
            structureWeights=structureWeights,
            initFunction=initFunction,
            validationFunction=validationFunction,
        )
        if attempt > maxAttempts:
            raise Exception(f'WFC did not collapse after {maxAttempts} retries.')
    print(f'WFC collapsed after {attempt} attempts')
    onResolve(wfc)
    return wfc
