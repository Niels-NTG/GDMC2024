from pathlib import Path

from glm import ivec3

import globals
from Adjacency import StructureAdjacency
from StructureBase import Structure


class WallLectern(Structure):
    adjecencies = StructureAdjacency(
        name='wall_lectern',
        xForward=[
            ('wall_lectern', 2),
            ('t_junction', 0),
            ('balcony_corner', 0),
            ('balcony_corner', 3),
        ],
        xBackward=[
            ('air', -1),
            ('wall_lectern', 2),
            ('wall_r', 0),
            ('wall_l', 0),
            ('wall_l_inner', 0),
            ('wall_r_inner', 0),
            ('corner_outer', 1),
            ('corner_outer', 2),
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
            ('wall_r', 2),
            ('corner_outer', 3),
        ],
        zBackward=[
            ('wall_l', 2),
            ('corner_outer', 0),
        ],
        walls=[
            'xBackward',
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
