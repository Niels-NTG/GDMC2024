from pathlib import Path

from glm import ivec3

import globals
from Adjacency import StructureAdjacency
from StructureBase import Structure


class AtriumCeilingPlantsB(Structure):
    adjecencies = StructureAdjacency(
        name='atrium_ceiling_plants_b',
        xForward=[
            ('atrium_ceiling_a', -1),
            ('atrium_ceiling_plants_a', -1),
            ('atrium_ceiling_edge', 2),
        ],
        xBackward=[
            ('atrium_ceiling_a', -1),
            ('atrium_ceiling_plants_a', -1),
            ('atrium_ceiling_edge', 0),
        ],
        yForward=[
            ('air', -1),
        ],
        yBackward=[
            ('atrium_air', -1),
        ],
        zForward=[
            ('atrium_ceiling_c', -1),
            ('atrium_ceiling_plants_c', -1),
            ('atrium_ceiling_edge', 3),
        ],
        zBackward=[
            ('atrium_ceiling_c', -1),
            ('atrium_ceiling_plants_c', -1),
            ('atrium_ceiling_edge', 1),
        ],
        walls=[
            'yForward',
        ],
    )

    weight = 0.2

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
