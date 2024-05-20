from typing import Dict

from glm import ivec3
from ordered_set import OrderedSet

import Adjacency
import globals
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

        volumeGrid1 = Box(
            offset=self.volumeGrid.offset,
            size=ivec3(self.volumeGrid.size.x, self.volumeGrid.size.y - 1, self.volumeGrid.size.z)
        )
        print(f'Running WFC 1 on box {volumeGrid1}')
        startMultiThreadedWFC(
            volumeGrid=self.volumeGrid,
            initFunction=self.reinitWFC,
            validationFunction=Builder.isValid,
            structureWeights=Builder.generateWeights('noCeiling'),
            onResolve=self.onResolveWFC,
        )


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

    def onResolveWFC(self, wfc: WaveFunctionCollapse):
        # wfc.removeOrphanedBuildings()
        for building in wfc.getCollapsedState(buildVolumeOffset=self.volume.offset):
            building.place()
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
