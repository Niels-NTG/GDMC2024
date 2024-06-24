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
from gdpc.src.gdpc import Box, Rect, interface
from structures.doha9.bottom_garden.bottom_garden import BottomGarden
from structures.doha9.subsurface_tower.subsurface_tower import SubsurfaceTower
from structures.doha9.surface_tower.surface_tower import SurfaceTower

os.system('color')

globals.initialize()

libraryRects: List[Rect] = []
libraryCategories: List[Dict[str, str]] = [
    {
        'code': 'cs.',
        'acronym': 'CS',
        'name': 'Computer Science',
    },
    {
        'code': 'math.',
        'acronym': 'Math',
        'name': 'Mathematics',
    },
    {
        'code': 'astro-ph',
        'acronym': 'AP',
        'name': 'Astrophysics',
    },
    {
        'code': 'stat.',
        'acronym': 'STAT',
        'name': 'Statistics',
    },
    {
        'code': 'physics.',
        'acronym': 'Physics',
        'name': 'Physics',
    },
    {
        'code': 'econ.',
        'acronym': 'ECON',
        'name': 'Economics',
    },
]

for category in libraryCategories:
    print(f'Loading books of category {category["name"]}…')
    categoryName = category['acronym']
    books: List[str] = bookTools.gatherBooksOfCategory(category['code'])
    volumeRotation = 0
    VOLUME_Y_SIZE = 10
    floorNumber = 0
    tileSize = ivec3(9, VOLUME_Y_SIZE, 9)

    print(f'Finding suitable area to build {category["name"]} library…')
    area = worldTools.findSuitableArea(ivec2(7, 7) * ivec2(9, 9), libraryRects)
    if area is None:
        print(f'No suitable area found in build area {globals.buildVolume}')
        exit()
    print(f'Suitable area found at {area}')
    interface.runCommand(
        f'tp @a {area.offset.x} 240 {area.offset.y}'
    )
    interface.runCommand(
        'kill @e[type=minecraft:item]'
    )

    bookRangesByFloor: Dict[int, List[Dict[str, str]]] = dict()
    centralAtriumBuildings: Dict[int, Structure] = dict()

    volume = area.toBox().centeredSubBox(size=ivec3(26, 1, 26) * tileSize)
    surfaceStandardDeviation = worldTools.getSurfaceStandardDeviation(
        area.centeredSubRect(size=ivec2(50, 50)),
        'MOTION_BLOCKING_NO_PLANTS',
    )
    surfaceY = surfaceStandardDeviation[2]
    volumeGrid = Box(
        size=volume.size // tileSize
    )

    libraryRects.append(volume.toRect().dilated(10))

    surfaceTowerBox = volumeGrid.centeredSubBox(size=ivec3(5, 1, 5))
    surfaceTower = SurfaceTower(
        tile=surfaceTowerBox.offset,
        offset=ivec3(volume.offset.x - 1, surfaceY, volume.offset.z - 1),
    )
    surfaceTower.addWayFinding(category['name'], 0, dict())
    surfaceTower.place()
    cprint(f'Surface entry building placed at {surfaceTower.position}', 'black', 'on_green')

    floorNumber -= 1
    surfaceY -= VOLUME_Y_SIZE
    volumeRotation += 1

    while surfaceY > 40:
        if len(books) == 0:
            break
        subSurfaceTower = SubsurfaceTower(
            tile=surfaceTowerBox.offset,
            offset=ivec3(volume.offset.x, surfaceY, volume.offset.z),
            withRotation=volumeRotation,
        )
        cprint(
            f'Filling floor {floorNumber} (y: {surfaceY}) with books. {len(books)} books remaining…',
            'black', 'on_green'
        )
        bookRangesByFloor[floorNumber] = subSurfaceTower.addBooks(books, categoryName, floorNumber, False)
        centralAtriumBuildings[floorNumber] = subSurfaceTower
        floorNumber -= 1
        surfaceY -= VOLUME_Y_SIZE
        volumeRotation += 1

    yOffset = surfaceY
    for yOffset in range(surfaceY, -50, -VOLUME_Y_SIZE):
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
        cprint(
            f'Filling floor {floorNumber} (y: {surfaceY}) with books. {len(books)} books remaining…',
            'black', 'on_green'
        )
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
        building.place()
        # Bandage to give Minecraft time to catch up.
        time.sleep(4)

    cprint(
        f'Placing garden at floor {floorNumber}',
        'black', 'on_green'
    )
    bottomGarden = BottomGarden(
        tile=surfaceTowerBox.offset,
        offset=ivec3(volume.offset.x, yOffset, volume.offset.z),
    )
    bottomGarden.place()

    cprint(f'Completed construction of {category["name"]} library', 'black', 'on_green')
    time.sleep(10)

cprint('Completed construction of all libraries', 'black', 'on_green')
