import os

from glm import ivec3

from LibraryFloor import LibraryFloor
import globals
from gdpc.src.gdpc import Box

os.system('color')

globals.initialize()

volumeRotatiom = 3
for y in range(100, -70, -10):
    floorVolume = Box(
        offset=ivec3(
            globals.buildVolume.offset.x,
            y,
            globals.buildVolume.offset.z,
        ),
        size=ivec3(
            globals.buildVolume.size.x,
            10,
            globals.buildVolume.size.z,
        )
    )
    LibraryFloor(
        volume=floorVolume,
        volumeRotation=volumeRotatiom,
    )
    volumeRotatiom += 1
