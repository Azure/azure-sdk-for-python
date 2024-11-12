#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import re
import ast
import os
import jsondiff
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
from typing import Dict, Union, Type, Callable, Optional
from packaging_tools.venvtools import create_venv_with_package
from breaking_changes_allowlist import RUN_BREAKING_CHANGES_PACKAGES, IGNORE_BREAKING_CHANGES
from breaking_changes_tracker import BreakingChangesTracker
from changelog_tracker import ChangelogTracker
from pathlib import Path
from supported_checkers import CHECKERS

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
        elif hasattr(default_value, "value"):
            # Get the enum value
            if isinstance(default_value.value, object):
                # Accounting for enum values like: default = DefaultProfile()
                default_value = default_value.value.__class__.__name__
            else:
                default_value = default_value.value
        elif inspect.isfunction(default_value):
            default_value = default_value.__name__
        elif inspect.isclass(default_value):
            default_value = default_value.__name__
        elif hasattr(default_value, "__class__"):
            # Some default values are objects, e.g. _UNSET = object()
            default_value = default_value.__class__.__name__

    return default_value


def get_property_type(node: ast.AST) -> str:
    if hasattr(node, "value"):
        if isinstance(node.value, ast.Call):
            if hasattr(node.value.func, "id"):
                return node.value.func.id
            elif hasattr(node.value.func, "attr"):
                return node.value.func.attr
        elif isinstance(node.value, ast.Name):
            return node.value.id
        elif isinstance(node.value, ast.Constant):
            return node.value.value
    return None


def get_property_names(node: ast.AST, attribute_names: Dict) -> None:
    assign_nodes = [node for node in node.body if isinstance(node, ast.AnnAssign)]
    # Check for class level attributes that follow the pattern: foo: List["_models.FooItem"] = rest_field(name="foo")
    for assign in assign_nodes:
        if hasattr(assign, "target"):
            if hasattr(assign.target, "id") and not assign.target.id.startswith("_"):
                attr = assign.target.id
                attr_type = None
                # FIXME: This can get the type hint for a limited set attributes. We need to address more complex
                # type hints in the future.
                # Build type hint for the attribute
                if hasattr(assign.annotation, "value") and isinstance(assign.annotation.value, ast.Name):
                    attr_type = assign.annotation.value.id
                    if attr_type == "List" and hasattr(assign.annotation, "slice"):
                        if isinstance(assign.annotation.slice, ast.Constant):
                            attr_type = f"{attr_type}[{assign.annotation.slice.value}]"
                attribute_names.update({attr: attr_type})

    func_nodes = [node for node in node.body if isinstance(node, ast.FunctionDef)]
    if func_nodes:
        assigns = [node for node in func_nodes[0].body if isinstance(node, (ast.Assign, ast.AnnAssign))]
        if assigns:
            for assign in assigns:
                if hasattr(assign, "target"):
                    if hasattr(assign.target, "attr") and not assign.target.attr.startswith("_"):
                        attr = assign.target
                        attribute_names.update({attr.attr: {
                                "attr_type": get_property_type(assign)
                            }})
                if hasattr(assign, "targets"):
                    for target in assign.targets:
                        if hasattr(target, "attr") and not target.attr.startswith("_"):
                            attribute_names.update({target.attr: {
                                "attr_type": get_property_type(assign)
                            }})


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
    if cls_node.bases:
        should_look = True
    return should_look


def get_properties(cls: Type) -> Dict:
    """Get the public instance variables of the class and any inherited.

    :param cls:
    :return:
    """
    attribute_names = {}

    path = inspect.getsourcefile(cls)
    with open(path, "r", encoding="utf-8-sig") as source:
        module = ast.parse(source.read())

    analyzer = ClassTreeAnalyzer(cls.__name__)
    analyzer.visit(module)
    cls_node = analyzer.cls_node
    extract_base_classes = True if hasattr(cls_node, "bases") else False

    if extract_base_classes:
        base_classes = inspect.getmro(cls)  # includes cls itself
        for base_class in base_classes:
            try:
                path = inspect.getsourcefile(base_class)
                with open(path, "r", encoding="utf-8-sig") as source:
                    module = ast.parse(source.read())
            except (TypeError, SyntaxError):
                _LOGGER.info(f"Unable to create ast of {base_class}")
                continue  # was a built-in, e.g. "object", Exception, or a Model from msrest fails here

            analyzer = ClassTreeAnalyzer(base_class.__name__)
            analyzer.visit(module)
            cls_node = analyzer.cls_node
            if cls_node:
                get_property_names(cls_node, attribute_names)
            else:
                # Abstract base classes fail here, e.g. "collections.abc.MuttableMapping"
                _LOGGER.info(f"Unable to get class node for {base_class.__name__}. Skipping...")
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


def get_parameter_default_ast(default):
    if isinstance(default, ast.Constant):
        return default.value
    if isinstance(default, ast.Name):
        return default.id
    if isinstance(default, ast.Attribute):
        return default.attr
    return None


def get_parameter_type(annotation) -> str:
    if isinstance(annotation, ast.Name):
        return annotation.id
    if isinstance(annotation, ast.Attribute):
        return annotation.attr
    if isinstance(annotation, ast.Constant):
        if annotation.value is None:
            return "None"
        return annotation.value
    if isinstance(annotation, ast.Subscript):
        if isinstance(annotation.slice, tuple):
            # TODO handle multiple types in the subscript
            return get_parameter_type(annotation.value)
        return f"{get_parameter_type(annotation.value)}[{get_parameter_type(annotation.slice)}]"
    if isinstance(annotation, ast.Tuple):
        return ", ".join([get_parameter_type(el) for el in annotation.elts])
    return annotation


def create_parameters(args: ast.arg) -> Dict:
    params = {}
    if hasattr(args, "posonlyargs"):
        for arg in args.posonlyargs:
            # Initialize the function parameters
            params.update({arg.arg: {
                "type": get_parameter_type(arg.annotation),
                "default": None,
                "param_type": "positional_only"
            }})
    if hasattr(args, "args"):
        for arg in args.args:
            # Initialize the function parameters
            params.update({arg.arg: {
                "type": get_parameter_type(arg.annotation),
                "default": None,
                "param_type": "positional_or_keyword"
            }})
    # Range through the corresponding default values
    all_args = args.posonlyargs + args.args
    positional_defaults = [None] * (len(all_args) - len(args.defaults)) + args.defaults
    for arg, default in zip(all_args, positional_defaults):
        params[arg.arg]["default"] = get_parameter_default_ast(default)
    if hasattr(args, "vararg"):
        if args.vararg:
            params.update({args.vararg.arg: {
                "type": get_parameter_type(args.vararg.annotation),
                "default": None,
                "param_type": "var_positional"
            }})
    if hasattr(args, "kwonlyargs"):
        for arg in args.kwonlyargs:
            # Initialize the function parameters
            params.update({
                arg.arg: {
                    "type": get_parameter_type(arg.annotation),
                    "default": None,
                    "param_type": "keyword_only"
                }
            })
        # Range through the corresponding default values
        for i in range(len(args.kwonlyargs) - len(args.kw_defaults), len(args.kwonlyargs)):
            params[args.kwonlyargs[i].arg]["default"] = get_parameter_default_ast(args.kw_defaults[i])
    return params

def get_overloads(cls: Type, cls_methods: Dict):
    path = inspect.getsourcefile(cls)
    with open(path, "r", encoding="utf-8-sig") as source:
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
                with open(path, "r", encoding="utf-8-sig") as source:
                    module = ast.parse(source.read())
            except (TypeError, SyntaxError):
                _LOGGER.info(f"Unable to create ast of {base_class}")
                continue  # was a built-in, e.g. "object", Exception, or a Model from msrest fails here

            analyzer = ClassTreeAnalyzer(base_class.__name__)
            analyzer.visit(module)
            cls_node = analyzer.cls_node
            if cls_node:
                get_overload_data(cls_node, cls_methods)
            else:
                # Abstract base classes fail here, e.g. "collections.abc.MuttableMapping"
                _LOGGER.info(f"Unable to get class node for {base_class.__name__}. Skipping...")
    else:
        get_overload_data(cls_node, cls_methods)


def get_overload_data(node: ast.ClassDef, cls_methods: Dict) -> None:
    func_nodes = [node for node in node.body if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))]
    public_func_nodes = [func for func in func_nodes if not func.name.startswith("_") or func.name.startswith("__init__")]
    # Check for method overloads on a class
    for func in public_func_nodes:
        if func.name not in cls_methods:
            _LOGGER.debug(f"Skipping overloads check for method {func.name}.")
            continue
        if "overloads" not in cls_methods[func.name]:
            cls_methods[func.name]["overloads"] = []
        is_async = False
        if isinstance(func, ast.AsyncFunctionDef):
            is_async = True
        # method_overloads.update({func.name: {"parameters": {}, "is_async": False, "return_type": None}})
        for decorator in func.decorator_list:
            if hasattr(decorator, "id") and decorator.id == "overload":
                overload_report = {
                    "parameters": create_parameters(func.args),
                    "is_async": is_async,
                    "return_type": None
                }
                cls_methods[func.name]["overloads"].append(overload_report)


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
        try:
            # Some class level properties get picked up as methods. Try to get the method and skip if it fails.
            m = getattr(cls, method)
        except AttributeError:
            _LOGGER.info(f"Skipping method check for {method} on {cls}.")
            continue
    
        if inspect.isfunction(m) or inspect.ismethod(m):
            if inspect.iscoroutinefunction(m):
                async_func = True
            cls_info["methods"][method] = create_function_report(m, async_func)
    # Search for overloads
    get_overloads(cls, cls_info["methods"])
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


def test_compare_reports(pkg_dir: str, changelog: bool, source_report: str = "stable.json", target_report: str = "current.json") -> None:
    package_name = os.path.basename(pkg_dir)

    with open(os.path.join(pkg_dir, source_report), "r") as fd:
        stable = json.load(fd)
    with open(os.path.join(pkg_dir, target_report), "r") as fd:
        current = json.load(fd)

    if "azure-mgmt-" in package_name:
        stable = report_azure_mgmt_versioned_module(stable)
        current = report_azure_mgmt_versioned_module(current)

    checker = BreakingChangesTracker(
        stable,
        current,
        package_name,
        checkers = CHECKERS,
        ignore = IGNORE_BREAKING_CHANGES
    )
    if changelog:
        checker = ChangelogTracker(stable, current, package_name, checkers = CHECKERS, ignore = IGNORE_BREAKING_CHANGES)
    checker.run_checks()

    remove_json_files(pkg_dir)

    print(checker.report_changes())

    if not changelog and checker.breaking_changes:
        exit(1)


def remove_json_files(pkg_dir: str) -> None:
    stable_json = os.path.join(pkg_dir, "stable.json")
    current_json = os.path.join(pkg_dir, "current.json")
    if os.path.isfile(stable_json):
        os.remove(stable_json)
    if os.path.isfile(current_json):
        os.remove(current_json)
    _LOGGER.info("cleaning up")


def report_azure_mgmt_versioned_module(code_report):
    
    def parse_module_name(module):
        split_module = module.split(".")
        # Azure mgmt packages are typically in the form of: azure.mgmt.<service>
        # If the module has a version, it will be in the form of: azure.mgmt.<service>.<version> or azure.mgmt.<service>.<version>.<submodule>
        if len(split_module) >= 4:
            for i in range(3, len(split_module)):
                if re.search(r"v\d{4}_\d{2}_\d{2}", split_module[i]):
                    split_module.pop(i)
                    break
        return ".".join(split_module)

    sorted_modules = sorted(code_report.keys())
    merged_report = {}
    for module in sorted_modules:
        non_version_module_name = parse_module_name(module)
        if non_version_module_name not in merged_report:
            merged_report[non_version_module_name] = code_report[module]
            continue
        merged_report[non_version_module_name].update(code_report[module])
    return merged_report


def main(
        package_name: str,
        target_module: str,
        version: str,
        in_venv: Union[bool, str],
        pkg_dir: str,
        changelog: bool,
        code_report: bool,
        latest_pypi_version: bool,
        source_report: Optional[Path],
        target_report: Optional[Path]
    ):
    # If code_report is set, only generate a code report for the package and return
    if code_report:
        public_api = build_library_report(target_module)
        with open("code_report.json", "w") as fd:
            json.dump(public_api, fd, indent=2)
        _LOGGER.info("code_report.json is written.")
        return

    # If source_report and target_report are provided, compare the two reports
    if source_report and target_report:
        test_compare_reports(pkg_dir, changelog, str(source_report), str(target_report))
        return

    # For default behavior, find the latest stable version on PyPi
    if not version:

        from pypi_tools.pypi import PyPIClient
        client = PyPIClient()

        try:
            if latest_pypi_version:
                versions = client.get_ordered_versions(package_name)
                version = str(versions[-1])
            else:
                version = str(client.get_relevant_versions(package_name)[1])
        except IndexError:
            _LOGGER.warning(f"No revelant version for {package_name} on PyPi. Exiting...")
            exit(0)

    in_venv = True if in_venv == "true" else False  # subprocess sends back string so convert to bool

    if not in_venv:
        packages = [f"{package_name}=={version}", "jsondiff==1.2.0"]
        with create_venv_with_package(packages) as venv:
            subprocess.check_call(
                [
                    venv.env_exe,
                    "-m",
                    "pip",
                    "install",
                    "-r",
                    os.path.join(pkg_dir, "dev_requirements.txt")
                ]
            )
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

        test_compare_reports(pkg_dir, changelog)

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

    parser.add_argument(
        "-c",
        "--changelog",
        dest="changelog",
        help="Output changes listed in changelog format.",
        action="store_true",
        default=False,
    )

    parser.add_argument(
        "--code-report",
        dest="code_report",
        help="Output a code report for a package.",
        action="store_true",
        default=False,
    )

    parser.add_argument(
        "--source-report",
        dest="source_report",
        help="Path to the code report for the previous package version.",
    )

    parser.add_argument(
        "--target-report",
        dest="target_report",
        help="Path to the code report for the new package version.",
    )

    parser.add_argument(
        "--latest-pypi-version",
        dest="latest_pypi_version",
        help="Use the latest package version on PyPi (can be preview or stable).",
        action="store_true",
        default=False,
    )

    args, unknown = parser.parse_known_args()
    if unknown:
        _LOGGER.info(f"Ignoring unknown arguments: {unknown}")

    in_venv = args.in_venv
    stable_version = args.stable_version
    target_module = args.target_module
    pkg_dir = os.path.abspath(args.target_package)
    package_name = os.path.basename(pkg_dir)
    changelog = args.changelog
    logging.basicConfig(level=logging.INFO)

    # We dont need to block for code report generation
    if not args.code_report:
        if package_name not in RUN_BREAKING_CHANGES_PACKAGES and not any(bool(re.findall(p, package_name)) for p in RUN_BREAKING_CHANGES_PACKAGES):
            _LOGGER.info(f"{package_name} opted out of breaking changes checks. "
                        f"See http://aka.ms/azsdk/breaking-changes-tool to opt-in.")
            exit(0)

    if not target_module:
        from ci_tools.parsing import ParsedSetup
        pkg_details = ParsedSetup.from_path(pkg_dir)
        target_module = pkg_details.namespace

    if args.source_report:
        if not args.target_report:
            _LOGGER.exception("If providing the `--source-report` flag, the `--target-report` flag is also required.")
            exit(1)
    if args.target_report:
        if not args.source_report:
            _LOGGER.exception("If providing the `--target-report` flag, the `--source-report` flag is also required.")
            exit(1)

    main(package_name, target_module, stable_version, in_venv, pkg_dir, changelog, args.code_report, args.latest_pypi_version, args.source_report, args.target_report)
