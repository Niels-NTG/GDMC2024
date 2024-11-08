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
            ('wall_l', 2),
            ('wall_r', 2),
            ('wall_l_inner', 2),
            ('wall_r_inner', 2),
            ('wall_middle', 2),
            ('hallway', 1),
            ('hallway', 3),
            ('wall_lectern', 0),
            ('corner_outer', 0),
            ('corner_outer', 3),
            ('atrium_ceiling_edge', 0),
            ('atrium_ceiling_edge_corner', 0),
            ('atrium_ceiling_edge_corner', 3),
        ],
        xBackward=[
            ('air', -1),
            ('wall_l', 0),
            ('wall_r', 0),
            ('wall_l_inner', 0),
            ('wall_r_inner', 0),
            ('wall_middle', 0),
            ('hallway', 1),
            ('hallway', 3),
            ('wall_lectern', 2),
            ('corner_outer', 1),
            ('corner_outer', 2),
            ('atrium_ceiling_edge', 2),
            ('atrium_ceiling_edge_corner', 1),
            ('atrium_ceiling_edge_corner', 2),
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
            ('atrium_ceiling_edge', -1),
            ('atrium_ceiling_edge_corner', -1),
            ('atrium_ceiling_a', -1),
            ('atrium_ceiling_b', -1),
            ('atrium_ceiling_c', -1),
            ('atrium_ceiling_plants_a', -1),
            ('atrium_ceiling_plants_b', -1),
            ('atrium_ceiling_plants_c', -1),
        ],
        zForward=[
            ('air', -1),
            ('wall_l', 3),
            ('wall_r', 3),
            ('wall_l_inner', 3),
            ('wall_r_inner', 3),
            ('wall_middle', 3),
            ('hallway', 0),
            ('hallway', 2),
            ('wall_lectern', 1),
            ('corner_outer', 0),
            ('corner_outer', 1),
            ('atrium_ceiling_edge', 1),
            ('atrium_ceiling_edge_corner', 0),
            ('atrium_ceiling_edge_corner', 1),
        ],
        zBackward=[
            ('air', -1),
            ('wall_l', 1),
            ('wall_r', 1),
            ('wall_l_inner', 1),
            ('wall_r_inner', 1),
            ('wall_middle', 1),
            ('hallway', 0),
            ('hallway', 2),
            ('wall_lectern', 3),
            ('corner_outer', 2),
            ('corner_outer', 3),
            ('atrium_ceiling_edge', 3),
            ('atrium_ceiling_edge_corner', 2),
            ('atrium_ceiling_edge_corner', 3),
        ]
    )

    weight = 0.01

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
