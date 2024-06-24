from pathlib import Path
from typing import Dict, List

import nbtlib
from glm import ivec3

import bookTools
import globals
import nbtTools
import vectorTools
from Adjacency import StructureAdjacency
from StructureBase import Structure
from gdpc.src.gdpc import minecraft_tools, Box


class CentralCore(Structure):

    adjecencies = StructureAdjacency(
        name='central_core',
        xForward=[
            ('central_core_hallway', 0),
        ],
        xBackward=[],
        yForward=[],
        yBackward=[],
        zForward=[
            ('central_core_hallway', 1),
        ],
        zBackward=[
            ('central_core_hallway', 3),
        ]
    )

    weight = 0.0001

    bookShelves = {
        'east1': {
            ivec3(7, 4, 13): 'east',
            ivec3(7, 4, 12): 'east',
            ivec3(7, 4, 11): 'east',
            ivec3(7, 4, 10): 'east',
            ivec3(7, 4, 9): 'east',
            ivec3(7, 3, 13): 'east',
            ivec3(7, 3, 12): 'east',
            ivec3(7, 3, 11): 'east',
            ivec3(7, 3, 10): 'east',
            ivec3(7, 3, 9): 'east',
            ivec3(7, 2, 13): 'east',
            ivec3(7, 2, 12): 'east',
            ivec3(7, 2, 11): 'east',
            ivec3(7, 2, 10): 'east',
            ivec3(7, 2, 9): 'east',
        },
        'south1': {
            ivec3(9, 4, 7): 'south',
            ivec3(10, 4, 7): 'south',
            ivec3(11, 4, 7): 'south',
            ivec3(12, 4, 7): 'south',
            ivec3(13, 4, 7): 'south',
            ivec3(9, 3, 7): 'south',
            ivec3(10, 3, 7): 'south',
            ivec3(11, 3, 7): 'south',
            ivec3(12, 3, 7): 'south',
            ivec3(13, 3, 7): 'south',
            ivec3(9, 2, 7): 'south',
            ivec3(10, 2, 7): 'south',
            ivec3(11, 2, 7): 'south',
            ivec3(12, 2, 7): 'south',
            ivec3(13, 2, 7): 'south',
        },
        'south2': {
            ivec3(15, 4, 7): 'south',
            ivec3(16, 4, 7): 'south',
            ivec3(17, 4, 7): 'south',
            ivec3(18, 4, 7): 'south',
            ivec3(19, 4, 7): 'south',
            ivec3(15, 3, 7): 'south',
            ivec3(16, 3, 7): 'south',
            ivec3(17, 3, 7): 'south',
            ivec3(18, 3, 7): 'south',
            ivec3(19, 3, 7): 'south',
            ivec3(15, 2, 7): 'south',
            ivec3(16, 2, 7): 'south',
            ivec3(17, 2, 7): 'south',
            ivec3(18, 2, 7): 'south',
            ivec3(19, 2, 7): 'south',
        },
        'south3': {
            ivec3(25, 4, 7): 'south',
            ivec3(26, 4, 7): 'south',
            ivec3(27, 4, 7): 'south',
            ivec3(28, 4, 7): 'south',
            ivec3(29, 4, 7): 'south',
            ivec3(25, 3, 7): 'south',
            ivec3(26, 3, 7): 'south',
            ivec3(27, 3, 7): 'south',
            ivec3(28, 3, 7): 'south',
            ivec3(29, 3, 7): 'south',
            ivec3(25, 2, 7): 'south',
            ivec3(26, 2, 7): 'south',
            ivec3(27, 2, 7): 'south',
            ivec3(28, 2, 7): 'south',
            ivec3(29, 2, 7): 'south',
        },
        'south4': {
            ivec3(31, 4, 7): 'south',
            ivec3(32, 4, 7): 'south',
            ivec3(33, 4, 7): 'south',
            ivec3(34, 4, 7): 'south',
            ivec3(35, 4, 7): 'south',
            ivec3(31, 3, 7): 'south',
            ivec3(32, 3, 7): 'south',
            ivec3(33, 3, 7): 'south',
            ivec3(34, 3, 7): 'south',
            ivec3(35, 3, 7): 'south',
            ivec3(31, 2, 7): 'south',
            ivec3(32, 2, 7): 'south',
            ivec3(33, 2, 7): 'south',
            ivec3(34, 2, 7): 'south',
            ivec3(35, 2, 7): 'south',
        },
        'west1': {
            ivec3(37, 4, 9): 'west',
            ivec3(37, 4, 10): 'west',
            ivec3(37, 4, 11): 'west',
            ivec3(37, 4, 12): 'west',
            ivec3(37, 4, 13): 'west',
            ivec3(37, 3, 9): 'west',
            ivec3(37, 3, 10): 'west',
            ivec3(37, 3, 11): 'west',
            ivec3(37, 3, 12): 'west',
            ivec3(37, 3, 13): 'west',
            ivec3(37, 2, 9): 'west',
            ivec3(37, 2, 10): 'west',
            ivec3(37, 2, 11): 'west',
            ivec3(37, 2, 12): 'west',
            ivec3(37, 2, 13): 'west',
        },
        'west2': {
            ivec3(37, 4, 15): 'west',
            ivec3(37, 4, 16): 'west',
            ivec3(37, 4, 17): 'west',
            ivec3(37, 4, 18): 'west',
            ivec3(37, 4, 19): 'west',
            ivec3(37, 3, 15): 'west',
            ivec3(37, 3, 16): 'west',
            ivec3(37, 3, 17): 'west',
            ivec3(37, 3, 18): 'west',
            ivec3(37, 3, 19): 'west',
            ivec3(37, 2, 15): 'west',
            ivec3(37, 2, 16): 'west',
            ivec3(37, 2, 17): 'west',
            ivec3(37, 2, 18): 'west',
            ivec3(37, 2, 19): 'west',
        },
        'west3': {
            ivec3(37, 4, 25): 'west',
            ivec3(37, 4, 26): 'west',
            ivec3(37, 4, 27): 'west',
            ivec3(37, 4, 28): 'west',
            ivec3(37, 4, 29): 'west',
            ivec3(37, 3, 25): 'west',
            ivec3(37, 3, 26): 'west',
            ivec3(37, 3, 27): 'west',
            ivec3(37, 3, 28): 'west',
            ivec3(37, 3, 29): 'west',
            ivec3(37, 2, 25): 'west',
            ivec3(37, 2, 26): 'west',
            ivec3(37, 2, 27): 'west',
            ivec3(37, 2, 28): 'west',
            ivec3(37, 2, 29): 'west',
        },
        'west4': {
            ivec3(37, 4, 31): 'west',
            ivec3(37, 4, 32): 'west',
            ivec3(37, 4, 33): 'west',
            ivec3(37, 4, 34): 'west',
            ivec3(37, 4, 35): 'west',
            ivec3(37, 3, 31): 'west',
            ivec3(37, 3, 32): 'west',
            ivec3(37, 3, 33): 'west',
            ivec3(37, 3, 34): 'west',
            ivec3(37, 3, 35): 'west',
            ivec3(37, 2, 31): 'west',
            ivec3(37, 2, 32): 'west',
            ivec3(37, 2, 33): 'west',
            ivec3(37, 2, 34): 'west',
            ivec3(37, 2, 35): 'west',
        },
        'north1': {
            ivec3(35, 4, 37): 'north',
            ivec3(34, 4, 37): 'north',
            ivec3(33, 4, 37): 'north',
            ivec3(32, 4, 37): 'north',
            ivec3(31, 4, 37): 'north',
            ivec3(35, 3, 37): 'north',
            ivec3(34, 3, 37): 'north',
            ivec3(33, 3, 37): 'north',
            ivec3(32, 3, 37): 'north',
            ivec3(31, 3, 37): 'north',
            ivec3(35, 2, 37): 'north',
            ivec3(34, 2, 37): 'north',
            ivec3(33, 2, 37): 'north',
            ivec3(32, 2, 37): 'north',
            ivec3(31, 2, 37): 'north',
        },
        'north2': {
            ivec3(29, 4, 37): 'north',
            ivec3(28, 4, 37): 'north',
            ivec3(27, 4, 37): 'north',
            ivec3(26, 4, 37): 'north',
            ivec3(25, 4, 37): 'north',
            ivec3(29, 3, 37): 'north',
            ivec3(28, 3, 37): 'north',
            ivec3(27, 3, 37): 'north',
            ivec3(26, 3, 37): 'north',
            ivec3(25, 3, 37): 'north',
            ivec3(29, 2, 37): 'north',
            ivec3(28, 2, 37): 'north',
            ivec3(27, 2, 37): 'north',
            ivec3(26, 2, 37): 'north',
            ivec3(25, 2, 37): 'north',
        },
        'north3': {
            ivec3(19, 4, 37): 'north',
            ivec3(18, 4, 37): 'north',
            ivec3(17, 4, 37): 'north',
            ivec3(16, 4, 37): 'north',
            ivec3(15, 4, 37): 'north',
            ivec3(19, 3, 37): 'north',
            ivec3(18, 3, 37): 'north',
            ivec3(17, 3, 37): 'north',
            ivec3(16, 3, 37): 'north',
            ivec3(15, 3, 37): 'north',
            ivec3(19, 2, 37): 'north',
            ivec3(18, 2, 37): 'north',
            ivec3(17, 2, 37): 'north',
            ivec3(16, 2, 37): 'north',
            ivec3(15, 2, 37): 'north',
        },
        'north4': {
            ivec3(13, 4, 37): 'north',
            ivec3(12, 4, 37): 'north',
            ivec3(11, 4, 37): 'north',
            ivec3(10, 4, 37): 'north',
            ivec3(9, 4, 37): 'north',
            ivec3(13, 3, 37): 'north',
            ivec3(12, 3, 37): 'north',
            ivec3(11, 3, 37): 'north',
            ivec3(10, 3, 37): 'north',
            ivec3(9, 3, 37): 'north',
            ivec3(13, 2, 37): 'north',
            ivec3(12, 2, 37): 'north',
            ivec3(11, 2, 37): 'north',
            ivec3(10, 2, 37): 'north',
            ivec3(9, 2, 37): 'north',
        },
        'east2': {
            ivec3(7, 4, 35): 'east',
            ivec3(7, 4, 34): 'east',
            ivec3(7, 4, 33): 'east',
            ivec3(7, 4, 32): 'east',
            ivec3(7, 4, 31): 'east',
            ivec3(7, 3, 35): 'east',
            ivec3(7, 3, 34): 'east',
            ivec3(7, 3, 33): 'east',
            ivec3(7, 3, 32): 'east',
            ivec3(7, 3, 31): 'east',
            ivec3(7, 2, 35): 'east',
            ivec3(7, 2, 34): 'east',
            ivec3(7, 2, 33): 'east',
            ivec3(7, 2, 32): 'east',
            ivec3(7, 2, 31): 'east',
        },
    }

    signs = {
        'east1': ivec3(8, 6, 11),
        'south1': ivec3(11, 6, 8),
        'south2': ivec3(17, 6, 8),
        'south3': ivec3(27, 6, 8),
        'south4': ivec3(33, 6, 8),
        'west1': ivec3(36, 6, 11),
        'west2': ivec3(36, 6, 17),
        'west3': ivec3(36, 6, 27),
        'west4': ivec3(36, 6, 33),
        'north1': ivec3(33, 6, 36),
        'north2': ivec3(27, 6, 36),
        'north3': ivec3(17, 6, 36),
        'north4': ivec3(11, 6, 36),
        'east2': ivec3(8, 6, 33),
        'up1': ivec3(8, 6, 27),
        'up2': ivec3(8, 5, 27),
        'down1': ivec3(8, 6, 17),
        'down2': ivec3(8, 5, 17),
        'floor1': ivec3(7, 3, 23),
        'floor2': ivec3(7, 3, 22),
        'floor3': ivec3(7, 3, 21),
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

    def addWayFinding(self, categoryLabel: str, floorNumber: int, data: Dict[int, List[Dict[str, str]]]):
        floorData = data[floorNumber]
        upperFloor = data.get(floorNumber + 1, None)
        lowerFloor = data.get(floorNumber - 1, None)

        self.writeSign(
            signIndex='floor1',
            signData=minecraft_tools.signData(
                frontLine2='FROM',
                frontLine3=bookTools.yearFromSNBT(floorData[0]['firstBook']),
                frontLine4=bookTools.getAuthor4LA(bookTools.primaryAuthorFromSNBT(floorData[0]['firstBook'])),
                frontIsGlowing=True,
                isWaxed=True,
            )
        )
        self.writeSign(
            signIndex='floor2',
            signData=minecraft_tools.signData(
                frontLine1=categoryLabel,
                frontLine2='⬌',
                frontLine3=f'FLOOR {floorNumber}',
                frontIsGlowing=True,
                isWaxed=True,
            )
        )
        self.writeSign(
            signIndex='floor3',
            signData=minecraft_tools.signData(
                frontLine2='TO',
                frontLine3=bookTools.yearFromSNBT(floorData[-1]['lastBook']),
                frontLine4=bookTools.getAuthor4LA(bookTools.primaryAuthorFromSNBT(floorData[-1]['lastBook'])),
                frontIsGlowing=True,
                isWaxed=True,
            )
        )

        self.writeSign(
            signIndex='up1',
            signData=minecraft_tools.signData(
                frontLine1='⬆⬆⬆',
                frontLine2='FLOOR',
                frontLine3=f'{floorNumber + 1}',
                frontLine4=categoryLabel if upperFloor else '',
                frontIsGlowing=True,
                backLine1='⬌',
                backLine2=categoryLabel,
                backLine3=f'FLOOR {floorNumber}',
                backLine4='⬌',
                backIsGlowing=True,
                isWaxed=True,
            )
        )
        self.writeSign(
            signIndex='up2',
            signData=minecraft_tools.signData(
                frontLine3=bookTools.yearFromSNBT(upperFloor[-1]["lastBook"]) if upperFloor else '',
                frontLine2='—' if upperFloor else 'EXIT',
                frontLine1=bookTools.yearFromSNBT(upperFloor[0]["firstBook"]) if upperFloor else '',
                frontLine4='⬆⬆⬆' if upperFloor else '',
                frontIsGlowing=True,
                backLine3=bookTools.yearFromSNBT(lowerFloor[-1]["lastBook"]) if lowerFloor else '',
                backLine2='—' if lowerFloor else '',
                backLine1=bookTools.yearFromSNBT(lowerFloor[0]["firstBook"]) if lowerFloor else '',
                backLine4='⭩⭩⭩' if lowerFloor else '',
                backIsGlowing=True,
                isWaxed=True,
            )
        )

        if lowerFloor:
            self.writeSign(
                signIndex='down1',
                signData=minecraft_tools.signData(
                    frontLine1='⬇⬇⬇' if lowerFloor else '',
                    frontLine2='FLOOR' if lowerFloor else '',
                    frontLine3=f'{floorNumber - 1}' if lowerFloor else '',
                    frontLine4=categoryLabel if lowerFloor else '',
                    frontIsGlowing=True,
                    backLine1='⬌',
                    backLine2=categoryLabel,
                    backLine3=f'FLOOR {floorNumber}',
                    backLine4='⬌',
                    backIsGlowing=True,
                    isWaxed=True,
                )
            )
            self.writeSign(
                signIndex='down2',
                signData=minecraft_tools.signData(
                    frontLine3=bookTools.yearFromSNBT(lowerFloor[-1]["lastBook"]) if lowerFloor else '',
                    frontLine2='—' if lowerFloor else '',
                    frontLine1=bookTools.yearFromSNBT(lowerFloor[0]["firstBook"]) if lowerFloor else '',
                    frontLine4='⬇⬇⬇' if lowerFloor else '',
                    frontIsGlowing=True,
                    backLine3=bookTools.yearFromSNBT(upperFloor[-1]["lastBook"]) if upperFloor else '',
                    backLine2='—' if upperFloor else '',
                    backLine1=bookTools.yearFromSNBT(upperFloor[0]["firstBook"]) if upperFloor else '',
                    backLine4='⬈⬈⬈' if upperFloor else '',
                    backIsGlowing=True,
                    isWaxed=True,
                )
            )
        else:
            blockWall = Box.between(ivec3(6, 1, 18), ivec3(6, 7, 16))
            for pos in vectorTools.boxPositions(blockWall):
                nbtTools.setStructureBlock(
                    self.nbt,
                    pos,
                    'minecraft:stripped_spruce_log',
                    {
                        'axis': 'y',
                    },
                    None,
                )
            nbtTools.setStructureBlock(
                self.nbt,
                self.signs['down1'],
                'minecraft:air',
                dict(),
                None,
            )
            nbtTools.setStructureBlock(
                self.nbt,
                self.signs['down2'],
                'minecraft:air',
                dict(),
                None,
            )

        indexBookText = '\\\\s'
        lineNumber = 0
        cabinetCount = 0
        lastYear = bookTools.yearFromSNBT(floorData[0]["firstBook"])
        for cabinet in floorData:
            year = bookTools.yearFromSNBT(cabinet["firstBook"])
            if lineNumber == 10 or year != lastYear:
                lineNumber = 0
                if cabinetCount < len(floorData):
                    indexBookText += '\f\\\\s'
            if lineNumber == 0:
                indexBookText += f'§7§l§n{year}§r\n'
            firstAuthor = bookTools.getAuthor4LA(bookTools.primaryAuthorFromSNBT(cabinet['firstBook']))
            lastAuthor = bookTools.getAuthor4LA(bookTools.primaryAuthorFromSNBT(cabinet['lastBook']))
            indexBookText += f'{firstAuthor}–{lastAuthor} §5{cabinet["cabinet"]}§r\n'
            lineNumber += 1
            cabinetCount += 1
            lastYear = year

        lecternData = nbtlib.parse_nbt(minecraft_tools.lecternData(
            bookData=minecraft_tools.bookData(
                title=f'Floor {floorNumber} index',
                author='The Librarian',
                text=indexBookText,
            )
        ))
        nbtTools.setStructureBlock(
            self.nbt,
            ivec3(7, 1, 22),
            'minecraft:lectern',
            {
                'has_book': '"true"',
                'facing': 'east',
            },
            lecternData
        )
