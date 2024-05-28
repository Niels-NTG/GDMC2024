from pathlib import Path

from glm import ivec3

import globals
from Adjacency import StructureAdjacency
from StructureBase import Structure


class BalconyMiddle(Structure):
    adjecencies = StructureAdjacency(
        name='balcony_middle',
        xForward=[
            ('atrium_air', -1),
        ],
        xBackward=[
            ('wall_middle', 2),
        ],
        yForward=[
            ('balcony_middle', 0),
            ('atrium_ceiling_edge', 0),
        ],
        yBackward=[
            ('balcony_middle', 0),
        ],
        zForward=[
            ('balcony_l_inner', 0),
            ('balcony_corner', 3),
        ],
        zBackward=[
            ('balcony_r_inner', 0),
            ('balcony_corner', 0),
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
