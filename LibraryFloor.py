from typing import Dict, List, Set, Iterator

import numpy as np
from glm import ivec3, ivec2
from ordered_set import OrderedSet
from termcolor import cprint

import Adjacency
import globals
import vectorTools
from Adjacency import StructureAdjacency, StructureRotation
from StructureBase import Structure
from WaveFunctionCollapse import WaveFunctionCollapse, startMultiThreadedWFC
from gdpc.src.gdpc import Box


class LibraryFloor:

    allStateSpace: Dict[ivec3, OrderedSet[StructureRotation]]
    allLockedTiles: dict[ivec3, bool]
    allDefaultAdjacencies: Dict[str, StructureAdjacency]
    subGridVolumes: List[Box]
    volumeGrid: Box
    volumeRotation: int

    def __init__(
        self,
        volume: Box,
        tileSize: ivec3 = ivec3(9, 10, 9),
        volumeRotation: int = 0,
    ):

        self.volume = volume

        self.allStateSpace = dict()
        self.allLockedTiles = dict()
        self.allDefaultAdjacencies = dict()
        self.subGridVolumes = []

        self.volumeGrid = Box(size=volume.size // tileSize)
        # Ensure volume is an odd number to make rotation easier.
        if self.volume.toRect().size % 2 == ivec2(0, 0):
            self.volumeGrid.size = self.volumeGrid.size + ivec3(1, 0, 1)
        # Ensure volume is flat
        self.volumeGrid.size.y = 1
        print(f'Running WFC in volume {self.volumeGrid.size.x}x{self.volumeGrid.size.y}x{self.volumeGrid.size.z}')

        self.volumeRotation = volumeRotation

        self.atriumBox = self.volumeGrid.centeredSubBox(ivec3(5, 1, 5))
        self.atriumExitPos1 = vectorTools.rotatePointAroundOrigin3D(
            self.atriumBox.middle,
            self.atriumBox.offset + ivec3(2, 0, 4),
            self.volumeRotation,
        )
        self.atriumExitPos2 = vectorTools.rotatePointAroundOrigin3D(
            self.atriumBox.middle,
            self.atriumBox.offset + ivec3(4, 0, 2),
            self.volumeRotation,
        )
        self.atriumExitPos3 = vectorTools.rotatePointAroundOrigin3D(
            self.atriumBox.middle,
            self.atriumBox.offset + ivec3(2, 0, 0),
            self.volumeRotation,
        )

        # TODO offset=ivec3(0, 0, self.atriumBox.last.z),
        #   - 23 attempts (x_junction only)
        #   - 15 attempts (x_junction + t_junction + book_hallway_outer)
        #   - 12 attempts without locking air tiles
        # TODO offset=self.volumeGrid.offset
        #   - 41 attempts without locking air tiles
        #   - 59 attempts without locking air tiles (replace book_hallway_outer with book_hallway_inner)

        subGrid1 = vectorTools.intersectionBox(Box(
            offset=self.volumeGrid.offset,
            size=self.volumeGrid.size,
        ), self.volumeGrid)
        cprint(f'Running WFC 1 on box {subGrid1}', 'magenta', 'on_light_grey')
        startMultiThreadedWFC(
            volumeGrid=subGrid1,
            initFunction=self.reinitWFC,
            validationFunction=self.isValid,
            structureWeights=self.generateWeights(),
            onResolve=self.onResolve,
        )

        self.removeOrphanedBuildings()
        self.buildStructure(volume.offset)

    def reinitWFC(self, wfc: WaveFunctionCollapse):
        self.collapseVolumeEdgeToAir(wfc)
        self.collapseCentralAtriumSpace(wfc)
        if wfc.lowestEntropy == 0:
            raise Exception('Init function created invalid state space')

    @staticmethod
    def collapseVolumeEdgeToAir(wfc: WaveFunctionCollapse):
        for index in vectorTools.getBoxWalls(wfc.stateSpaceBox):
            if index in wfc.stateSpace:
                wfc.stateSpace[index] = OrderedSet(Adjacency.getAllRotations(structureName='air'))

    def collapseCentralAtriumSpace(self, wfc: WaveFunctionCollapse):
        for index in wfc.cellCoordinates:
            if index == self.atriumExitPos1:
                wfc.stateSpace[index] = OrderedSet([
                    StructureRotation(
                        structureName='central_core_hallway',
                        rotation=(1 + self.volumeRotation) % 4,
                    )
                ])
                wfc.lockedTiles[index] = True
                continue

            if index == self.atriumExitPos2:
                wfc.stateSpace[index] = OrderedSet([
                    StructureRotation(
                        structureName='central_core_hallway',
                        rotation=(0 + self.volumeRotation) % 4,
                    )
                ])
                wfc.lockedTiles[index] = True
                continue

            if index == self.atriumExitPos3:
                wfc.stateSpace[index] = OrderedSet([
                    StructureRotation(
                        structureName='central_core_hallway',
                        rotation=(3 + self.volumeRotation) % 4,
                    )
                ])
                wfc.lockedTiles[index] = True
                continue

            if self.atriumBox.contains(index):
                wfc.stateSpace[index] = OrderedSet(Adjacency.getAllRotations(structureName='air'))
                continue

            # Remove central_core_hallway from all other cells.
            if wfc.lockedTiles[index] is False:
                wfc.stateSpace[index] = OrderedSet(filter(
                    lambda state: not state.structureName == 'central_core_hallway', wfc.stateSpace[index]
                ))

        self.collapseSpaceAroundConnector(wfc, self.atriumExitPos1)
        self.collapseSpaceAroundConnector(wfc, self.atriumExitPos2)
        self.collapseSpaceAroundConnector(wfc, self.atriumExitPos3)

    @staticmethod
    def collapseSpaceAroundConnector(wfc: WaveFunctionCollapse, cellIndex: ivec3):
        if cellIndex is None or wfc.stateSpaceBox.contains(cellIndex) is False:
            return
        for axis in Adjacency.ROTATIONAL_AXES:
            neighbourCellIndex = Adjacency.getPositionFromAxis(axis, cellIndex)[0]
            if wfc.stateSpaceBox.contains(neighbourCellIndex) and len(wfc.stateSpace[neighbourCellIndex]) > 1:
                intersectingStates = wfc.stateSpace[neighbourCellIndex].intersection(
                    wfc.computeNeighbourStates(
                        cellIndex,
                        axis
                    )
                )
                wfc.stateSpace[neighbourCellIndex] = intersectingStates
        wfc.firstPositions.add(cellIndex)

    @staticmethod
    def generateWeights(condition: str = '') -> Dict[str, float]:
        match condition:
            case 'noAtrium':
                # For tileset 'doha'
                return globals.defaultStructureWeights | {
                    'balcony_corner': 0.0,
                    'balcony_l': 0.0,
                    'balcony_r': 0.0,
                    'balcony_l_inner': 0.0,
                    'balcony_r_inner': 0.0,
                    'balcony_middle_inner': 0.0,
                    'balcony_middle': 0.0,
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
                # For tileset 'doha'
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
        return True

    def onResolve(self, wfc: WaveFunctionCollapse):
        self.allStateSpace.update(wfc.stateSpace)
        self.allLockedTiles.update(wfc.lockedTiles)
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
                if cellIndex in self.allLockedTiles and self.allLockedTiles[cellIndex]:
                    newBuilding.add(cellIndex)
                    cellsVisited.add(cellIndex)
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
                tile=cellIndex,
                offset=buildVolumeOffset,
            )
            yield structureInstance

    def buildStructure(self, buildVolumeOffset: ivec3 = ivec3(0, 0, 0)):
        print('Placing tiles…')
        for building in self.getCollapsedState(buildVolumeOffset=buildVolumeOffset):
            building.place()
        # Build central atrium/staircase
        atriumCoreFolder = globals.structureFolders['central_core']
        atriumCoreBuildingInstance: Structure = atriumCoreFolder.structureClass(
            withRotation=self.volumeRotation,
            tile=ivec3(*self.atriumBox.offset),
            offset=buildVolumeOffset,
        )
        atriumCoreBuildingInstance.place()
