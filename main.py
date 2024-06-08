import os

from glm import ivec3
from termcolor import cprint

import bookTools
from LibraryFloor import LibraryFloor
import globals
from gdpc.src.gdpc import Box

os.system('color')

globals.initialize()

computerScienceBooks = bookTools.gatherBooksOfCategory('cs.')
volumeRotatiom = 0
volumeY = 100
VOLUME_Y_SIZE = 10
floorNumber = 0
while volumeY > -70 and len(computerScienceBooks) > 0:
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
        volumeRotation=volumeRotatiom,
    )

    bookCapacity = libraryFloor.bookCapacity
    cprint(f'Filling floor {floorNumber} with {bookCapacity} books', 'black', 'on_green')
    booksForFloor = computerScienceBooks[-bookCapacity:]
    libraryFloor.placeBooks(booksForFloor)

    del computerScienceBooks[-bookCapacity:]

    volumeY -= VOLUME_Y_SIZE
    volumeRotatiom += 1
    floorNumber -= 1
