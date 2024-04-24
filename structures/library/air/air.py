from pathlib import Path

from glm import ivec3

import globals
from Adjacency import StructureAdjacency
from StructureBase import Structure


class Air(Structure):

    adjecencies = StructureAdjacency(
        name='air',
        xForward=[
            ('air', -1),
            ('balcony_l', 2),
            ('balcony_r', 2),
            ('wall_l_book', 2),
            ('wall_r_book', 2),
            ('stairs', 1),
            ('stairs', 2),
            ('stairs', 3),
            ('hallway', 1),
            ('hallway', 3),
            ('wall_seat', 0),
            ('corner_outer', 0),
            ('corner_outer', 3),
        ],
        xBackward=[
            ('air', -1),
            ('balcony_l', 0),
            ('balcony_r', 0),
            ('wall_l_book', 0),
            ('wall_r_book', 0),
            ('stairs', 0),
            ('stairs', 1),
            ('stairs', 3),
            ('hallway', 1),
            ('hallway', 3),
            ('wall_seat', 2),
            ('corner_outer', 1),
            ('corner_outer', 2),
        ],
        yForward=[
            ('air', -1),
            ('balcony_r', -1),
            ('balcony_l', -1),
            ('balcony_corner', -1),
        ],
        yBackward=[
            ('air', -1),
            ('balcony_r', -1),
            ('balcony_l', -1),
            ('balcony_corner', -1),
        ],
        zForward=[
            ('air', -1),
            ('balcony_l', 3),
            ('balcony_r', 3),
            ('wall_l_book', 3),
            ('wall_r_book', 3),
            ('stairs', 0),
            ('stairs', 2),
            ('stairs', 3),
            ('hallway', 0),
            ('hallway', 2),
            ('wall_seat', 1),
            ('corner_outer', 0),
            ('corner_outer', 1),
        ],
        zBackward=[
            ('air', -1),
            ('balcony_l', 1),
            ('balcony_r', 1),
            ('wall_l_book', 1),
            ('wall_r_book', 1),
            ('stairs', 0),
            ('stairs', 1),
            ('stairs', 2),
            ('hallway', 0),
            ('hallway', 2),
            ('wall_seat', 3),
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
