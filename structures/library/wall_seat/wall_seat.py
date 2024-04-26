from pathlib import Path

from glm import ivec3

import globals
from Adjacency import StructureAdjacency
from StructureBase import Structure


class WallSeat(Structure):

    adjecencies = StructureAdjacency(
        name='wall_seat',
        xForward=[
            ('wall_seat', 2),
            ('t_junction', 0),
            ('balcony_l', 0),
            ('balcony_r', 0),
            ('balcony_corner', 0),
            ('balcony_corner', 3),
        ],
        xBackward=[
            ('air', -1),
            ('wall_seat', 2),
            ('wall_r_book', 0),
            ('wall_l_book', 0),
            ('hallway', 1),
            ('hallway', 3),
            ('stairs', 0),
            ('stairs', 1),
            ('stairs', 3),
            ('corner_outer', 1),
            ('corner_outer', 2),
        ],
        yForward=[
            ('air', -1),
            ('corner_inner', -1),
            ('corner_outer', -1),
            ('hallway', -1),
            ('t_junction', -1),
            ('wall_l_book', -1),
            ('wall_r_book', -1),
            ('wall_seat', -1),
        ],
        yBackward=[
            ('air', -1),
            ('corner_inner', -1),
            ('corner_outer', -1),
            ('hallway', -1),
            ('t_junction', -1),
            ('wall_l_book', -1),
            ('wall_r_book', -1),
            ('wall_seat', -1),
        ],
        zForward=[
            ('wall_r_book', 2),
            ('corner_outer', 3),
        ],
        zBackward=[
            ('wall_l_book', 2),
            ('corner_outer', 0),
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
