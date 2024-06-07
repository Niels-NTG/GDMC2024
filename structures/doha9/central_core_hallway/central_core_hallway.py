from pathlib import Path

from glm import ivec3

import globals
from Adjacency import StructureAdjacency
from StructureBase import Structure


class CentralCoreHallway(Structure):
    adjecencies = StructureAdjacency(
        name='central_core_hallway',
        xForward=[
            ('x_junction', 0),
        ],
        xBackward=[
            ('air', -1),
        ],
        yForward=[
            ('air', -1),
            ('central_core_hallway', -1),
        ],
        yBackward=[
            ('air', -1),
            ('central_core_hallway', -1),
        ],
        zForward=[
            ('air', -1),
        ],
        zBackward=[
            ('air', -1),
        ]
    )

    weight = 0.0001

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