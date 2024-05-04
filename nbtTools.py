import nbtlib
from nbt import nbt
import numpy as np
from glm import ivec3

from gdpc.src.gdpc.block import Block
from gdpc.src.gdpc.lookup import INVENTORY_BLOCKS, CONTAINER_BLOCK_TO_INVENTORY_SIZE


def SnbttoNbt(snbt: str) -> nbtlib.Compound:
    return nbtlib.parse_nbt(snbt)


def extractEntityBlockPos(compound: nbtlib.Compound) -> ivec3:
    return ivec3(
        np.floor(compound.get('Pos').get(0)),
        np.floor(compound.get('Pos').get(1)),
        np.floor(compound.get('Pos').get(2))
    )


def extractEntityId(compound: nbtlib.Compound) -> str:
    return compound.get('id')


def getBlockAt(nbtFile: nbt.NBTFile, pos: ivec3) -> Block:
    for nbtBlock in list(nbtFile['blocks']):
        if nbtBlock['pos'][0].value == pos.x and \
                nbtBlock['pos'][1].value == pos.y and \
                nbtBlock['pos'][2].value == pos.z:
            return Block.fromBlockStateTag(getBlockMaterial(nbtFile, nbtBlock))


def getBlockMaterial(nbtFile: nbt.NBTFile, block) -> nbt.TAG_Compound:
    return nbtFile['palette'][block['state'].value]


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
