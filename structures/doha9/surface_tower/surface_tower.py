from pathlib import Path
from typing import Dict, List

from glm import ivec3

import globals
from StructureBase import Structure
from gdpc.src.gdpc import minecraft_tools


class SurfaceTower(Structure):

    signs = {
        'down1': ivec3(7, 5, 19),
        'down2': ivec3(7, 5, 18),
        'down3': ivec3(7, 5, 17),
        'surface1': ivec3(3, 6, 28),
        'surface2': ivec3(3, 6, 34),
        'surface3': ivec3(12, 6, 43),
        'surface4': ivec3(18, 6, 43),
        'surface5': ivec3(28, 6, 43),
        'surface6': ivec3(34, 6, 43),
        'surface7': ivec3(43, 6, 34),
        'surface8': ivec3(43, 6, 34),
        'surface9': ivec3(43, 6, 28),
        'surface10': ivec3(43, 6, 18),
        'surface11': ivec3(43, 6, 12),
        'surface12': ivec3(34, 6, 3),
        'surface13': ivec3(28, 6, 3),
        'surface14': ivec3(18, 6, 3),
    }

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

    @property
    def position(self) -> ivec3:
        return self.offset + (self.tile * ivec3(9, 10, 9))

    def place(self):
        self.doPreProcessingSteps()
        super().place()

    def addWayFinding(self, categoryLabel: str, floorNumber: int, data: Dict[int, List[Dict[str, str]]]):
        labels = (categoryLabel + ' ').split(' ')
        outdoorSigns = [
            'surface1',
            'surface2',
            'surface3',
            'surface4',
            'surface5',
            'surface6',
            'surface7',
            'surface8',
            'surface9',
            'surface10',
            'surface11',
            'surface12',
            'surface13',
            'surface14',
        ]
        for outdoorSign in outdoorSigns:
            self.writeSign(
                signIndex=outdoorSign,
                signData=minecraft_tools.signData(
                    frontLine1='Library',
                    frontLine2='of',
                    frontLine3=labels[0],
                    frontLine4=labels[1],
                    frontIsGlowing=True,
                    isWaxed=True,
                )
            )
        self.writeSign(
            signIndex='down1',
            signData=minecraft_tools.signData(
                frontLine1='⬇⬇⬇⬇⬇⬇⬇⬇',
                frontLine2='⬇⬇⬇⬇⬇⬇⬇⬇',
                frontLine3='⬇⬇⬇⬇⬇⬇⬇⬇',
                frontLine4='⬇⬇⬇⬇⬇⬇⬇⬇',
                frontIsGlowing=True,
                isWaxed=True,
            )
        )
        self.writeSign(
            signIndex='down2',
            signData=minecraft_tools.signData(
                frontLine1='⬇⬇⬇⬇⬇⬇⬇⬇',
                frontLine2='TO',
                frontLine3='COLLECTION',
                frontLine4='⬇⬇⬇⬇⬇⬇⬇⬇',
                frontIsGlowing=True,
                isWaxed=True,
            )
        )
        self.writeSign(
            signIndex='down3',
            signData=minecraft_tools.signData(
                frontLine1='⬇⬇⬇⬇⬇⬇⬇⬇',
                frontLine2='⬇⬇⬇⬇⬇⬇⬇⬇',
                frontLine3='⬇⬇⬇⬇⬇⬇⬇⬇',
                frontLine4='⬇⬇⬇⬇⬇⬇⬇⬇',
                frontIsGlowing=True,
                isWaxed=True,
            )
        )
