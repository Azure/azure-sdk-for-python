# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import importlib
import json
import argparse
from pathlib import Path
from typing import Dict, Optional, List, Set, Any, TypeVar, Type, Callable


def _get_metadata(path: Path) -> Dict[str, Any]:
    with open(path / "_metadata.json", "r") as fd:
        return json.load(fd)


class VersionedObject:
    """An object that can be added / removed in an api version"""

    def __init__(
        self,
        code_model: "CodeModel",
        name: str,
        *,
        added_on: Optional[str] = None,
    ) -> None:
        self.code_model = code_model
        self.name = name
        self.added_on = added_on or ""


T = TypeVar("T", bound=VersionedObject)


def _combine_helper(
    code_model: "CodeModel",
    sorted_api_versions: List[str],
    get_cls: Callable[["CodeModel", str, Optional[str]], T],
    get_names_by_api_version: Callable[[str], List[str]],
    *,
    sort: bool = True,
) -> List[T]:
    """Helper to combine operation groups, operations, and parameters"""
    objs: List[T] = [get_cls(code_model, name, None) for name in get_names_by_api_version(sorted_api_versions[0])]
    for idx in range(1, len(sorted_api_versions)):
        if sort:
            objs = sorted(objs, key=lambda x: x.name)
        curr_api_version = sorted_api_versions[idx]
        curr_names = get_names_by_api_version(curr_api_version)

        new_objs: List[T] = []

        prev_counter = 0
        curr_counter = 0

        while prev_counter < len(objs) and curr_counter < len(curr_names):
            if objs[prev_counter].name < curr_names[curr_counter]:
                raise ValueError(
                    "Can not run multiapi combiner because "
                    f"{objs[prev_counter].name} was removed in {curr_api_version}"
                )
            elif objs[prev_counter].name > curr_names[curr_counter]:
                while objs[prev_counter].name > curr_names[curr_counter]:
                    new_objs.append(
                        get_cls(
                            code_model,
                            curr_names[curr_counter],
                            curr_api_version,
                        )
                    )
                    curr_counter += 1
            prev_counter += 1
            curr_counter += 1
        new_objs.extend(
            [  # add the remaining objs if there are any to new_objs
                get_cls(code_model, name, curr_api_version) for name in curr_names[curr_counter + 1 :]
            ]
        )

        objs.extend(new_objs)
    return objs


class Parameter(VersionedObject):
    def __init__(
        self,
        code_model: "CodeModel",
        name: str,
        operation: "Operation",
        *,
        added_on: Optional[str] = None,
    ) -> None:
        super().__init__(code_model, name, added_on=added_on)
        self.operation = operation


class Operation(VersionedObject):
    def __init__(
        self,
        code_model: "CodeModel",
        name: str,
        operation_group: "OperationGroup",
        *,
        added_on: Optional[str] = None,
    ) -> None:
        super().__init__(code_model, name, added_on=added_on)
        self.operation_group = operation_group
        self.parameters: List[Parameter] = self._combine_parameters()

    def _combine_parameters(self) -> List[Parameter]:
        # don't want api versions if my operation group isn't in them
        api_versions = [
            v for v in self.code_model.sorted_api_versions if v >= self.operation_group.added_on and v >= self.added_on
        ]

        def _get_names_by_api_version(api_version: str):
            module = importlib.import_module(f"{self.code_model.module_name}.{api_version}")
            operation_group = getattr(module.operations, self.operation_group.name)
            op = getattr(operation_group, self.name)
            # return retvals beside kwargs and the response
            return list(op.__annotations__.keys())[: len(op.__annotations__.keys()) - 2]

        def _get_parameter(code_model: "CodeModel", name: str, added_on: Optional[str] = None) -> Parameter:
            return Parameter(code_model, name, operation=self, added_on=added_on)

        params = _combine_helper(
            code_model=self.code_model,
            sorted_api_versions=api_versions,
            get_cls=_get_parameter,
            get_names_by_api_version=_get_names_by_api_version,
            sort=False,
        )
        return params


class OperationGroup(VersionedObject):
    def __init__(
        self,
        code_model: "CodeModel",
        name: str,
        *,
        added_on: Optional[str] = None,
    ):
        super().__init__(code_model, name=name, added_on=added_on)
        self.operations: List[Operation] = self._combine_operations()

    def _combine_operations(self) -> List[Operation]:
        # chose api versions greater than when I was added
        api_versions = [v for v in self.code_model.sorted_api_versions if v >= self.added_on]

        def _get_names_by_api_version(api_version: str):
            module = importlib.import_module(f"{self.code_model.module_name}.{api_version}")
            operation_group = getattr(module.operations, self.name)
            return [d for d in dir(operation_group) if d[0] != "_" and d != "models"]

        def _get_operation(code_model: "CodeModel", name: str, added_on: Optional[str] = None) -> Operation:
            return Operation(code_model, name, operation_group=self, added_on=added_on)

        return _combine_helper(
            code_model=self.code_model,
            sorted_api_versions=api_versions,
            get_cls=_get_operation,
            get_names_by_api_version=_get_names_by_api_version,
        )


class Serializer:
    def serialize(self):
        pass


class CodeModel:
    def __init__(self, pkg_path: Path):
        self.serializer = Serializer()
        root_of_code = pkg_path
        for sub_folder in pkg_path.stem.split("-"):
            root_of_code = root_of_code / sub_folder
        self.api_version_to_metadata: Dict[str, Dict[str, Any]] = {
            dir.stem: _get_metadata(dir)
            for dir in root_of_code.iterdir()
            if dir.stem.startswith("v") and dir.stem >= "v2020_11_01" and "preview" not in dir.stem
        }
        self.sorted_api_versions = sorted(self.api_version_to_metadata.keys())
        self.module_name = pkg_path.stem.replace("-", ".")
        self.operation_groups = self._combine_operation_groups()

    def _combine_operation_groups(self) -> List[OperationGroup]:
        initial_metadata = self.api_version_to_metadata[self.sorted_api_versions[0]]

        def _get_names_by_api_version(api_version: str):
            if not api_version:
                return [og for og in initial_metadata["operation_groups"].values()]
            curr_metadata = self.api_version_to_metadata[api_version]
            return sorted(curr_metadata["operation_groups"].values())

        def _get_operation_group(code_model: "CodeModel", name: str, added_on: Optional[str] = None):
            return OperationGroup(code_model, name, added_on=added_on)

        ogs = _combine_helper(
            code_model=self,
            sorted_api_versions=self.sorted_api_versions,
            get_cls=_get_operation_group,
            get_names_by_api_version=_get_names_by_api_version,
        )
        if initial_metadata.get("operation_mixins"):
            # we're going to assume mixins are never added / removed for now
            ogs.append(
                OperationGroup(
                    code_model=self,
                    name=f"{initial_metadata['client']['name']}OperationsMixin",
                )
            )
        return ogs

    def serialize(self):
        # return self.serializer.serialize()
        retval = {}

        for operation_group in self.operation_groups:
            if operation_group.added_on:
                retval[operation_group.name] = {"added_on": operation_group.added_on}
            for operation in operation_group.operations:
                if operation.added_on:
                    retval.setdefault(operation_group.name, {}).setdefault("operations", {}).setdefault(
                        operation.name, {}
                    )["addedOn"] = operation.added_on
                for parameter in operation.parameters:
                    if parameter.added_on:
                        retval.setdefault(operation_group.name, {}).setdefault("operations", {}).setdefault(
                            operation.name, {}
                        ).setdefault("parameters", {}).setdefault(parameter.name, {})["addedOn"] = parameter.added_on
        with open("output.json", "w") as fd:
            fd.write(json.dumps(retval))


def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Combine multiapi SDKs into a single SDK")
    parser.add_argument("--pkg-path", required=True, help=("Path to the package source root"))
    return parser.parse_args()


if __name__ == "__main__":
    code_model = CodeModel(Path(get_args().pkg_path))
    code_model.serialize()
