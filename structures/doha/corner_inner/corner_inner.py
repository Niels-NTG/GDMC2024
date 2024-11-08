from pathlib import Path

from glm import ivec3

import globals
from Adjacency import StructureAdjacency
from StructureBase import Structure


class CornerInner(Structure):
    adjecencies = StructureAdjacency(
        name='corner_inner',
        xForward=[
            ('wall_l', 3),
            ('wall_middle', 3),
        ],
        xBackward=[
            ('wall_r_inner', 2),
            ('balcony_r_inner', 2),
            ('corner_inner', 3),
            ('balcony_corner', 2),
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
            ('wall_middle', -1),
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
            ('wall_middle', -1),
            ('wall_lectern', -1),
        ],
        zForward=[
            ('corner_inner', 1),
            ('wall_l_inner', 1),
            ('balcony_l_inner', 1),
            ('balcony_corner', 0),
        ],
        zBackward=[
            ('wall_r', 0),
            ('wall_middle', 0),
        ],
        walls=[
            'yForward',
            'yBackward',
        ],
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
        # TODO implement pre/post-processing to change flowers
