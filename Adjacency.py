from __future__ import annotations

import functools
from copy import deepcopy
from dataclasses import dataclass, replace
from typing import List, Tuple, Optional, Dict, Set

from glm import ivec3

AXES: List[str] = ['xForward', 'xBackward', 'yForward', 'yBackward', 'zForward', 'zBackward']

@dataclass(frozen=True)
class StructureRotation:
    structureName: str
    rotation: int

    def rotate(self, amount: int) -> StructureRotation:
        return replace(self, rotation=(self.rotation + amount) % 4)

    def __eq__(self, other: StructureRotation) -> bool:
        return self.rotation == other.rotation and self.structureName == other.structureName

    def __hash__(self) -> int:
        return hash((self.rotation, self.structureName))


class StructureAdjacency:
    name: str

    xForward: Set[StructureRotation]
    xBackward: Set[StructureRotation]
    yForward: Set[StructureRotation]
    yBackward: Set[StructureRotation]
    zForward: Set[StructureRotation]
    zBackward: Set[StructureRotation]

    def __init__(
        self,
        name: str,
        xForward: Optional[List[Tuple[str, int]]] = None,
        xBackward: Optional[List[Tuple[str, int]]] = None,
        yForward: Optional[List[Tuple[str, int]]] = None,
        yBackward: Optional[List[Tuple[str, int]]] = None,
        zForward: Optional[List[Tuple[str, int]]] = None,
        zBackward: Optional[List[Tuple[str, int]]] = None,
    ):
        self.name = name
        self.xForward = createRotationList(xForward)
        self.xBackward = createRotationList(xBackward)
        self.yForward = createRotationList(yForward)
        self.yBackward = createRotationList(yBackward)
        self.zForward = createRotationList(zForward)
        self.zBackward = createRotationList(zBackward)

    @functools.cache
    def adjacentStructures(self, axis: str, selfRotation: int) -> Set[StructureRotation]:
        selfRotation = selfRotation % 4

        if axis not in AXES:
            raise ValueError(f'Invalid axis "{axis}"')

        if selfRotation == 0:
            return getattr(self, axis)
        rotationAxes = [self.xForward, self.zForward, self.xBackward, self.zBackward]
        match axis:
            case 'xForward':
                return set(map(lambda r: r.rotate(selfRotation), rotationAxes[-selfRotation + 0]))
            case 'zForward':
                return set(map(lambda r: r.rotate(selfRotation), rotationAxes[-selfRotation + 1]))
            case 'xBackward':
                return set(map(lambda r: r.rotate(selfRotation), rotationAxes[-selfRotation + 2]))
            case 'zBackward':
                return set(map(lambda r: r.rotate(selfRotation), rotationAxes[-selfRotation + 3]))
            case 'yForward':
                return set(map(lambda r: r.rotate(selfRotation), self.yForward))
            case 'yBackward':
                return set(map(lambda r: r.rotate(selfRotation), self.yBackward))
        raise ValueError(f'Invalid axis "{axis}"')

    def __hash__(self):
        return hash(self.name)


def createRotationList(rotationTuples: List[Tuple[str, int]]) -> Set[StructureRotation]:
    rotationSet: Set[StructureRotation] = set()
    for rotationTuple in rotationTuples:
        if rotationTuple[1] == -1:
            rotationSet.update(getAllRotations(structureName=rotationTuple[0]))
        else:
            rotationSet.add(StructureRotation(structureName=rotationTuple[0], rotation=rotationTuple[1]))
    return rotationSet


@functools.cache
def getAllRotations(structureName: str) -> Set[StructureRotation]:
    return set(StructureRotation(structureName, r) for r in range(4))


@functools.cache
def getOppositeAxis(axis: str) -> str:
    match axis:
        case 'xForward':
            return 'xBackward'
        case 'xBackward':
            return 'xForward'
        case 'yForward':
            return 'yBackward'
        case 'yBackward':
            return 'yForward'
        case 'zForward':
            return 'zBackward'
        case 'zBackward':
            return 'zForward'
    raise ValueError(f'axis "{axis}" has no opposite. Axis is invalid!')


@functools.cache
def getPositionFromAxis(axis: str, pos: ivec3) -> Tuple[ivec3, str]:
    match axis:
        case 'xBackward':
            return ivec3(pos.x - 1, pos.y, pos.z), axis
        case 'xForward':
            return ivec3(pos.x + 1, pos.y, pos.z), axis
        case 'yBackward':
            return ivec3(pos.x, pos.y - 1, pos.z), axis
        case 'yForward':
            return ivec3(pos.x, pos.y + 1, pos.z), axis
        case 'zBackward':
            return ivec3(pos.x, pos.y, pos.z - 1), axis
        case 'zForward':
            return ivec3(pos.x, pos.y, pos.z + 1), axis
    raise ValueError(f'Axis {axis} is invalid!')


def checkSymmetry(adjacencies: Dict[str, StructureAdjacency]):
    for structureName in adjacencies.keys():
        adjacency = adjacencies[structureName]

        for axis in AXES:
            rules: Set[StructureRotation] = getattr(adjacency, axis)
            if len(rules) == 0:
                raise Exception(f'Ruleset {structureName} {axis} cannot be empty!')
            for rule in rules:
                if rule.structureName not in adjacencies:
                    raise KeyError(f'{rule.structureName} in rules for {structureName} is not a valid structure!')

                otherAdjecency = adjacencies[rule.structureName]
                oppositeAxis = getOppositeAxis(axis)

                otherRules: Set[StructureRotation] = otherAdjecency.adjacentStructures(
                    oppositeAxis,
                    rule.rotation
                )

                matchingRules = list(
                    filter(lambda r: r.structureName == structureName and r.rotation == 0, otherRules)
                )

                if len(matchingRules) == 0:
                    raise Exception(f'No symmetrical rule found for {structureName} {axis}.{rule} in '
                                    f'{rule.structureName}!')
                elif len(matchingRules) > 1:
                    raise Exception(f'Too many symmetrical rules found for {structureName} {axis}.{rule}: '
                                    f'{matchingRules}!')


def omitAdjacencies(
    adjacencies: Dict[str, StructureAdjacency],
    omitList: List[str],
) -> Dict[str, StructureAdjacency]:
    newAdjacencies = deepcopy(adjacencies)
    omitRotations: Set[StructureRotation] = set()
    for structureToOmit in omitList:
        newAdjacencies.pop(structureToOmit)
        omitRotations.update(getAllRotations(structureToOmit))
    for adjacency in newAdjacencies.values():
        for axis in AXES:
            rules: Set[StructureRotation] = getattr(adjacency, axis)
            rules = rules.difference(omitRotations)
            setattr(adjacency, axis, rules)
    checkSymmetry(newAdjacencies)
    return newAdjacencies


def omitAdjacenciesWithZeroWeight(
    adjacencies: Dict[str, StructureAdjacency],
    weights: Dict[str, float],
) -> Dict[str, StructureAdjacency]:
    omitList: List[str] = []
    for structureName, weight in weights.items():
        if weight == 0.0:
            omitList.append(structureName)
    return omitAdjacencies(adjacencies, omitList)
