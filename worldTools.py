from __future__ import annotations

import re
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from StructureBase import Structure

import nbtlib
import numpy as np
from glm import ivec2, ivec3

import globals
import nbtTools
import vectorTools
from gdpc.gdpc import lookup, interface
from gdpc.gdpc.block import Block
from gdpc.gdpc.vector_tools import Box, Rect, loop2D

DEFAULT_HEIGHTMAP_TYPE: str = 'MOTION_BLOCKING_NO_PLANTS'


class PlacementInstruction:

    def __init__(
        self,
        position: ivec3 = None,
        block: Block = None
    ):
        self.position = position
        self.block = block

    def __hash__(self):
        return hash(self.position)


class SimpleEntity:

    def __init__(
        self,
        uuid: str,
        snbt: str = None,
    ):
        self.uuid = uuid
        if snbt:
            self._nbt = nbtTools.SnbttoNbt(snbt)
            self._position = nbtTools.extractEntityBlockPos(self._nbt)
            self._id = nbtTools.extractEntityId(self._nbt)

    @property
    def position(self) -> ivec3 | None:
        if self._position:
            return self._position

    @property
    def id(self) -> str:
        if self._id:
            return self._id
        return ''

    @property
    def nbt(self) -> nbtlib.Compound:
        if self._nbt:
            return self._nbt
        return nbtlib.Compound()

    @property
    def isAboveGround(self) -> bool:
        if self.position:
            try:
                return self.position.y >= getHeightAt(pos=self.position, heightmapType='OCEAN_FLOOR')
            except IndexError:
                return False
        return False

    def __hash__(self):
        return hash(self.nbt)


class EntitiesPerArea:

    def __init__(
        self,
        area: Box,
        entityList: list[SimpleEntity] = None,
    ):
        self.area = area
        self.entityList = entityList if entityList else []

    def __len__(self):
        return len(self.entityList)

    def __hash__(self):
        return hash(self.area)

    def __eq__(self, other):
        return hash(self) == hash(other)


def isStructureInsideBuildArea(structure: Structure) -> bool:
    return isBoxInsideBuildArea(structure.boxInWorldSpace)


def isBoxInsideBuildArea(box: Box) -> bool:
    return vectorTools.isRectinRect(globals.buildarea, box.toRect())


def isStructureTouchingSurface(
    structure: Structure,
    heightmapType: str = DEFAULT_HEIGHTMAP_TYPE
) -> bool:
    return isBoxTouchingSurface(box=structure.boxInWorldSpace, heightmapType=heightmapType)


def isBoxTouchingSurface(
    box: Box,
    heightmapType: str = DEFAULT_HEIGHTMAP_TYPE
) -> bool:
    floorRect = box.toRect()
    for point in loop2D(floorRect.begin, floorRect.end):
        if getHeightAt(pos=point, heightmapType=heightmapType) > box.offset.y:
            return True
    return False


def getSurfaceStandardDeviation(
    rect: Rect,
    heightmapType: str = DEFAULT_HEIGHTMAP_TYPE
) -> (float, int, int):
    heightmapFragment: list[int] = []
    points = rect.inner
    for point in points:
        heightmapFragment.append(getHeightAt(pos=point, heightmapType=heightmapType))
    return float(np.std(heightmapFragment)), min(heightmapFragment), max(heightmapFragment)


def getHeightAt(
    pos: ivec3 | ivec2,
    heightmapType: str = DEFAULT_HEIGHTMAP_TYPE
) -> int:
    # WORLD_SURFACE
    # Stores the Y-level of the highest non-air block.
    #
    # OCEAN_FLOOR
    # Stores the Y-level of the highest block whose material blocks motion. Used only on the server side.
    #
    # MOTION_BLOCKING
    # Stores the Y-level of the highest block whose material blocks motion or blocks that contains a
    # fluid (water, lava, or waterlogging blocks).
    #
    # MOTION_BLOCKING_NO_LEAVES
    # Stores the Y-level of the highest block whose material blocks motion, or blocks that contains a
    # fluid (water, lava, or waterlogging blocks), except various leaves. Used only on the server side.
    if isinstance(pos, ivec3):
        pos = ivec2(pos.x, pos.z)
    heightmap = globals.editor.worldSlice.heightmaps[heightmapType]

    positionRelativeToWorldSlice = (pos - globals.editor.worldSlice.rect.offset)
    return heightmap[positionRelativeToWorldSlice.x, positionRelativeToWorldSlice.y]


def getSurfacePositionAt(
    pos: ivec3 | ivec2,
    heightmapType: str = DEFAULT_HEIGHTMAP_TYPE
) -> ivec3:
    if isinstance(pos, ivec3):
        pos = ivec2(pos.x, pos.z)
    return ivec3(
        pos.x,
        getHeightAt(pos=pos, heightmapType=heightmapType),
        pos.y
    )


def getRandomSurfacePosition(
    rng=np.random.default_rng(),
    heightmapType: str = DEFAULT_HEIGHTMAP_TYPE
) -> ivec3:
    startPosition = ivec3(
        rng.integers(globals.buildarea.begin.x, globals.buildarea.end.x),
        0,
        rng.integers(globals.buildarea.begin.y, globals.buildarea.end.y)
    )
    startPosition.y = getHeightAt(startPosition, heightmapType=heightmapType)
    return startPosition


def getRandomSurfacePositionForBox(
    box: Box,
    rng=np.random.default_rng(),
    heightmapType: str = DEFAULT_HEIGHTMAP_TYPE
) -> ivec3:
    box = Box(box.offset, box.size)
    MAX_ATTEMPTS = 128
    for _ in range(MAX_ATTEMPTS):
        pos = getRandomSurfacePosition(rng, heightmapType)
        box.offset = pos
        if isBoxInsideBuildArea(box):
            return pos
    raise Exception('Could not fit box inside build area')


def getSapling(
    block: Block = None
) -> Block:
    woodType = re.sub(r'minecraft:|_.+$', '', block.id)
    if woodType == 'mangrove':
        return Block(id='minecraft:mangrove_propagule', states={'stage': '1'})
    if woodType in lookup.WOOD_TYPES:
        return Block(id=f'minecraft:{woodType}_sapling', states={'stage': '1'})


def calculateTreeCuttingCost(
    area: Rect
) -> int:
    diffHeightmap = globals.editor.worldSlice.heightmaps['MOTION_BLOCKING_NO_LEAVES'] - \
                    globals.editor.worldSlice.heightmaps['MOTION_BLOCKING_NO_PLANTS']
    outerArea = area.centeredSubRect(size=area.size + 10)
    outerAreaRelativeToBuildArea = Rect(
        offset=outerArea.offset - globals.editor.worldSlice.rect.offset,
        size=outerArea.size
    )
    diffHeightmap = diffHeightmap[
        outerAreaRelativeToBuildArea.begin.x:outerAreaRelativeToBuildArea.end.x,
        outerAreaRelativeToBuildArea.begin.y:outerAreaRelativeToBuildArea.end.y,
    ]
    return int(np.sum(diffHeightmap))


def getTreeCuttingInstructions(
    area: Rect
) -> list[PlacementInstruction]:
    treeCuttingInstructions: list[PlacementInstruction] = []

    innerArea = area.centeredSubRect(size=area.size + 4)
    outerArea = area.centeredSubRect(size=area.size + 10)

    diffHeightmap = globals.editor.worldSlice.heightmaps['MOTION_BLOCKING'] - \
        globals.editor.worldSlice.heightmaps['MOTION_BLOCKING_NO_PLANTS']

    treePositions = np.argwhere(diffHeightmap > 0)

    rng = np.random.default_rng()

    for xzPos in treePositions:
        pos2DInWorldSpace = ivec2(xzPos[0], xzPos[1]) + globals.editor.worldSlice.rect.offset
        if not outerArea.contains(pos2DInWorldSpace):
            continue
        for y in range(diffHeightmap[xzPos[0], xzPos[1]]):
            pos3D = ivec3(
                pos2DInWorldSpace.x,
                y + globals.editor.worldSlice.heightmaps['MOTION_BLOCKING_NO_PLANTS'][xzPos[0], xzPos[1]],
                pos2DInWorldSpace.y
            )
            block: Block = globals.editor.worldSlice.getBlockGlobal(pos3D)
            if block.id in lookup.PLANT_BLOCKS:
                if not innerArea.contains(pos2DInWorldSpace):
                    if block.id in lookup.LEAVES and rng.random() > 0.25:
                        continue
                    if y == 0 and rng.random() > 0.25 and block.id in lookup.LOGS and \
                            not is2DPositionContainedInNodes(pos=pos2DInWorldSpace, exludeRect=innerArea):
                        replacementSapling = getSapling(block)
                        if replacementSapling:
                            treeCuttingInstructions.append(PlacementInstruction(
                                block=replacementSapling,
                                position=pos3D
                            ))
                            continue
                treeCuttingInstructions.append(PlacementInstruction(
                    block=Block('minecraft:air'),
                    position=pos3D
                ))

    # NOTE: all pre-processing steps are applied, set /gamerule randomTickSpeed to 100, then after a few seconds set
    # it back to the default value of 3 and remove all items with globals.editor.runCommandGlobal('kill @e[type=item]')
    return treeCuttingInstructions


def is2DPositionContainedInNodes(
    pos: ivec2,
    exludeRect: Rect = None
) -> bool:
    if exludeRect and exludeRect.contains(pos):
        return True
    for node in globals.nodeList:
        nodeRect: Rect = node.structure.rectInWorldSpace
        if nodeRect.centeredSubRect(size=nodeRect.size + 4).contains(pos):
            return True
    return False


def buildAreaSqrt() -> float:
    return np.sqrt(globals.buildarea.area)


def facingBlockState(facing: int = 0) -> str:
    facing = facing % 4
    facingStates = ['east', 'south', 'west', 'north']
    return facingStates[facing]


def getEntities(
    area: Box = None,
    query: dict = None,
    includeData: bool = False,
    dimension: str = None,
) -> list[SimpleEntity]:
    foundEntities = interface.getEntities(
        selector=getEntitySelectorQuery(area, query),
        includeData=includeData,
        dimension=dimension,
    )
    entityList: list[SimpleEntity] = []
    for entity in foundEntities:
        entityList.append(SimpleEntity(
            uuid=entity.get('uuid'),
            snbt=entity.get('data'),
        ))
    return entityList


def getEntitiesPerGrid(
    area: Box = None,
    query: dict = None,
    includeData: bool = False,
    dimension: str = None,
    gridSize: ivec2 = ivec2(128, 128),
) -> list[EntitiesPerArea]:
    if area is None:
        area = globals.editor.worldSlice.box
    entityListPerArea: list[EntitiesPerArea] = []
    for subArea in vectorTools.loop2DwithRects(
        begin=area.toRect().begin,
        end=area.toRect().end,
        stride=gridSize,
    ):
        searchBox = Box(
            offset=ivec3(subArea.offset.x, area.offset.y, subArea.offset.y),
            size=ivec3(subArea.size.x, area.size.y, subArea.size.y),
        )
        entityList = getEntities(area=searchBox, query=query, includeData=includeData, dimension=dimension)
        if len(entityList) > 0:
            entityListPerArea.append(
                EntitiesPerArea(
                    area=searchBox,
                    entityList=entityList,
                )
            )
    return entityListPerArea


def getEntitySelectorQuery(area: Box = None, query: dict = None) -> str:
    if area is None:
        area = globals.editor.worldSlice.box
    if query is None:
        query = dict()
    query['x'] = area.offset.x
    query['y'] = area.offset.y
    query['z'] = area.offset.z
    query['dx'] = area.size.x
    query['dy'] = area.size.y
    query['dz'] = area.size.z
    return f"@e[{','.join([f'{key}={value}' for key, value in query.items()])}]"
