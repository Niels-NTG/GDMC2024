from pathlib import Path

from glm import ivec3

import globals
from Adjacency import StructureAdjacency
from StructureBase import Structure


class Wall(Structure):

    adjecencies = StructureAdjacency(
        name='wall',
        xForward=[
            ('air', -1),
        ],
        xBackward=[
            ('center', -1),
            ('corner', 1),
            ('corner', 2),
            ('wall', 1),
            ('wall', 2),
            ('wall', 3),
        ],
        zForward=[
            ('center', -1),
            ('corner', 0),
            ('wall', 0),
            ('wall', 1),
        ],
        zBackward=[
            ('center', -1),
            ('corner', 3),
            ('wall', 0),
            ('wall', 3),
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
