import functools
from typing import Iterator

import numpy as np
from glm import ivec3, ivec2

from gdpc.src.gdpc.vector_tools import Rect, Box


@functools.cache
def rotatePointAroundOrigin3D(
    origin: ivec3 = ivec3(0, 0, 0),
    point: ivec3 = ivec3(0, 0, 0),
    rotation: int = 0
) -> ivec3:
    if rotation == 0:
        return point
    angle = np.deg2rad(rotation * 90)
    return ivec3(
        int(np.round(np.cos(angle) * (point.x - origin.x) - np.sin(angle) * (point.z - origin.z) + origin.x)),
        point.y,
        int(np.round(np.sin(angle) * (point.x - origin.x) + np.cos(angle) * (point.z - origin.z) + origin.z))
    )


@functools.cache
def isRectinRect(rectA: Rect, rectB: Rect) -> bool:
    return (
        rectB.begin.x >= rectA.begin.x and
        rectB.begin.y >= rectA.begin.y and
        rectB.end.x <= rectA.last.x and
        rectB.end.y <= rectA.last.y
    )


@functools.cache
def loop2DwithRects(
    begin: ivec2 = ivec2(0, 0),
    end: ivec2 = ivec2(0, 0),
    size: ivec2 = ivec2(1, 1),
    stride: ivec2 = ivec2(1, 1)
) -> Iterator[Rect]:
    for x in range(begin.x, end.x, stride.x):
        for y in range(begin.y, end.y, stride.y):
            newRect = Rect(
                offset=ivec2(x, y),
                size=size
            )
            yield newRect


def boxPositions(
    box: Box
) -> Iterator[ivec3]:
    for x in range(box.begin.x, box.end.x):
        for y in range(box.begin.y, box.end.y):
            for z in range(box.begin.z, box.end.z):
                yield ivec3(x, y, z)


def getBoxWalls(
    box: Box
) -> Iterator[ivec3]:
    for x in range(box.begin.x, box.end.x):
        for y in range(box.begin.y, box.end.y):
            for z in range(box.begin.z, box.end.z):
                if not (
                    x > box.begin.x and x < box.last.x and
                    z > box.begin.z and z < box.last.z
                ):
                    yield ivec3(x, y, z)


@functools.cache
def intersectionBox(
    boxA: Box | None,
    boxB: Box | None,
) -> Box | None:
    if boxA is None or boxB is None:
        return None
    if boxA.collides(boxB):
        x = max(boxA.offset.x, boxB.offset.x)
        y = max(boxA.offset.y, boxB.offset.y)
        z = max(boxA.offset.z, boxB.offset.z)
        box = Box(
            offset=ivec3(x, y, z),
            size=ivec3(
                min(boxA.end.x, boxB.end.x) - x,
                min(boxA.end.y, boxB.end.y) - y,
                min(boxA.end.z, boxB.end.z) - z
            )
        )
        if box.size > ivec3(0, 0, 0):
            return box
