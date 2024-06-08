from pathlib import Path

from glm import ivec3

import globals
from Adjacency import StructureAdjacency
from StructureBase import Structure


class TJunction(Structure):
    adjecencies = StructureAdjacency(
        name='t_junction',
        xForward=[
            ('book_hallway_outer', 1),
            ('book_hallway_outer', 3),
            ('t_junction', 1),
            ('t_junction', 2),
            ('t_junction', 3),
            ('central_core_hallway', 2),
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
            ('book_hallway_outer', 0),
            ('book_hallway_outer', 2),
            ('t_junction', 0),
            ('t_junction', 2),
            ('t_junction', 3),
        ],
        zBackward=[
            ('book_hallway_outer', 0),
            ('book_hallway_outer', 2),
            ('t_junction', 0),
            ('t_junction', 1),
            ('t_junction', 2),
        ],
        walls=[
            'xBackward',
            'yForward',
            'yBackward',
        ]
    )

    bookShelves = {
        ivec3(1, 5, 7): 'east',
        ivec3(1, 5, 6): 'east',
        ivec3(1, 5, 5): 'east',
        ivec3(1, 5, 4): 'east',
        ivec3(1, 5, 3): 'east',
        ivec3(1, 5, 2): 'east',
        ivec3(1, 5, 1): 'east',
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
        ivec3(1, 1, 7): 'east',
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
