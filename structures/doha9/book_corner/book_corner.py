from pathlib import Path

from glm import ivec3

import globals
from Adjacency import StructureAdjacency
from StructureBase import Structure


class BookCorner(Structure):
    adjecencies = StructureAdjacency(
        name='book_corner',
        xForward=[
            ('book_hallway_outer', 1),
            ('book_hallway_outer', 3),
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
            ('book_end', -1),
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
        ],
        zForward=[
            ('air', -1),
            ('book_hallway_inner', 1),
            ('book_hallway_inner', 3),
            ('book_hallway_outer', 1),
            ('book_hallway_outer', 3),
            ('book_corner', 1),
            ('book_corner', 2),
            ('t_junction', 1),
        ],
        zBackward=[
            ('book_hallway_outer', 0),
            ('book_hallway_outer', 2),
        ],
        walls=[
            'zForward',
            'xBackward',
            'yForward',
            'yBackward',
        ]
    )

    weight = 0.2

    bookShelves = {
        ivec3(7, 5, 7): 'north',
        ivec3(6, 5, 7): 'north',
        ivec3(5, 5, 7): 'north',
        ivec3(4, 5, 7): 'north',
        ivec3(3, 5, 7): 'north',
        ivec3(2, 5, 7): 'north',
        ivec3(1, 5, 6): 'east',
        ivec3(1, 5, 5): 'east',
        ivec3(1, 5, 4): 'east',
        ivec3(1, 5, 3): 'east',
        ivec3(1, 5, 2): 'east',
        ivec3(1, 5, 1): 'east',
        ivec3(7, 4, 7): 'north',
        ivec3(6, 4, 7): 'north',
        ivec3(5, 4, 7): 'north',
        ivec3(4, 4, 7): 'north',
        ivec3(3, 4, 7): 'north',
        ivec3(2, 4, 7): 'north',
        ivec3(1, 4, 6): 'east',
        ivec3(1, 4, 5): 'east',
        ivec3(1, 4, 4): 'east',
        ivec3(1, 4, 3): 'east',
        ivec3(1, 4, 2): 'east',
        ivec3(1, 4, 1): 'east',
        ivec3(7, 3, 7): 'north',
        ivec3(6, 3, 7): 'north',
        ivec3(5, 3, 7): 'north',
        ivec3(4, 3, 7): 'north',
        ivec3(3, 3, 7): 'north',
        ivec3(2, 3, 7): 'north',
        ivec3(1, 3, 6): 'east',
        ivec3(1, 3, 5): 'east',
        ivec3(1, 3, 4): 'east',
        ivec3(1, 3, 3): 'east',
        ivec3(1, 3, 2): 'east',
        ivec3(1, 3, 1): 'east',
        ivec3(7, 2, 7): 'north',
        ivec3(6, 2, 7): 'north',
        ivec3(5, 2, 7): 'north',
        ivec3(4, 2, 7): 'north',
        ivec3(3, 2, 7): 'north',
        ivec3(2, 2, 7): 'north',
        ivec3(1, 2, 6): 'east',
        ivec3(1, 2, 5): 'east',
        ivec3(1, 2, 4): 'east',
        ivec3(1, 2, 3): 'east',
        ivec3(1, 2, 2): 'east',
        ivec3(1, 2, 1): 'east',
        ivec3(7, 1, 7): 'north',
        ivec3(6, 1, 7): 'north',
        ivec3(5, 1, 7): 'north',
        ivec3(4, 1, 7): 'north',
        ivec3(3, 1, 7): 'north',
        ivec3(2, 1, 7): 'north',
        ivec3(1, 1, 6): 'east',
        ivec3(1, 1, 5): 'east',
        ivec3(1, 1, 4): 'east',
        ivec3(1, 1, 3): 'east',
        ivec3(1, 1, 2): 'east',
        ivec3(1, 1, 1): 'east',
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
