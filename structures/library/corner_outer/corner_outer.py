from pathlib import Path

from glm import ivec3

import globals
from Adjacency import StructureAdjacency
from StructureBase import Structure


class CornerOuter(Structure):

    adjecencies = StructureAdjacency(
        name='corner_outer',
        xForward=[
            ('wall_seat', 1),
            ('t_junction', 3),
            ('wall_l_book', 3),
            # ('corner_outer', 1),
        ],
        xBackward=[
            ('air', -1),
            ('corner_outer', 1),
            ('corner_outer', 2),
        ],
        zForward=[
            ('wall_seat', 0),
            ('t_junction', 2),
            ('wall_r_book', 2),
            # ('corner_outer', 3),
        ],
        zBackward=[
            ('air', -1),
            ('corner_outer', 2),
            ('corner_outer', 3),
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
