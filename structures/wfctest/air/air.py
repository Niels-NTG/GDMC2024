from pathlib import Path

from glm import ivec3

import globals
from Adjacency import StructureAdjacency
from StructureBase import Structure


class Air(Structure):

    adjecencies = StructureAdjacency(
        name='air',
        xForward=[
            ('wall', 2),
            ('corner', 1),
            ('corner', 2),
            ('air', -1),
        ],
        xBackward=[
            ('wall', 0),
            ('corner', 0),
            ('corner', 3),
            ('air', -1),
        ],
        yForward=[
            ('air', -1),
        ],
        yBackward=[
            ('center', -1),
            ('air', -1),
            ('corner', -1),
            ('wall', -1),
        ],
        zForward=[
            ('wall', 3),
            ('corner', 2),
            ('corner', 3),
            ('air', -1),
        ],
        zBackward=[
            ('wall', 1),
            ('corner', 0),
            ('corner', 1),
            ('air', -1),
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
