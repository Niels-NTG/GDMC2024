from pathlib import Path

from glm import ivec3

import globals
from Adjacency import StructureAdjacency
from StructureBase import Structure


class Ladder(Structure):
    adjecencies = StructureAdjacency(
        name='ladder',
        xForward=[
            ('air', -1),
        ],
        xBackward=[
            ('t_junction', 0),
        ],
        yForward=[
            ('ladder', -1),
        ],
        yBackward=[
            ('ladder', -1),
        ],
        zForward=[
            ('air', -1),
        ],
        zBackward=[
            ('air', -1),
        ],
        walls=[
            'xForward',
            'zForward',
            'zBackward',
        ],
    )

    weight = 0.1

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
