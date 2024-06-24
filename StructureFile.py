from pathlib import Path

import nbtlib
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

    @property
    def sizeX(self) -> int:
        return self.nbt["size"][0]

    @property
    def sizeY(self) -> int:
        return self.nbt["size"][1]

    @property
    def sizeZ(self) -> int:
        return self.nbt["size"][2]

    @property
    def centerPivot(self) -> ivec3:
        return ivec3(
            self.sizeX // 2,
            0,
            self.sizeZ // 2
        )

    def __repr__(self):
        return f'{self.name}'
