from pathlib import Path

from glm import ivec3

import globals
from Adjacency import StructureAdjacency
from StructureBase import Structure


class BookHallwayInner(Structure):
    adjecencies = StructureAdjacency(
        name='book_hallway_inner',
        xForward=[
            ('air', -1),
            ('book_hallway_inner', 0),
            ('book_hallway_inner', 2),
            ('book_hallway_outer', 0),
            ('book_hallway_outer', 2),
            ('book_corner', 0),
            ('book_corner', 1),
            ('t_junction', 0),
        ],
        xBackward=[
            ('air', -1),
            ('book_hallway_inner', 0),
            ('book_hallway_inner', 2),
            ('book_hallway_outer', 0),
            ('book_hallway_outer', 2),
            ('book_corner', 2),
            ('book_corner', 3),
            ('t_junction', 2),
        ],
        yForward=[
            ('air', -1),
            ('book_hallway_inner', -1),
            ('book_hallway_outer', -1),
            ('book_corner', -1),
            ('book_corner', -1),
            ('t_junction', -1),
            ('x_junction', -1),
        ],
        yBackward=[
            ('air', -1),
            ('book_hallway_inner', -1),
            ('book_hallway_outer', -1),
            ('book_corner', -1),
            ('book_corner', -1),
            ('t_junction', -1),
            ('x_junction', -1),
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
            'xForward',
            'xBackward',
            'yForward',
            'yBackward',
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
