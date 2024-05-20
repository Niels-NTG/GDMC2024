from pathlib import Path

from glm import ivec3

import globals
from Adjacency import StructureAdjacency
from StructureBase import Structure


class AtriumAir(Structure):
    adjecencies = StructureAdjacency(
        name='atrium_air',
        xForward=[
            ('atrium_air', -1),
            ('balcony_l', 2),
            ('balcony_r', 2),
            ('balcony_l_inner', 2),
            ('balcony_r_inner', 2),
            ('balcony_middle_inner', 2),
        ],
        xBackward=[
            ('atrium_air', -1),
            ('balcony_l', 0),
            ('balcony_r', 0),
            ('balcony_l_inner', 0),
            ('balcony_r_inner', 0),
            ('balcony_middle_inner', 0),
        ],
        yForward=[
            ('atrium_air', -1),
            ('atrium_ceiling_a', -1),
            ('atrium_ceiling_b', -1),
            ('atrium_ceiling_c', -1),
            ('atrium_ceiling_plants_a', -1),
            ('atrium_ceiling_plants_b', -1),
            ('atrium_ceiling_plants_c', -1),
        ],
        yBackward=[
            ('atrium_air', -1),
            # TODO create atrium floor
        ],
        zForward=[
            ('atrium_air', -1),
            ('balcony_l', 3),
            ('balcony_r', 3),
            ('balcony_l_inner', 3),
            ('balcony_r_inner', 3),
            ('balcony_middle_inner', 3),
        ],
        zBackward=[
            ('atrium_air', -1),
            ('balcony_l', 1),
            ('balcony_r', 1),
            ('balcony_l_inner', 1),
            ('balcony_r_inner', 1),
            ('balcony_middle_inner', 1),
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
