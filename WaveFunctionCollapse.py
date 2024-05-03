from __future__ import annotations

import itertools
from typing import Tuple, Callable, Union, List, Iterator, Dict, Set

import numpy as np
from glm import ivec3
from ordered_set import OrderedSet

import Adjacency
import globals
from Adjacency import StructureRotation, StructureAdjacency
from StructureBase import Structure


class WaveFunctionCollapse:

    structureAdjacencies: Dict[str, StructureAdjacency]
    stateSpaceSize: Tuple[int, int, int]
    stateSpace: List[List[List[OrderedSet[StructureRotation]]]]
    workList: Dict[Tuple[int, int, int], OrderedSet[StructureRotation]]

    def __init__(
        self,
        volumeGrid: Tuple[int, int, int],
    ):

        self.workList = dict()

        self.stateSpaceSize = volumeGrid
        self.stateSpace = np.full(shape=self.stateSpaceSize, fill_value=None).tolist()

        if not self.stateSpaceSize >= (1, 1, 1):
            raise ValueError('State space size should be at least (1, 1, 1)')
        print('WFC state space {}x{}x{}'.format(*self.stateSpaceSize))

        self.structureAdjacencies = globals.adjacencies
        self.defaultDomain = OrderedSet(
            StructureRotation(structureName, rotation)
            for structureName, rotation in itertools.product(self.structureAdjacencies.keys(), range(4))
        )

        self.initStateSpaceWithDefaultDomain()

    def initStateSpaceWithDefaultDomain(self):
        self.stateSpace = np.full(shape=self.stateSpaceSize, fill_value=None).tolist()
        for x, y, z in self.cellCoordinates:
            self.stateSpace[x][y][z] = self.defaultDomain.copy()

    @property
    def cellCoordinates(self) -> Iterator[Tuple[int, int, int]]:
        for x in range(self.stateSpaceSize[0]):
            for y in range(self.stateSpaceSize[1]):
                for z in range(self.stateSpaceSize[2]):
                    yield x, y, z

    @property
    def uncollapsedCellIndicies(self) -> Iterator[Tuple[int, int, int]]:
        for x, y, z in self.cellCoordinates:
            cell = self.stateSpace[x][y][z]
            if len(cell) > 1:
                yield x, y, z

    def getCellIndicesWithEntropy(self, entropy: int = 1) -> Iterator[Tuple[int, int, int]]:
        for x, y, z in self.cellCoordinates:
            cell = self.stateSpace[x][y][z]
            if len(cell) == entropy:
                yield x, y, z

    @property
    def lowestEntropy(self) -> int:
        minEntrophy = len(self.defaultDomain) + 1
        for x, y, z in self.cellCoordinates:
            cell = self.stateSpace[x][y][z]
            entrophySize = len(cell)
            if entrophySize < minEntrophy and entrophySize != 1:
                minEntrophy = entrophySize
        return minEntrophy

    @staticmethod
    def getRandomStateFromSuperposition(cellSuperPosition: OrderedSet) -> StructureRotation:
        assert len(cellSuperPosition) > 1
        # TODO implement weighting
        return globals.rng.choice(cellSuperPosition)

    @property
    def randomUncollapsedCellIndex(self) -> Tuple[int, int, int]:
        nextCellsToCollapse = []
        for x, y, z in self.uncollapsedCellIndicies:
            nextCellsToCollapse.append((x, y, z))
        return globals.rng.choice(nextCellsToCollapse)

    @property
    def isCollapsed(self) -> bool:
        return len(list(self.getCellIndicesWithEntropy(entropy=1))) == (
            self.stateSpaceSize[0] * self.stateSpaceSize[1] * self.stateSpaceSize[2]
        )

    def collapseWithRetry(
            self,
            maxRetries=1000,
            reinit: Union[Callable, None] = None,
            validationFunction: Union[Callable[[WaveFunctionCollapse], bool], None] = None,
    ):
        attempts = 1

        self.initStateSpaceWithDefaultDomain()
        if reinit:
            reinit()

        while not self.collapse(validationFunction):
            self.initStateSpaceWithDefaultDomain()
            if reinit:
                reinit()
            print(f'WFC collapse attempt {attempts}')
            attempts += 1
            if attempts > maxRetries:
                raise Exception(f"WFC did not collapse after {maxRetries} retries.")

        print(f'WFC collapsed after {attempts} attempts')

    def collapse(self, validationFunction: Union[Callable[[WaveFunctionCollapse], bool], None] = None) -> bool:
        while not self.isCollapsed:
            minEntropy = self.lowestEntropy
            if minEntropy == 0:
                return False
            nextCellsToCollapse = list(self.getCellIndicesWithEntropy(minEntropy))
            assert len(nextCellsToCollapse) > 0
            x, y, z = globals.rng.choice(nextCellsToCollapse)

            stateSuperposition = self.stateSpace[x][y][z]
            collapsedState = self.getRandomStateFromSuperposition(stateSuperposition)
            self.collapseCellToState((x, y, z), collapsedState)
        if validationFunction:
            return validationFunction(self)
        return True

    def collapseCellToState(self, cellIndex: Tuple[int, int, int], structureToCollapse: StructureRotation):
        if cellIndex not in self.workList:
            self.workList[cellIndex] = OrderedSet([structureToCollapse])
        while len(self.workList) > 0:
            taskCellIndex, remainingStates = self.workList.popitem()
            newTasks = self.propagate(cellIndex=taskCellIndex, remainingStates=remainingStates)
            for newTaskCellIndex in newTasks:
                if newTaskCellIndex not in self.workList:
                    self.workList[newTaskCellIndex] = newTasks[newTaskCellIndex]

        x, y, z = cellIndex
        assert self.stateSpace[x][y][z] in (OrderedSet(), OrderedSet([structureToCollapse])), \
            f'Cell should have been set to {structureToCollapse} or {OrderedSet()} but is {self.stateSpace[x][y][z]}'

    def propagate(
        self,
        cellIndex: Tuple[int, int, int],
        remainingStates: OrderedSet[StructureRotation]
    ) -> Dict[Tuple[int, int, int], OrderedSet[StructureRotation]]:
        x, y, z = cellIndex
        nextTasks: Dict[Tuple[int, int, int], OrderedSet[StructureRotation]] = dict()
        if not remainingStates.issubset(self.stateSpace[x][y][z]):
            raise Exception(
                f'{x} {y} {z} tried to colapse a state to values not available in current superposition: '
                f'{remainingStates} ⊄ {self.stateSpace[x][y][z]}'
            )
        if set(remainingStates) == set(self.stateSpace[x][y][z]):
            # No change in states. No need to propagate further.
            return nextTasks

        # Update cell to new collapsed state
        self.stateSpace[x][y][z] = remainingStates

        if x > 0:
            neighbourRemainingStates = self.stateSpace[x - 1][y][z].intersection(
                self.computeNeighbourStates(cellIndex, 'xBackward')
            )
            nextTasks[(x - 1, y, z)] = neighbourRemainingStates
        if x < self.stateSpaceSize[0] - 1:
            neighbourRemainingStates = self.stateSpace[x + 1][y][z].intersection(
                self.computeNeighbourStates(cellIndex, 'xForward')
            )
            nextTasks[(x + 1, y, z)] = neighbourRemainingStates

        if y > 0:
            neighbourRemainingStates = self.stateSpace[x][y - 1][z].intersection(
                self.computeNeighbourStates(cellIndex, 'yBackward')
            )
            nextTasks[(x, y - 1, z)] = neighbourRemainingStates
        if y < self.stateSpaceSize[1] - 1:
            neighbourRemainingStates = self.stateSpace[x][y + 1][z].intersection(
                self.computeNeighbourStates(cellIndex, 'yForward')
            )
            nextTasks[(x, y + 1, z)] = neighbourRemainingStates

        if z > 0:
            neighbourRemainingStates = self.stateSpace[x][y][z - 1].intersection(
                self.computeNeighbourStates(cellIndex, 'zBackward')
            )
            nextTasks[(x, y, z - 1)] = neighbourRemainingStates
        if z < self.stateSpaceSize[2] - 1:
            neighbourRemainingStates = self.stateSpace[x][y][z + 1].intersection(
                self.computeNeighbourStates(cellIndex, 'zForward')
            )
            nextTasks[(x, y, z + 1)] = neighbourRemainingStates

        return nextTasks

    def computeNeighbourStates(self, cellIndex: Tuple[int, int, int], axis: str) -> Set[StructureRotation]:
        x, y, z = cellIndex
        allowedStates: Set[StructureRotation] = set()
        for s in self.stateSpace[x][y][z]:
            allowedStates = allowedStates.union(self.structureAdjacencies[s.structureName].adjacentStructures(
                axis,
                s.rotation
            ))
        return allowedStates

    def getCollapsedState(self, buildVolumeOffset: ivec3 = ivec3(0, 0, 0)) -> Iterator[Structure]:
        if not self.isCollapsed:
            raise Exception('WFC is not fully collapsed yet! Therefore the state cannot yet be extracted.')
        for x, y, z in self.cellCoordinates:
            cellState: StructureRotation = self.stateSpace[x][y][z][0]
            if cellState.structureName not in globals.structureFolders:
                raise Exception(f'Structure file {cellState.structureName} not found in {globals.structureFolders}')
            structureFolder = globals.structureFolders[cellState.structureName]
            structureInstance: Structure = structureFolder.structureClass(
                withRotation=cellState.rotation,
                tile=ivec3(x, y, z),
                offset=buildVolumeOffset,
            )
            yield structureInstance
    
    @property
    def structuresUsed(self) -> Iterator[StructureRotation]:
        for x, y, z in self.cellCoordinates:
            yield self.stateSpace[x][y][z][0]

    def collapseVolumeEdgeToAir(self):
        for x, y, z in self.cellCoordinates:
            if not (x > 0 and x < self.stateSpaceSize[0] - 1 and z > 0 and z < self.stateSpaceSize[2] - 1):
                self.stateSpace[x][y][z] = OrderedSet(Adjacency.getAllRotations(structureName='air'))
