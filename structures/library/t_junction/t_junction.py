from pathlib import Path

from glm import ivec3

import globals
from Adjacency import StructureAdjacency
from StructureBase import Structure


class TJunction(Structure):

    adjecencies = StructureAdjacency(
        name='t_junction',
        xForward=[
            ('hallway', 0),
            ('hallway', 2),
            ('stairs', 0),
            ('t_junction', 2),
        ],
        xBackward=[
            ('t_junction', 2),
            ('wall_seat', 0),
            ('balcony_r', 2),
            ('balcony_l', 2),
            ('balcony_corner', 1),
            ('balcony_corner', 2),
        ],
        zForward=[
            ('wall_l_book', 0),
            ('corner_outer', 2),
        ],
        zBackward=[
            ('wall_r_book', 0),
            ('corner_outer', 1),
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
