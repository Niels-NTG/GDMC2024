from pathlib import Path

from glm import ivec3

import globals
from Adjacency import StructureAdjacency
from StructureBase import Structure


class BalconyR(Structure):
    adjecencies = StructureAdjacency(
        name='balcony_r',
        xForward=[
            ('atrium_air', -1),
        ],
        xBackward=[
            ('wall_l', 2),
        ],
        yForward=[
            ('balcony_r', 0),
            ('atrium_ceiling_edge', 0),
        ],
        yBackward=[
            ('balcony_r', 0),
        ],
        zForward=[
            ('balcony_l_inner', 0),
            ('balcony_corner', 3),
            ('balcony_middle_inner', 0),
        ],
        zBackward=[
            ('balcony_l', 0),
        ],
        walls=[
            'xForward',
            'yForward',
            'yBackward',
        ],
    )

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
