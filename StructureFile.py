import functools
from pathlib import Path

import nbtlib
import numpy as np
from glm import ivec3
from nbtlib import Compound


class StructureFile:

    name: str
    nbt: Compound
    file: bytes

    def __init__(
        self,
        filePath: Path
    ):
        filePath = filePath.with_suffix('.nbt')
        self.name = filePath.name
        self.nbt = nbtlib.load(filename=filePath, gzipped=True)
        with open(filePath, 'rb') as file:
            self.file = file.read()

    def getBlockAt(self, pos: ivec3) -> ivec3:
        for block in self.nbt['blocks']:
            if block["pos"][0] == pos.x and block["pos"][1] == pos.y and block["pos"][2] == pos.z:
                return block

    def getBlockMaterial(self, block):
        return self.nbt["palette"][block["state"]]['Name']

    def getBlockMaterialAt(self, pos: ivec3):
        return self.getBlockMaterial(self.getBlockAt(pos))

    # Get block properties (also known as block states: https://minecraft.fandom.com/wiki/Block_states) of a block.
    # This may contain information on the orientation of a block or open or closed stated of a door.
    def getBlockProperties(self, block) -> dict:
        properties = dict()
        if "Properties" in self.nbt["palette"][block["state"]].keys():
            for key in self.nbt["palette"][block["state"]]["Properties"].keys():
                properties[key] = self.nbt["palette"][block["state"]]["Properties"][key]
        return properties

    def getBlockPropertiesAt(self, pos: ivec3) -> dict:
        return self.getBlockProperties(self.getBlockAt(pos))

    @functools.cached_property
    def sizeX(self) -> int:
        return self.nbt["size"][0]

    @functools.cached_property
    def sizeY(self) -> int:
        return self.nbt["size"][1]

    @functools.cached_property
    def sizeZ(self) -> int:
        return self.nbt["size"][2]

    @functools.cached_property
    def shortestDimension(self):
        return np.argmin([np.abs(self.sizeX), np.abs(self.sizeY), np.abs(self.sizeZ)])

    @functools.cached_property
    def longestDimension(self):
        return np.argmax([np.abs(self.sizeX), np.abs(self.sizeY), np.abs(self.sizeZ)])

    @functools.cached_property
    def shortestHorizontalDimension(self) -> int:
        return np.argmin([np.abs(self.sizeX), np.abs(self.sizeZ)]) * 2

    @functools.cached_property
    def longestHorizontalDimension(self) -> int:
        return np.argmax([np.abs(self.sizeX), np.abs(self.sizeZ)]) * 2

    @functools.cached_property
    def shortestSize(self) -> int:
        return [self.sizeX, self.sizeY, self.sizeZ][self.shortestDimension]

    @functools.cached_property
    def longestSize(self) -> int:
        return [self.sizeX, self.sizeY, self.sizeZ][self.longestDimension]

    @functools.cached_property
    def shortestHorizontalSize(self) -> int:
        return [self.sizeX, 0, self.sizeZ][self.shortestHorizontalDimension]

    @functools.cached_property
    def longestHorizontalSize(self) -> int:
        return [self.sizeX, 0, self.sizeZ][self.longestHorizontalDimension]

    @functools.cached_property
    def centerPivot(self) -> ivec3:
        return ivec3(
            self.sizeX // 2,
            0,
            self.sizeZ // 2
        )

    def __repr__(self):
        return f'{self.name}'
