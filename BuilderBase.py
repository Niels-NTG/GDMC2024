from typing import Dict

from glm import ivec3
from ordered_set import OrderedSet

import Adjacency
import globals
from WaveFunctionCollapse import WaveFunctionCollapse, startMultiThreadedWFC, startSingleThreadedWFC
from gdpc.src.gdpc import Box


class Builder:

    def __init__(
        self,
        volume: Box,
        tileSize: ivec3 = ivec3(5, 10, 5),
    ):

        volumeGrid = Box(ivec3(0, 0, 0), volume.size // tileSize)
        print(f'Running WFC in volume {volumeGrid.size.x}x{volumeGrid.size.y}x{volumeGrid.size.z}')
        wfc = startMultiThreadedWFC(
            volumeGrid=volumeGrid,
            initFunction=self.reinitWFC,
            validationFunction=Builder.isValid,
            structureWeights=Builder.generateWeights(),
        )

        wfc.removeOrphanedBuildings()
        for building in wfc.getCollapsedState(buildVolumeOffset=volume.offset):
            building.place()

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

    def collapseVolumeEdgeToAir(self, wfcInstance: WaveFunctionCollapse):
        keys = wfcInstance.stateSpace.keys()
        for index in keys:
            if not (
                index.x > wfcInstance.stateSpaceBox.begin.x and index.x < wfcInstance.stateSpaceBox.last.x and
                index.z > wfcInstance.stateSpaceBox.begin.z and index.z < wfcInstance.stateSpaceBox.last.z
            ):
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
