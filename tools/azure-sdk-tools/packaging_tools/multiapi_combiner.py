# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import importlib
import re
import inspect
import json
import argparse
from pathlib import Path
from typing import Dict, Optional, List, Any, TypeVar, Callable

from jinja2 import FileSystemLoader, Environment

PACKAGING_TOOLS_DIR = (Path(__file__) / "..").resolve()


def _get_metadata(path: Path) -> Dict[str, Any]:
    with open(path / "_metadata.json", "r") as fd:
        return json.load(fd)

def modify_relative_imports(regex: str, file: str) -> str:
    dots = re.search(regex, file).group(1)
    original_str = regex.replace("(.*)", dots)
    new_str = regex.replace("(.*)", "." * (len(dots) - 1))
    return file.replace(original_str, new_str)

class VersionedObject:
    """An object that can be added / removed in an api version"""

    def __init__(
        self,
        code_model: "CodeModel",
        name: str,
    ) -> None:
        self.code_model = code_model
        self.name = name
        self.api_versions = []  # api versions this object exists for


T = TypeVar("T", bound=VersionedObject)


def _combine_helper(
    code_model: "CodeModel",
    sorted_api_versions: List[str],
    get_cls: Callable[["CodeModel", str], T],
    get_names_by_api_version: Callable[[str], List[str]],
) -> List[T]:
    """Helper to combine operation groups, operations, and parameters"""

    # objs is union of all operation groups we've seen
    objs: List[T] = [get_cls(code_model, name) for name in get_names_by_api_version(sorted_api_versions[0])]
    for obj in objs:
        obj.api_versions.append(sorted_api_versions[0])

    curr_objs = objs # operation groups we see for our current api version
    for idx in range(1, len(sorted_api_versions)):

        next_api_version = sorted_api_versions[idx]
        next_names = get_names_by_api_version(next_api_version)
        curr_obj_names = [obj.name for obj in curr_objs]

        existing_objs = [o for o in curr_objs if o.name in next_names]

        added_next_names = [n for n in next_names if n not in curr_obj_names]
        new_objs: List[T] = [
            get_cls(code_model, name) for name in added_next_names
        ]
        curr_objs = existing_objs + new_objs
        for obj in curr_objs:
            obj.api_versions.append(next_api_version)
        objs.extend(new_objs)
    return objs


class Parameter(VersionedObject):
    def __init__(
        self,
        code_model: "CodeModel",
        name: str,
        operation: "Operation",
    ) -> None:
        super().__init__(code_model, name)
        self.operation = operation

    @property
    def need_decorator(self) -> bool:
        return any(a for a in self.operation.api_versions if a not in self.api_versions)


class Operation(VersionedObject):
    def __init__(
        self,
        code_model: "CodeModel",
        name: str,
        operation_group: "OperationGroup",
    ) -> None:
        super().__init__(code_model, name)
        self.operation_group = operation_group
        self.parameters: List[Parameter] = []

    def source_code(self, async_mode: bool) -> str:
        return inspect.getsource(self._get_op(self.api_versions[-1], async_mode))

    @property
    def _need_method_api_version_check(self) -> bool:
        """Whether we need to check the api version of the method"""
        return any(a for a in self.operation_group.api_versions if a not in self.api_versions)

    @property
    def _need_params_api_version_check(self) -> bool:
        """Whether we need to check the api versions of any params"""
        return any(p for p in self.parameters if p.need_decorator)

    @property
    def need_decorator(self) -> bool:
        """Whether we need to decorate the method with a decorator

        Since this decorator handles both method-level and parameter-level
        checks, we need a decorator if any of them need a check
        """
        return self.name[0] != "_" and (self._need_method_api_version_check or self._need_params_api_version_check)

    @property
    def decorator(self) -> str:
        retval: List[str] = ["    @api_version_validation("]
        # only need to validate operations that don't include
        # all of the api versions of the operation group
        # because the operation group handles first round of validation
        if self._need_method_api_version_check:
            retval.append(f"        api_versions={self.api_versions},")
        if self._need_params_api_version_check:
            retval.append("        params={")
            retval.extend([
                f'            "{p.name}": {p.api_versions},'
                for p in self.parameters if p.need_decorator
            ])
            retval.append("        }")
        retval.append("    )")
        return "\n".join(retval)

    def _get_op(self, api_version: str, async_mode: bool = False):
        module = importlib.import_module(f"{self.code_model.module_name}.{api_version}{'.aio' if async_mode else ''}")
        operation_group = getattr(module.operations, self.operation_group.name)
        return getattr(operation_group, self.name)

    def combine_parameters(self) -> None:
        # don't want api versions if my operation group isn't in them
        api_versions = [
            v for v in self.code_model.sorted_api_versions
            if v in self.operation_group.api_versions and v in self.api_versions
        ]

        def _get_names_by_api_version(api_version: str):
            op = self._get_op(api_version)
            # return retvals beside kwargs and the response
            return list(op.__annotations__.keys())[: len(op.__annotations__.keys()) - 2]

        def _get_parameter(code_model: "CodeModel", name: str) -> Parameter:
            return Parameter(code_model, name, operation=self)

        self.parameters = _combine_helper(
            code_model=self.code_model,
            sorted_api_versions=api_versions,
            get_cls=_get_parameter,
            get_names_by_api_version=_get_names_by_api_version,
        )


class OperationGroup(VersionedObject):
    def __init__(
        self,
        code_model: "CodeModel",
        name: str,
        *,
        property_name: Optional[str] = None,
    ):
        super().__init__(code_model, name=name)
        self.operations: List[Operation] = []
        self.is_mixin = self.name.endswith("OperationsMixin")
        self.property_name = property_name

    def _get_og(self, api_version: str):
        module = importlib.import_module(f"{self.code_model.module_name}.{api_version}")
        return getattr(module.operations, self.name)

    @property
    def generated_class(self):
        return self._get_og(self.api_versions[-1])

    @property
    def need_decorator(self) -> bool:
        return any(a for a in self.code_model.sorted_api_versions if a not in self.api_versions)

    @property
    def decorator(self) -> str:
        return "\n".join([
            "@api_version_validation(",
            f"    api_versions={self.api_versions}",
            ")"
        ])

    def combine_operations(self) -> None:
        # chose api versions greater than when I was added
        api_versions = [v for v in self.code_model.sorted_api_versions if v in self.api_versions]
        def _get_names_by_api_version(api_version: str):
            operation_group = self._get_og(api_version)
            return [d for d in dir(operation_group) if callable(getattr(operation_group, d)) and d[:2] != "__"]

        def _get_operation(code_model: "CodeModel", name: str) -> Operation:
            return Operation(code_model, name, operation_group=self)

        self.operations = _combine_helper(
            code_model=self.code_model,
            sorted_api_versions=api_versions,
            get_cls=_get_operation,
            get_names_by_api_version=_get_names_by_api_version,
        )


class CodeModel:
    def __init__(self, pkg_path: Path):
        self.root_of_code = pkg_path
        for sub_folder in pkg_path.stem.split("-"):
            self.root_of_code = self.root_of_code / sub_folder
        self.api_version_to_metadata: Dict[str, Dict[str, Any]] = {
            dir.stem: _get_metadata(dir)
            for dir in self.root_of_code.iterdir()
            if dir.stem.startswith("v") and "preview" not in dir.stem
        }
        self.sorted_api_versions = sorted([metadata["chosen_version"] for metadata in self.api_version_to_metadata.values()])
        self.default_api_version = self.sorted_api_versions[-1]
        self.module_name = pkg_path.stem.replace("-", ".")
        self.operation_groups = self._combine_operation_groups()

    def _combine_operation_groups(self) -> List[OperationGroup]:
        initial_metadata = self.api_version_to_metadata[self.sorted_api_versions[0]]

        def _get_names_by_api_version(api_version: str):
            if not api_version:
                return [og for og in initial_metadata["operation_groups"].values()]
            curr_metadata = self.api_version_to_metadata[api_version]
            return sorted(curr_metadata["operation_groups"].values())

        def _get_operation_group(code_model: "CodeModel", name: str):
            property_name = next(
                property_name
                for _, metadata in code_model.api_version_to_metadata.items()
                for property_name, og_name in metadata["operation_groups"].items()
                if og_name == name
            )
            return OperationGroup(code_model, name, property_name=property_name)

        ogs = _combine_helper(
            code_model=self,
            sorted_api_versions=self.sorted_api_versions,
            get_cls=_get_operation_group,
            get_names_by_api_version=_get_names_by_api_version,
        )
        if initial_metadata.get("operation_mixins"):
            # we're going to assume mixins are never added / removed for now
            mixin = OperationGroup(
                code_model=self,
                name=f"{initial_metadata['client']['name']}OperationsMixin",
            )
            mixin.api_versions = self.sorted_api_versions
            ogs.append(mixin)

        for operation_group in ogs:
            operation_group.combine_operations()
            for operation in operation_group.operations:
                operation.combine_parameters()
        return ogs


class Serializer:
    def __init__(self, code_model: "CodeModel") -> None:
        self.code_model = code_model
        self.env = Environment(
            loader=FileSystemLoader(searchpath="templates/multiapi_combiner"),
            keep_trailing_newline=True,
            line_statement_prefix="##",
            line_comment_prefix="###",
            trim_blocks=True,
            lstrip_blocks=True,
        )

    def _copy_file_contents(self, filename: str, async_mode: bool, module: Optional[Path] = None):
        module = module or self.code_model.root_of_code
        root_of_code = (self.code_model.root_of_code / Path("aio")) if async_mode else self.code_model.root_of_code
        default_api_version_folder = self.code_model.root_of_code / Path(self.code_model.default_api_version)
        default_api_version_root_of_code = (
            (default_api_version_folder / Path("aio")) if async_mode else default_api_version_folder
        )
        default_api_version_filepath = default_api_version_root_of_code / Path(f"{filename}.py")
        if not default_api_version_filepath.exists():
            return
        with open(default_api_version_filepath, "r") as rfd:
            with open(root_of_code / Path(f"{filename}.py"), "w") as wfd:
                wfd.write(rfd.read())

    def _get_file_path_from_module(self, module_name: str, strip_api_version: bool) -> Path:
        module_stem = module_name.strip(f"{self.code_model.module_name}.")
        if strip_api_version:
            module_stem = module_stem.strip(f"{self.code_model.default_api_version}.")
        return self.code_model.root_of_code / Path(module_stem.replace(".", "/"))

    def serialize_operations_folder(self, async_mode: bool):
        template = self.env.get_template("operation_groups.py.jinja2")
        operations_folder_module = f"{self.code_model.module_name}.{self.code_model.default_api_version}.{'aio.' if async_mode else ''}operations"
        operations_folder = self._get_file_path_from_module(operations_folder_module, strip_api_version=True)
        operations_module = importlib.import_module(f"{operations_folder_module}._operations")
        setup = inspect.getsource(operations_module).split("class ")[0]  # get all request builders and imports
        try:
            setup = modify_relative_imports(r"from (.*)_serialization import Serializer", setup)
        except AttributeError:
            pass
        validation_relative = "..." if async_mode else ".."
        setup += f"from {validation_relative}_validation import api_version_validation\n"
        Path(operations_folder).mkdir(parents=True, exist_ok=True)
        with open(f"{operations_folder}/_operations.py", "w") as fd:
            fd.write(template.render(code_model=self.code_model, setup=setup, async_mode=async_mode))
        with open(f"{operations_folder}/__init__.py", "w") as wfd:
            with open(f"{self._get_file_path_from_module(operations_folder_module, strip_api_version=False)}/__init__.py", "r") as rfd:
                wfd.write(rfd.read())
        with open(f"{operations_folder}/_patch.py", "w") as wfd:
            with open(f"{self._get_file_path_from_module(operations_folder_module, strip_api_version=False)}/_patch.py", "r") as rfd:
                wfd.write(rfd.read())


    def serialize_client(self, async_mode: bool):
        template = self.env.get_template("client.py.jinja2")
        filename = self.code_model.api_version_to_metadata[
            self.code_model.default_api_version
        ]["client"]["filename"]
        client_file_module = f"{self.code_model.module_name}.{'aio.' if async_mode else ''}{filename}"
        client_module = importlib.import_module(client_file_module)

        # do parsing on the source so we can build up our client
        main_client_source = inspect.getsource(client_module)
        imports = main_client_source.split("class")[0]
        vadilation_relative = ".." if async_mode else "."
        imports += f"from {vadilation_relative}_validation import api_version_validation\n"

        main_client_source = main_client_source[len(imports):]

        client_initialization = re.search(r'((?s).*?)    @classmethod', main_client_source).group(1)

        # TODO: switch to current file path
        with open(f"{self.code_model.root_of_code}/{'aio/' if async_mode else ''}_client.py", "w") as fd:
            fd.write(template.render(
                code_model=self.code_model,
                imports=imports,
                client_initialization=client_initialization,
        ))

    def _serialize_general_helper(self, async_mode: bool):
        general_files = ["_configuration", "_patch", "__init__"]
        for file in general_files:
            self._copy_file_contents(file, async_mode)

    def serialize_general(self):
        # sync
        self._serialize_general_helper(async_mode=False)
        sync_general_files = ["_serialization", "_vendor", "_version"]
        for file in sync_general_files:
            self._copy_file_contents(file, async_mode=False)

        with open(f"{self.code_model.root_of_code}/_validation.py", "w") as fd:
            fd.write(self.env.get_template("validation.py.jinja2").render())

        # async
        # self._serialize_general_helper(async_mode=True)

    def serialize(self):
        self.serialize_operations_folder(async_mode=False)
        self.serialize_operations_folder(async_mode=True)
        self.serialize_client(async_mode=False)
        self.serialize_client(async_mode=True)
        # self.serialize_models_file()
        self.serialize_general()


def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Combine multiapi SDKs into a single SDK")
    parser.add_argument("--pkg-path", required=True, help=("Path to the package source root"))
    return parser.parse_args()


if __name__ == "__main__":
    code_model = CodeModel(Path(get_args().pkg_path))
    Serializer(code_model).serialize()
