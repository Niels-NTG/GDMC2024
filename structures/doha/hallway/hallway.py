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
            ('air', -1),
            ('wall_l', 3),
            ('wall_r', 3),
            ('wall_l_inner', 3),
            ('wall_r_inner', 3),
            ('wall_lectern', 1),
            ('ladder', 0),
            ('ladder', 2),
            ('ladder', 3),
            ('corner_outer', 0),
            ('corner_outer', 1),
        ],
        zBackward=[
            ('air', -1),
            ('wall_l', 1),
            ('wall_r', 1),
            ('wall_l_inner', 1),
            ('wall_r_inner', 1),
            ('wall_lectern', 3),
            ('ladder', 0),
            ('ladder', 1),
            ('ladder', 2),
            ('corner_outer', 2),
            ('corner_outer', 3),
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
