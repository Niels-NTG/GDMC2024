from pathlib import Path

from glm import ivec3

import globals
from Adjacency import StructureAdjacency
from StructureBase import Structure


class XJunction(Structure):
    adjecencies = StructureAdjacency(
        name='x_junction',
        xForward=[
            ('book_hallway_outer', 1),
            ('book_hallway_outer', 3),
        ],
        xBackward=[
            ('book_hallway_outer', 1),
            ('book_hallway_outer', 3),
            ('central_core_hallway', 0),
        ],
        yForward=[
            ('air', -1),
            ('book_hallway_inner', -1),
            ('book_hallway_outer', -1),
            ('book_corner', -1),
            ('book_corner', -1),
            ('t_junction', -1),
            ('x_junction', -1),
            ('book_end', -1),
            ('bed', -1),
        ],
        yBackward=[
            ('air', -1),
            ('book_hallway_inner', -1),
            ('book_hallway_outer', -1),
            ('book_corner', -1),
            ('book_corner', -1),
            ('t_junction', -1),
            ('x_junction', -1),
            ('book_end', -1),
            ('bed', -1),
        ],
        zForward=[
            ('book_hallway_outer', 0),
            ('book_hallway_outer', 2),
        ],
        zBackward=[
            ('book_hallway_outer', 0),
            ('book_hallway_outer', 2),
        ],
        walls=[
            'yForward',
            'yBackward',
        ]
    )

    weight = 0.6

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
