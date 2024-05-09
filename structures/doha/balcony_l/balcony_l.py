from pathlib import Path

from glm import ivec3

import globals
from Adjacency import StructureAdjacency
from StructureBase import Structure


class BalconyL(Structure):
    adjecencies = StructureAdjacency(
        name='balcony_l',
        xForward=[
            ('atrium_air', -1),
        ],
        xBackward=[
            ('wall_r', 2),
        ],
        yForward=[
            ('balcony_l', 0),
            ('atrium_ceiling_edge', 0),
        ],
        yBackward=[
            ('balcony_l', 0),
        ],
        zForward=[
            ('balcony_r', 0),
        ],
        zBackward=[
            ('balcony_r_inner', 0),
            ('balcony_corner', 0)
        ]
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
