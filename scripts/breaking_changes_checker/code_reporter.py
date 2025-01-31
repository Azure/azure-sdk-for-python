#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import ast
import os
import importlib
import inspect
import json
import json
import ast
import logging
import inspect
import subprocess
from enum import Enum
from typing import Any, Dict, Type, Callable, Optional
from ci_tools.parsing import ParsedSetup
from packaging_tools.venvtools import create_venv_with_package

_LOGGER = logging.getLogger(__name__)

class CodeReporter:
    def __init__(
            self,
            pkg_dir: str,
            **kwargs
        ):
        self.pkg_dir = pkg_dir
        self.in_venv = kwargs.get("in_venv", False)
        self.pkg_name = kwargs.get("pkg_name", None)
        self.target_module = kwargs.get("target_module", None)
        try:
            self.pkg_details = ParsedSetup.from_path(self.pkg_dir)
            # The package name may not be set, so we need to populate the value from the setup.py
            self.pkg_name = self.pkg_name or self.pkg_details.name
            # The target module may not be set, so we need to populate the value from the setup.py
            self.target_module = self.target_module or self.pkg_details.namespace
        except:
            _LOGGER.warning(f"Unable to parse setup.py in {pkg_dir}. If the pkg_dir is incorrect or if pkg_name and target_module aren't specified this can result in unexpected failures.")
        # Must have the pkg_name assigned correctly, before attempting to get the pkg_version
        self.pkg_version = kwargs.get("pkg_version", None) or self._check_version(kwargs.get("latest_pypi_version", False))

    def report(self) -> None:
        """Creates a stable_report.json and a current_report.json for the target package.
        """
        if not self.in_venv:
            packages = [f"{self.pkg_name}=={self.pkg_version}", "jsondiff==1.2.0"]
            with create_venv_with_package(packages) as venv:
                subprocess.check_call(
                    [
                        venv.env_exe,
                        "-m",
                        "pip",
                        "install",
                        "-r",
                        os.path.join(self.pkg_dir, "dev_requirements.txt")
                    ]
                )
                _LOGGER.info(f"Installed version {self.pkg_version} of {self.pkg_name} in a venv")
                args = [
                    venv.env_exe,
                    __file__,
                    "-t",
                    self.pkg_name,
                    "-m",
                    self.target_module,
                    "--in-venv",
                    "true",
                    "-s",
                    self.pkg_version
                ]
                try:
                    self._find_installed_source_package(self.pkg_name, venv.env_dir)
                    return
                except subprocess.CalledProcessError:
                    _LOGGER.warning(f"Version {self.pkg_version} failed to create a JSON report.")
                    exit(1)

        public_api = self.build_library_report()

        with open("current.json", "w") as fd:
            json.dump(public_api, fd, indent=2)
        _LOGGER.info("current.json is written.")

    def _find_installed_source_package(self, pkg_name: str, venv_path: str):
        import importlib.util
        import sys
        from pathlib import Path

        pkg_name = pkg_name.replace("-", ".")

        # Save the original sys.path
        original_sys_path = sys.path.copy()
        
        # Determine the site-packages path based on the operating system
        if sys.platform == 'win32':
            site_packages_path = Path(venv_path) / 'Lib' / 'site-packages'
        else:
            site_packages_path = Path(venv_path) / 'lib' / f'python{sys.version_info.major}.{sys.version_info.minor}' / 'site-packages'
        
        # Add the virtual environment's site-packages directory to sys.path
        sys.path.insert(0, str(site_packages_path))
        
        # Check if the package is installed
        package_spec = importlib.util.find_spec(pkg_name)
        if not package_spec:
            _LOGGER.warning(f"Version {self.pkg_version} of {self.pkg_name} not found in the virtual environment.")
            exit(1)

        source_reporter = CodeReporter(os.path.dirname(package_spec.origin), pkg_name=self.pkg_name, target_module=self.target_module, in_venv=True, pkg_version=self.pkg_version)
        
        public_api = source_reporter.build_library_report()
        with open("stable.json", "w") as fd:
            json.dump(public_api, fd, indent=2)
        _LOGGER.info("stable.json is written.")

        # Restore the original sys.path
        sys.path = original_sys_path

    def build_library_report(self) -> Dict:
        module = importlib.import_module(self.target_module)
        modules = self._find_modules(module.__path__[0])

        public_api = {}
        for module_name, val in modules.items():
            module_name = self._resolve_module_name(module_name, self.target_module)
            public_api[module_name] = {"class_nodes": {}, "function_nodes": {}}
            module = importlib.import_module(module_name)
            importables = [importable for importable in dir(module)]
            for importable in importables:
                if not importable.startswith("_"):
                    live_obj = getattr(module, importable)
                    if inspect.isfunction(live_obj):
                        public_api[module_name]["function_nodes"].update({importable: self._create_function_report(live_obj)})
                    elif inspect.isclass(live_obj):
                        public_api[module_name]["class_nodes"].update({importable: self._create_class_report(live_obj)})
                    # else:  # Constants, version, etc. Nothing of interest at the moment
                    #     public_api[module_name]["others"].update({importable: live_obj})

        return public_api



    def _resolve_module_name(self, module_name: str, target_module: str) -> str:
        if module_name == ".":
            module_name = target_module
        else:
            module_name = target_module + "." + module_name
        return module_name


    def _find_modules(self, pkg_root_path: str) -> Dict:
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

    def _check_version(self, latest_pypi_version: Optional[bool]) -> str:
        # For default behavior, find the latest stable version on PyPi
        from pypi_tools.pypi import PyPIClient
        client = PyPIClient()

        try:
            if latest_pypi_version:
                versions = client.get_ordered_versions(self.pkg_name)
                version = str(versions[-1])
            else:
                version = str(client.get_relevant_versions(self.pkg_name)[1])
        except IndexError:
            _LOGGER.warning(f"No revelant version for {self.pkg_name} on PyPi. Exiting...")
            exit(0)
        return version


    def _get_parameter_default(self, param: inspect.Parameter):
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


    def _get_property_type(self, node: ast.AST):
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


    def _get_property_names(self, node: ast.AST, attribute_names: Dict) -> None:
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
                                    "attr_type": self._get_property_type(assign)
                                }})
                    if hasattr(assign, "targets"):
                        for target in assign.targets:
                            if hasattr(target, "attr") and not target.attr.startswith("_"):
                                attribute_names.update({target.attr: {
                                    "attr_type": self._get_property_type(assign)
                                }})


    def _check_base_classes(self, cls_node: ast.ClassDef) -> bool:
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


    def _get_properties(self, cls: Type) -> Dict:
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
                    self._get_property_names(cls_node, attribute_names)
                else:
                    # Abstract base classes fail here, e.g. "collections.abc.MuttableMapping"
                    _LOGGER.info(f"Unable to get class node for {base_class.__name__}. Skipping...")
        else:
            self._get_property_names(cls_node, attribute_names)
        return attribute_names


    def _create_function_report(self, f: Callable, is_async: bool = False) -> Dict:
        function = inspect.signature(f)
        func_obj = {
            "parameters": {},
            "is_async": is_async
        }

        for par in function.parameters.values():
            default_value = self._get_parameter_default(par)
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


    def _get_parameter_default_ast(self, default):
        if isinstance(default, ast.Constant):
            return default.value
        if isinstance(default, ast.Name):
            return default.id
        if isinstance(default, ast.Attribute):
            return default.attr
        return None


    def _get_parameter_type(self, annotation) -> str:
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
                return self._get_parameter_type(annotation.value)
            return f"{self._get_parameter_type(annotation.value)}[{self._get_parameter_type(annotation.slice)}]"
        if isinstance(annotation, ast.Tuple):
            return ", ".join([self._get_parameter_type(el) for el in annotation.elts])
        return annotation


    def _create_parameters(self, args: ast.arg) -> Dict:
        params = {}
        if hasattr(args, "posonlyargs"):
            for arg in args.posonlyargs:
                # Initialize the function parameters
                params.update({arg.arg: {
                    "type": self._get_parameter_type(arg.annotation),
                    "default": None,
                    "param_type": "positional_only"
                }})
        if hasattr(args, "args"):
            for arg in args.args:
                # Initialize the function parameters
                params.update({arg.arg: {
                    "type": self._get_parameter_type(arg.annotation),
                    "default": None,
                    "param_type": "positional_or_keyword"
                }})
        # Range through the corresponding default values
        all_args = args.posonlyargs + args.args
        positional_defaults = [None] * (len(all_args) - len(args.defaults)) + args.defaults
        for arg, default in zip(all_args, positional_defaults):
            params[arg.arg]["default"] = self._get_parameter_default_ast(default)
        if hasattr(args, "vararg"):
            if args.vararg:
                params.update({args.vararg.arg: {
                    "type": self._get_parameter_type(args.vararg.annotation),
                    "default": None,
                    "param_type": "var_positional"
                }})
        if hasattr(args, "kwonlyargs"):
            for arg in args.kwonlyargs:
                # Initialize the function parameters
                params.update({
                    arg.arg: {
                        "type": self._get_parameter_type(arg.annotation),
                        "default": None,
                        "param_type": "keyword_only"
                    }
                })
            # Range through the corresponding default values
            for i in range(len(args.kwonlyargs) - len(args.kw_defaults), len(args.kwonlyargs)):
                params[args.kwonlyargs[i].arg]["default"] = self._get_parameter_default_ast(args.kw_defaults[i])
        return params

    def _get_overloads(self, cls: Type, cls_methods: Dict):
        path = inspect.getsourcefile(cls)
        with open(path, "r", encoding="utf-8-sig") as source:
            module = ast.parse(source.read())

        analyzer = ClassTreeAnalyzer(cls.__name__)
        analyzer.visit(module)
        cls_node = analyzer.cls_node
        extract_base_classes = self._check_base_classes(cls_node)

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
                    self._get_overload_data(cls_node, cls_methods)
                else:
                    # Abstract base classes fail here, e.g. "collections.abc.MuttableMapping"
                    _LOGGER.info(f"Unable to get class node for {base_class.__name__}. Skipping...")
        else:
            self._get_overload_data(cls_node, cls_methods)


    def _get_overload_data(self, node: ast.ClassDef, cls_methods: Dict) -> None:
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
                        "parameters": self._create_parameters(func.args),
                        "is_async": is_async,
                        "return_type": None
                    }
                    cls_methods[func.name]["overloads"].append(overload_report)


    def _create_class_report(self, cls: Type) -> Dict:
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

        cls_info["properties"] = self._get_properties(cls)

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
                cls_info["methods"][method] = self._create_function_report(m, async_func)
        # Search for overloads
        self._get_overloads(cls, cls_info["methods"])
        return cls_info


class ClassTreeAnalyzer(ast.NodeVisitor):
    def __init__(self, name: str) -> None:
        self.name = name
        self.cls_node = None

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        if node.name == self.name:
            self.cls_node = node
        self.generic_visit(node)
