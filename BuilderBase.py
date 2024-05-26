from copy import deepcopy
from typing import Dict, List, Set, Iterator

import numpy as np
from glm import ivec3
from ordered_set import OrderedSet

import Adjacency
from Adjacency import StructureAdjacency, StructureRotation
import globals
import vectorTools
from StructureBase import Structure
from WaveFunctionCollapse import WaveFunctionCollapse, startSingleThreadedWFC, startMultiThreadedWFC
from gdpc.src.gdpc import Box


class Builder:

    def __init__(
        self,
        volume: Box,
        tileSize: ivec3 = ivec3(5, 10, 5),
    ):

        self.volume = volume

        self.volumeGrid = Box(size=volume.size // tileSize)
        print(f'Running WFC in volume {self.volumeGrid.size.x}x{self.volumeGrid.size.y}x{self.volumeGrid.size.z}')

        self.volumeGrid1 = Box(
            offset=self.volumeGrid.offset,
            size=ivec3(12, 1, 12),
        )
        print(f'Running WFC 1 on box {self.volumeGrid1}')
        self.wfc1 = startMultiThreadedWFC(
            volumeGrid=self.volumeGrid1,
            initFunction=self.reinitWFC,
            validationFunction=Builder.isValid,
            structureWeights=Builder.generateWeights('noAtrium'),
            onResolve=None,
        )

        self.volumeGrid2 = Box(
            offset=ivec3(
                self.volumeGrid1.last.x,
                self.volumeGrid1.offset.y,
                self.volumeGrid1.offset.z,
            ),
            size=ivec3(12, 1, 12),
        )
        print(f'Running WFC 2 on box {self.volumeGrid2}')
        self.wfc2 = startMultiThreadedWFC(
            volumeGrid=self.volumeGrid2,
            initFunction=self.reinitWFC2,
            validationFunction=Builder.isValid,
            structureWeights=Builder.generateWeights('noCeiling'),
            onResolve=None,
        )

        completeStateSpace = self.wfc1.stateSpace | self.wfc2.stateSpace
        completeDefaultAdjacencies = self.wfc1.defaultAdjacencies | self.wfc2.defaultAdjacencies

        Builder.removeOrphanedBuildings(completeStateSpace, completeDefaultAdjacencies)
        Builder.buildStructure(completeStateSpace, volume.offset)


    @staticmethod
    def isValid(wfcInstance: WaveFunctionCollapse) -> bool:
        structuresUsed = set(wfcInstance.structuresUsed)
        isAirOnly = structuresUsed.issubset(Adjacency.getAllRotations('air'))
        if isAirOnly:
            print('Invalid WFC result! Volume has only air!')
            return False
        return True

    def reinitWFC(self, wfcInstance: WaveFunctionCollapse):
        self.collapseVolumeEdgeToAir(wfcInstance)

    def reinitWFC2(self, wfcInstance: WaveFunctionCollapse):
        self.collapseVolumeEdgeToAir(wfcInstance)
        intersectionBox = vectorTools.intersectionBox(wfcInstance.stateSpaceBox, self.wfc1.stateSpaceBox)
        if intersectionBox:
            intersectionPositions = set(vectorTools.boxPositions(intersectionBox))
            for index in intersectionPositions:
                wfcInstance.stateSpace[index] = deepcopy(self.wfc1.stateSpace[index])
                wfcInstance.lockedTiles[index] = True
            for index in intersectionPositions:
                neighbourCellIndex = ivec3(index.x + 1, index.y, index.z)
                wfcInstance.stateSpace[neighbourCellIndex] = wfcInstance.stateSpace[neighbourCellIndex].intersection(
                    wfcInstance.computeNeighbourStates(
                        index,
                        'xForward'
                    )
                )
            wfcInstance.firstPositions = intersectionPositions

    def collapseVolumeEdgeToAir(self, wfcInstance: WaveFunctionCollapse):
        for index in wfcInstance.stateSpace:
            if not (
                index.x > self.volumeGrid.begin.x and index.x < self.volumeGrid.last.x and
                index.z > self.volumeGrid.begin.z and index.z < self.volumeGrid.last.z
            ) or index.y == self.volumeGrid.last.y:
                wfcInstance.stateSpace[index] = OrderedSet(Adjacency.getAllRotations(structureName='air'))

    @staticmethod
    def generateWeights(condition: str = '') -> Dict[str, float]:
        match condition:
            case 'noAtrium':
                return globals.defaultStructureWeights | {
                    'balcony_corner': 0.0,
                    'balcony_l': 0.0,
                    'balcony_r': 0.0,
                    'balcony_l_inner': 0.0,
                    'balcony_r_inner': 0.0,
                    'balcony_middle_inner': 0.0,
                    'atrium_ceiling_edge': 0.0,
                    'atrium_ceiling_edge_corner': 0.0,
                    'atrium_ceiling_a': 0.0,
                    'atrium_ceiling_b': 0.0,
                    'atrium_ceiling_c': 0.0,
                    'atrium_ceiling_plants_a': 0.0,
                    'atrium_ceiling_plants_b': 0.0,
                    'atrium_ceiling_plants_c': 0.0,
                    'atrium_air': 0.0,
                }
            case 'noCeiling':
                return globals.defaultStructureWeights | {
                    'atrium_ceiling_edge': 0.0,
                    'atrium_ceiling_edge_corner': 0.0,
                    'atrium_ceiling_a': 0.0,
                    'atrium_ceiling_b': 0.0,
                    'atrium_ceiling_c': 0.0,
                    'atrium_ceiling_plants_a': 0.0,
                    'atrium_ceiling_plants_b': 0.0,
                    'atrium_ceiling_plants_c': 0.0,
                }
        print('No weight set preset specified')
        return globals.defaultStructureWeights

    @staticmethod
    def scanForBuildings(
        stateSpace: Dict[ivec3, OrderedSet[StructureRotation]],
        defaultAdjacencies: Dict[str, StructureAdjacency],
    ) -> List[Set[ivec3]]:
        buildings: List[Set[ivec3]] = []
        newBuilding: Set[ivec3] = set()
        cellsVisited: Set[ivec3] = set()
        stateSpaceKeys: Set[ivec3] = set(stateSpace.keys())

        rng = np.random.default_rng(seed=globals.rngSeed)

        while len(cellsVisited) != len(stateSpace):
            # noinspection PyTypeChecker
            randomIndex = ivec3(rng.choice(list(stateSpace.keys())))
            if randomIndex in cellsVisited:
                continue

            if stateSpace[randomIndex][0].structureName.endswith('air'):
                cellsVisited.add(randomIndex)
                continue

            scanWorkList: List[ivec3] = [randomIndex]
            while len(scanWorkList) > 0:
                cellIndex = scanWorkList.pop()
                if cellIndex in cellsVisited:
                    continue

                cellState: StructureRotation = stateSpace[cellIndex][0]
                if cellState.structureName.endswith('air'):
                    raise Exception(f'Wall leak found at {cellIndex} {cellState} in building {newBuilding}')

                openPositions: Set[ivec3] = defaultAdjacencies[cellState.structureName].getNonWallPositions(
                    cellState.rotation,
                    cellIndex,
                    stateSpaceKeys,
                )
                newBuilding.add(cellIndex)
                newBuilding.update(openPositions)
                scanWorkList.extend(openPositions)
                cellsVisited.add(cellIndex)
            buildings.append(newBuilding.copy())
            newBuilding.clear()

        return buildings

    @staticmethod
    def removeOrphanedBuildings(
        stateSpace: Dict[ivec3, OrderedSet[StructureRotation]],
        defaultAdjacencies: Dict[str, StructureAdjacency],
    ):
        buildings = Builder.scanForBuildings(stateSpace, defaultAdjacencies)
        print(f'Found {len(buildings)} distinct buildings, removing orphaned buildings…')
        largestBuilding = max(buildings, key=lambda x: len(x))
        for building in buildings:
            if building != largestBuilding:
                for pos in building:
                    stateSpace[pos] = OrderedSet({StructureRotation(structureName='air', rotation=0)})

    @staticmethod
    def getCollapsedState(
        stateSpace: Dict[ivec3, OrderedSet[StructureRotation]],
        buildVolumeOffset: ivec3 = ivec3(0, 0, 0),
    ) -> Iterator[Structure]:
        for cellIndex in stateSpace:
            cellState: StructureRotation = stateSpace[cellIndex][0]
            if cellState.structureName not in globals.structureFolders:
                raise Exception(f'Structure file {cellState.structureName} not found in {globals.structureFolders}')
            structureFolder = globals.structureFolders[cellState.structureName]
            structureInstance: Structure = structureFolder.structureClass(
                withRotation=cellState.rotation,
                tile=ivec3(*cellIndex),
                offset=buildVolumeOffset,
            )
            yield structureInstance

    @staticmethod
    def buildStructure(
        stateSpace: Dict[ivec3, OrderedSet[StructureRotation]],
        buildVolumeOffset: ivec3 = ivec3(0, 0, 0),
    ):
        print('Placing tiles…')
        for building in Builder.getCollapsedState(buildVolumeOffset=buildVolumeOffset, stateSpace=stateSpace):
            building.place()
