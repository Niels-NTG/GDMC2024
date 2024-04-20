from pathlib import Path
from copy import deepcopy

import numpy as np
from glm import ivec3

from StructureFolder import StructureFolder
from gdpc.gdpc import Editor, vector_tools, Block
from gdpc.gdpc import interface

global rng

global structureFolders

global buildarea
global editor

global buildVolume
global volumeGrid
global adjacencies
global nodeList


def initialize():
    global rng
    rng = np.random.default_rng()

    global structureFolders
    structureFolders = dict()
    loadStructureFiles()

    interface.runCommand(
        'setbuildarea 72 -60 105 102 -50 135'
    )
    interface.runCommand(
        'fill 72 -60 105 102 -50 135 minecraft:air'
    )
    interface.runCommand(
        'kill @e[type=minecraft:item]'
    )

    global buildarea
    buildarea = interface.getBuildArea()
    global editor
    editor = Editor()
    editor.loadWorldSlice(rect=buildarea.toRect(), cache=True)

    tileSize = ivec3(5, 5, 5)
    # TODO implement algorithm to find and define an suitable build volume
    # TODO system should be able to define multiple different build volumes for each
    #   settlement type
    global buildVolume
    buildVolume = buildarea

    global volumeGrid
    volumeGrid = buildVolume.size // tileSize
    # TODO set to flat grid for now
    volumeGrid.y = 1

    global adjacencies
    adjacencies = dict()
    for name, structureFolder in structureFolders.items():
        adjacencies[name] = deepcopy(structureFolder.structureClass.adjecencies)

    global nodeList
    nodeList = set()


def loadStructureFiles():
    namespace = 'wfctest'
    for structureFolder in Path('.').glob(f'structures/{namespace}/*/'):
        if structureFolder.is_dir():
            structureName = structureFolder.name
            structureFolders[structureName] = StructureFolder(
                structureFolder=structureFolder,
                name=structureName,
                namespace=namespace
            )
