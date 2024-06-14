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
            ('book_end', 0),
            ('book_end', 1),
            ('book_end', 2),
            ('bed', 0),
            ('bed', 1),
            ('bed', 2),
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
            ('book_end', 0),
            ('book_end', 2),
            ('book_end', 3),
            ('bed', 0),
            ('bed', 2),
            ('bed', 3),
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
            ('central_core_hallway', 3),
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

    weight = 0.6

    bookShelves = {
        'west': {
            ivec3(7, 4, 1): 'west',
            ivec3(7, 4, 2): 'west',
            ivec3(7, 4, 3): 'west',
            ivec3(7, 4, 4): 'west',
            ivec3(7, 4, 5): 'west',
            ivec3(7, 4, 6): 'west',
            ivec3(7, 4, 7): 'west',
            ivec3(7, 3, 1): 'west',
            ivec3(7, 3, 2): 'west',
            ivec3(7, 3, 3): 'west',
            ivec3(7, 3, 4): 'west',
            ivec3(7, 3, 5): 'west',
            ivec3(7, 3, 6): 'west',
            ivec3(7, 3, 7): 'west',
            ivec3(7, 2, 1): 'west',
            ivec3(7, 2, 2): 'west',
            ivec3(7, 2, 3): 'west',
            ivec3(7, 2, 4): 'west',
            ivec3(7, 2, 5): 'west',
            ivec3(7, 2, 6): 'west',
            ivec3(7, 2, 7): 'west',
        },
        'east': {
            ivec3(1, 4, 7): 'east',
            ivec3(1, 4, 6): 'east',
            ivec3(1, 4, 5): 'east',
            ivec3(1, 4, 4): 'east',
            ivec3(1, 4, 3): 'east',
            ivec3(1, 4, 2): 'east',
            ivec3(1, 4, 1): 'east',
            ivec3(1, 3, 7): 'east',
            ivec3(1, 3, 6): 'east',
            ivec3(1, 3, 5): 'east',
            ivec3(1, 3, 4): 'east',
            ivec3(1, 3, 3): 'east',
            ivec3(1, 3, 2): 'east',
            ivec3(1, 3, 1): 'east',
            ivec3(1, 2, 7): 'east',
            ivec3(1, 2, 6): 'east',
            ivec3(1, 2, 5): 'east',
            ivec3(1, 2, 4): 'east',
            ivec3(1, 2, 3): 'east',
            ivec3(1, 2, 2): 'east',
            ivec3(1, 2, 1): 'east',
        },
    }

    signs = {
        'east': ivec3(2, 6, 4),
        'west': ivec3(6, 6, 4),
    }

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
