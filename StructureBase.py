from __future__ import annotations

import functools
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from StructureFolder import StructureFolder
    from StructureFile import StructureFile

from glm import ivec3, ivec2

import globals
import worldTools
from Adjacency import StructureAdjacency
from gdpc.gdpc.interface import placeStructure
from gdpc.gdpc.vector_tools import Box, Rect


class Structure:

    decorationStructureFiles: dict[str, StructureFile]
    transitionStructureFiles: dict[str, StructureFile]
    structureFile: StructureFile

    customProperties: dict[str, Any]

    preProcessingSteps: list[worldTools.PlacementInstruction]

    adjecencies: StructureAdjacency

    _rotation: int
    tile: ivec3

    def __init__(
        self,
        structureFolder: StructureFolder,
        withRotation: int = 0,
        tile: ivec3 = ivec3(0, 0, 0),
        offset: ivec3 = ivec3(0, 0, 0),
    ):

        self.structureFile = structureFolder.structureFile
        self.transitionStructureFiles = structureFolder.transitionStructureFiles
        self.decorationStructureFiles = structureFolder.decorationStructureFiles

        self.customProperties = dict()

        self.preProcessingSteps = []

        self.rotation = withRotation
        self.tile = tile
        self.offset = offset

    @property
    def connectors(self) -> dict[ivec3, list[Structure]]:
        rotatedConnectors: dict[ivec3, list[Structure]] = {}
        # for direction in self.adjecencies:
        #     rotatedDirection = vectorTools.rotatePointAroundOrigin3D(
        #         point=direction,
        #         rotation=self.rotation,
        #     )
        #     rotatedConnectors[rotatedDirection] = []
        #     for structureRotation in self.adjecencies[direction]:
        #         structureFolder = globals.structureFolders[structureRotation.name]
        #         newStructure: Structure = structureFolder.structureClass(
        #             withRotation=self.rotation + structureRotation.rotation,
        #             tile=self.tile + rotatedDirection,
        #         )
        #         rotatedConnectors[rotatedDirection].append(newStructure)
        return rotatedConnectors

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
        # noinspection PyTypeChecker
        return Box(
            size=ivec3(
                self.structureFile.sizeX,
                self.structureFile.sizeY,
                self.structureFile.sizeZ
            )
        )

    @property
    def boxInWorldSpace(self) -> Box:
        # noinspection PyTypeChecker
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
        self.preProcessingSteps.extend(worldTools.getTreeCuttingInstructions(self.rectInWorldSpace))

        for preProcessingStep in self.preProcessingSteps:
            globals.editor.placeBlockGlobal(
                position=preProcessingStep.position,
                block=preProcessingStep.block,
            )

    def place(self):
        placeStructure(
            self.structureFile.file,
            position=self.position, rotate=self.rotation, mirror=None,
            pivot=self.structureFile.centerPivot
        )
        print(f'Placed {self}')

    @staticmethod
    def doPostProcessingSteps():
        # for connector in node.connectorSlots:
        #     if connector.transitionStructure is None:
        #         continue
        #     # noinspection PyTypeChecker
        #     placeStructure(
        #         connector.transitionStructure.file,
        #         position=self.position, rotate=(connector.rotation + self.rotation) % 4, mirror=None,
        #         pivot=connector.transitionStructure.centerPivot,
        #     )
        postProcessingSteps: list[worldTools.PlacementInstruction] = []
        for postProcessingStep in postProcessingSteps:
            globals.editor.placeBlockGlobal(
                position=postProcessingStep.position,
                block=postProcessingStep.block,
            )

    def __eq__(self, other):
        return hash(self) == hash(other)

    def __hash__(self):
        return hash((self.structureFile, self.position, self.rotation))

    def __repr__(self):
        return f'{self.structureFile}; pos: {self.position.x},{self.position.y},{self.position.z}; r: {self.rotation}'
