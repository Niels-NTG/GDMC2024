from pathlib import Path

from glm import ivec3

import globals
from Adjacency import StructureAdjacency
from StructureBase import Structure


class WallLInner(Structure):
    adjecencies = StructureAdjacency(
        name='wall_l_inner',
        xForward=[
            ('air', -1),
            ('wall_l', 2),
            ('wall_r', 2),
            ('wall_l_inner', 2),
            ('wall_r_inner', 2),
            ('wall_lectern', 0),
        ],
        xBackward=[
            ('wall_r_inner', 2),
            ('balcony_r_inner', 2),
            ('corner_inner', 3),
        ],
        yForward=[
            ('air', -1),
            ('corner_inner', -1),
            ('corner_outer', -1),
            ('hallway', -1),
            ('t_junction', -1),
            ('wall_l', -1),
            ('wall_r', -1),
            ('wall_l_inner', -1),
            ('wall_r_inner', -1),
            ('wall_lectern', -1),
        ],
        yBackward=[
            ('air', -1),
            ('corner_inner', -1),
            ('corner_outer', -1),
            ('hallway', -1),
            ('t_junction', -1),
            ('wall_l', -1),
            ('wall_r', -1),
            ('wall_l_inner', -1),
            ('wall_r_inner', -1),
            ('wall_lectern', -1),
        ],
        zForward=[
            ('wall_r_inner', 0),
        ],
        zBackward=[
            ('wall_r', 0),
            ('corner_outer', 1),
        ]
    )

    weight = 0.8

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
