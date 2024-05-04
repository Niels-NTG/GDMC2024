from glm import ivec3

import Adjacency
from WaveFunctionCollapse import WaveFunctionCollapse
from gdpc.src.gdpc import Box


class Builder:

    def __init__(
        self,
        volume: Box,
        buildingName: str,
        tileSize: ivec3 = ivec3(5, 8, 5),
    ):
        self.name = buildingName

        wfc = WaveFunctionCollapse(
            volumeGrid=(volume.size // tileSize).to_tuple()
        )
        wfc.collapseWithRetry(
            initFunction=Builder.reinitWFC,
            validationFunction=Builder.isValid
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
