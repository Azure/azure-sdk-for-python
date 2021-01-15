#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import ast
import os
import enum
import argparse
import importlib
import inspect
import json
import json
import ast
import logging
import inspect
import subprocess
from enum import Enum
from typing import Dict, Union, Type, Callable
from breaking_changes_allowlist import RUN_BREAKING_CHANGES_PACKAGES
from breaking_changes_tracker import BreakingChangesTracker
try:
    # won't be able to import these in the created venv
    from packaging_tools.venvtools import create_venv_with_package
    import jsondiff
except (ModuleNotFoundError, ImportError) as e:
    pass


root_dir = os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "..", ".."))
_LOGGER = logging.getLogger(__name__)


class ClassTreeAnalyzer(ast.NodeVisitor):
    def __init__(self, name: str) -> None:
        self.name = name
        self.cls_node = None

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        if node.name == self.name:
            self.cls_node = node
        self.generic_visit(node)


def test_find_modules(pkg_root_path: str) -> Dict:
    """Find modules within the package to import and parse.
    Code borrowed and edited from APIview.

    :param str: pkg_root_path
        Package root path
    :rtype: Dict
    """
    modules = {}
    for root, subdirs, files in os.walk(pkg_root_path):
        # Ignore any modules with name starts with "_"
        # For e.g. _generated, _shared etc
        dirs_to_skip = [x for x in subdirs if x.startswith("_") or x.startswith(".")]
        for d in dirs_to_skip:
            subdirs.remove(d)

        # Add current path as module name if _init.py is present
        if "__init__.py" in files:
            module_name = os.path.relpath(root, pkg_root_path).replace(
                os.path.sep, "."
            )
            modules[module_name] = []
            for f in files:
                if f.endswith(".py"):
                    modules[module_name].append(os.path.join(root, f))
            # Add any public py file names as modules
            sub_modules = [
                os.path.splitext(os.path.basename(f))[0]
                for f in files
                if f.endswith(".py") and not os.path.basename(f).startswith("_")
            ]
            modules[module_name].extend(["{0}.{1}".format(module_name, x) for x in sub_modules])

    return modules


def get_parameter_default(param: inspect.Parameter) -> None:
    default_value = None
    if param.default is not param.empty:
        default_value = param.default
        if default_value is None:  # the default is actually None
            default_value = "none"
        if inspect.isfunction(default_value):
            default_value = default_value.__name__
        if inspect.isclass(default_value):
            default_value = default_value.__name__
        if hasattr(default_value, "value"):
            default_value = default_value.value

    return default_value


def get_property_names(node: ast.AST, attribute_names: Dict) -> None:
    func_nodes = [node for node in node.body if isinstance(node, ast.FunctionDef)]
    if func_nodes:
        assigns = [node for node in func_nodes[0].body if isinstance(node, ast.Assign)]
        if assigns:
            for assign in assigns:
                if hasattr(assign, "targets"):
                    for attr in assign.targets:
                        if hasattr(attr, "attr") and not attr.attr.startswith("_"):
                            attribute_names.update({attr.attr: attr.attr})


def check_base_classes(cls_node: ast.ClassDef) -> bool:
    should_look = False
    init_node = [
        node for node in cls_node.body
        if isinstance(node, ast.FunctionDef) and node.name.startswith("__init__")
    ]
    if init_node:
        if hasattr(init_node, "body"):
            for node in init_node.body:
                if isinstance(node, ast.Expr):
                    if hasattr(node, "value") and isinstance(node.value, ast.Call):
                        if isinstance(node.value.func, ast.Name):
                            if node.value.func.id == "super":
                                should_look = True
    else:
        should_look = True  # no init node so it is using init from base class
    return should_look


def get_properties(cls: Type) -> Dict:
    """Get the public instance variables of the class and any inherited.

    :param cls:
    :return:
    """
    attribute_names = {}

    path = inspect.getsourcefile(cls)
    with open(path, "r") as source:
        module = ast.parse(source.read())

    analyzer = ClassTreeAnalyzer(cls.__name__)
    analyzer.visit(module)
    cls_node = analyzer.cls_node
    extract_base_classes = check_base_classes(cls_node)

    if extract_base_classes:
        base_classes = inspect.getmro(cls)  # includes cls itself
        for base_class in base_classes:
            try:
                path = inspect.getsourcefile(base_class)
                if path.find("azure") == -1:
                    continue
                with open(path, "r") as source:
                    module = ast.parse(source.read())
            except (TypeError, SyntaxError):
                _LOGGER.info(f"Unable to create ast of {base_class}")
                continue  # was a built-in, e.g. "object", Exception, or a Model from msrest fails here

            analyzer = ClassTreeAnalyzer(base_class.__name__)
            analyzer.visit(module)
            cls_node = analyzer.cls_node
            get_property_names(cls_node, attribute_names)
    else:
        get_property_names(cls_node, attribute_names)
    return attribute_names


def create_function_report(f: Callable, is_async: bool = False) -> Dict:
    function = inspect.signature(f)
    func_obj = {
        "parameters": {},
        "is_async": is_async
    }

    for par in function.parameters.values():
        default_value = get_parameter_default(par)
        param = {par.name: {"default": default_value, "param_type": None}}

        param_type = None
        if par.kind == par.KEYWORD_ONLY:
            param_type = "keyword_only"
        elif par.kind == par.POSITIONAL_ONLY:
            param_type = "positional_only"
        elif par.kind == par.POSITIONAL_OR_KEYWORD:
            param_type = "positional_or_keyword"
        elif par.kind == par.VAR_POSITIONAL:
            param_type = "var_positional"
        elif par.kind == par.VAR_KEYWORD:
            param_type = "var_keyword"

        param[par.name]["param_type"] = param_type
        func_obj["parameters"].update(param)

    return func_obj


def create_class_report(cls: Type) -> Dict:
    cls_info = {
        "type": None,
        "methods": {},
        "properties": {},
    }

    is_enum = Enum in cls.__mro__
    if is_enum:
        cls_info["type"] = "Enum"
        cls_info["properties"] = {str(value): str(value) for value in dir(cls) if not value.startswith("_")}
        return cls_info

    cls_info["properties"] = get_properties(cls)

    methods = [method for method in dir(cls) if not method.startswith("_") or method.startswith("__init__")]
    for method in methods:
        async_func = False
        m = getattr(cls, method)
        if inspect.isfunction(m) or inspect.ismethod(m):
            if inspect.iscoroutinefunction(m):
                async_func = True
            cls_info["methods"][method] = create_function_report(m, async_func)

    return cls_info


def resolve_module_name(module_name: str, target_module: str) -> str:
    if module_name == ".":
        module_name = target_module
    else:
        module_name = target_module + "." + module_name
    return module_name


def build_library_report(target_module: str) -> Dict:
    module = importlib.import_module(target_module)
    modules = test_find_modules(module.__path__[0])

    public_api = {}
    for module_name, val in modules.items():
        module_name = resolve_module_name(module_name, target_module)
        public_api[module_name] = {"class_nodes": {}, "function_nodes": {}}
        module = importlib.import_module(module_name)
        importables = [importable for importable in dir(module)]
        for importable in importables:
            if not importable.startswith("_"):
                live_obj = getattr(module, importable)
                if inspect.isfunction(live_obj):
                    public_api[module_name]["function_nodes"].update({importable: create_function_report(live_obj)})
                elif inspect.isclass(live_obj):
                    public_api[module_name]["class_nodes"].update({importable: create_class_report(live_obj)})
                # else:  # Constants, version, etc. Nothing of interest at the moment
                #     public_api[module_name]["others"].update({importable: live_obj})

    return public_api


def test_compare_reports(pkg_dir: str, version: str) -> None:
    package_name = os.path.basename(pkg_dir)

    with open(os.path.join(pkg_dir, "stable.json"), "r") as fd:
        stable = json.load(fd)
    with open(os.path.join(pkg_dir, "current.json"), "r") as fd:
        current = json.load(fd)
    diff = jsondiff.diff(stable, current)

    bc = BreakingChangesTracker(stable, current, diff, package_name)
    bc.run_checks()

    remove_json_files(pkg_dir)

    if bc.breaking_changes:
        print(bc)
        exit(1)

    print(f"\nNo breaking changes found for {package_name} between stable version {version} and current version.")


def remove_json_files(pkg_dir: str) -> None:
    stable_json = os.path.join(pkg_dir, "stable.json")
    current_json = os.path.join(pkg_dir, "current.json")
    if os.path.isfile(stable_json):
        os.remove(stable_json)
    if os.path.isfile(current_json):
        os.remove(current_json)
    _LOGGER.info("cleaning up")


def main(package_name: str, target_module: str, version: str, in_venv: Union[bool, str], pkg_dir: str):
    in_venv = True if in_venv == "true" else False  # subprocess sends back string so convert to bool

    if not in_venv:
        packages = [f"{package_name}=={version}", "aiohttp"]
        with create_venv_with_package(packages) as venv:
            _LOGGER.info(f"Installed version {version} of {package_name} in a venv")
            args = [
                venv.env_exe,
                __file__,
                "-t",
                package_name,
                "-m",
                target_module,
                "--in-venv",
                "true",
                "-s",
                version
            ]
            try:
                subprocess.check_call(args)
            except subprocess.CalledProcessError:
                _LOGGER.warning(f"Version {version} failed to create a JSON report.")
                exit(1)
    try:
        public_api = build_library_report(target_module)

        if in_venv:
            with open("stable.json", "w") as fd:
                json.dump(public_api, fd, indent=2)
            _LOGGER.info("stable.json is written.")
            return

        with open("current.json", "w") as fd:
            json.dump(public_api, fd, indent=2)
        _LOGGER.info("current.json is written.")

        test_compare_reports(pkg_dir, version)

    except Exception as err:  # catch any issues with capturing the public API and building the report
        print("\n*****See aka.ms/azsdk/breaking-changes-tool to resolve any build issues*****\n")
        remove_json_files(pkg_dir)
        raise err


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run breaking changes checks against target folder."
    )

    parser.add_argument(
        "-t",
        "--target",
        dest="target_package",
        help="The target package directory on disk. The target module passed to will be <target_package>/azure.",
        required=True,
    )

    parser.add_argument(
        "-m",
        "--module",
        dest="target_module",
        help="The target module. The target module passed will be the top most module in the package",
    )

    parser.add_argument(
        "-v",
        "--in-venv",
        dest="in_venv",
        help="Check if we are in the newly created venv.",
        default=False
    )

    parser.add_argument(
        "-s",
        "--stable_version",
        dest="stable_version",
        help="The stable version of the target package, if it exists on PyPi.",
        default=None
    )

    args = parser.parse_args()
    in_venv = args.in_venv
    stable_version = args.stable_version

    pkg_dir = os.path.abspath(args.target_package)
    package_name = os.path.basename(pkg_dir)
    logging.basicConfig(level=logging.INFO)
    if package_name not in RUN_BREAKING_CHANGES_PACKAGES:
        _LOGGER.info(f"{package_name} opted out of breaking changes checks. "
                     f"See http://aka.ms/azsdk/breaking-changes-tool to opt-in.")
        exit(0)

    # TODO need to parse setup.py here to get the top module/namespace since not always the same.
    #  e.g. azure-storage-file-share and azure.storage.fileshare
    target_module = package_name.replace("-", ".")
    if not stable_version:

        from pypi_tools.pypi import PyPIClient
        client = PyPIClient()

        try:
            stable_version = str(client.get_relevant_versions(package_name)[1])
        except IndexError:
            _LOGGER.warning(f"No stable version for {package_name} on PyPi. Exiting...")
            exit(0)

    main(package_name, target_module, stable_version, in_venv, pkg_dir)


