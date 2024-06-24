from pathlib import Path
from typing import Dict, List

from glm import ivec3

import globals
import vectorTools
import worldTools
from StructureBase import Structure
from gdpc.src.gdpc import minecraft_tools, Box, Block
from gdpc.src.gdpc.interface import placeBlocks


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

    def doPreProcessingSteps(self):
        self.preProcessingSteps.update(worldTools.getTreeCuttingInstructions(self.rectInWorldSpace))
        foundations: List[ivec3] = []
        for y in range(self.box.size.y):
            foundations.extend(list(vectorTools.boxPositions(Box.between(ivec3(0, -1, 0) + self.position + ivec3(0, -y, 0), ivec3(0, -1, 21) + self.position + ivec3(0, -y, 0)))))
            foundations.extend(list(vectorTools.boxPositions(Box.between(ivec3(0, -1, 21) + self.position + ivec3(0, -y, 0), ivec3(7, -1, 21) + self.position + ivec3(0, -y, 0)))))
            foundations.extend(list(vectorTools.boxPositions(Box.between(ivec3(8, -1, 21) + self.position + ivec3(0, -y, 0), ivec3(8, -1, 25) + self.position + ivec3(0, -y, 0)))))
            foundations.extend(list(vectorTools.boxPositions(Box.between(ivec3(8, -1, 25) + self.position + ivec3(0, -y, 0), ivec3(3, -1, 25) + self.position + ivec3(0, -y, 0)))))
            foundations.extend(list(vectorTools.boxPositions(Box.between(ivec3(3, -1, 25) + self.position + ivec3(0, -y, 0), ivec3(3, -1, 37) + self.position + ivec3(0, -y, 0)))))
            foundations.extend(list(vectorTools.boxPositions(Box.between(ivec3(4, -1, 37) + self.position + ivec3(0, -y, 0), ivec3(4, -1, 42) + self.position + ivec3(0, -y, 0)))))
            foundations.extend(list(vectorTools.boxPositions(Box.between(ivec3(4, -1, 42) + self.position + ivec3(0, -y, 0), ivec3(9, -1, 42) + self.position + ivec3(0, -y, 0)))))
            foundations.extend(list(vectorTools.boxPositions(Box.between(ivec3(9, -1, 42) + self.position + ivec3(0, -y, 0), ivec3(9, -1, 43) + self.position + ivec3(0, -y, 0)))))
            foundations.extend(list(vectorTools.boxPositions(Box.between(ivec3(9, -1, 43) + self.position + ivec3(0, -y, 0), ivec3(21, -1, 43) + self.position + ivec3(0, -y, 0)))))
            foundations.extend(list(vectorTools.boxPositions(Box.between(ivec3(21, -1, 42) + self.position + ivec3(0, -y, 0), ivec3(24, -1, 42) + self.position + ivec3(0, -y, 0)))))
            foundations.extend(list(vectorTools.boxPositions(Box.between(ivec3(25, -1, 43) + self.position + ivec3(0, -y, 0), ivec3(37, -1, 43) + self.position + ivec3(0, -y, 0)))))
            foundations.extend(list(vectorTools.boxPositions(Box.between(ivec3(42, -1, 42) + self.position + ivec3(0, -y, 0), ivec3(37, -1, 43) + self.position + ivec3(0, -y, 0)))))
            foundations.extend(list(vectorTools.boxPositions(Box.between(ivec3(42, -1, 42) + self.position + ivec3(0, -y, 0), ivec3(42, -1, 37) + self.position + ivec3(0, -y, 0)))))
            foundations.extend(list(vectorTools.boxPositions(Box.between(ivec3(43, -1, 37) + self.position + ivec3(0, -y, 0), ivec3(43, -1, 25) + self.position + ivec3(0, -y, 0)))))
            foundations.extend(list(vectorTools.boxPositions(Box.between(ivec3(42, -1, 25) + self.position + ivec3(0, -y, 0), ivec3(42, -1, 21) + self.position + ivec3(0, -y, 0)))))
            foundations.extend(list(vectorTools.boxPositions(Box.between(ivec3(43, -1, 21) + self.position + ivec3(0, -y, 0), ivec3(42, -1, 9) + self.position + ivec3(0, -y, 0)))))
            foundations.extend(list(vectorTools.boxPositions(Box.between(ivec3(42, -1, 9) + self.position + ivec3(0, -y, 0), ivec3(42, -1, 4) + self.position + ivec3(0, -y, 0)))))
            foundations.extend(list(vectorTools.boxPositions(Box.between(ivec3(42, -1, 4) + self.position + ivec3(0, -y, 0), ivec3(37, -1, 4) + self.position + ivec3(0, -y, 0)))))
            foundations.extend(list(vectorTools.boxPositions(Box.between(ivec3(37, -1, 4) + self.position + ivec3(0, -y, 0), ivec3(25, -1, 3) + self.position + ivec3(0, -y, 0)))))
            foundations.extend(list(vectorTools.boxPositions(Box.between(ivec3(25, -1, 4) + self.position + ivec3(0, -y, 0), ivec3(21, -1, 4) + self.position + ivec3(0, -y, 0)))))
            foundations.extend(list(vectorTools.boxPositions(Box.between(ivec3(25, -1, 4) + self.position + ivec3(0, -y, 0), ivec3(15, -1, 3) + self.position + ivec3(0, -y, 0)))))
            foundations.extend(list(vectorTools.boxPositions(Box.between(ivec3(15, -1, 3) + self.position + ivec3(0, -y, 0), ivec3(15, -1, 7) + self.position + ivec3(0, -y, 0)))))
            foundations.extend(list(vectorTools.boxPositions(Box.between(ivec3(15, -1, 7) + self.position + ivec3(0, -y, 0), ivec3(11, -1, 7) + self.position + ivec3(0, -y, 0)))))
            foundations.extend(list(vectorTools.boxPositions(Box.between(ivec3(11, -1, 7) + self.position + ivec3(0, -y, 0), ivec3(11, -1, 0) + self.position + ivec3(0, -y, 0)))))
            foundations.extend(list(vectorTools.boxPositions(Box.between(ivec3(11, -1, 0) + self.position + ivec3(0, -y, 0), ivec3(0, -1, 0) + self.position + ivec3(0, -y, 0)))))
            foundations.extend(list(vectorTools.boxPositions(Box.between(ivec3(9, -1, 44) + self.position + ivec3(0, -y, 0), ivec3(21, -1, 46) + self.position + ivec3(0, -y, 0)))))
            foundations.extend(list(vectorTools.boxPositions(Box.between(ivec3(25, -1, 43) + self.position + ivec3(0, -y, 0), ivec3(37, -1, 46) + self.position + ivec3(0, -y, 0)))))
            foundations.extend(list(vectorTools.boxPositions(Box.between(ivec3(43, -1, 37) + self.position + ivec3(0, -y, 0), ivec3(46, -1, 25) + self.position + ivec3(0, -y, 0)))))
            foundations.extend(list(vectorTools.boxPositions(Box.between(ivec3(43, -1, 21) + self.position + ivec3(0, -y, 0), ivec3(46, -1, 9) + self.position + ivec3(0, -y, 0)))))
            foundations.extend(list(vectorTools.boxPositions(Box.between(ivec3(37, -1, 3) + self.position + ivec3(0, -y, 0), ivec3(25, -1, 0) + self.position + ivec3(0, -y, 0)))))
            foundations.extend(list(vectorTools.boxPositions(Box.between(ivec3(21, -1, 0) + self.position + ivec3(0, -y, 0), ivec3(15, -1, 6) + self.position + ivec3(0, -y, 0)))))
            foundations.extend(list(vectorTools.boxPositions(Box.between(ivec3(0, -1, 25) + self.position + ivec3(0, -y, 0), ivec3(3, -1, 37) + self.position + ivec3(0, -y, 0)))))
        for foundation in foundations:
            self.preProcessingSteps[foundation] = Block(id='minecraft:polished_andesite')

        # noinspection PyTypeChecker
        placeBlocks(blocks=self.preProcessingSteps.items())

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
