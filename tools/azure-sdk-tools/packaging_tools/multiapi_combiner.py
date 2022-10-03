# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import argparse
from typing import Optional, List

class VersionedObject:
    """An object that can be added / removed in an api version"""
    def __init__(
        self,
        name: str,
        contents,
    ) -> None:
        self.name = name
        self.contents = contents
        self.added_on = self.get_added_on()
        self.removed_on = self.get_removed_on()

    def get_added_on(self) -> Optional[str]:
        return

    def get_removed_on(self) -> Optional[str]:
        return

class Parameter(VersionedObject):

    @classmethod
    def from_inspect(cls, contents):
        return cls(
            name="",
            contents=contents,
        )

class Operation(VersionedObject):

    def __init__(self, name: str, contents, parameters: List[Parameter]) -> None:
        super().__init__(name, contents)
        self.parameters = parameters

    @classmethod
    def from_inspect(cls, contents):
        return cls(
            name="",
            contents=contents,
            parameters=[],
        )


class OperationGroup(VersionedObject):
    def __init__(
        self,
        name: str,
        contents,
        operations: List[Operation],
    ):
        super().__init__(name=name, contents=contents)
        self.name = name
        self.contents = contents
        self.operations = operations

    @classmethod
    def from_inspect(cls, contents):
        return cls(
            name="",
            contents=contents,
            operations=[],
        )


class Serializer:
    def serialize(self):
        pass

class CodeModel:
    def __init__(self, operation_groups: List[OperationGroup]):
        self.operation_groups = operation_groups
        self.serializer = Serializer()

    @classmethod
    def from_inspect(cls, pkg_path: argparse.Namespace):
        return cls(operation_groups=[])

    def serialize(self):
        return self.serializer.serialize()

def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Combine multiapi SDKs into a single SDK"
    )
    parser.add_argument(
        "--pkg-path", required=True, help=("Path to the package source root")
    )
    return parser.parse_args()

if __name__ == "__main__":
    code_model = CodeModel.from_inspect(get_args())
    code_model.serialize()
