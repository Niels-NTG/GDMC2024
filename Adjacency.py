import functools
from dataclasses import dataclass, replace
from typing import List, Tuple, Optional, Union, Dict


AXES: list[str] = ['xForward', 'xBackward', 'yForward', 'yBackward', 'zForward', 'zBackward']


@dataclass(frozen=True)
class StructureRotation:
    structureName: str
    rotation: int

    def rotate(self, amount: int):
        return replace(self, rotation=(self.rotation + amount) % 4)


class StructureAdjacency:
    name: str

    xForward: Union[List[StructureRotation] | None]
    xBackward: Union[List[StructureRotation] | None]
    yForward: Union[List[StructureRotation] | None]
    yBackward: Union[List[StructureRotation] | None]
    zForward: Union[List[StructureRotation] | None]
    zBackward: Union[List[StructureRotation] | None]

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
    def adjacentStructures(self, axis: str, selfRotation: int) -> List[StructureRotation]:
        selfRotation = selfRotation % 4

        if axis not in AXES:
            raise ValueError(f'Invalid axis "{axis}"')

        match axis:
            case 'yForward':
                return list(map(lambda r: r.rotate(selfRotation), self.yForward))
            case 'yBackward':
                return list(map(lambda r: r.rotate(selfRotation), self.yBackward))

        if selfRotation == 0:
            return getattr(self, axis)
        rotationAxes = [self.xForward, self.zForward, self.xBackward, self.zBackward]
        match axis:
            case 'xForward':
                return list(map(lambda r: r.rotate(selfRotation), rotationAxes[-selfRotation + 0]))
            case 'zForward':
                return list(map(lambda r: r.rotate(selfRotation), rotationAxes[-selfRotation + 1]))
            case 'xBackward':
                return list(map(lambda r: r.rotate(selfRotation), rotationAxes[-selfRotation + 2]))
            case 'zBackward':
                return list(map(lambda r: r.rotate(selfRotation), rotationAxes[-selfRotation + 3]))
        raise ValueError(f'Invalid axis "{axis}"')


def createRotationList(rotationTuples: Union[List[Tuple[str, int]] | None]) -> List[StructureRotation]:
    rotationList: List[StructureRotation] = []
    if rotationTuples is None or len(rotationTuples) == 0:
        return rotationList
    for rotationTuple in rotationTuples:
        if rotationTuple[1] == -1:
            rotationList.extend(getAllRotations(structureName=rotationTuple[0]))
        else:
            rotationList.append(StructureRotation(structureName=rotationTuple[0], rotation=rotationTuple[1]))
    return rotationList


def getAllRotations(structureName: str) -> List[StructureRotation]:
    return [StructureRotation(structureName, r) for r in range(4)]


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


def checkSymmetry(adjacencies: Dict[str, StructureAdjacency]):
    SELF_ROTATION = 0
    for structureName in adjacencies.keys():
        adjacency = adjacencies[structureName]

        for axis in AXES:
            rules: List[StructureRotation] = getattr(adjacency, axis)
            for rule in rules:
                if rule.structureName not in adjacencies:
                    raise KeyError(f'{rule.structureName} in rules for {structureName} is not a valid structure!')

                otherAdjecency = adjacencies[rule.structureName]
                oppositeAxis = getOppositeAxis(axis)

                otherRules: List[StructureRotation] = otherAdjecency.adjacentStructures(oppositeAxis, rule.rotation)

                matchingRules = list(
                    filter(lambda r: r.structureName == structureName and r.rotation == SELF_ROTATION, otherRules)
                )

                if len(matchingRules) == 0:
                    raise Exception(f'No symmetrical rule found for {structureName}.{axis}.{rule} in '
                                    f'{rule.structureName} with rules {otherRules}!')
                elif len(matchingRules) > 1:
                    raise Exception(f'Too many symmetrical rules found for {structureName}.{axis}.{rule}: '
                                    f'{matchingRules}!')
