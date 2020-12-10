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
from tox_helper_tasks import get_package_details
try:
    # won't be able to import these in the created venv
    from packaging_tools.venvtools import create_venv_with_package
    import jsondiff
except (ModuleNotFoundError, ImportError) as e:
    pass


root_dir = os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "..", ".."))
_LOGGER = logging.getLogger(__name__)


class BreakingChangeType(str, enum.Enum):
    REMOVE_OR_RENAME_CLIENT = "RemoveOrRenameClient"
    REMOVE_OR_RENAME_CLIENT_METHOD = "RemoveOrRenameClientMethod"
    REMOVE_OR_RENAME_MODEL = "RemoveOrRenameModel"
    REMOVE_OR_RENAME_MODULE_LEVEL_FUNCTION = "RemoveOrRenameModuleLevelFunction"
    REMOVE_OR_RENAME_POSITIONAL_PARAM = "RemoveOrRenamePositionalParam"
    ADDED_POSITIONAL_PARAM = "AddedPositionalParam"
    REMOVE_OR_RENAME_INSTANCE_ATTRIBUTE_FROM_MODEL = "RemoveOrRenameInstanceAttributeFromModel"


class ClassDefTree(ast.NodeVisitor):
    def __init__(self, name):
        self.name = name
        self.cls_node = None

    def visit_ClassDef(self, node):
        if node.name == self.name:
            self.cls_node = node
        self.generic_visit(node)


def test_find_modules(pkg_root_path):
    """Find modules within the package to import and parse.
    Code borrowed and edited from APIview.

    :param str: pkg_root_path
        Package root path
    :rtype: dict
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

    logging.debug("Modules in package: {}".format(modules))
    return modules


def create_function_report(name, f):
    function = inspect.signature(f)
    func_obj = {
        "name": name,
        "ignore": False,
        "parameters": {
            "positional_only": {},
            "positional_or_keyword": {},
            "keyword_only": {},
            "var_positional": {},
            "var_keyword": {}
        }
    }
    # TODO add ignore / metadata
    # source_lines = inspect.getsourcelines(f)[0]
    # if source_lines[0].find("ignore") != -1 and source_lines[0].find("breaking-changes") != -1:
    #     func_obj["ignore"] = True
    #     return func_obj

    # TODO we could capture whether the param has a default value and if that changes
    for par in function.parameters.values():
        if par.kind == par.KEYWORD_ONLY:
            func_obj["parameters"]["keyword_only"].update({par.name: par.name})
        if par.kind == par.POSITIONAL_ONLY:
            func_obj["parameters"]["positional_only"].update({par.name: par.name})
        if par.kind == par.POSITIONAL_OR_KEYWORD:
            func_obj["parameters"]["positional_or_keyword"].update({par.name: par.name})
        if par.kind == par.VAR_POSITIONAL:
            func_obj["parameters"]["var_positional"].update({par.name: par.name})
        if par.kind == par.VAR_KEYWORD:
            func_obj["parameters"]["var_keyword"].update({par.name: par.name})

    return func_obj


def get_properties(cls):

    base_classes = inspect.getmro(cls)

    attribute_names = {}
    for klass in base_classes:
        try:
            path = inspect.getsourcefile(klass)
            if path.find("azure") == -1:
                continue
            with open(path, "r") as source:
                module = ast.parse(source.read())
        except (TypeError, SyntaxError):
            continue  # was a built-in, e.g. "object" or a Model from msrest fails here

        analyzer = ClassDefTree(klass.__name__)
        analyzer.visit(module)
        cls_node = analyzer.cls_node

        init_node = [node for node in cls_node.body if isinstance(node, ast.FunctionDef)]
        if init_node:
            assigns = [node for node in init_node[0].body if isinstance(node, ast.Assign)]
            if assigns:
                for assign in assigns:
                    if hasattr(assign, "targets"):
                        for attr in assign.targets:
                            if hasattr(attr, "attr") and not attr.attr.startswith("_"):
                                attribute_names.update({attr.attr: attr.attr})
    return attribute_names


def create_class_report(name, cls):
    cls_info = {
        "name": name,
        "type": None,
        "methods": {},
        "properties": {},
        "metadata": {
            "ignore": False,
            "lineno": None,
            "path": None,
        }
    }

    source_line = inspect.getsourcelines(cls)
    cls_info["metadata"]["lineno"] = source_line[1]
    lines = source_line[0]
    if lines[0].find("ignore") != -1 and lines[0].find("breaking-changes") != -1:
        cls_info["metadata"]["ignore"] = True
        return cls_info

    is_enum = Enum in cls.__mro__
    if is_enum:
        cls_info["type"] = "Enum"
        cls_info["properties"] = {value: value for value in dir(cls) if not value.startswith("_")}
        return cls_info

    path = inspect.getsourcefile(cls)
    cls_info["metadata"]["path"] = path
    cls_info["properties"] = get_properties(cls)

    methods = [method for method in dir(cls) if not method.startswith("_")]
    for method in methods:
        m = getattr(cls, method)
        if inspect.isfunction(m):
            cls_info["methods"][method] = create_function_report(method, m)

    cls_init = getattr(cls, "__init__")
    cls_info["methods"]["__init__"] = create_function_report("__init__", cls_init)

    return cls_info


def test_detect_breaking_changes(target_module="azure.storage.blob"):

    module = importlib.import_module(target_module)
    modules = test_find_modules(module.__path__[0])

    public_api = {}
    for module_name, val in modules.items():
        if module_name == ".":
            module_name = target_module
        else:
            module_name = target_module + "." + module_name

        public_api[module_name] = {"class_nodes": {}, "function_nodes": {}}
        module = importlib.import_module(module_name)
        importables = [importable for importable in dir(module)]
        for importable in importables:
            if not importable.startswith("_"):
                live_obj = getattr(module, importable)
                if inspect.isfunction(live_obj):
                    public_api[module_name]["function_nodes"].update({importable: create_function_report(importable, live_obj)})
                elif inspect.isclass(live_obj):
                    public_api[module_name]["class_nodes"].update({importable: create_class_report(importable, live_obj)})
                # else:  # Constants, etc. Too much of an issue / not JSON serializable
                #     public_api[module_name]["others"].update({importable: live_obj})

    return public_api


class BreakingChange:

    def __init__(self, **kwargs):
        self.line_number = kwargs.get("line_number")
        self.file_name = kwargs.get("file_name")
        self.breaking_change_type = kwargs.get("breaking_change_type")
        self.message = kwargs.get("message")
        self.ignore = kwargs.get("ignore", False)

    def __str__(self):
        return self.message


class BreakingChangesTracker:
    
    def __init__(self, stable, current, diff):
        self.stable = stable
        self.current = current
        self.diff = diff
        self.breaking_changes = []

    def run_checks(self):
        self.run_class_level_checks()
        self.run_function_level_checks()

    def run_class_level_checks(self):
        for module_name, module in self.diff.items():
            for class_name, components in module.get("class_nodes", {}).items():
                if class_name not in self.stable[module_name]["class_nodes"] and \
                        not isinstance(class_name, jsondiff.Symbol):
                    continue  # this is a new model/additive change in current version so skip checks
                self.class_instance_attribute_removed_or_renamed(module_name, class_name, components)
                self.class_removed_or_renamed(module_name, class_name, components)

                for method_name, props in components.get("methods", {}).items():
                    if method_name not in self.stable[module_name]["class_nodes"][class_name]["methods"] and \
                            not isinstance(method_name, jsondiff.Symbol):
                        continue  # this is a new method/additive change in current version so skip checks
                    for param_type, param_name in props.get("parameters", {}).items():
                        if param_type == "positional_or_keyword":
                            self.class_method_positional_parameter_added(
                                class_name, param_name, param_type, method_name
                            )
                            self.class_method_positional_parameter_removed_or_renamed(
                                module_name, class_name, param_name, param_type, props, method_name
                            )

    def run_function_level_checks(self):
        for module_name, module in self.diff.items():
            for function_name, components in module.get("function_nodes", {}).items():
                if function_name not in self.stable[module_name]["function_nodes"] and \
                        not isinstance(function_name, jsondiff.Symbol):
                    continue  # this is a new function/additive change in current version so skip checks
                self.module_level_function_removed_or_renamed(module_name, function_name, components)

    def module_level_function_removed_or_renamed(self, module_name, function_name, components):
        if isinstance(function_name, jsondiff.Symbol):
            if function_name.label == "delete":
                for function in components:
                    bc = BreakingChange(
                        breaking_change_type=BreakingChangeType.REMOVE_OR_RENAME_MODULE_LEVEL_FUNCTION,
                        message=f"The publicly exposed function '{function}' was deleted or renamed in the current version"
                    )
                    self.breaking_changes.append(bc)
            elif function_name.label == "replace":
                self.report_replacement(replacement_type="function_nodes", module_name=module_name)

    def class_instance_attribute_removed_or_renamed(self, module_name, class_name, components):
        for prop in components.get("properties", []):
            if isinstance(prop, jsondiff.Symbol):
                if prop.label == "delete":
                    deleted_prop = components["properties"][prop]
                    for property in deleted_prop:
                        if property.endswith("Client"):
                            bc = BreakingChange(
                                breaking_change_type=BreakingChangeType.REMOVE_OR_RENAME_INSTANCE_ATTRIBUTE_FROM_CLIENT,
                                message=f"The '{class_name}' had its instance variable "
                                        f"'{property}' deleted or renamed in the current version"
                            )
                        else:
                            bc = BreakingChange(
                                breaking_change_type=BreakingChangeType.REMOVE_OR_RENAME_INSTANCE_ATTRIBUTE_FROM_MODEL,
                                message=f"The model or publicly exposed class '{class_name}' had its instance variable "
                                        f"'{property}' deleted or renamed in the current version"
                            )
                        self.breaking_changes.append(bc)
                elif prop.label == "replace":
                    self.report_replacement(replacement_type="properties", module_name=module_name, class_name=class_name)

    def class_removed_or_renamed(self, module_name, model_name, components):
        if isinstance(model_name, jsondiff.Symbol):
            if model_name.label == "delete":
                for name in components:
                    if name.endswith("Client"):
                        bc = BreakingChange(
                            breaking_change_type=BreakingChangeType.REMOVE_OR_RENAME_CLIENT,
                            message=f"The client {name} was deleted or renamed in the current version"
                        )
                    else:
                        bc = BreakingChange(
                            breaking_change_type=BreakingChangeType.REMOVE_OR_RENAME_MODEL,
                            message=f"The model or publicly exposed class '{name}' was deleted or renamed in the "
                                    f"current version",
                        )
                    self.breaking_changes.append(bc)
            elif model_name.label == "replace":
                self.report_replacement(replacement_type="class_nodes", module_name=module_name)

    def class_method_positional_parameter_added(self, class_name, param_name, param_type, method_name):
        for param in param_name:
            if not isinstance(param, jsondiff.Symbol):
                bc = BreakingChange(
                    breaking_change_type=BreakingChangeType.ADDED_POSITIONAL_PARAM,
                    message=f"The '{class_name} method '{method_name}' had a {param_type} parameter "
                            f"'{param}' inserted in the current version"
                )
                self.breaking_changes.append(bc)

    def class_method_positional_parameter_removed_or_renamed(self, module_name, class_name, param_name, param_type, props, method_name):
        for param in param_name:
            if isinstance(param, jsondiff.Symbol):
                if param.label == "delete":
                    deleted_param = props["parameters"][param_type][param]
                    for deleted in deleted_param:
                        if deleted != "self":
                            bc = BreakingChange(
                                breaking_change_type=BreakingChangeType.REMOVE_OR_RENAME_POSITIONAL_PARAM,
                                message=f"The '{class_name} method '{method_name}' had its {param_type} parameter "
                                        f"'{deleted}' deleted or renamed in the current version"
                            )
                            self.breaking_changes.append(bc)
                elif param.label == "replace":
                    self.report_replacement(
                        replacement_type="parameters",
                        module_name=module_name,
                        class_name=class_name,
                        method_name=method_name,
                        param_type=param_type
                    )

    def class_method_removed_or_renamed(self, module_name, class_name, components):
        for method_name, props in components.get("methods", {}).items():
            if isinstance(method_name, jsondiff.Symbol):
                if method_name.label == "delete":
                    for name in props:
                        if name.endswith("Client"):
                            bc = BreakingChange(
                                breaking_change_type=BreakingChangeType.REMOVE_OR_RENAME_CLIENT_METHOD,
                                message=f"The '{class_name}' method '{name}' was deleted or renamed in the current "
                                        f"version",
                            )
                        else:
                            bc = BreakingChange(
                                breaking_change_type=BreakingChangeType.REMOVE_OR_RENAME_CLASS_METHOD,
                                message=f"The '{class_name}' method '{name}' was deleted or renamed in the current "
                                        f"version",
                            )
                        self.breaking_changes.append(bc)
                elif method_name.label == "replace":
                    self.report_replacement(replacement_type="methods", module_name=module_name, class_name=class_name)

    def report_replacement(self, replacement_type, **kwargs):
        """A replacement occurs when all of an importable type or component (e.g. class, function, parameter)
        is removed in the current version. This shouldn't ever happen, but we should check anyway.
        """
        module_name = kwargs.get("module_name")

        if replacement_type == "class_nodes":
            for cls in self.stable[module_name]["class_nodes"]:
                bc = BreakingChange(
                    breaking_change_type=BreakingChangeType.REMOVE_OR_RENAME_MODEL,
                    message=f"The model or publicly exposed class '{cls}' was deleted or renamed in the "
                            f"current version",
                )
                self.breaking_changes.append(bc)

        elif replacement_type == "function_nodes":
            for function in self.stable[module_name]["function_nodes"]:
                bc = BreakingChange(
                    breaking_change_type=BreakingChangeType.REMOVE_OR_RENAME_MODULE_LEVEL_FUNCTION,
                    message=f"The publicly exposed function '{function}' was deleted or renamed in the current version"
                )
                self.breaking_changes.append(bc)

        elif replacement_type == "properties":
            class_name = kwargs.get("class_name")
            for prop in self.stable[module_name]["class_nodes"][class_name]["properties"]:
                bc = BreakingChange(
                    breaking_change_type=BreakingChangeType.REMOVE_OR_RENAME_INSTANCE_ATTRIBUTE_FROM_MODEL,
                    message=f"The model or publicly exposed class '{class_name}' had its instance variable "
                            f"'{prop}' deleted or renamed in the current version"
                )
                self.breaking_changes.append(bc)

        elif replacement_type == "parameters":
            method_name = kwargs.get("method_name")
            param_type = kwargs.get("param_type")
            class_name = kwargs.get("class_name")
            for p in self.stable[module_name]["class_nodes"][class_name]["methods"][method_name]["parameters"][param_type]:
                if p != "self":
                    bc = BreakingChange(
                        breaking_change_type=BreakingChangeType.REMOVE_OR_RENAME_POSITIONAL_PARAM,
                        message=f"The '{class_name} method '{method_name}' had its {param_type} parameter "
                                f"'{p}' deleted or renamed in the current version"
                    )
                    self.breaking_changes.append(bc)

        elif replacement_type == "methods":
            class_name = kwargs.get("class_name")
            for method in self.stable[module_name]["class_nodes"][class_name]["methods"]:
                bc = BreakingChange(
                    breaking_change_type=BreakingChangeType.REMOVE_OR_RENAME_CLIENT_METHOD,
                    message=f"The '{class_name}' method '{method}' was deleted or renamed in the current "
                            f"version",
                )
                self.breaking_changes.append(bc)

# "C:\\Users\\krpratic\\azure-sdk-for-python\\sdk\\formrecognizer\\azure-ai-formrecognizer"
def test_compare(pkg_dir="C:\\Users\\krpratic\\azure-sdk-for-python\\sdk\\formrecognizer\\azure-ai-formrecognizer"):

    with open(os.path.join(pkg_dir, "stable.json"), "r") as fd:
        stable = json.load(fd)
    with open(os.path.join(pkg_dir, "current.json"), "r") as fd:
        current = json.load(fd)
    diff = jsondiff.diff(stable, current)

    bc = BreakingChangesTracker(stable, current, diff)
    bc.run_checks()

    print([change.message for change in bc.breaking_changes])


def main(package_name, target_module, version, create_venv, pkg_dir):
    if create_venv == "False":
        create_venv = False
    else:
        create_venv = True

    if create_venv:
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
                "--create-venv",
                "False",
                "-s",
                version
            ]
            try:
                subprocess.check_call(args)
            except subprocess.CalledProcessError:
                # If it fail, just assume this version is too old to get an Autorest report
                _LOGGER.warning(f"Version {version} seems to be too old to build a report (probably not Autorest based)")

    public_api = test_detect_breaking_changes(target_module)

    if create_venv is False:
        with open("stable.json", "w") as fd:
            json.dump(public_api, fd, indent=2)
        return

    with open("current.json", "w") as fd:
        json.dump(public_api, fd, indent=2)

    # test_compare(pkg_dir)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run pylint against target folder. Add a local custom plugin to the path prior to execution. "
    )

    parser.add_argument(
        "-t",
        "--target",
        dest="target_package",
        help="The target package directory on disk. The target module passed to pylint will be <target_package>/azure.",
        required=True,
    )

    parser.add_argument(
        "-m",
        "--module",
        dest="target_module",
        help="The target package directory on disk. The target module passed to pylint will be <target_package>/azure.",
    )

    parser.add_argument(
        "-v",
        "--create-venv",
        dest="create_env",
        help="The target package directory on disk. The target module passed to pylint will be <target_package>/azure.",
        default=True
    )

    parser.add_argument(
        "-s",
        "--stable_version",
        dest="stable_version",
        help="The target package directory on disk. The target module passed to pylint will be <target_package>/azure.",
        default=None
    )

    args = parser.parse_args()
    _LOGGER.warning(f"target package {args.target_package}")
    pkg_dir = os.path.abspath(args.target_package)
    _LOGGER.warning(f"package dir {pkg_dir}")
    if args.target_package == ".":
        package_name, target_module, ver = get_package_details(os.path.join(pkg_dir, "setup.py"))
    else:
        package_name, target_module, ver = get_package_details(os.path.join(pkg_dir, "..", "setup.py"))
    create_env = args.create_env
    stable_version = args.stable_version
    if not stable_version:

        from pypi_tools.pypi import PyPIClient
        client = PyPIClient()

        try:
            stable_version = str(client.get_relevant_versions(package_name)[1])
        except IndexError:
            _LOGGER.warning(f"No stable version for {package_name} on PyPi. Exiting...")
            exit(0)

    main(package_name, target_module, stable_version, create_env, pkg_dir)


