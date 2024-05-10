from typing import Dict

from glm import ivec3
from ordered_set import OrderedSet

import Adjacency
import globals
from WaveFunctionCollapse import WaveFunctionCollapse, startMultiThreadedWFC
from gdpc.src.gdpc import Box


class Builder:

    def __init__(
        self,
        volume: Box,
        buildingName: str,
        tileSize: ivec3 = ivec3(5, 10, 5),
    ):
        self.name = buildingName

        volumeGrid = volume.size // tileSize
        print(f'Running WFC in volume {volumeGrid.x}x{volumeGrid.y}x{volumeGrid.z}')
        wfc = startMultiThreadedWFC(
            volumeGrid=volume.size // tileSize,
            initFunction=Builder.reinitWFC,
            validationFunction=Builder.isValid,
            structureWeights=Builder.generateWeights()
        )

        for building in wfc.getCollapsedState(buildVolumeOffset=volume.offset):
            building.place()

    @staticmethod
    def isValid(wfcInstance: WaveFunctionCollapse) -> bool:
        structuresUsed = set(wfcInstance.structureAdjacencies)
        isAirOnly = structuresUsed.issubset(Adjacency.getAllRotations('air'))
        if isAirOnly:
            print('Invalid WFC result! Volume has only air!')
            return False
        return True

    @staticmethod
    def reinitWFC(wfcInstance: WaveFunctionCollapse):
        wfcInstance.collapseVolumeEdgeToAir()

    @staticmethod
    def generateWeights(condition: str = '') -> Dict[str, float]:
        match condition:
            case 'top':
                return globals.structureWeights | {
                    'atrium_ceiling_edge': 0.5,
                    'atrium_ceiling_edge_corner': 0.5
                }
        return globals.structureWeights
