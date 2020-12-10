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
    import json_delta
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
    REMOVED_KWARGS_FROM_CLIENT_METHOD = "RemovedKwargsFromClientMethod"


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


class BreakingChangesTracker:
    
    def __init__(self, stable, current, diff):
        self.stable = stable
        self.current = current
        self.diff = diff
        self.breaking_changes = []

    def run_checks(self):
        self.run_client_level_checks()
        self.run_class_level_checks()
        self.run_function_level_checks()

    def run_client_level_checks(self):
        for module_name, module in self.diff.items():
            for client, components in module.get("clients", {}).items():
                self.client_removed_or_renamed(client)
                self.client_method_removed_or_renamed(client, components)
                for method_name, props in components.get("methods", {}).items():
                    for param_type, param_name in props.get("parameters", {}).items():
                        if param_type == "positional_or_keyword":
                            self.client_method_positional_parameter_added(param_name, param_type, props, method_name)
                            self.client_method_positional_parameter_removed_or_renamed(
                                module_name, client, param_name, param_type, props, method_name
                            )
                        # if param_type == "var_keyword":
                        #     self.client_method_kwargs_removed(module_name, param_name, param_type, props, method_name)

    def run_class_level_checks(self):
        for module_name, module in self.diff.items():
            for model_name, components in module.get("class_nodes", {}).items():
                self.model_or_exposed_class_instance_attribute_removed_or_renamed(module_name, model_name, components)
                self.model_or_exposed_class_removed_or_renamed(model_name, components)

    def run_function_level_checks(self):
        for module_name, module in self.diff.items():
            for function_name, components in module.get("function_nodes", {}).items():
                self.module_level_function_removed_or_renamed(function_name, components)

    def module_level_function_removed_or_renamed(self, function_name, components):
        if isinstance(function_name, jsondiff.Symbol):
            if function_name.label == "delete":
                for function in components:
                    bc = BreakingChange(
                        breaking_change_type=BreakingChangeType.REMOVE_OR_RENAME_MODULE_LEVEL_FUNCTION,
                        message=f"The publicly exposed function '{function}' was deleted or renamed in the current version"
                    )
                    self.breaking_changes.append(bc)

    def model_or_exposed_class_instance_attribute_removed_or_renamed(self, module_name, model_name, components):
        deleted_indices = []
        if "properties" in components:
            for prop in components["properties"]:
                if isinstance(prop, jsondiff.Symbol):
                    if prop.label == "delete":
                        deleted_indices = components["properties"][prop]
            if deleted_indices:
                for deleted_idx in deleted_indices:
                    deleted_property = self.stable[module_name]["class_nodes"][model_name]["properties"][
                        deleted_idx]
                    bc = BreakingChange(
                        breaking_change_type=BreakingChangeType.REMOVE_OR_RENAME_INSTANCE_ATTRIBUTE_FROM_MODEL,
                        message=f"The model or publicly exposed class '{model_name}' had its instance variable "
                                f"'{deleted_property}' deleted or renamed in the current version"
                    )
                    self.breaking_changes.append(bc)

    def model_or_exposed_class_removed_or_renamed(self, model_name, components):
        if isinstance(model_name, jsondiff.Symbol):
            if model_name.label == "delete":
                for name in components:
                    bc = BreakingChange(
                        breaking_change_type=BreakingChangeType.REMOVE_OR_RENAME_MODEL,
                        message=f"The model or publicly exposed class '{name}' was deleted or renamed in the "
                                f"current version",
                    )
                    self.breaking_changes.append(bc)

    def client_method_positional_parameter_added(self, param_name, param_type, props, method_name):
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
                self.breaking_changes.append(bc)

    def client_method_positional_parameter_removed_or_renamed(self, module_name, client, param_name, param_type, props, method_name):
        deleted_indices = []
        if isinstance(param_name, dict):
            for operation in param_name:
                if operation.label == "delete":
                    deleted_indices = props["parameters"][param_type][operation]
        if deleted_indices:
            for deleted_idx in deleted_indices:
                deleted_parameter = self.stable[module_name]["clients"][client]["methods"][method_name]["parameters"][param_type][deleted_idx]
                bc = BreakingChange(
                    breaking_change_type=BreakingChangeType.REMOVE_OR_RENAME_POSITIONAL_PARAM,
                    message=f"The '{client} method '{method_name}' had its {param_type} parameter "
                            f"'{deleted_parameter}' deleted or renamed in the current version"
                )
                self.breaking_changes.append(bc)

    # def client_method_kwargs_removed(self, module_name, param_name, param_type, props, method_name):
    #     deleted_indices = []
    #     if isinstance(param_name, dict):
    #         for operation in param_name:
    #             if operation.label == "delete":
    #                 deleted_indices = props["parameters"][param_type][operation]
    #     if deleted_indices:
    #         for deleted_idx in deleted_indices:
    #             deleted_parameter = self.stable[module_name]["clients"][client]["methods"][method_name]["parameters"][param_type][deleted_idx]
    #             bc = BreakingChange(
    #                 breaking_change_type=BreakingChangeType.REMOVED_KWARGS_FROM_CLIENT_METHOD,
    #                 message=f"The '{client} method '{method_name}' had its **kwargs parameter deleted"
    #             )
    #             self.breaking_changes.append(bc)

    def client_removed_or_renamed(self, client):
        if isinstance(client, jsondiff.Symbol):
            if client.label == "delete":
                bc = BreakingChange(
                    breaking_change_type=BreakingChangeType.REMOVE_OR_RENAME_CLIENT,
                    message=f"The client {client} was deleted or renamed in the current version"
                )
                self.breaking_changes.append(bc)

    def client_method_removed_or_renamed(self, client, components):
        for method_name, props in components.get("methods", {}).items():
            if isinstance(method_name, jsondiff.Symbol):
                if method_name.label == "delete":
                    for name in props:
                        bc = BreakingChange(
                            breaking_change_type=BreakingChangeType.REMOVE_OR_RENAME_CLIENT_METHOD,
                            message=f"The '{client}' method '{name}' was deleted or renamed in the current "
                                    f"version",
                        )
                        self.breaking_changes.append(bc)


def test_compare(pkg_dir="C:\\Users\\krpratic\\azure-sdk-for-python\\sdk\\formrecognizer\\azure-ai-formrecognizer"):

    with open(os.path.join(pkg_dir, "stable.json"), "r") as fd:
        stable = json.load(fd)
    with open(os.path.join(pkg_dir, "current.json"), "r") as fd:
        current = json.load(fd)
    # results1 = json_delta.diff(stable, current)
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


