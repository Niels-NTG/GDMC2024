from pathlib import Path

import Adjacency
from StructureFolder import StructureFolder
from gdpc.src.gdpc import Editor
from gdpc.src.gdpc import interface

global rngSeed

global structureFolders
global adjacencies
global structureWeights

global buildarea
global editor

global buildVolume


def initialize():
    global rngSeed
    rngSeed = 89347849

    global structureFolders
    structureFolders = dict()
    loadStructureFiles()

    global adjacencies
    adjacencies = dict()
    generateAdjacencies()

    global structureWeights
    structureWeights = dict()
    setupStructureWeights()

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
    buildarea = interface.getBuildArea()
    global editor
    editor = Editor()
    editor.loadWorldSlice(rect=buildarea.toRect(), cache=True)

    # TODO implement algorithm to find and define an suitable build volume
    # TODO system should be able to define multiple different build volumes for each
    #   settlement type
    global buildVolume
    buildVolume = buildarea


def loadStructureFiles():
    namespace = 'doha'
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
        adjacencies[name] = structureFolder.structureClass.adjecencies
    Adjacency.checkSymmetry(adjacencies)


def setupStructureWeights():
    for name, structureFolder in structureFolders.items():
        structureWeights[name] = structureFolder.structureClass.weight
