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


def getBlockInStructure(structureFile: nbtlib.Compound, pos: ivec3) -> Block:
    for nbtBlock in list(structureFile['blocks']):
        if (
            nbtBlock['pos'][0] == pos.x and
            nbtBlock['pos'][1] == pos.y and
            nbtBlock['pos'][2] == pos.z
        ):
            return Block.fromBlockStateTag(
                getBlockMaterial(structureFile, nbtBlock),
                nbtBlock['nbt']
            )


def setBlockInStructure(structureFile: nbtlib.Compound, pos: ivec3, inputBlock: Block):
    try:
        newNBTTag = nbtlib.parse_nbt(inputBlock.data)
    except Exception as e:
        print(f'Could not parse {inputBlock.data}: {e}')
        return
    structureFile['palette'].append(nbtlib.parse_nbt(
        f'{{Properties: {inputBlock.stateString()}, Name: "{inputBlock.id}"}}'
    ))
    paletteId = len(structureFile['palette']) - 1
    for nbtBlock in structureFile['blocks']:
        if (
            nbtBlock['pos'][0] == pos.x and
            nbtBlock['pos'][1] == pos.y and
            nbtBlock['pos'][2] == pos.z
        ):
            nbtBlock['nbt'] = newNBTTag
            nbtBlock['state'] = nbtlib.Int(paletteId)
            return
    raise Exception(f'structureFile has no block at position {pos}')


def getBlockMaterial(nbtFile: nbtlib.Compound, block) -> nbtlib.Compound:
    return nbtFile['palette'][block['state']]


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
