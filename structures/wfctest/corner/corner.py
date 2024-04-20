from pathlib import Path

from glm import ivec3

import globals
from Adjacency import StructureAdjacency
from StructureBase import Structure


class Corner(Structure):

    adjecencies = StructureAdjacency(
        name='corner',
        xForward=[
            ('air', 0),
        ],
        xBackward=[
            ('center', 0),
            ('corner', 1),
            ('wall', 1),
        ],
        zForward=[
            ('air', 0),
        ],
        zBackward=[
            ('center', 0),
            ('corner', 3),
            ('wall', 0),
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
