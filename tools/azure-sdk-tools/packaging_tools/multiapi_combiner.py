# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import importlib
import pkgutil
import json
import argparse
from pathlib import Path
from typing import Dict, Optional, List, Set, Any

def _get_metadata(path: Path) -> Dict[str, Any]:
    with open(path / "_metadata.json", "r") as fd:
        return json.load(fd)

class VersionedObject:
    """An object that can be added / removed in an api version"""
    def __init__(
        self,
        name: str,
        *,
        added_on: Optional[str] = None,
    ) -> None:
        self.name = name
        self.added_on = added_on

class Parameter(VersionedObject):

    pass

class Operation(VersionedObject):

    def __init__(
        self,
        name: str,
        parameters: List[Parameter],
        *,
        added_on: Optional[str] = None,
    )-> None:
        super().__init__(name, added_on=added_on)
        self.parameters = parameters

class OperationGroup(VersionedObject):
    def __init__(
        self,
        name: str,
        *,
        added_on: Optional[str] = None,
    ):
        super().__init__(name=name, added_on=added_on)
        self.operations: List[Operation] = []

class Serializer:
    def serialize(self):
        pass

class CodeModel:
    def __init__(self, pkg_path: Path):
        self.serializer = Serializer()
        self.module_name = pkg_path.stem.replace("-", ".")
        root_of_code = pkg_path
        for sub_folder in pkg_path.stem.split("-"):
            root_of_code = root_of_code / sub_folder
        self.api_version_to_metadata: Dict[str, Dict[str, Any]] = {
            dir.stem: _get_metadata(dir)
            for dir in root_of_code.iterdir()
            if dir.stem.startswith("v") and dir.stem > "v2020_11_01" and "preview" not in dir.stem
        }
        self.operation_groups = self._combine_operation_groups()

    def _combine_operation_groups(self) -> List[OperationGroup]:
        sorted_api_versions = sorted(self.api_version_to_metadata.keys())
        initial_metadata = self.api_version_to_metadata[sorted_api_versions[0]]
        ogs = [
            OperationGroup(name=og)
            for og in initial_metadata["operation_groups"].values()
        ]
        for idx in range(1, len(sorted_api_versions)):
            ogs = sorted(ogs, key=lambda x: x.name)
            curr_api_version = sorted_api_versions[idx]
            curr_metadata = self.api_version_to_metadata[curr_api_version]
            new_orgs: List[OperationGroup] = []
            curr_og_names = sorted(curr_metadata["operation_groups"].values())

            prev_counter = 0
            curr_counter = 0

            while prev_counter < len(ogs) and curr_counter < len(curr_og_names):
                if ogs[prev_counter].name < curr_og_names[curr_counter]:
                    raise ValueError(
                        "Can not run multiapi combiner because operation group "
                        f"{ogs[prev_counter].name} was remove in {curr_api_version}"
                    )
                elif ogs[prev_counter].name > curr_og_names[curr_counter]:
                    while ogs[prev_counter].name > curr_og_names[curr_counter]:
                        new_orgs.append(OperationGroup(name=curr_og_names[curr_counter], added_on=curr_api_version))
                        curr_counter += 1
                prev_counter += 1
                curr_counter += 1
            new_orgs.extend([  # add the remaining ogs if there are any to new_orgs
                OperationGroup(name=og, added_on=curr_api_version)
                for og in curr_og_names[curr_counter + 1:]
            ])

            ogs.extend(new_orgs)
        if initial_metadata.get("operation_mixins"):
            # we're going to assume mixins are never added / removed for now
            ogs.append(OperationGroup(name=f"{initial_metadata['client']['name']}OperationsMixin"))
        return ogs



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
    code_model = CodeModel(Path(get_args().pkg_path))
    code_model.serialize()
