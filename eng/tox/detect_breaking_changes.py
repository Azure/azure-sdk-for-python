import ast
import os
import enum
import argparse
import importlib
import inspect
import json
import logging
import inspect
import subprocess
from tox_helper_tasks import get_package_details
try:
    # If I'm started as a module __main__
    from packaging_tools.venvtools import create_venv_with_package
except (ModuleNotFoundError, ImportError) as e:
    # If I'm started by my main directly
    pass



root_dir = os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "..", ".."))
tmpdir = "temp"


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
    """Find modules within the package to import and parse
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
            "positional_only": [],
            "positional_or_keyword": [],
            "keyword_only": [],
            "var_positional": [],
            "var_keyword": []
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
            func_obj["parameters"]["keyword_only"].append(par.name)
        if par.kind == par.POSITIONAL_ONLY:
            func_obj["parameters"]["positional_only"].append(par.name)
        if par.kind == par.POSITIONAL_OR_KEYWORD:
            func_obj["parameters"]["positional_or_keyword"].append(par.name)
        if par.kind == par.VAR_POSITIONAL:
            func_obj["parameters"]["var_positional"].append(par.name)
        if par.kind == par.VAR_KEYWORD:
            func_obj["parameters"]["var_keyword"].append(par.name)

    return func_obj


def get_properties(name, cls, path):
    # this only looks at the constructor of the class passed in. if there is a base class it is missed
    import ast

    with open(path, "r") as source:
        module = ast.parse(source.read())

    analyzer = ClassDefTree(name)
    analyzer.visit(module)
    cls_node = analyzer.cls_node
    attribute_names = []
    init_node = [node for node in cls_node.body if isinstance(node, ast.FunctionDef) and node.name == "__init__"]
    if init_node:
        assigns = [node for node in init_node[0].body if isinstance(node, ast.Assign)]
        if assigns:
            for assign in assigns:
                if hasattr(assign, "targets"):
                    for attr in assign.targets:
                        if hasattr(attr, "attr"):
                            attribute_names.append(attr.attr)
    return attribute_names


def create_class_report(name, cls):
    # print(cls)
    cls_info = {
        "name": name,
        "type": None,
        "methods": {},
        "properties": [],
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

    from enum import Enum
    is_enum = Enum in cls.__mro__
    if is_enum:
        cls_info["type"] = "Enum"
        cls_info["properties"] = [value for value in dir(cls) if not value.startswith("_")]
        return cls_info


    path = inspect.getsourcefile(cls)
    cls_info["metadata"]["path"] = path
    class_attributes = get_properties(name, cls, path)
    if class_attributes:
        cls_info["properties"] = class_attributes
    # try:
    #     props = list(cls.__init__.__code__.co_names)
    #     cls_info["properties"] = [prop for prop in props if not prop.startswith("_")]
    # except AttributeError:
    #     cls_info["properties"] = [value for value in dir(cls) if not value.startswith("_")]

    methods = [method for method in dir(cls) if not method.startswith("_")]
    for method in methods:
        m = getattr(cls, method)
        if inspect.isfunction(m):
            method_info = create_function_report(method, m)
            cls_info["methods"][method] = method_info

    cls_init = getattr(cls, "__init__")
    init = create_function_report("__init__", cls_init)
    cls_info["methods"]["__init__"] = init

    return cls_info


def test_detect_breaking_changes(package_name, target_module, current):

    module = importlib.import_module(target_module)
    modules = test_find_modules(module.__path__[0])

    public_api = {}
    for module_name, val in modules.items():
        if module_name == ".":
            module_name = target_module
        else:
            module_name = target_module + "." + module_name

        public_api[module_name] = {"class_nodes": {}, "clients": {}, "function_nodes": {}}
        module = importlib.import_module(module_name)
        model_names = [model_name for model_name in dir(module)]
        for model_name in model_names:
            if not model_name.startswith("_"):
                thing = getattr(module, model_name)
                if inspect.isfunction(thing):
                    public_api[module_name]["function_nodes"].update({model_name: create_function_report(model_name, thing)})
                elif inspect.isclass(thing) and model_name.endswith("Client"):
                    public_api[module_name]["clients"].update({model_name: create_class_report(model_name, thing)})
                elif inspect.isclass(thing):
                    public_api[module_name]["class_nodes"].update({model_name: create_class_report(model_name, thing)})

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


def model_or_exposed_class_instance_attribute_removed_or_renamed(stable, current, diff, breaking_changes):
    from jsondiff.symbols import Symbol
    for module_name, module in diff.items():
        if "class_nodes" in module:
            for model_name, components in module["class_nodes"].items():
                deleted_indices = []
                if "properties" in components:
                    for prop in components["properties"]:
                        if isinstance(prop, Symbol):
                            if prop.label == "delete":
                                deleted_indices = components["properties"][prop]
                if deleted_indices:
                    for deleted_idx in deleted_indices:
                        deleted_property = stable[module_name]["class_nodes"][model_name]["properties"][deleted_idx]
                        bc = BreakingChange(
                            breaking_change_type=BreakingChangeType.REMOVE_OR_RENAME_INSTANCE_ATTRIBUTE_FROM_MODEL,
                            message=f"The model or publicly exposed class '{model_name}' had its instance variable "
                                    f"'{deleted_property}' deleted or renamed in the current version"
                        )
                        breaking_changes.append(bc)


def model_or_exposed_class_removed_or_renamed(stable, current, diff, breaking_changes):
    from jsondiff.symbols import Symbol
    for module_name, module in diff.items():
        if "class_nodes" in module:
            for model_name, components in module["class_nodes"].items():
                if isinstance(model_name, Symbol):
                    if model_name.label == "delete":
                        for name in components:
                            bc = BreakingChange(
                                breaking_change_type=BreakingChangeType.REMOVE_OR_RENAME_MODEL,
                                message=f"The model or publicly exposed class '{name}' was deleted or renamed in the "
                                        f"current version",
                            )
                            breaking_changes.append(bc)


def client_method_removed_or_renamed(stable, current, diff, breaking_changes):
    from jsondiff.symbols import Symbol
    for module_name, module in diff.items():
        for client, components in module["clients"].items():
            if "methods" in components:
                for method_name, props in components["methods"].items():
                    if isinstance(method_name, Symbol):
                        if method_name.label == "delete":
                            for name in props:
                                bc = BreakingChange(
                                    breaking_change_type=BreakingChangeType.REMOVE_OR_RENAME_CLIENT_METHOD,
                                    message=f"The '{client}' method '{name}' was deleted or renamed in the current "
                                            f"version",
                                )
                                breaking_changes.append(bc)


def client_removed_or_renamed(stable, current, diff, breaking_changes):
    from jsondiff.symbols import Symbol
    for module_name, module in diff.items():
        if "clients" in module:
            for operation, client in module["clients"].items():
                if isinstance(operation, Symbol):
                    if operation.label == "delete":
                        bc = BreakingChange(
                            breaking_change_type=BreakingChangeType.REMOVE_OR_RENAME_CLIENT,
                            message=f"The client {client} was deleted or renamed in the current version"
                        )
                        breaking_changes.append(bc)


def client_method_positional_parameter_removed_or_renamed(stable, current, diff, breaking_changes):
    from jsondiff.symbols import Symbol
    for module_name, module in diff.items():
        for client, components in module["clients"].items():
            if "methods" in components:
                for method_name, props in components["methods"].items():
                    if "parameters" in props:
                        for param_type, param_name in props["parameters"].items():
                            if param_type != "positional_or_keyword":
                                continue
                            deleted_indices = []
                            if isinstance(param_name, dict):
                                for operation in param_name:
                                    if operation.label == "delete":
                                        deleted_indices = props["parameters"][param_type][operation]
                            if deleted_indices:
                                for deleted_idx in deleted_indices:
                                    deleted_parameter = stable[module_name]["clients"][client]["methods"][method_name]["parameters"][param_type][deleted_idx]
                                    bc = BreakingChange(
                                        breaking_change_type=BreakingChangeType.REMOVE_OR_RENAME_POSITIONAL_PARAM,
                                        message=f"The '{client} method '{method_name}' had its {param_type} parameter "
                                                f"'{deleted_parameter}' deleted or renamed in the current version"
                                    )
                                    breaking_changes.append(bc)

def client_method_positional_parameter_added(stable, current, diff, breaking_changes):
    for module_name, module in diff.items():
        for client, components in module["clients"].items():
            if "methods" in components:
                for method_name, props in components["methods"].items():
                    if "parameters" in props:
                        for param_type, param_name in props["parameters"].items():
                            if param_type != "positional_or_keyword":
                                continue
                            inserted_parameters = []
                            if isinstance(param_name, dict):
                                for operation in param_name:
                                    if operation.label == "insert":
                                        inserted_parameters = props["parameters"][param_type][operation]
                            if inserted_parameters:
                                for inserted_param in inserted_parameters:
                                    bc = BreakingChange(
                                        breaking_change_type=BreakingChangeType.REMOVE_OR_RENAME_POSITIONAL_PARAM,
                                        message=f"The '{client} method '{method_name}' had a {param_type} parameter "
                                                f"'{inserted_param[1]}' inserted in the current version"
                                    )
                                    breaking_changes.append(bc)


def check_for_breaking_changes(stable, current, diff):
    breaking_changes = []
    client_removed_or_renamed(stable, current, diff, breaking_changes)
    client_method_removed_or_renamed(stable, current, diff, breaking_changes)
    model_or_exposed_class_removed_or_renamed(stable, current, diff, breaking_changes)
    model_or_exposed_class_instance_attribute_removed_or_renamed(stable, current, diff, breaking_changes)
    client_method_positional_parameter_removed_or_renamed(stable, current, diff, breaking_changes)
    client_method_positional_parameter_added(stable, current, diff, breaking_changes)
    print([change.message for change in breaking_changes])

def test_compare(pkg_dir):
    import json_delta
    import json
    import jsondiff
    with open(os.path.join(pkg_dir, "stable.json"), "r") as fd:
        stable = json.load(fd)
    with open(os.path.join(pkg_dir, "current.json"), "r") as fd:
        current = json.load(fd)
    results1 = json_delta.diff(stable, current)
    results2 = jsondiff.diff(stable, current)

    check_for_breaking_changes(stable, current, results2)


def main(package_name, target_module, version, create_venv, pkg_dir):
    if create_venv == "False":
        create_venv = False
    else:
        create_venv = True

    if create_venv:
        packages = [package_name + "==" + version, "aiohttp"]  # need to include aiohttp since some libs import AioHttpTransport from azure.core
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

    public_api = test_detect_breaking_changes(package_name, target_module, current=create_venv)

    if create_venv is False:
        with open("stable.json", "w") as fd:
            json.dump(public_api, fd, indent=2)
        return

    with open("current.json", "w") as fd:
        json.dump(public_api, fd, indent=2)

    test_compare(pkg_dir)


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


