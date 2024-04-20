from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from StructureBase import Structure
from pathlib import Path
from importlib import import_module

from StructureFile import StructureFile


class StructureFolder:

    structureClass: Structure
    name: str
    structureFile: StructureFile
    decorationStructureFiles: dict[str, StructureFile]
    transitionStructureFiles: dict[str, StructureFile]

    def __init__(
        self,
        structureFolder: Path,
        name: str,
        namespace: str
    ):

        self.name = name
        self.namespace = namespace

        self.structureFile = StructureFile(structureFolder / name)

        self.transitionStructureFiles = dict()
        for connectorStructureFile in structureFolder.glob('transitions/*'):
            if connectorStructureFile.is_file() and connectorStructureFile.name.endswith('.nbt'):
                self.transitionStructureFiles[connectorStructureFile.name] = StructureFile(connectorStructureFile)

        self.decorationStructureFiles = dict()
        for decorationStructionFile in structureFolder.glob('decorations/*'):
            if decorationStructionFile.is_file() and decorationStructionFile.name.endswith('.nbt'):
                self.decorationStructureFiles[decorationStructionFile.name] = StructureFile(decorationStructionFile)

        structureModulePath = f'structures.{self.namespace}.{self.name}.{self.name}'
        structureModule = import_module(structureModulePath)
        if structureModule is None:
            raise FileNotFoundError(f'No module found at {structureModulePath}')
        self.structureClass = getattr(
            structureModule,
            name.replace('_', ' ').title().replace(' ', '')
        )

    def __repr__(self):
        return f'{__class__.__name__} {self.namespace}.{self.name}'
