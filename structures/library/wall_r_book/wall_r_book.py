from pathlib import Path

from glm import ivec3

import globals
from Adjacency import StructureAdjacency
from StructureBase import Structure


class WallRBook(Structure):

    adjecencies = StructureAdjacency(
        name='wall_r_book',
        xForward=[
            ('air', -1),
            ('wall_l_book', 2),
            ('wall_r_book', 2),
            ('wall_seat', 0),
            ('hallway', 1),
            ('hallway', 3),
            ('stairs', 1),
            ('stairs', 2),
            ('stairs', 3),
            ('corner_outer', 0),
            ('corner_outer', 3),
        ],
        xBackward=[
            ('wall_l_book', 2),
            ('balcony_l', 2),
        ],
        zForward=[
            ('wall_l_book', 0),
            ('t_junction', 0),
            ('wall_seat', 2),
            ('corner_outer', 2),
            ('corner_inner', 1),
        ],
        zBackward=[
            ('wall_l_book', 0),
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
