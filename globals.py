from pathlib import Path

import Adjacency
from StructureFolder import StructureFolder
from gdpc.src.gdpc import Editor
from gdpc.src.gdpc import interface

global rngSeed

global structureFolders
global defaultAdjacencies
global defaultStructureWeights

global buildarea
global editor

global buildVolume


def initialize():
    global rngSeed
    rngSeed = 89347849

    global structureFolders
    structureFolders = dict()
    loadStructureFiles()

    global defaultAdjacencies
    defaultAdjacencies = dict()
    generateAdjacencies()

    global defaultStructureWeights
    defaultStructureWeights = dict()
    setupStructureWeights()

    # interface.runCommand(
    #     'setbuildarea 20 -60 163 120 -50 263'
    # )
    interface.runCommand(
        'setbuildarea 20 -60 160 120 0 260'
    )
    # interface.runCommand(
    #     'setbuildarea 20 -60 160 160 0 300'
    # )
    interface.runCommand(
        'kill @e[type=minecraft:item]'
    )

    global buildarea
    buildarea = interface.getBuildArea()
    global editor
    editor = Editor()
    # editor.loadWorldSlice(rect=buildarea.toRect(), cache=True)

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
        defaultAdjacencies[name] = structureFolder.structureClass.adjecencies
    Adjacency.checkSymmetry(defaultAdjacencies)


def setupStructureWeights():
    for name, structureFolder in structureFolders.items():
        defaultStructureWeights[name] = structureFolder.structureClass.weight
