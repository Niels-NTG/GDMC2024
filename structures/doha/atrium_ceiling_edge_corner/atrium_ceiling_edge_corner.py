from pathlib import Path

from glm import ivec3

import globals
from Adjacency import StructureAdjacency
from StructureBase import Structure


class AtriumCeilingEdgeCorner(Structure):
    adjecencies = StructureAdjacency(
        name='atrium_ceiling_edge_corner',
        xForward=[
            ('atrium_ceiling_edge', 1),
        ],
        xBackward=[
            ('air', -1),
        ],
        yForward=[
            ('air', -1),
        ],
        yBackward=[
            ('balcony_corner', 0),
        ],
        zForward=[
            ('atrium_ceiling_edge', 0),
        ],
        zBackward=[
            ('air', -1),
        ],
        walls=[
            'xBackward',
            'zBackward',
            'yForward',
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
