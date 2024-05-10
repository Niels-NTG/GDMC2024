from pathlib import Path

from glm import ivec3

import globals
from Adjacency import StructureAdjacency
from StructureBase import Structure


class AtriumCeilingEdge(Structure):
    adjecencies = StructureAdjacency(
        name='atrium_ceiling_edge',
        xForward=[
            ('atrium_ceiling_a', -1),
            ('atrium_ceiling_b', -1),
            ('atrium_ceiling_c', -1),
            ('atrium_ceiling_plants_a', -1),
            ('atrium_ceiling_plants_b', -1),
            ('atrium_ceiling_plants_c', -1),
        ],
        xBackward=[
            ('air', -1),
        ],
        yForward=[
            ('air', -1),
        ],
        yBackward=[
            ('balcony_l', 0),
            ('balcony_r', 0),
            ('balcony_l_inner', 0),
            ('balcony_r_inner', 0),
        ],
        zForward=[
            ('atrium_ceiling_edge', 0),
            ('atrium_ceiling_edge_corner', 3),
        ],
        zBackward=[
            ('atrium_ceiling_edge', 0),
            ('atrium_ceiling_edge_corner', 0),
        ]
    )

    weight = 0

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
