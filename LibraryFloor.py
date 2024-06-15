from typing import Dict, List, Iterator, Tuple, Set

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
from structures.doha9.central_core.central_core import CentralCore


class LibraryFloor:

    allStateSpace: Dict[ivec3, OrderedSet[StructureRotation]]
    allLockedTiles: Dict[ivec3, bool]
    allDefaultAdjacencies: Dict[str, StructureAdjacency]
    subGridVolumes: List[Box]
    volumeGrid: Box
    volumeRotation: int
    placedTiles: Dict[ivec3, Structure]
    centralTile: ivec3

    def __init__(
        self,
        volume: Box,
        volumeGrid: Box,
        volumeRotation: int = 0,
    ):

        self.volume = volume

        self.allStateSpace = dict()
        self.allLockedTiles = dict()
        self.allDefaultAdjacencies = dict()
        self.subGridVolumes = []
        self.placedTiles = dict()

        self.volumeGrid = volumeGrid
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
                    lambda state: not state.structureName.startswith('central_core_hallway'), wfc.stateSpace[index]
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

    def isValid(self, wfc: WaveFunctionCollapse) -> bool:
        structuresUsed = set(wfc.structuresUsed)
        isAirOnly = structuresUsed.issubset(Adjacency.getAllRotations('air'))
        if isAirOnly:
            print('Invalid WFC result! Volume has only air!')
            return False
        wfc.foundBuildings = wfc.scanForBuildings()
        if len(wfc.foundBuildings) == 0:
            print('Invalid WFC result! Volume has no buildings!')
            return False
        largestBuilding = max(wfc.foundBuildings, key=lambda x: len(x))
        if (
            self.atriumExitPos1 not in largestBuilding or
            self.atriumExitPos2 not in largestBuilding or
            self.atriumExitPos3 not in largestBuilding
        ):
            print('Invalid WFC result! Volume has missing atrium exit!')
            return False
        return True

    def onResolve(self, wfc: WaveFunctionCollapse):
        self.removeOrphanedBuildings(wfc)
        self.allStateSpace.update(wfc.stateSpace)
        self.allLockedTiles.update(wfc.lockedTiles)
        self.allDefaultAdjacencies.update(wfc.defaultAdjacencies)
        self.subGridVolumes.append(wfc.stateSpaceBox)

        for index, building in self.getCollapsedState:
            if not building.name.startswith('air'):
                self.placedTiles[index] = building
        # Add central atrium/staircase
        atriumCoreBuildingInstance = CentralCore(
            withRotation=self.volumeRotation,
            tile=self.atriumBox.offset,
            offset=self.volume.offset,
        )
        self.placedTiles[atriumCoreBuildingInstance.tile] = atriumCoreBuildingInstance
        self.centralTile = atriumCoreBuildingInstance.tile

    @staticmethod
    def removeOrphanedBuildings(wfc: WaveFunctionCollapse):
        buildings = wfc.foundBuildings
        print(f'Found {len(buildings)} distinct buildings, removing orphaned buildings…')
        largestBuilding = max(buildings, key=lambda x: len(x))
        for building in buildings:
            if building != largestBuilding:
                for index in building:
                    wfc.stateSpace[index] = OrderedSet({StructureRotation(structureName='air', rotation=0)})

    @property
    def getCollapsedState(self) -> Iterator[Tuple[ivec3, Structure]]:
        for index in self.allStateSpace:
            cellState: StructureRotation = self.allStateSpace[index][0]
            if cellState.structureName not in globals.structureFolders:
                raise Exception(f'Structure file {cellState.structureName} not found in {globals.structureFolders}')
            structureFolder = globals.structureFolders[cellState.structureName]
            structureInstance: Structure = structureFolder.structureClass(
                withRotation=cellState.rotation,
                tile=index,
                offset=self.volume.offset,
            )
            yield index, structureInstance

    def placeStructure(self):
        print('Placing tiles…')
        for building in self.placedTiles.values():
            if building is not self.centralCore:
                building.place()

    @property
    def centralCore(self) -> Structure:
        return self.placedTiles[self.centralTile]

    @property
    def bookCapacity(self) -> int:
        capacity = 0
        for building in self.placedTiles.values():
            capacity += building.bookCapacity
        return capacity

    def addBooks(self, books: List[str], categoryLabel: str, floorNumber: int) -> List[Dict[str, str]]:
        bookRanges: List[Dict[str, str]] = []
        rng = np.random.default_rng(seed=globals.rngSeed)
        stateSpaceKeys: List[ivec3] = list(self.placedTiles.keys())
        tilesVisited: Set[ivec3] = {self.centralTile}
        currentBuilding = self.centralCore
        isDirectionInverted = False
        while len(tilesVisited) != len(self.placedTiles):
            bookRanges.extend(currentBuilding.addBooks(books, categoryLabel, floorNumber, isDirectionInverted))

            openPositions: Set[ivec3] = self.allDefaultAdjacencies[currentBuilding.name].getNonWallPositions(
                currentBuilding.rotation,
                currentBuilding.tile,
                stateSpaceKeys,
            ).difference(tilesVisited)
            if len(openPositions) == 0:
                # noinspection PyTypeChecker
                nextPosition = ivec3(rng.choice(list(set(self.placedTiles).difference(tilesVisited))))
                tilesVisited.add(nextPosition)
                isDirectionInverted = False
                currentBuilding = self.placedTiles[nextPosition]
                continue
            # noinspection PyTypeChecker
            nextPosition = ivec3(rng.choice(list(openPositions)))
            tilesVisited.add(nextPosition)
            nextBuilding = self.placedTiles[nextPosition]
            isDirectionInverted = nextBuilding.rotation != currentBuilding.rotation
            currentBuilding = nextBuilding

        return bookRanges
