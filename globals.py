from pathlib import Path

import Adjacency
from StructureFolder import StructureFolder
from gdpc.src.gdpc import interface

global rngSeed

global structureFolders
global defaultAdjacencies
global defaultStructureWeights

global heightMaps

global buildVolume


def initialize():
    global rngSeed
    rngSeed = None

    global structureFolders
    structureFolders = dict()
    loadStructureFiles()

    global defaultAdjacencies
    defaultAdjacencies = dict()
    generateAdjacencies()

    global defaultStructureWeights
    defaultStructureWeights = dict()
    setupStructureWeights()

    global buildVolume
    buildVolume = interface.getBuildArea()

    global heightMaps
    heightMaps = dict()
    print('Loading height maps…')
    updateHeightMap('MOTION_BLOCKING_NO_PLANTS')
    updateHeightMap('MOTION_BLOCKING')


def loadStructureFiles():
    namespace = 'doha9'
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
        if hasattr(structureFolder.structureClass, 'adjecencies'):
            defaultAdjacencies[name] = structureFolder.structureClass.adjecencies
    Adjacency.checkSymmetry(defaultAdjacencies)


def setupStructureWeights():
    for name, structureFolder in structureFolders.items():
        defaultStructureWeights[name] = structureFolder.structureClass.weight


def updateHeightMap(heightMapType: str = 'WORLD_SURFACE'):
    heightMaps[heightMapType] = interface.getHeightMap(heightMapType)
