from pathlib import Path

from glm import ivec3

import globals
from Adjacency import StructureAdjacency
from StructureBase import Structure


class CornerInner(Structure):

    adjecencies = StructureAdjacency(
        name='corner_inner',
        xForward=[
            ('balcony_l', 0),
            ('corner_inner', 1),
            ('wall_l_book', 0),
        ],
        xBackward=[
            ('wall_r_book', 3),
        ],
        zForward=[
            ('corner_inner', 3),
            ('balcony_r', 1),
            ('wall_r_book', 1),
        ],
        zBackward=[
            ('wall_l_book', 2),
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
