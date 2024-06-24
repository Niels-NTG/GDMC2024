from typing import Dict

import nbtlib
from glm import ivec3


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
