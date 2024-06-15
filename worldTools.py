from __future__ import annotations

import re
from typing import TYPE_CHECKING, Dict

if TYPE_CHECKING:
    from StructureBase import Structure

import numpy as np
from glm import ivec2, ivec3

import globals
import vectorTools
from gdpc.src.gdpc import lookup
from gdpc.src.gdpc.block import Block
from gdpc.src.gdpc.vector_tools import Box, Rect, loop2D
from gdpc.src.gdpc.interface import getBlocks

DEFAULT_HEIGHTMAP_TYPE: str = 'MOTION_BLOCKING_NO_PLANTS'


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
    heightmap = globals.heightMaps[heightmapType]

    positionRelativeToWorldSlice = (pos - globals.buildVolume.toRect().offset)
    return heightmap[positionRelativeToWorldSlice.x][positionRelativeToWorldSlice.y]


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
    diffHeightmap = globals.heightMaps['MOTION_BLOCKING_NO_LEAVES'] - \
                    globals.heightMaps['MOTION_BLOCKING_NO_PLANTS']
    outerArea = area.centeredSubRect(size=area.size + 10)
    outerAreaRelativeToBuildArea = Rect(
        offset=outerArea.offset - globals.buildVolume.toRect().offset,
        size=outerArea.size
    )
    diffHeightmap = diffHeightmap[
        outerAreaRelativeToBuildArea.begin.x:outerAreaRelativeToBuildArea.end.x,
        outerAreaRelativeToBuildArea.begin.y:outerAreaRelativeToBuildArea.end.y,
    ]
    return int(np.sum(diffHeightmap))


def getTreeCuttingInstructions(
    area: Rect
) -> Dict[ivec3, Block]:
    treeCuttingInstructions: Dict[ivec3, Block] = dict()

    innerArea = area.centeredSubRect(size=area.size + 4)
    outerArea = area.centeredSubRect(size=area.size + 10)

    diffHeightmap = np.subtract(
        globals.heightMaps['MOTION_BLOCKING'],
        globals.heightMaps['MOTION_BLOCKING_NO_PLANTS']
    )

    treePositions = np.argwhere(diffHeightmap > 0)

    rng = np.random.default_rng()

    for xzPos in treePositions:
        pos2DInWorldSpace = ivec2(xzPos[0], xzPos[1]) + globals.buildVolume.toRect().offset
        if not outerArea.contains(pos2DInWorldSpace):
            continue
        for y in range(diffHeightmap[xzPos[0], xzPos[1]]):
            pos3D = ivec3(
                pos2DInWorldSpace.x,
                y + globals.heightMaps['MOTION_BLOCKING_NO_PLANTS'][xzPos[0]][xzPos[1]],
                pos2DInWorldSpace.y
            )
            block: Block = getBlocks(position=pos3D, includeData=False, includeState=False)[0][1]
            if block.id in lookup.PLANT_BLOCKS:
                if not innerArea.contains(pos2DInWorldSpace):
                    if block.id in lookup.LEAVES and rng.random() > 0.25:
                        continue
                    if y == 0 and rng.random() > 0.25 and block.id in lookup.LOGS:
                        replacementSapling = getSapling(block)
                        if replacementSapling:
                            treeCuttingInstructions[pos3D] = replacementSapling
                            continue
                treeCuttingInstructions[pos3D] = Block('minecraft:air')

    # NOTE: all pre-processing steps are applied, set /gamerule randomTickSpeed to 100, then after a few seconds set
    # it back to the default value of 3 and remove all items with globals.editor.runCommandGlobal('kill @e[type=item]')
    return treeCuttingInstructions


def findSuitableArea(
    volumeRectSize: ivec2 = ivec2(55, 55),
) -> Rect | None:
    area: Box = globals.buildVolume
    flattestArea = None
    lowestGradient = 999999
    for subArea in vectorTools.loop2DwithRects(
        begin=area.toRect().begin,
        end=area.toRect().end,
        stride=volumeRectSize,
    ):
        gradientOfArea = getSurfaceStandardDeviation(subArea, 'OCEAN_FLOOR_NO_PLANTS')
        if gradientOfArea[1] < 64 or gradientOfArea[0] > 10:
            continue
        if abs(gradientOfArea[0]) < lowestGradient:
            lowestGradient = abs(gradientOfArea[0])
            flattestArea = subArea
    return flattestArea
