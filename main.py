import os
import time
from typing import List, Dict

from glm import ivec3, ivec2
from termcolor import cprint

import bookTools
import worldTools
from LibraryFloor import LibraryFloor
import globals
from StructureBase import Structure
from gdpc.src.gdpc import Box
from structures.doha9.bottom_garden.bottom_garden import BottomGarden
from structures.doha9.subsurface_tower.subsurface_tower import SubsurfaceTower
from structures.doha9.surface_tower.surface_tower import SurfaceTower

os.system('color')

categoryName = 'CS'
books: List[str] = bookTools.gatherBooksOfCategory('cs.')
volumeRotation = 0
VOLUME_Y_SIZE = 10
floorNumber = 0
tileSize = ivec3(9, VOLUME_Y_SIZE, 9)

globals.initialize()

area = worldTools.findSuitableArea(ivec2(6, 6) * ivec2(9, 9))
if area is None:
    print(f'No suitable area found in build area {globals.buildVolume}')
    exit()
print(f'Suitable area found at {area}')

bookRangesByFloor: Dict[int, List[Dict[str, str]]] = dict()
centralAtriumBuildings: Dict[int, Structure] = dict()

volume = area.toBox().centeredSubBox(size=ivec3(22, 1, 22) * tileSize)
surfaceStandardDeviation = worldTools.getSurfaceStandardDeviation(
    area.centeredSubRect(size=ivec2(50, 50)),
    'MOTION_BLOCKING_NO_PLANTS',
)
surfaceY = int(surfaceStandardDeviation[1] + surfaceStandardDeviation[0])
volumeGrid = Box(
    size=volume.size // tileSize
)

surfaceTowerBox = volumeGrid.centeredSubBox(size=ivec3(5, 1, 5))
surfaceTower = SurfaceTower(
    tile=surfaceTowerBox.offset,
    offset=ivec3(volume.offset.x - 1, surfaceY, volume.offset.z - 1),
)
surfaceTower.addWayFinding('Computer Science', 0, dict())
surfaceTower.place()

floorNumber -= 1
surfaceY -= VOLUME_Y_SIZE
volumeRotation += 1

while surfaceY > 40:
    subSurfaceTower = SubsurfaceTower(
        tile=surfaceTowerBox.offset,
        offset=ivec3(volume.offset.x, surfaceY, volume.offset.z),
        withRotation=volumeRotation,
    )
    bookRangesByFloor[floorNumber] = subSurfaceTower.addBooks(books, categoryName, floorNumber, False)
    centralAtriumBuildings[floorNumber] = subSurfaceTower
    floorNumber -= 1
    surfaceY -= VOLUME_Y_SIZE
    volumeRotation += 1

yOffset = surfaceY
for yOffset in range(surfaceY, -60, -VOLUME_Y_SIZE):
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

    # Bandage to give Minecraft time to catch up.
    time.sleep(4)

    volumeRotation += 1
    floorNumber -= 1

for floorNumber, building in centralAtriumBuildings.items():
    cprint(f'Placing atrium for floor {floorNumber}', 'black', 'on_green')
    building.addWayFinding(categoryName, floorNumber, bookRangesByFloor)
    # Bandage to give Minecraft time to catch up.
    time.sleep(4)
    building.place()

cprint(f'Placing garden at floor {floorNumber} ({ivec3(volume.offset.x, surfaceY - VOLUME_Y_SIZE, volume.offset.z)})', 'black', 'on_green')
bottomGarden = BottomGarden(
    tile=surfaceTowerBox.offset,
    offset=ivec3(volume.offset.x, yOffset - VOLUME_Y_SIZE, volume.offset.z),
)
bottomGarden.place()

cprint(f'Completed construction of {categoryName} library', 'black', 'on_green')
