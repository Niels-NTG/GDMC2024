from copy import deepcopy
from pathlib import Path

import numpy as np
from glm import ivec3

import Adjacency
from StructureFolder import StructureFolder
from gdpc.src.gdpc import Editor, Box
from gdpc.src.gdpc import interface

global rng

global structureFolders

global buildarea
global editor

global buildVolume
global adjacencies
global nodeList


def initialize():
    global rng
    rng = np.random.default_rng(seed=8132)

    global structureFolders
    structureFolders = dict()
    loadStructureFiles()

    global adjacencies
    adjacencies = dict()
    generateAdjacencies()

    interface.runCommand(
        'setbuildarea 21 -60 164 101 -40 244'
    )
    interface.runCommand(
        'fill 21 -60 164 101 -40 244 minecraft:air'
    )
    interface.runCommand(
        'kill @e[type=minecraft:item]'
    )

    global buildarea
    buildarea = Box(ivec3(20, -60, 164), ivec3(80, 20, 80))
    # buildarea = interface.getBuildArea()
    global editor
    editor = Editor()
    editor.loadWorldSlice(rect=buildarea.toRect(), cache=True)

    # TODO implement algorithm to find and define an suitable build volume
    # TODO system should be able to define multiple different build volumes for each
    #   settlement type
    global buildVolume
    buildVolume = buildarea


def loadStructureFiles():
    namespace = 'library'
    for structureFolder in Path('.').glob(f'structures/{namespace}/*/'):
        if structureFolder.is_dir():
            structureName = structureFolder.name
            structureFolders[structureName] = StructureFolder(
                structureFolder=structureFolder,
                name=structureName,
                namespace=namespace
            )


def generateAdjacencies():
    for name, structureFolder in structureFolders.items():
        structureAdjacency = structureFolder.structureClass.adjecencies
        adjacencies[name] = deepcopy(structureAdjacency)
    Adjacency.checkSymmetry(adjacencies)
