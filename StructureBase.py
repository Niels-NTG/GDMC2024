from __future__ import annotations

import functools
from copy import deepcopy
from typing import TYPE_CHECKING, Any, Dict, List, Tuple

import nbtlib

import bookTools
import nbtTools
from gdpc.src.gdpc import Block, minecraft_tools

if TYPE_CHECKING:
    from StructureFolder import StructureFolder
    from StructureFile import StructureFile

from glm import ivec3, ivec2

import globals
import worldTools
from Adjacency import StructureAdjacency
from gdpc.src.gdpc.interface import placeStructure, placeBlocks
from gdpc.src.gdpc.vector_tools import Box, Rect


class Structure:

    decorationStructureFiles: Dict[str, StructureFile]
    transitionStructureFiles: Dict[str, StructureFile]
    structureFile: StructureFile

    customProperties: Dict[str, Any]

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

        self.structureFile = structureFolder.structureFile
        self.nbt = deepcopy(self.structureFile.nbt)
        self.transitionStructureFiles = structureFolder.transitionStructureFiles
        self.decorationStructureFiles = structureFolder.decorationStructureFiles

        self.customProperties = dict()

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
        self.preProcessingSteps.update(worldTools.getTreeCuttingInstructions(self.rectInWorldSpace))

        for preProcessingStep in self.preProcessingSteps:
            globals.editor.placeBlockGlobal(
                position=preProcessingStep.position,
                block=preProcessingStep.block,
            )

    def place(self):
        placeStructure(
            self.nbt,
            position=self.position, rotate=self.rotation, mirror=None,
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

    def addBooks(self, books: List[str]):
        if len(books) == 0:
            return

        lastBookYear = bookTools.yearFromSNBT(books[0])
        lastBookAuthor = bookTools.primaryAuthorFromSNBT(books[0])
        moveToNextWall = False
        for bookCabinet in self.bookShelves:

            firstBookInCabinetYear = lastBookYear
            firstBookInCabinetAuthor = lastBookAuthor

            for bookShelfPosition, bookShelfRotation in self.bookShelves[bookCabinet].items():
                if len(books) == 0:
                    return
                for bookIndex in range(6):
                    if (len(books) - 1) < bookIndex:
                        return
                    book = books[bookIndex]
                    bookYear = bookTools.yearFromSNBT(book)
                    bookAuthor = bookTools.primaryAuthorFromSNBT(book)
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
                    lastBookYear = bookYear
                    lastBookAuthor = bookAuthor
                if moveToNextWall:
                    moveToNextWall = False
                    break

            # lastBookInCabinetYear = lastBookYear
            lastBookInCabinetAuthor = lastBookAuthor

            signPosition = self.signs[bookCabinet]
            signData = nbtlib.parse_nbt(minecraft_tools.signData(
                frontLine2=firstBookInCabinetYear,
                frontLine3=f'{bookTools.getAuthorTLA(firstBookInCabinetAuthor)} — {bookTools.getAuthorTLA(lastBookInCabinetAuthor)}',
                frontIsGlowing=True,
                isWaxed=True,
            ))
            signBlockId = nbtTools.getBlockIdAt(self.nbt, signPosition)['Name']
            nbtTools.setStructureBlock(
                self.nbt,
                signPosition,
                signBlockId,
                None,
                signData
            )

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

    def __eq__(self, other):
        return hash(self) == hash(other)

    def __hash__(self):
        return hash((self.structureFile, self.position, self.rotation))

    def __repr__(self):
        return f'{self.structureFile}; pos: {self.position.x},{self.position.y},{self.position.z}; r: {self.rotation}'
