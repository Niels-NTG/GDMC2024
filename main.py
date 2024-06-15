import os
from typing import List, Dict

from glm import ivec3
from termcolor import cprint

import bookTools
from LibraryFloor import LibraryFloor
import globals
from StructureBase import Structure
from gdpc.src.gdpc import Box
from structures.doha9.subsurface_tower.subsurface_tower import SubsurfaceTower
from structures.doha9.surface_tower.surface_tower import SurfaceTower

os.system('color')

globals.initialize()

categoryName = 'CS'
books: List[str] = bookTools.gatherBooksOfCategory('cs.')
volumeRotation = 2
VOLUME_Y_SIZE = 10
floorNumber = 0

bookRangesByFloor: Dict[int, List[Dict[str, str]]] = dict()
centralAtriumBuildings: Dict[int, Structure] = dict()

# TODO should be become an algorithm that samples candiate areas inside the build area for suitable flatness.
# TODO should be equal to highest position heightmap within area.
volume = Box(
    offset=globals.buildVolume.offset,
    size=globals.buildVolume.size,
)
surfaceY = 120

tileSize = ivec3(9, 10, 9)
volumeGrid = Box(
    size=volume.size // tileSize
)

volumeGrid.size = volumeGrid.size + ivec3(1, 0, 1)
surfaceTowerBox = volumeGrid.centeredSubBox(size=ivec3(5, 1, 5))
surfaceTower = SurfaceTower(
    tile=surfaceTowerBox.offset,
    offset=ivec3(volume.offset.x - 1, surfaceY, volume.offset.z - 1),
)
surfaceTower.place()

floorNumber -= 1

subSurfaceTower = SubsurfaceTower(
    tile=surfaceTowerBox.offset,
    offset=ivec3(volume.offset.x, surfaceY - VOLUME_Y_SIZE, volume.offset.z),
    withRotation=1,
)
bookRangesByFloor[floorNumber] = subSurfaceTower.addBooks(books, categoryName, floorNumber, False)
centralAtriumBuildings[floorNumber] = subSurfaceTower

floorNumber -= 1

for yOffset in range(surfaceY, -70, -VOLUME_Y_SIZE):
    if len(books) == 0:
        break

    floorVolume = Box(
        offset=ivec3(
            volume.offset.x,
            yOffset,
            volume.offset.z,
        ),
        size=volume.size,
    )
    floorGridVolume = Box(
        size=volumeGrid.size
    )
    libraryFloor = LibraryFloor(
        volume=floorVolume,
        volumeGrid=floorGridVolume,
        volumeRotation=volumeRotation,
    )
    cprint(f'Filling floor {floorNumber} with books. {len(books)} books remaining', 'black', 'on_green')
    bookRangesByFloor[floorNumber] = libraryFloor.addBooks(books, categoryName, floorNumber)
    centralAtriumBuildings[floorNumber] = libraryFloor.centralCore
    libraryFloor.placeStructure()

    volumeRotation += 1
    floorNumber -= 1

for floorNumber, building in centralAtriumBuildings.items():
    building.addWayFinding(categoryName, floorNumber, bookRangesByFloor)
    building.place()
