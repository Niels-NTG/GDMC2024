from __future__ import annotations

import itertools
from typing import Tuple, Callable, Union, Iterator, Dict, Set, List

from glm import ivec3
from ordered_set import OrderedSet

import Adjacency
import globals
from Adjacency import StructureRotation, StructureAdjacency
from StructureBase import Structure


class WaveFunctionCollapse:

    structureAdjacencies: Dict[str, StructureAdjacency]
    stateSpaceSize: Tuple[int, int, int]
    stateSpace: Dict[Tuple[int, int, int], OrderedSet[StructureRotation]]
    workList: Dict[Tuple[int, int, int], OrderedSet[StructureRotation]]

    def __init__(
        self,
        volumeGrid: Tuple[int, int, int],
    ):

        self.workList = dict()

        self.stateSpaceSize = volumeGrid
        self.stateSpace = dict()

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
        self.stateSpace.clear()
        for x, y, z in self.cellCoordinates:
            self.stateSpace[(x, y, z)] = self.defaultDomain.copy()

    @property
    def cellCoordinates(self) -> Iterator[Tuple[int, int, int]]:
        for x in range(self.stateSpaceSize[0]):
            for y in range(self.stateSpaceSize[1]):
                for z in range(self.stateSpaceSize[2]):
                    yield x, y, z

    @property
    def uncollapsedCellIndicies(self) -> Iterator[Tuple[int, int, int]]:
        for cellIndex, cellState in self.stateSpace.items():
            if len(cellState) > 1:
                yield cellIndex

    def getCellIndicesWithEntropy(self, entropy: int = 1) -> Iterator[Tuple[int, int, int]]:
        for cellIndex, cellState in self.stateSpace.items():
            if len(cellState) == entropy:
                yield cellIndex

    @property
    def lowestEntropy(self) -> int:
        minEntrophy = len(self.defaultDomain) + 1
        for cellState in self.stateSpace.values():
            entrophySize = len(cellState)
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
        return globals.rng.choice(list(self.uncollapsedCellIndicies))

    @property
    def isCollapsed(self) -> bool:
        return len(list(self.getCellIndicesWithEntropy(entropy=1))) == len(self.stateSpace)

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

            nextCellIndex = globals.rng.choice(nextCellsToCollapse)
            nextCellIndex = (nextCellIndex[0], nextCellIndex[1], nextCellIndex[2])

            nextCellState = self.stateSpace[nextCellIndex]
            collapsedState = self.getRandomStateFromSuperposition(nextCellState)
            self.collapseCellToState(nextCellIndex, collapsedState)

        if validationFunction:
            return validationFunction(self)
        return True

    def collapseCellToState(self, cellIndex: Tuple[int, int, int], structureToCollapse: StructureRotation):
        if cellIndex not in self.workList:
            self.workList[cellIndex] = OrderedSet([structureToCollapse])
        while len(self.workList) > 0:
            taskCellIndex, remainingStates = self.workList.popitem()
            newTasks = self.propagate(
                cellIndex=taskCellIndex,
                remainingStates=remainingStates,
            )
            for newTaskCellIndex in newTasks:
                if newTaskCellIndex not in self.workList:
                    self.workList[newTaskCellIndex] = newTasks[newTaskCellIndex]

        assert self.stateSpace[cellIndex] in (OrderedSet(), OrderedSet([structureToCollapse])), \
            f'Cell should have been set to {structureToCollapse} or {OrderedSet()} but is {self.stateSpace[cellIndex]}'

    def propagate(
        self,
        cellIndex: Tuple[int, int, int],
        remainingStates: OrderedSet[StructureRotation],
    ) -> Dict[Tuple[int, int, int], OrderedSet[StructureRotation]]:
        x, y, z = cellIndex
        nextTasks: Dict[Tuple[int, int, int], OrderedSet[StructureRotation]] = dict()
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

        if x > 0 and (x - 1, y, z) not in self.workList:
            nextTasks[(x - 1, y, z)] = self.computeNeighbourStatesIntersection((x - 1, y, z), cellIndex, 'xBackward')[1]
        if x < self.stateSpaceSize[0] - 1 and (x + 1, y, z) not in self.workList:
            nextTasks[(x + 1, y, z)] = self.computeNeighbourStatesIntersection((x + 1, y, z), cellIndex, 'xForward')[1]

        if y > 0 and (x, y - 1, z) not in self.workList:
            nextTasks[(x, y - 1, z)] = self.computeNeighbourStatesIntersection((x, y - 1, z), cellIndex, 'yBackward')[1]
        if y < self.stateSpaceSize[1] - 1 and (x, y + 1, z) not in self.workList:
            nextTasks[(x, y + 1, z)] = self.computeNeighbourStatesIntersection((x, y + 1, z), cellIndex, 'yForward')[1]

        if z > 0 and (x, y, z - 1) not in self.workList:
            nextTasks[(x, y, z - 1)] = self.computeNeighbourStatesIntersection((x, y, z - 1), cellIndex, 'zBackward')[1]
        if z < self.stateSpaceSize[2] - 1 and (x, y, z + 1) not in self.workList:
            nextTasks[(x, y, z + 1)] = self.computeNeighbourStatesIntersection((x, y, z + 1), cellIndex, 'zForward')[1]

        return nextTasks

    def computeNeighbourStatesIntersection(
        self,
        neighbourCellIndex: Tuple[int, int, int],
        cellIndex: Tuple[int, int, int],
        axis: str
    ) -> Tuple[Tuple[int, int, int], OrderedSet[StructureRotation]]:
        return (
            neighbourCellIndex,
            self.stateSpace[neighbourCellIndex].intersection(self.computeNeighbourStates(cellIndex, axis))
        )

    def computeNeighbourStates(self, cellIndex: Tuple[int, int, int], axis: str) -> Set[StructureRotation]:
        allowedStates: Set[StructureRotation] = set()
        for s in self.stateSpace[cellIndex]:
            allowedStates.update(self.structureAdjacencies[s.structureName].adjacentStructures(
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
        for x, y, z in self.stateSpace.keys():
            if not (x > 0 and x < self.stateSpaceSize[0] - 1 and z > 0 and z < self.stateSpaceSize[2] - 1):
                self.stateSpace[(x, y, z)] = OrderedSet(Adjacency.getAllRotations(structureName='air'))
