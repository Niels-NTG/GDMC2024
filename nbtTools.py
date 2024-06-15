from typing import Dict

import nbtlib
import numpy as np
from glm import ivec3

from gdpc.src.gdpc.block import Block
from gdpc.src.gdpc.lookup import INVENTORY_BLOCKS, CONTAINER_BLOCK_TO_INVENTORY_SIZE


def extractEntityBlockPos(compound: nbtlib.Compound) -> ivec3:
    return ivec3(
        np.floor(compound.get('Pos').get(0)),
        np.floor(compound.get('Pos').get(1)),
        np.floor(compound.get('Pos').get(2))
    )


def extractEntityId(compound: nbtlib.Compound) -> str:
    return compound.get('id')


def getBlockIdAt(structureFile: nbtlib.Compound, pos: ivec3) -> nbtlib.Compound:
    for nbtBlock in list(structureFile['blocks']):
        if (
            nbtBlock['pos'][0] == pos.x and
            nbtBlock['pos'][1] == pos.y and
            nbtBlock['pos'][2] == pos.z
        ):
            return getStructurePalette(structureFile, nbtBlock)


def setStructureBlock(
    structureFile: nbtlib.Compound,
    pos: ivec3,
    inputBlockId: str,
    inputBlockState: Dict[str, str] | None,
    inputBlockData: nbtlib.Compound | None,
) -> object:
    for nbtBlock in structureFile['blocks']:
        if (
            nbtBlock['pos'][0] == pos.x and
            nbtBlock['pos'][1] == pos.y and
            nbtBlock['pos'][2] == pos.z
        ):
            if inputBlockData is not None:
                nbtBlock['nbt'] = inputBlockData
            if inputBlockState is not None:
                nbtBlock['state'] = nbtlib.Int(setStructurePalette(
                    structureFile,
                    inputBlockId,
                    inputBlockState,
                ))
            return
    raise Exception(f'structureFile has no block at position {pos}')


def getStructurePalette(nbtFile: nbtlib.Compound, block) -> nbtlib.Compound:
    return nbtFile['palette'][block['state']]


def setStructurePalette(
    structureFile: nbtlib.Compound,
    inputBlockId: str,
    blockState: Dict[str, str],
) -> int:
    if len(blockState.keys()) == 0:
        structureFile['palette'].append(nbtlib.parse_nbt(
            f'{{Name: "{inputBlockId}"}}'
        ))
        return len(structureFile['palette']) - 1
    else:
        stateString = ','.join([f'{key}:{value}' for key, value in blockState.items()])
        if stateString:
            try:
                structureFile['palette'].append(nbtlib.parse_nbt(
                    f'{{Properties: {{{stateString}}}, Name: "{inputBlockId}"}}'
                ))
                return len(structureFile['palette']) - 1
            except Exception as e:
                print(f'Invalid block state {stateString} - {e}')


def setInventoryContents(inventoryBlock: Block, contents: list[dict]) -> Block:
    if inventoryBlock.id not in INVENTORY_BLOCKS:
        return inventoryBlock

    if len(contents) == 0:
        return inventoryBlock

    newChestContents = '{Items: ['
    inventoryDimensions = CONTAINER_BLOCK_TO_INVENTORY_SIZE[inventoryBlock.id]
    inventorySlots = np.reshape(
        range(inventoryDimensions.x * inventoryDimensions.y),
        (inventoryDimensions.y, inventoryDimensions.x)
    )

    for item in contents:
        slotIndex = inventorySlots[
            min(item['y'], inventoryDimensions.y - 1),
            min(item['x'], inventoryDimensions.x - 1)
        ]
        newChestContents += f'{{Slot: {slotIndex}b, Count: {item.get("amount")}b, id: "{item.get("material")}", tag: {item.get("tag")}}},'

    newChestContents = newChestContents[:-1]
    newChestContents += ']}'
    inventoryBlock.data = newChestContents
    return inventoryBlock
