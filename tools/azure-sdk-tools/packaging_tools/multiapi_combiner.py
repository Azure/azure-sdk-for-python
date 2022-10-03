# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import importlib
import pkgutil
import argparse
from types import ModuleType
from typing import Optional, List, Set

class VersionedObject:
    """An object that can be added / removed in an api version"""
    def __init__(
        self,
        name: str,
        *,
        added_on: Optional[str] = None,
        removed_on: Optional[str] = None,
    ) -> None:
        self.name = name
        self.added_on = added_on
        if removed_on:
            raise ValueError(
                f"Can not combine a multiapi package because {removed_on} was removed in an api version"
            )

    def get_added_on(self) -> Optional[str]:
        return

    def get_removed_on(self) -> Optional[str]:
        return

class Parameter(VersionedObject):

    pass

class Operation(VersionedObject):

    def __init__(
        self,
        name: str,
        parameters: List[Parameter],
        *,
        added_on: Optional[str] = None,
        removed_on: Optional[str] = None,
    )-> None:
        super().__init__(name, added_on=added_on, removed_on=removed_on)
        self.parameters = parameters

class OperationGroup(VersionedObject):
    def __init__(
        self,
        name: str,
        operations: List[Operation],
        *,
        added_on: Optional[str] = None,
        removed_on: Optional[str] = None,
    ):
        super().__init__(name=name, added_on=added_on, removed_on=removed_on)
        self.operations = operations

class Serializer:
    def serialize(self):
        pass

class CodeModel:
    def __init__(self, module: ModuleType):
        self.serializer = Serializer()
        self.api_version_to_module = {
            mod.name: importlib.import_module(f"{module.__name__}.{mod.name}")
            for mod in pkgutil.iter_modules(module.__path__)
            if getattr(mod, "name", "").startswith("v")
        }
        self.default_module = self.api_version_to_module.get(
            sorted(self.api_version_to_module.keys())[-1]
        )
        self.operation_groups = self._combine_operation_groups()

    def _combine_operation_groups(self) -> List[OperationGroup]:
        previous_version_operation_groups: Set[str] = set()
        operation_groups: List[OperationGroup] = []
        for api_version, curr_module in self.api_version_to_module.items():
            if not previous_version_operation_groups:
                previous_version_operation_groups = set(
                    og for og in dir(curr_module.operations)
                )
                operation_groups.extend([
                    OperationGroup(name=og_name)
                    for og_name in dir(curr_module.operations)
                ])
                continue
            for operation_group in code_model.operation_groups:
                if not previous_version_operation_groups:
                    previous_version_operation_groups
        return operation_groups

    def serialize(self):
        return self.serializer.serialize()

def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Combine multiapi SDKs into a single SDK"
    )
    parser.add_argument(
        "--pkg-name", required=True, help=("Path to the package source root")
    )
    return parser.parse_args()

if __name__ == "__main__":
    code_model = CodeModel(importlib.import_module(get_args().pkg_name))
    code_model.serialize()
