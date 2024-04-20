import itertools
from typing import Tuple, Callable, Union, Set, List, Iterator

import numpy as np
from glm import ivec3

import globals
from Adjacency import StructureRotation
from StructureBase import Structure


class WaveFunctionCollapse:

    stateSpaceSize: Tuple[int, int, int]
    stateSpace: List[List[List[Set[StructureRotation]]]]

    def __init__(
        self,
        volumeGrid: Tuple[int, int, int],
    ):
        self.stateSpaceSize = volumeGrid
        self.stateSpace = np.full(shape=self.stateSpaceSize, fill_value=set()).tolist()

        if not self.stateSpaceSize >= (1, 1, 1):
            raise ValueError('State space size should be at least (1, 1, 1)')

        self.structureAdjacencies = globals.adjacencies
        self.superPosition = set(
            StructureRotation(structureName, rotation)
            for structureName, rotation in itertools.product(self.structureAdjacencies.keys(), range(4))
        )

        self.initStateSpaceSuperPosition()

    def initStateSpaceSuperPosition(self):
        self.stateSpace = np.full(shape=self.stateSpaceSize, fill_value=self.superPosition.copy()).tolist()

    def cellCoordinates(self) -> Iterator[Tuple[int, int, int]]:
        for x in range(self.stateSpaceSize[0]):
            for y in range(self.stateSpaceSize[1]):
                for z in range(self.stateSpaceSize[2]):
                    yield x, y, z

    def getUncollapsedCellIndicies(self) -> Iterator[Tuple[int, int, int]]:
        for x, y, z in self.cellCoordinates():
            cell = self.stateSpace[x][y][z]
            if len(cell) > 1:
                yield x, y, z

    def getCellIndicesWithEntropy(self, entropy: int = 1) -> Iterator[Tuple[int, int, int]]:
        for x, y, z in self.cellCoordinates():
            cell = self.stateSpace[x][y][z]
            if len(cell) == entropy:
                yield x, y, z

    def getLowestEntropy(self) -> int:
        minEntrophy = len(self.superPosition) + 1
        for x, y, z in self.cellCoordinates():
            cell = self.stateSpace[x][y][z]
            entrophySize = len(cell)
            if entrophySize < minEntrophy and entrophySize != 1:
                minEntrophy = entrophySize
        return minEntrophy

    @staticmethod
    def getRandomStateFromSuperposition(cellSuperPosition: Set) -> StructureRotation:
        assert len(cellSuperPosition) > 1
        # TODO implement weighting
        return globals.rng.choice(list(cellSuperPosition))

    def getRandomUncollapsedCellIndex(self) -> Tuple[int, int, int]:
        nextCellsToCollapse = list(self.getUncollapsedCellIndicies())
        return globals.rng.choice(nextCellsToCollapse)

    def isCollapsed(self) -> bool:
        return len(list(self.getCellIndicesWithEntropy(entropy=1))) == (
            self.stateSpaceSize[0] * self.stateSpaceSize[1] * self.stateSpaceSize[2]
        )

    def collapseWithRetry(self, maxRetries=100, reinit: Union[Callable, None] = None) -> int:
        attempts = 0

        if reinit:
            reinit()

        while not self.collapse():
            self.initStateSpaceSuperPosition()
            if reinit:
                reinit()
            attempts += 1
            if attempts > maxRetries:
                raise Exception(f"WFC did not collapse after {maxRetries} retries.")

        return attempts

    def collapse(self) -> bool:
        while not self.isCollapsed():
            minEntropy = self.getLowestEntropy()
            if minEntropy == 0:
                return False
            nextCellsToCollapse = list(self.getCellIndicesWithEntropy(minEntropy))
            assert len(nextCellsToCollapse) > 0
            x, y, z = globals.rng.choice(nextCellsToCollapse)

            stateSuperposition = set(self.stateSpace[x][y][z])
            collapsedState = self.getRandomStateFromSuperposition(stateSuperposition)
            self.collapseCellToState((x, y, z), collapsedState)
        return True

    def collapseRandomCell(self):
        x, y, z = self.getRandomUncollapsedCellIndex()
        cellSuperPosition = self.stateSpace[x][y][z]
        collapsedState = self.getRandomStateFromSuperposition(cellSuperPosition)
        self.collapseCellToState((x, y, z), collapsedState)

    def collapseCellToState(self, cellIndex: Tuple[int, int, int], structureToCollapse: StructureRotation):
        self.propagate(cellIndex, {structureToCollapse})

        x, y, z = cellIndex
        assert self.stateSpace[x][y][z] in (set(), {structureToCollapse}), \
            f'This cell should have been set to {structureToCollapse} or {set()} but is {self.stateSpace[x][y][z]}'

    def propagate(self, cellIndex: Tuple[int, int, int], remainingStates: Set[StructureRotation]):
        if len(remainingStates) == 0:
            return
        x, y, z = cellIndex
        if not remainingStates.issubset(self.stateSpace[x][y][z]):
            raise Exception(
                f'{x} {y} {z} tried to colapse a state to values not available in current superposition: '
                f'{remainingStates} ⊄ {self.stateSpace[x][y][z]}'
            )
        if remainingStates == self.stateSpace[x][y][z]:
            # No change in states. No need to propagate further.
            return

        # Update cell to new collapsed state
        self.stateSpace[x][y][z] = remainingStates

        def computeNeighbourStates(axis: str):
            allowedStates: Set[StructureRotation] = set()
            for s in self.stateSpace[x][y][z]:
                allowedStates = allowedStates.union(set(self.structureAdjacencies[s.structureName].adjacentStructures(
                    axis,
                    s.rotation
                )))
            return allowedStates

        if x > 0:
            neighbourRemainingStates = computeNeighbourStates("xBackward").intersection(self.stateSpace[x - 1][y][z])
            self.propagate(cellIndex=(x - 1, y, z), remainingStates=neighbourRemainingStates)
        if x < self.stateSpaceSize[0] - 1:
            neighbourRemainingStates = computeNeighbourStates("xForward").intersection(self.stateSpace[x + 1][y][z])
            self.propagate(cellIndex=(x + 1, y, z), remainingStates=neighbourRemainingStates)
        if y > 0:
            neighbourRemainingStates = computeNeighbourStates("yBackward").intersection(self.stateSpace[x][y - 1][z])
            self.propagate(cellIndex=(x, y - 1, z), remainingStates=neighbourRemainingStates)
        if y < self.stateSpaceSize[1] - 1:
            neighbourRemainingStates = computeNeighbourStates("yForward").intersection(self.stateSpace[x][y + 1][z])
            self.propagate(cellIndex=(x, y + 1, z), remainingStates=neighbourRemainingStates)
        if z > 0:
            neighbourRemainingStates = computeNeighbourStates("zBackward").intersection(self.stateSpace[x][y][z - 1])
            self.propagate(cellIndex=(x, y, z - 1), remainingStates=neighbourRemainingStates)
        if z < self.stateSpaceSize[2] - 1:
            neighbourRemainingStates = computeNeighbourStates("zForward").intersection(self.stateSpace[x][y][z + 1])
            self.propagate(cellIndex=(x, y, z + 1), remainingStates=neighbourRemainingStates)

    def getCollapsedState(self, buildVolumeOffset: ivec3 = ivec3(0, 0, 0)) -> Iterator[Structure]:
        if not self.isCollapsed():
            raise Exception('WFC is not fully collapsed yet! Therefore the state cannot yet be extracted.')
        for x, y, z in self.cellCoordinates():
            cellState: StructureRotation = list(self.stateSpace[x][y][z])[0]
            if cellState.structureName not in globals.structureFolders:
                raise Exception(f'Structure file {cellState.structureName} not found in {globals.structureFolders}')
            structureFolder = globals.structureFolders[cellState.structureName]
            structureInstance: Structure = structureFolder.structureClass(
                withRotation=cellState.rotation,
                tile=ivec3(x, y, z),
                offset=buildVolumeOffset,
            )
            yield structureInstance
    
    def getStructuresUsed(self) -> Iterator[StructureRotation]:
        for x, y, z in self.cellCoordinates():
            yield list(self.stateSpace[x][y][z])[0]    

    def collapseVolumeEdgeToAir(self):
        for x in range(self.stateSpaceSize[0]):
            lastZ = self.stateSpaceSize[2] - 1
            self.collapseCellToState((x, 0, 0), StructureRotation(structureName='air', rotation=0))
            self.collapseCellToState((x, 0, lastZ), StructureRotation(structureName='air', rotation=0))
        for z in range(self.stateSpaceSize[2]):
            lastX = self.stateSpaceSize[0] - 1
            self.collapseCellToState((0, 0, z), StructureRotation(structureName='air', rotation=0))
            self.collapseCellToState((lastX, 0, z), StructureRotation(structureName='air', rotation=0))
