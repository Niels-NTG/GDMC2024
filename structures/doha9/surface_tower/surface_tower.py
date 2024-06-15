from pathlib import Path

from glm import ivec3

import globals
from StructureBase import Structure


class SurfaceTower(Structure):

    signs = {
        'down1': ivec3(7, 5, 19),
        'down2': ivec3(7, 5, 18),
        'down3': ivec3(7, 5, 17),
    }

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
