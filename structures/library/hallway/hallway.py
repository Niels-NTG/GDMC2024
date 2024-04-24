from pathlib import Path

from glm import ivec3

import globals
from Adjacency import StructureAdjacency
from StructureBase import Structure


class Hallway(Structure):

    adjecencies = StructureAdjacency(
        name='hallway',
        xForward=[
            ('t_junction', 2),
        ],
        xBackward=[
            ('t_junction', 0),
        ],
        zForward=[
            ('air', -1),
            ('wall_l_book', 3),
            ('wall_r_book', 3),
            ('stairs', 0),
            ('stairs', 2),
            ('stairs', 3),
            ('corner_outer', 0),
            ('corner_outer', 1),
            ('wall_seat', 1),
        ],
        zBackward=[
            ('air', -1),
            ('wall_l_book', 1),
            ('wall_r_book', 1),
            ('stairs', 0),
            ('stairs', 2),
            ('stairs', 1),
            ('corner_outer', 2),
            ('corner_outer', 3),
            ('wall_seat', 3),
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
