import functools
from pathlib import Path

from glm import ivec3
from nbt import nbt
import numpy as np


class StructureFile:

    def __init__(
        self,
        filePath: Path
    ):
        filePath = filePath.with_suffix('.nbt')
        self.name = filePath.name
        self.nbt = nbt.NBTFile(filename=filePath)
        with open(filePath, 'rb') as file:
            self.file = file.read()

    def getBlockAt(self, x, y, z):
        for block in self.nbt['blocks']:
            if block["pos"][0].value == x and block["pos"][1].value == y and block["pos"][2].value == z:
                return block

    def getBlockMaterial(self, block):
        return self.nbt["palette"][block["state"].value]['Name'].value

    def getBlockMaterialAt(self, x, y, z):
        return self.getBlockMaterial(self.getBlockAt(x, y, z))

    # Get block properties (also known as block states: https://minecraft.fandom.com/wiki/Block_states) of a block.
    # This may contain information on the orientation of a block or open or closed stated of a door.
    def getBlockProperties(self, block) -> dict:
        properties = dict()
        if "Properties" in self.nbt["palette"][block["state"].value].keys():
            for key in self.nbt["palette"][block["state"].value]["Properties"].keys():
                properties[key] = self.nbt["palette"][block["state"].value]["Properties"][key].value
        return properties

    def getBlockPropertiesAt(self, x, y, z) -> dict:
        return self.getBlockProperties(self.getBlockAt(x, y, z))

    @functools.cached_property
    def sizeX(self) -> int:
        return self.nbt["size"][0].value

    @functools.cached_property
    def sizeY(self) -> int:
        return self.nbt["size"][1].value

    @functools.cached_property
    def sizeZ(self) -> int:
        return self.nbt["size"][2].value

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
