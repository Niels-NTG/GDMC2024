from pathlib import Path

from glm import ivec3

import globals
import nbtTools
from StructureBase import Structure


class BottomGarden(Structure):

    def __init__(
        self,
        withRotation: int = 0,
        tile: ivec3 = ivec3(0, 0, 0),
        offset: ivec3 = ivec3(0, 0, 0),
    ):
        super().__init__(
            structureFolder=globals.structureFolders[Path(__file__).parent.name],
            withRotation=withRotation,
            tile=tile,
            offset=offset,
        )

    @property
    def position(self) -> ivec3:
        return self.offset + (self.tile * ivec3(9, 10, 9))

    def place(self):
        nbtTools.setStructureBlock(
            self.nbt,
            pos=ivec3(23, 5, 22),
            inputBlockId='minecraft:cherry_sapling',
            inputBlockState={
                'stage': '"1"'
            },
            inputBlockData=None,
        )
        super().place()
