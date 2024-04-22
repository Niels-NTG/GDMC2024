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
        ],
        xBackward=[
            ('t_junction', 2),
            ('wall_seat', 0),
        ],
        zForward=[
            ('balcony_l', 0),
        ],
        zBackward=[
            ('t_junction', 3),
            ('wall_seat', 1),
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
