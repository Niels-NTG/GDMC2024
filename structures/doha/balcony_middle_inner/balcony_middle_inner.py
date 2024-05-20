from pathlib import Path

from glm import ivec3

import globals
from Adjacency import StructureAdjacency
from StructureBase import Structure


class BalconyMiddleInner(Structure):
    adjecencies = StructureAdjacency(
        name='balcony_middle_inner',
        xForward=[
            ('atrium_air', -1),
        ],
        xBackward=[
            ('t_junction', 2),
            ('wall_lectern', 0),
        ],
        yForward=[
            ('balcony_middle_inner', 0),
            ('atrium_ceiling_edge', 0),
        ],
        yBackward=[
            ('balcony_middle_inner', 0),
        ],
        zForward=[
            ('balcony_l', 0),
        ],
        zBackward=[
            ('balcony_r', 0),
        ],
        walls=[
            'xForward',
            'yForward',
            'yBackward',
        ],
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
