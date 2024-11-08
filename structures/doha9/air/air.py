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
            ('book_hallway_inner', 0),
            ('book_hallway_inner', 2),
            ('book_hallway_outer', 0),
            ('book_hallway_outer', 2),
            ('book_corner', 0),
            ('book_corner', 1),
            ('t_junction', 0),
            ('central_core_hallway', 0),
            ('central_core_hallway', 1),
            ('central_core_hallway', 3),
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
            ('central_core_hallway', 1),
            ('central_core_hallway', 2),
            ('central_core_hallway', 3),
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
            ('central_core_hallway', -1),
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
            ('central_core_hallway', -1),
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
            ('central_core_hallway', 0),
            ('central_core_hallway', 1),
            ('central_core_hallway', 2),
        ],
        zBackward=[
            ('air', -1),
            ('book_hallway_inner', 1),
            ('book_hallway_inner', 3),
            ('book_hallway_outer', 1),
            ('book_hallway_outer', 3),
            ('book_corner', 0),
            ('book_corner', 3),
            ('t_junction', 3),
            ('central_core_hallway', 0),
            ('central_core_hallway', 2),
            ('central_core_hallway', 3),
        ]
    )

    weight = 0.08

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
