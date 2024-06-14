import os
from typing import List, Dict

from glm import ivec3
from termcolor import cprint

import bookTools
from LibraryFloor import LibraryFloor
import globals
from StructureBase import Structure
from gdpc.src.gdpc import Box

os.system('color')

globals.initialize()

categoryName = 'CS'
books: List[str] = bookTools.gatherBooksOfCategory('cs.')
volumeRotation = 0
volumeY = 100
VOLUME_Y_SIZE = 10
floorNumber = 0

bookRangesByFloor: Dict[int, List[Dict[str, str]]] = dict()
centralAtriumBuildings: Dict[int, Structure] = dict()

while volumeY > -70 and len(books) > 0:

    floorVolume = Box(
        offset=ivec3(
            globals.buildVolume.offset.x,
            volumeY,
            globals.buildVolume.offset.z,
        ),
        size=ivec3(
            globals.buildVolume.size.x,
            VOLUME_Y_SIZE,
            globals.buildVolume.size.z,
        )
    )
    libraryFloor = LibraryFloor(
        volume=floorVolume,
        volumeRotation=volumeRotation,
    )

    cprint(f'Filling floor {floorNumber} with at most {libraryFloor.bookCapacity} books', 'black', 'on_green')
    floorRange = libraryFloor.addBooks(books, categoryName, floorNumber)
    bookRangesByFloor[floorNumber] = floorRange
    centralAtriumBuildings[floorNumber] = libraryFloor.centralCore
    libraryFloor.placeStructure()

    volumeY -= VOLUME_Y_SIZE
    volumeRotation += 1
    floorNumber -= 1

for floorNumber, building in centralAtriumBuildings.items():
    building.addWayFinding(categoryName, floorNumber, bookRangesByFloor)
    building.place()
