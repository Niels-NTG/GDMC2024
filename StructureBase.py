from __future__ import annotations

import functools
from copy import deepcopy
from typing import TYPE_CHECKING, Dict, List, Tuple

import nbtlib

import bookTools
import nbtTools
from gdpc.src.gdpc import Block, minecraft_tools

if TYPE_CHECKING:
    from StructureFolder import StructureFolder
    from StructureFile import StructureFile

from glm import ivec3, ivec2

from Adjacency import StructureAdjacency
from gdpc.src.gdpc.interface import placeStructure, placeBlocks
from gdpc.src.gdpc.vector_tools import Box, Rect


class Structure:

    decorationStructureFiles: Dict[str, StructureFile]
    transitionStructureFiles: Dict[str, StructureFile]
    structureFolder: StructureFolder
    structureFile: StructureFile

    preProcessingSteps: Dict[ivec3, Block]
    postProcessingSteps: List[Tuple[ivec3, Block]]

    adjecencies: StructureAdjacency

    _rotation: int
    tile: ivec3

    weight: float = 0.5

    bookShelves: Dict[str, Dict[ivec3, str]] = []

    signs: Dict[str, ivec3] = dict()

    def __init__(
        self,
        structureFolder: StructureFolder,
        withRotation: int = 0,
        tile: ivec3 = ivec3(0, 0, 0),
        offset: ivec3 = ivec3(0, 0, 0),
    ):

        self.structureFolder = structureFolder
        self.structureFile = structureFolder.structureFile
        self.nbt = deepcopy(self.structureFile.nbt)
        self.transitionStructureFiles = structureFolder.transitionStructureFiles
        self.decorationStructureFiles = structureFolder.decorationStructureFiles

        self.preProcessingSteps = dict()
        self.postProcessingSteps = []

        self.rotation = withRotation
        self.tile = tile
        self.offset = offset

    @property
    def position(self) -> ivec3:
        return self.offset + (self.tile * self.box.size)

    @property
    def position2D(self) -> ivec2:
        return ivec2(self.position.x, self.position.z)

    @property
    def position2DCentered(self) -> ivec2:
        return self.rectInWorldSpace.center

    @property
    def rotation(self) -> int:
        return self._rotation

    @rotation.setter
    def rotation(self, value: int):
        self._rotation = value % 4

    @functools.cached_property
    def box(self) -> Box:
        return Box(
            size=ivec3(
                self.structureFile.sizeX,
                self.structureFile.sizeY,
                self.structureFile.sizeZ
            )
        )

    @property
    def boxInWorldSpace(self) -> Box:
        return Box(
            offset=self.position,
            size=ivec3(
                self.structureFile.sizeX,
                self.structureFile.sizeY,
                self.structureFile.sizeZ
            )
        )

    @functools.cached_property
    def rect(self) -> Rect:
        return self.box.toRect()

    @property
    def rectInWorldSpace(self) -> Rect:
        return self.boxInWorldSpace.toRect()

    @property
    def name(self):
        return self.structureFolder.name

    def isIntersection(self, otherStructure: Structure = None) -> bool:
        if otherStructure is None:
            return False
        otherStructureBox = otherStructure.boxInWorldSpace
        otherStructureBox.erode()
        currentBox = self.boxInWorldSpace
        return currentBox.collides(otherStructureBox)

    def isSameType(self, otherStructure: Structure = None) -> bool:
        if otherStructure:
            return otherStructure.structureFile == self.structureFile
        return False

    def doPreProcessingSteps(self):
        # noinspection PyTypeChecker
        placeBlocks(blocks=self.preProcessingSteps.items())

    def place(self):
        placeStructure(
            self.nbt,
            position=self.position, rotate=self.rotation, mirror=None, doBlockUpdates=False,
            pivot=self.structureFile.centerPivot,
        )

    def doPostProcessingSteps(self):
        if len(self.postProcessingSteps):
            placeBlocks(
                blocks=self.postProcessingSteps,
                doBlockUpdates=False,
            )

    @property
    def bookCapacity(self) -> int:
        # The minecraft:chiseled_bookshelf block has a capacity of 6 books.
        bookShelfCount = 0
        for bookWall in self.bookShelves:
            bookShelfCount += len(self.bookShelves[bookWall])
        return bookShelfCount * 6

    def addBooks(
        self,
        books: List[str],
        categoryLabel: str,
        floorNumber: int,
        isDirectionInverted: bool
    ) -> List[Dict[str, str]]:
        if len(books) == 0 or self.bookCapacity == 0:
            return []

        lastBook = books[0]
        lastBookYear = bookTools.yearFromSNBT(books[0])
        lastBookAuthor = bookTools.primaryAuthorFromSNBT(books[0])
        moveToNextWall = False
        bookShelfKeys = list(self.bookShelves.keys())
        if isDirectionInverted:
            bookShelfKeys.reverse()
        bookCabinetIndex = 0
        bookRanges = []
        for bookCabinet in bookShelfKeys:

            firstBookInCabinetYear = lastBookYear
            firstBookInCabinetAuthor = lastBookAuthor
            lastBookInCabinetAuthor = lastBookAuthor

            bookCabinetLocationLabel = f'{abs(floorNumber)}.{self.tile.x}.{self.tile.z}.{chr(65 + bookCabinetIndex)}'

            bookRanges.append({
                'firstBook': books[0],
                'lastBook': books[0],
                'cabinet': bookCabinetLocationLabel,
            })

            for bookShelfPosition, bookShelfRotation in self.bookShelves[bookCabinet].items():
                if len(books) == 0:
                    return bookRanges
                for bookIndex in range(6):
                    if (len(books) - 1) < bookIndex:
                        self.fillBookShelf(bookShelfPosition, bookShelfRotation, books[:bookIndex])
                        del books[:bookIndex]
                        bookRanges[bookCabinetIndex]['lastBook'] = lastBook
                        return bookRanges
                    book = books[bookIndex]
                    bookYear = bookTools.yearFromSNBT(book)
                    bookAuthor = bookTools.primaryAuthorFromSNBT(book)
                    lastBookInCabinetAuthor = lastBookAuthor
                    if bookYear != lastBookYear or not bookTools.isSameFirstCharacter(bookAuthor, lastBookAuthor):
                        self.fillBookShelf(bookShelfPosition, bookShelfRotation, books[:bookIndex])
                        del books[:bookIndex]
                        lastBookYear = bookYear
                        lastBookAuthor = bookAuthor
                        moveToNextWall = True
                        break
                    if bookIndex == 5:
                        self.fillBookShelf(bookShelfPosition, bookShelfRotation, books[:6])
                        del books[:6]
                    lastBook = book
                    lastBookYear = bookYear
                    lastBookAuthor = bookAuthor
                if moveToNextWall:
                    moveToNextWall = False
                    break

            bookRanges[bookCabinetIndex]['lastBook'] = lastBook
            signData = minecraft_tools.signData(
                frontLine1=categoryLabel,
                frontLine2=firstBookInCabinetYear,
                frontLine3=f'{bookTools.getAuthor4LA(firstBookInCabinetAuthor)}–{bookTools.getAuthor4LA(lastBookInCabinetAuthor)}',
                frontLine4=bookCabinetLocationLabel,
                frontIsGlowing=True,
                isWaxed=True,
            )
            self.writeSign(bookCabinet, signData)
            bookCabinetIndex += 1

        return bookRanges

    def fillBookShelf(self, pos: ivec3, rotation: str, bookShelfEntries: List[str]):
        blockState, blockData = bookTools.fillBookShelf(bookShelfEntries)
        blockState['facing'] = rotation
        nbtTools.setStructureBlock(
            self.nbt,
            pos,
            'minecraft:chiseled_bookshelf',
            blockState,
            blockData,
        )

    def writeSign(self, signIndex: str, signData: str):
        signData = nbtlib.parse_nbt(signData)
        signPosition = self.signs[signIndex]
        signBlockId = nbtTools.getBlockIdAt(self.nbt, signPosition)['Name']
        nbtTools.setStructureBlock(
            self.nbt,
            signPosition,
            signBlockId,
            None,
            signData
        )

    def addWayFinding(self, categoryLabel: str, floorNumber: int, data: Dict[int, List[Dict[str, str]]]):
        pass

    def __eq__(self, other):
        return hash(self) == hash(other)

    def __hash__(self):
        return hash((self.structureFile, self.position, self.rotation))

    def __repr__(self):
        return f'{self.structureFile}; pos: {self.position.x},{self.position.y},{self.position.z}; r: {self.rotation}'
