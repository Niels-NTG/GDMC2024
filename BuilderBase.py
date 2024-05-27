from copy import deepcopy
from typing import Dict, List, Set, Iterator

import numpy as np
from glm import ivec3
from ordered_set import OrderedSet
from termcolor import cprint

import Adjacency
import globals
import vectorTools
from Adjacency import StructureAdjacency, StructureRotation
from StructureBase import Structure
from WaveFunctionCollapse import WaveFunctionCollapse, startMultiThreadedWFC
from gdpc.src.gdpc import Box


class Builder:

    allStateSpace: Dict[ivec3, OrderedSet[StructureRotation]]
    allDefaultAdjacencies: Dict[str, StructureAdjacency]
    subGridVolumes: List[Box]
    volumeGrid: Box

    def __init__(
        self,
        volume: Box,
        tileSize: ivec3 = ivec3(5, 10, 5),
    ):

        self.volume = volume

        self.allStateSpace = dict()
        self.allDefaultAdjacencies = dict()
        self.subGridVolumes = []

        self.volumeGrid = Box(size=volume.size // tileSize)
        print(f'Running WFC in volume {self.volumeGrid.size.x}x{self.volumeGrid.size.y}x{self.volumeGrid.size.z}')

        subGridVolume1 = vectorTools.intersectionBox(Box(
            offset=self.volumeGrid.offset,
            size=ivec3(13, 1, 13),
        ), self.volumeGrid)
        cprint(f'Running WFC 1 on box {subGridVolume1}', 'magenta', 'on_light_grey')
        startMultiThreadedWFC(
            volumeGrid=subGridVolume1,
            initFunction=self.reinitWFC,
            validationFunction=Builder.isValid,
            structureWeights=Builder.generateWeights(),
            onResolve=self.onResolve,
        )

        subGridVolume2 = vectorTools.intersectionBox(Box(
            offset=ivec3(
                subGridVolume1.last.x,
                subGridVolume1.offset.y,
                subGridVolume1.offset.z,
            ),
            size=ivec3(13, 1, 13),
        ), self.volumeGrid)
        cprint(f'Running WFC 2 on box {subGridVolume2}', 'magenta', 'on_light_grey')
        startMultiThreadedWFC(
            volumeGrid=subGridVolume2,
            initFunction=self.reinitWFC,
            validationFunction=Builder.isValid,
            structureWeights=Builder.generateWeights(),
            onResolve=self.onResolve,
        )

        subGridVolume3 = vectorTools.intersectionBox(Box(
            offset=ivec3(
                subGridVolume2.last.x,
                subGridVolume2.offset.y,
                subGridVolume2.offset.z,
            ),
            size=ivec3(13, 1, 13),
        ), self.volumeGrid)
        cprint(f'Running WFC 3 on box {subGridVolume3}', 'magenta', 'on_light_grey')
        startMultiThreadedWFC(
            volumeGrid=subGridVolume3,
            initFunction=self.reinitWFC,
            validationFunction=Builder.isValid,
            structureWeights=Builder.generateWeights(),
            onResolve=self.onResolve,
        )

        self.removeOrphanedBuildings()
        self.buildStructure(volume.offset)


    def reinitWFC(self, wfc: WaveFunctionCollapse):
        self.collapseVolumeEdgeToAir(wfc)
        intersectionPositions = set()
        for otherVolumeGrid in self.subGridVolumes:
            intersectionBox = vectorTools.intersectionBox(wfc.stateSpaceBox, otherVolumeGrid)
            if intersectionBox:
                intersectionPositions.update(set(vectorTools.boxPositions(intersectionBox)))
        for index in intersectionPositions:
            wfc.stateSpace[index] = deepcopy(self.allStateSpace[index])
            wfc.lockedTiles[index] = True
        for index in intersectionPositions:
            for axis in Adjacency.ROTATIONAL_AXES:
                neighbourCellIndex = Adjacency.getPositionFromAxis(axis, index)[0]
                if neighbourCellIndex in wfc.stateSpace and len(wfc.stateSpace[neighbourCellIndex]) > 1:
                    wfc.stateSpace[neighbourCellIndex] = wfc.stateSpace[neighbourCellIndex].intersection(
                        wfc.computeNeighbourStates(
                            index,
                            axis
                        )
                    )
        wfc.firstPositions = intersectionPositions

    def collapseVolumeEdgeToAir(self, wfc: WaveFunctionCollapse):
        for index in wfc.stateSpace:
            if not (
                index.x > self.volumeGrid.begin.x and index.x < self.volumeGrid.last.x and
                index.z > self.volumeGrid.begin.z and index.z < self.volumeGrid.last.z
            ) or index.y == self.volumeGrid.last.y:
                wfc.stateSpace[index] = OrderedSet(Adjacency.getAllRotations(structureName='air'))

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
    def isValid(wfc: WaveFunctionCollapse) -> bool:
        structuresUsed = set(wfc.structuresUsed)
        isAirOnly = structuresUsed.issubset(Adjacency.getAllRotations('air'))
        if isAirOnly:
            print('Invalid WFC result! Volume has only air!')
            return False
        # isCeilingOnly = structuresUsed.issubset(Adjacency.getAllRotations('ceiling'))
        return True

    def onResolve(self, wfc: WaveFunctionCollapse):
        self.allStateSpace.update(wfc.stateSpace)
        self.allDefaultAdjacencies.update(wfc.defaultAdjacencies)
        self.subGridVolumes.append(wfc.stateSpaceBox)

    def scanForBuildings(self) -> List[Set[ivec3]]:
        buildings: List[Set[ivec3]] = []
        newBuilding: Set[ivec3] = set()
        cellsVisited: Set[ivec3] = set()
        stateSpaceKeys: List[ivec3] = list(self.allStateSpace.keys())

        rng = np.random.default_rng(seed=globals.rngSeed)

        while len(cellsVisited) != len(self.allStateSpace):
            # noinspection PyTypeChecker
            randomIndex = ivec3(rng.choice(stateSpaceKeys))
            if randomIndex in cellsVisited:
                continue

            if self.allStateSpace[randomIndex][0].structureName.endswith('air'):
                cellsVisited.add(randomIndex)
                continue

            scanWorkList: List[ivec3] = [randomIndex]
            while len(scanWorkList) > 0:
                cellIndex = scanWorkList.pop()
                if cellIndex in cellsVisited:
                    continue

                cellState: StructureRotation = self.allStateSpace[cellIndex][0]
                if cellState.structureName.endswith('air'):
                    raise Exception(f'Wall leak found at {cellIndex} {cellState} in building {newBuilding}')

                openPositions: Set[ivec3] = self.allDefaultAdjacencies[cellState.structureName].getNonWallPositions(
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

    def removeOrphanedBuildings(self):
        buildings = self.scanForBuildings()
        print(f'Found {len(buildings)} distinct buildings, removing orphaned buildings…')
        largestBuilding = max(buildings, key=lambda x: len(x))
        for building in buildings:
            if building != largestBuilding:
                for pos in building:
                    self.allStateSpace[pos] = OrderedSet({StructureRotation(structureName='air', rotation=0)})

    def getCollapsedState(self, buildVolumeOffset: ivec3 = ivec3(0, 0, 0)) -> Iterator[Structure]:
        for cellIndex in self.allStateSpace:
            cellState: StructureRotation = self.allStateSpace[cellIndex][0]
            if cellState.structureName not in globals.structureFolders:
                raise Exception(f'Structure file {cellState.structureName} not found in {globals.structureFolders}')
            structureFolder = globals.structureFolders[cellState.structureName]
            structureInstance: Structure = structureFolder.structureClass(
                withRotation=cellState.rotation,
                tile=ivec3(*cellIndex),
                offset=buildVolumeOffset,
            )
            yield structureInstance

    def buildStructure(self, buildVolumeOffset: ivec3 = ivec3(0, 0, 0)):
        print('Placing tiles…')
        for building in self.getCollapsedState(buildVolumeOffset=buildVolumeOffset):
            building.place()
