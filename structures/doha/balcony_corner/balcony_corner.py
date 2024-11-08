from pathlib import Path

from glm import ivec3

import globals
from Adjacency import StructureAdjacency
from StructureBase import Structure


class BalconyCorner(Structure):
    adjecencies = StructureAdjacency(
        name='balcony_corner',
        xForward=[
            ('balcony_r', 1),
            ('balcony_middle', 1),
        ],
        xBackward=[
            ('corner_inner', 2),
            ('wall_l_inner', 2),
        ],
        yForward=[
            ('balcony_corner', 0),
            ('atrium_ceiling_edge_corner', 0),
        ],
        yBackward=[
            ('balcony_corner', 0),
        ],
        zForward=[
            ('balcony_l', 0),
            ('balcony_middle', 0),
        ],
        zBackward=[
            ('corner_inner', 0),
            ('wall_r_inner', 3),
        ],
        walls=[
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
