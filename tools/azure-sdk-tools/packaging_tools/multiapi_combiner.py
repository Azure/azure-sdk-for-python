# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import importlib
import os
import re
import inspect
import json
import argparse
from pathlib import Path
import shutil
from typing import Dict, Optional, List, Any, TypeVar, Callable, Set

from jinja2 import PackageLoader, Environment

PACKAGING_TOOLS_DIR = (Path(__file__) / "..").resolve()


def _get_metadata(path: Path) -> Dict[str, Any]:
    with open(path / "_metadata.json", "r") as fd:
        return json.load(fd)


def _get_api_version(path: Path) -> str:
    return _get_metadata(path)["chosen_version"]


def modify_relative_imports(regex: str, file: str) -> str:
    dots = re.search(regex, file).group(1)
    original_str = regex.replace("(.*)", dots)
    new_str = regex.replace("(.*)", "." * (len(dots) - 1))
    return file.replace(original_str, new_str)


def strip_version_from_docs(input: str) -> str:
    return re.sub(r".v20[^.]*", "", input)


def remove_file(file_path: str) -> None:
    if (Path(file_path)).exists():
        os.remove(file_path)


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

    for idx in range(1, len(sorted_api_versions)):

        next_api_version = sorted_api_versions[idx]
        next_names = get_names_by_api_version(next_api_version)
        obj_names = [obj.name for obj in objs]

        existing_objs = [o for o in objs if o.name in next_names]
        new_objs: List[T] = [get_cls(code_model, n) for n in next_names if n not in obj_names]
        for obj in existing_objs + new_objs:
            obj.api_versions.append(next_api_version)
        objs.extend(new_objs)
    return objs


def _sort_models_helper(current: "ModelAndEnum", seen_model_names: Set[str]) -> List["ModelAndEnum"]:
    if current.name in seen_model_names:
        return []
    ancestors: List["ModelAndEnum"] = [current]
    for parent in current.parents:
        if parent.name in seen_model_names:
            continue
        ancestors = _sort_models_helper(parent, seen_model_names) + ancestors
        seen_model_names.add(parent.name)
    seen_model_names.add(current.name)
    return ancestors


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
        self._request_builder: Optional[str] = None

    def source_code(self, async_mode: bool) -> str:
        return strip_version_from_docs(inspect.getsource(self._get_op(self.api_versions[-1], async_mode)))

    @property
    def request_builder_name(self) -> Optional[str]:
        if self.name.startswith("begin_"):
            return None  # we use the initial function
        if self.name.startswith("_") and self.name.endswith("_initial"):
            operation_section = self.name[1 : len(self.name) - len("_initial")]
        else:
            operation_section = self.name
        if self.operation_group.property_name:
            og_name = self.operation_group.property_name
        else:
            client_filename = self.code_model.client.generated_filename
            og_name = client_filename[1 : len(client_filename) - len("_client")]
        return f"build_{og_name}_{operation_section}_request"

    @property
    def request_builder(self) -> Optional[str]:
        if self.request_builder_name is None:
            return None
        if self._request_builder is None:
            folder_api_version = self.code_model.api_version_to_folder_api_version[self.api_versions[-1]]
            module = importlib.import_module(f"{self.code_model.module_name}.{folder_api_version}")
            operations_file = getattr(module.operations, "_operations")
            self._request_builder = inspect.getsource(getattr(operations_file, self.request_builder_name))
        return self._request_builder

    @property
    def _need_method_api_version_check(self) -> bool:
        """Whether we need to check the api version of the method"""
        if self.operation_group.is_mixin and self.operation_group.need_decorator:
            # for mixin operations, we need to make sure the check shows up on the operations
            # bc we don't have decorators for mixins
            return True
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
            retval.extend([f'            "{p.name}": {p.api_versions},' for p in self.parameters if p.need_decorator])
            retval.append("        }")
        retval.append("    )")
        return "\n".join(retval)

    def _get_op(self, api_version: str, async_mode: bool = False):
        folder_api_version = self.code_model.api_version_to_folder_api_version[api_version]
        module = importlib.import_module(
            f"{self.code_model.module_name}.{folder_api_version}{'.aio' if async_mode else ''}"
        )
        operation_group = getattr(module.operations, self.operation_group.name)
        return getattr(operation_group, self.name)

    def combine_parameters(self) -> None:
        # don't want api versions if my operation group isn't in them
        api_versions = [
            v
            for v in self.code_model.sorted_api_versions
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

    @property
    def metadata(self) -> Optional[str]:
        op = self._get_op(self.api_versions[-1])
        return getattr(op, "metadata", None)


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

    def _get_og(self, api_version: str, async_mode: bool = False):
        folder_api_version = self.code_model.api_version_to_folder_api_version[api_version]
        module = importlib.import_module(
            f"{self.code_model.module_name}.{folder_api_version}{'.aio' if async_mode else ''}"
        )
        return getattr(module.operations, self.name)

    def generated_class(self, async_mode: bool):
        return self._get_og(self.api_versions[-1], async_mode)

    @property
    def need_decorator(self) -> bool:
        return any(a for a in self.code_model.sorted_api_versions if a not in self.api_versions)

    @property
    def decorator(self) -> str:
        return "\n".join(["@api_version_validation(", f"    api_versions={self.api_versions}", ")"])

    def combine_operations(self) -> None:
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

    def doc(self, async_mode: bool) -> str:
        return strip_version_from_docs(self.generated_class(async_mode).__doc__)


class Client:
    def __init__(self, code_model: "CodeModel") -> None:
        self.code_model = code_model

    def generated_module(self, async_mode: bool):
        return importlib.import_module(
            f"{self.code_model.module_name}{'.aio' if async_mode else ''}.{self.generated_filename}"
        )

    def generated_class(self, async_mode: bool):
        module = self.generated_module(async_mode)
        return getattr(module, self.name)

    @property
    def generated_filename(self) -> str:
        return list(self.code_model.api_version_to_metadata.values())[-1]["client"]["filename"]

    @property
    def name(self) -> str:
        return list(self.code_model.api_version_to_metadata.values())[-1]["client"]["name"]


class ModelAndEnum(VersionedObject):
    def __init__(self, code_model: "CodeModel", name: str) -> None:
        super().__init__(code_model, name)
        self._parents: List["ModelAndEnum"] = []

    @property
    def generated_class(self):
        folder_api_version = self.code_model.api_version_to_folder_api_version[self.api_versions[-1]]
        module = importlib.import_module(f"{self.code_model.module_name}.{folder_api_version}.models")
        return getattr(module, self.name)

    @property
    def source_code(self) -> str:
        return strip_version_from_docs(inspect.getsource(self.generated_class))

    @property
    def parents(self) -> List["ModelAndEnum"]:
        if not self._parents:
            for parent in self.generated_class.__mro__[1 : len(self.generated_class.__mro__) - 2]:
                self._parents.append(self.code_model.models[parent.__name__])
        return self._parents


class CodeModel:
    def __init__(self, pkg_path: Path):
        self._root_of_code = pkg_path
        for sub_folder in pkg_path.stem.split("-"):
            self._root_of_code = self._root_of_code / sub_folder
        self.api_version_to_metadata: Dict[str, Dict[str, Any]] = {
            _get_api_version(dir): _get_metadata(dir)
            for dir in self._root_of_code.iterdir()
            if dir.stem.startswith("v")
        }
        self.api_version_to_folder_api_version = {
            _get_api_version(dir): dir.stem for dir in self._root_of_code.iterdir() if dir.stem.startswith("v")
        }
        self.sorted_api_versions = sorted(self.api_version_to_metadata.keys())
        self.default_api_version = self.sorted_api_versions[-1]
        self.default_folder_api_version = self.api_version_to_folder_api_version[self.default_api_version]
        self.module_name = pkg_path.stem.replace("-", ".")
        self.operation_groups = self._combine_operation_groups()
        self.models: Dict[str, ModelAndEnum] = {}
        self.enums: List[ModelAndEnum] = []
        self._combine_models_and_enums()
        self.client = Client(self)

    def get_root_of_code(self, async_mode: bool) -> Path:
        return self._root_of_code / Path("aio") if async_mode else self._root_of_code

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
            mixin.api_versions = [
                a for a in self.sorted_api_versions if self.api_version_to_metadata[a].get("operation_mixins")
            ]
            ogs.append(mixin)

        for operation_group in ogs:
            operation_group.combine_operations()
            for operation in operation_group.operations:
                operation.combine_parameters()
        return ogs

    def _combine_models_and_enums(self) -> None:
        def _get_model(code_model: "CodeModel", name: str) -> ModelAndEnum:
            return ModelAndEnum(code_model, name)

        def _get_names_by_api_version(api_version: str):
            folder_api_version = self.api_version_to_folder_api_version[api_version]
            module = importlib.import_module(f"{self.module_name}.{folder_api_version}.models")
            return [m for m in dir(module) if m[0] != "_"]

        models_and_enums = _combine_helper(
            code_model=self,
            sorted_api_versions=self.sorted_api_versions,
            get_cls=_get_model,
            get_names_by_api_version=_get_names_by_api_version,
        )
        for m in models_and_enums:
            if hasattr(m.generated_class, "from_dict"):
                self.models[m.name] = m
            else:
                self.enums.append(m)
        self._sort_models()

    def _sort_models(self) -> None:
        seen_model_names: Set[str] = set()
        sorted_models: Dict[str, ModelAndEnum] = {}
        for model in self.models.values():
            sorted_models.update({m.name: m for m in _sort_models_helper(model, seen_model_names)})
        self.models = sorted_models


class Serializer:
    def __init__(self, code_model: "CodeModel") -> None:
        self.code_model = code_model
        self.env = Environment(
            loader=PackageLoader("packaging_tools", "templates/multiapi_combiner"),
            keep_trailing_newline=True,
            line_statement_prefix="##",
            line_comment_prefix="###",
            trim_blocks=True,
            lstrip_blocks=True,
        )

    def _copy_file_contents_helper(
        self,
        r_file: Path,
        w_file: Path,
        *,
        replacement_strings: Optional[Dict[str, Any]] = None,
    ):
        with open(r_file, "r") as rfd:
            with open(w_file, "w") as wfd:
                read_lines = rfd.read()
                if replacement_strings:
                    for orig, new in replacement_strings.items():
                        read_lines = read_lines.replace(orig, new)
                wfd.write(read_lines)

    def _copy_file_contents(
        self,
        filename: str,
        async_mode: bool,
        *,
        replacement_strings: Optional[Dict[str, Any]] = None,
        in_operations_folder: bool = False,
    ):
        root_of_code = self.code_model.get_root_of_code(async_mode)
        default_api_version_folder = self.code_model.get_root_of_code(False) / Path(
            self.code_model.default_folder_api_version
        )
        default_api_version_root_of_code = (
            (default_api_version_folder / Path("aio")) if async_mode else default_api_version_folder
        )
        if in_operations_folder:
            default_api_version_root_of_code /= Path("operations")
        default_api_version_filepath = default_api_version_root_of_code / Path(f"{filename}.py")
        if not default_api_version_filepath.exists():
            return
        self._copy_file_contents_helper(
            default_api_version_filepath, root_of_code / Path(f"{filename}.py"), replacement_strings=replacement_strings
        )

    def _get_file_path_from_module(self, module_name: str, strip_api_version: bool) -> Path:
        module_stem = module_name.strip(f"{self.code_model.module_name}.")
        if strip_api_version:
            module_stem = module_stem.strip(f"{self.code_model.default_folder_api_version}.")
        return self.code_model.get_root_of_code(False) / Path(module_stem.replace(".", "/"))

    def _get_operations_folder_module(self, async_mode: bool, *, api_version: Optional[str] = None) -> str:
        folder_api_version = self.code_model.api_version_to_folder_api_version.get(
            api_version, self.code_model.default_folder_api_version
        )
        return f"{self.code_model.module_name}.{folder_api_version}.{'aio.' if async_mode else ''}operations"

    def _get_operations_folder(self, async_mode: bool, *, api_version: Optional[str] = None) -> Path:
        operations_folder_module = self._get_operations_folder_module(async_mode, api_version=api_version)
        return self._get_file_path_from_module(operations_folder_module, strip_api_version=True)

    def serialize_operations_folder(self, async_mode: bool):
        template = self.env.get_template("operation_groups.py.jinja2")
        operations_folder_module = self._get_operations_folder_module(async_mode)
        operations_folder = self._get_operations_folder(async_mode)
        operations_module = importlib.import_module(f"{operations_folder_module}._operations")

        delimiter = "class " if async_mode else "def build_"  # sync as request builders
        imports = inspect.getsource(operations_module).split(delimiter)[0] + "\n"  # get all imports

        imports_splitlines = imports.splitlines()

        imports_to_add: List[str] = []
        # add imports if missing
        for api_version in self.code_model.sorted_api_versions:
            versioned_operations_folder_module = self._get_operations_folder_module(async_mode, api_version=api_version)
            versioned_operations_module = importlib.import_module(f"{versioned_operations_folder_module}._operations")
            versioned_imports = inspect.getsource(versioned_operations_module).split(delimiter)[0]  # get all imports
            versioned_imports_splitlines = versioned_imports.splitlines()
            for idx in range(len(versioned_imports_splitlines)):
                i = versioned_imports_splitlines[idx]
                if async_mode and "build_" in i:
                    # don't want to incorrectly add request builder imports here
                    continue

                if any(w for w in ["if ", "else:"] if w in i):
                    # we still want to do if else statements, check next line
                    if (
                        idx != len(versioned_imports_splitlines) - 1
                        and versioned_imports_splitlines[idx + 1] not in imports
                    ):
                        imports_to_add.append(i)
                elif i not in imports_splitlines:
                    imports_to_add.append(i)

        imports += "\n".join(imports_to_add)
        try:
            imports = modify_relative_imports(r"from (.*)_serialization import Serializer", imports)
        except AttributeError:
            pass
        validation_relative = "..." if async_mode else ".."
        imports += f"\nfrom {validation_relative}_validation import api_version_validation\n"
        Path(operations_folder).mkdir(parents=True, exist_ok=True)
        with open(f"{operations_folder}/_operations.py", "w", encoding="utf-8") as fd:
            fd.write(template.render(code_model=self.code_model, imports=imports, async_mode=async_mode))
        with open(f"{operations_folder}/__init__.py", "w") as fd:
            fd.write(self.env.get_template("operations_init.py.jinja2").render(code_model=self.code_model))
        with open(f"{operations_folder}/_patch.py", "w") as wfd:
            with open(
                f"{self._get_file_path_from_module(operations_folder_module, strip_api_version=False)}/_patch.py", "r"
            ) as rfd:
                wfd.write(rfd.read())

    def _get_operation_group_properties(self) -> List[OperationGroup]:
        map: Dict[str, OperationGroup] = {}
        for og in self.code_model.operation_groups:
            if not og.property_name:
                continue
            if og.property_name in map:
                existing_og = map[og.property_name]
                if og.api_versions[-1] > existing_og.api_versions[-1]:
                    map[og.property_name] = og
            else:
                map[og.property_name] = og
        return list(map.values())

    def serialize_client(self, async_mode: bool):
        template = self.env.get_template("client.py.jinja2")
        # do parsing on the source so we can build up our client
        main_client_source = inspect.getsource(self.code_model.client.generated_module(async_mode))
        split_main_client_source = main_client_source.split("class")
        imports = split_main_client_source[0]
        imports = imports.replace(f"from ._operations_mixin import {self.code_model.client.name}OperationsMixin\n", "")

        main_client_source = "class" + "class".join(split_main_client_source[1:])

        client_initialization = strip_version_from_docs(
            re.search(r"([\s\S]*?)    @classmethod", main_client_source).group(1)
        )
        if any(og.is_mixin for og in self.code_model.operation_groups):
            client_initialization = client_initialization + "".join([
                "        self._serialize = Serializer(self._models_dict())\n",
                "        self._deserialize = Deserializer(self._models_dict())\n",
                "        self._serialize.client_side_validation = False\n",
            ])

        # TODO: switch to current file path
        with open(f"{self.code_model.get_root_of_code(async_mode)}/_client.py", "w") as fd:
            fd.write(
                template.render(
                    code_model=self.code_model,
                    imports=imports,
                    client_initialization=client_initialization,
                    operation_group_properties=self._get_operation_group_properties(),
                    async_mode=async_mode,
                    getsource=inspect.getsource,
                )
            )

    def _serialize_general_helper(self, async_mode: bool):
        existing_files = ["_configuration", "_patch", "__init__", "_vendor"]
        replacement_strings = {f"from .{self.code_model.client.generated_filename}": "from ._client"}
        for file in existing_files:
            self._copy_file_contents(
                file,
                async_mode,
                replacement_strings=replacement_strings,
            )
        files_to_add = ["_vendor"]
        for file in files_to_add:
            self._copy_file_contents(file, async_mode, replacement_strings=replacement_strings)

    def _copy_files_from_operations_folder(self, async_mode: bool):
        files = ["_vendor"]
        for file in files:
            self._copy_file_contents(file, async_mode, in_operations_folder=True)

    def serialize_general(self):
        # sync
        self._serialize_general_helper(async_mode=False)
        self._serialize_general_helper(async_mode=True)
        self._copy_files_from_operations_folder(async_mode=False)
        self._copy_files_from_operations_folder(async_mode=True)
        sync_general_files = ["_serialization", "_version"]
        for file in sync_general_files:
            self._copy_file_contents(file, async_mode=False)

        with open(f"{self.code_model.get_root_of_code(False)}/_validation.py", "w") as fd:
            fd.write(self.env.get_template("validation.py.jinja2").render())

    def serialize_models_folder(self):
        # serialize init file
        models_folder = self.code_model.get_root_of_code(False) / "models"
        Path(models_folder).mkdir(parents=True, exist_ok=True)
        with open(f"{models_folder}/__init__.py", "w") as fd:
            fd.write(self.env.get_template("models_init.py.jinja2").render(code_model=self.code_model))
        default_api_version = self.code_model.default_folder_api_version
        default_models_folder_name = f"{self.code_model.module_name}.{default_api_version}.models"

        # serialize models file
        default_models_module = importlib.import_module(f"{default_models_folder_name}._models_py3")
        imports = inspect.getsource(default_models_module).split("class")[0]
        imports = modify_relative_imports(r"from (.*) import _serialization", imports)
        with open(f"{models_folder}/_models.py", "w", encoding="utf-8") as fd:
            fd.write(self.env.get_template("models.py.jinja2").render(code_model=self.code_model, imports=imports))

        # serialize enums file
        default_enums_module = importlib.import_module(
            f"{default_models_folder_name}.{self.code_model.client.generated_filename}_enums"
        )
        imports = inspect.getsource(default_enums_module).split("class")[0]
        if self.code_model.enums:
            with open(f"{models_folder}/_enums.py", "w", encoding="utf-8") as fd:
                fd.write(self.env.get_template("enums.py.jinja2").render(code_model=self.code_model, imports=imports))

        # serialize patch file
        with open(f"{models_folder}/_patch.py", "w") as wfd:
            with open(f"{self.code_model.get_root_of_code(False)}/{default_api_version}/models/_patch.py", "r") as rfd:
                wfd.write(rfd.read())

    def remove_versioned_files(self):
        root_of_code = self.code_model.get_root_of_code(False)
        for api_version_folder_stem in self.code_model.api_version_to_folder_api_version.values():
            api_version_folder = root_of_code / api_version_folder_stem
            shutil.rmtree(api_version_folder, ignore_errors=True)

    def remove_top_level_files(self, async_mode: bool):
        top_level_files = [
            self.code_model.client.generated_filename,
            "_operations_mixin",
        ]
        if not async_mode:
            top_level_files.append("models")
        for file in top_level_files:
            remove_file(f"{self.code_model.get_root_of_code(async_mode)}/{file}.py")

    def remove_old_code(self):
        self.remove_versioned_files()
        self.remove_top_level_files(async_mode=False)
        self.remove_top_level_files(async_mode=True)

    def serialize(self):
        self.serialize_operations_folder(async_mode=False)
        self.serialize_operations_folder(async_mode=True)
        self.serialize_client(async_mode=False)
        self.serialize_client(async_mode=True)
        self.serialize_general()
        self.serialize_models_folder()
        self.remove_old_code()


def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Combine multiapi SDKs into a single SDK")
    parser.add_argument("--pkg-path", required=True, help=("Path to the package source root"))
    return parser.parse_args()


def combine():
    code_model = CodeModel(Path(get_args().pkg_path))
    Serializer(code_model).serialize()


if __name__ == "__main__":
    combine()
