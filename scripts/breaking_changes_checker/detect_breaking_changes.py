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
from breaking_changes_allowlist import RUN_BREAKING_CHANGES_PACKAGES
try:
    # won't be able to import these in the created venv
    from packaging_tools.venvtools import create_venv_with_package
    import jsondiff
except (ModuleNotFoundError, ImportError) as e:
    pass


root_dir = os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "..", ".."))
_LOGGER = logging.getLogger(__name__)


class ClassTreeAnalyzer(ast.NodeVisitor):
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

    _LOGGER.info("Modules in package: {}".format(modules))
    return modules


def get_parameter_default(param):
    default_value = None
    if param.default is not param.empty:
        default_value = param.default
        if default_value is None:  # the default is actually None
            default_value = "none"
        if inspect.isfunction(default_value):
            default_value = default_value.__name__
        if inspect.isclass(default_value):
            default_value = default_value.__name__

    return default_value


def create_function_report(name, f):
    function = inspect.signature(f)
    func_obj = {
        "name": name,
        "parameters": {
            "positional_only": {},
            "positional_or_keyword": {},
            "keyword_only": {},
            "var_positional": {},
            "var_keyword": {}
        }
    }

    for par in function.parameters.values():
        default_value = get_parameter_default(par)
        if par.kind == par.KEYWORD_ONLY:
            func_obj["parameters"]["keyword_only"].update({par.name: default_value})
        elif par.kind == par.POSITIONAL_ONLY:
            func_obj["parameters"]["positional_only"].update({par.name: default_value})
        elif par.kind == par.POSITIONAL_OR_KEYWORD:
            func_obj["parameters"]["positional_or_keyword"].update({par.name: default_value})
        elif par.kind == par.VAR_POSITIONAL:
            func_obj["parameters"]["var_positional"].update({par.name: default_value})
        elif par.kind == par.VAR_KEYWORD:
            func_obj["parameters"]["var_keyword"].update({par.name: default_value})

    return func_obj


def get_properties(cls):
    """Get the public instance variables of the class and any inherited.

    :param cls:
    :return:
    """
    base_classes = inspect.getmro(cls)  # cls itself is included here

    attribute_names = {}
    for base_class in base_classes:
        try:
            path = inspect.getsourcefile(base_class)
            if path.find("azure") == -1:
                continue
            with open(path, "r") as source:
                module = ast.parse(source.read())
        except (TypeError, SyntaxError):
            _LOGGER.info(f"Unable to create ast of {base_class}")
            continue  # was a built-in, e.g. "object", Exception, or a Model from msrest fails here due to SyntaxError

        analyzer = ClassTreeAnalyzer(base_class.__name__)
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
    }

    is_enum = Enum in cls.__mro__
    if is_enum:
        cls_info["type"] = "Enum"
        cls_info["properties"] = {value: value for value in dir(cls) if not value.startswith("_")}
        return cls_info

    cls_info["properties"] = get_properties(cls)

    methods = [method for method in dir(cls) if not method.startswith("_")]
    for method in methods:
        m = getattr(cls, method)
        if inspect.isfunction(m) or inspect.ismethod(m):
            cls_info["methods"][method] = create_function_report(method, m)

    cls_init = getattr(cls, "__init__")
    cls_info["methods"]["__init__"] = create_function_report("__init__", cls_init)

    return cls_info


def resolve_module_name(module_name, target_module):
    if module_name == ".":
        module_name = target_module
    else:
        module_name = target_module + "." + module_name
    return module_name


def test_detect_breaking_changes(target_module="azure.storage.blob"):

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
                    public_api[module_name]["function_nodes"].update({importable: create_function_report(importable, live_obj)})
                elif inspect.isclass(live_obj):
                    public_api[module_name]["class_nodes"].update({importable: create_class_report(importable, live_obj)})
                # else:  # Constants, version, etc. Nothing of interest at the moment
                #     public_api[module_name]["others"].update({importable: live_obj})

    return public_api


class BreakingChangesTracker:
    REMOVE_OR_RENAME_CLIENT = \
        "(RemoveOrRenameClient): The client '{}' was deleted or renamed in the current version"
    REMOVE_OR_RENAME_CLIENT_METHOD = \
        "(RemoveOrRenameClientMethod): The '{}' client method '{}' was deleted or renamed in the current version"
    REMOVE_OR_RENAME_MODEL = \
        "(RemoveOrRenameModel): The model or publicly exposed class '().{}' was deleted or renamed in the current version"
    REMOVE_OR_RENAME_MODEL_METHOD = \
        "(RemoveOrRenameModelMethod): The '{}' method '{}' was deleted or renamed in the current version"
    REMOVE_OR_RENAME_MODULE_LEVEL_FUNCTION = \
        "(RemoveOrRenameModuleLevelFunction): The publicly exposed function '{}' was deleted or renamed in the " \
        "current version"
    REMOVE_OR_RENAME_POSITIONAL_PARAM_OF_METHOD = \
        "(RemoveOrRenamePositionalParam): The '{} method '{}' had its {} parameter '{}' deleted or renamed in the " \
        "current version"
    REMOVE_OR_RENAME_POSITIONAL_PARAM_OF_FUNCTION = \
        "(RemoveOrRenamePositionalParam): The function '{}' had its {} parameter '{}' deleted or renamed in the " \
        "current version"
    ADDED_POSITIONAL_PARAM_TO_METHOD = \
        "(AddedPositionalParam): The '{} method '{}' had a {} parameter '{}' inserted in the current version"
    ADDED_POSITIONAL_PARAM_TO_FUNCTION = \
        "(AddedPositionalParam): The function '{}' had a {} parameter '{}' inserted in the current version"
    REMOVE_OR_RENAME_INSTANCE_ATTRIBUTE_FROM_CLIENT = \
        "(RemoveOrRenameInstanceAttribute): The client '{}' had its instance variable" \
        " '{}' deleted or renamed in the current version"
    REMOVE_OR_RENAME_INSTANCE_ATTRIBUTE_FROM_MODEL = \
        "(RemoveOrRenameInstanceAttribute): The model or publicly exposed class '{}' had its instance " \
        "variable '{}' deleted or renamed in the current version"
    REMOVE_OR_RENAME_ENUM_VALUE = \
        "(RemoveOrRenameEnumValue): The '{}' enum had its value '{}' deleted or renamed in the current version"
    CHANGED_PARAMETER_DEFAULT_VALUE = \
        "(ChangedParameterDefaultValue): The class '{}' method '{}' had its parameter '{}' default value changed " \
        "from '{}' to '{}'"
    CHANGED_PARAMETER_DEFAULT_VALUE_OF_FUNCTION = \
        "(ChangedParameterDefaultValue): The publicly exposed function '{}' had its parameter '{}' default value " \
        "changed from '{}' to '{}'"
    CHANGED_PARAMETER_ORDERING = \
        "(ChangedParameterOrdering): The class '{}' method '{}' had its parameters re-ordered " \
        "from '{}' to '{}' in the current version"
    CHANGED_PARAMETER_ORDERING_OF_FUNCTION = \
        "(ChangedParameterOrdering): The publicly exposed function '{}' had its parameters re-ordered " \
        "from '{}' to '{}' in the current version"

    def __init__(self, stable, current, diff):
        self.stable = stable
        self.current = current
        self.diff = diff
        self.breaking_changes = []

    def __str__(self):
        formatted = "\n"
        for bc in self.breaking_changes:
            formatted += f"{bc}\n"

        formatted += "\nSee aka.ms/breaking-changes-tool to resolve any reported breaking changes or false positives.\n"
        return formatted

    def run_checks(self):
        self.run_class_level_diff_checks()
        self.run_function_level_diff_checks()
        self.check_positional_parameter_ordering()  # won't show up in a diff, need to iterate over stable vs current

    def run_class_level_diff_checks(self):
        for module_name, module in self.diff.items():
            for class_name, class_components in module.get("class_nodes", {}).items():
                if class_name not in self.stable[module_name]["class_nodes"] and \
                        not isinstance(class_name, jsondiff.Symbol):
                    continue  # this is a new model/additive change in current version so skip checks
                self.check_class_removed_or_renamed(module_name, class_name, class_components)
                self.check_class_instance_attribute_removed_or_renamed(module_name, class_name, class_components)

                for method_name, method_components in class_components.get("methods", {}).items():
                    if method_name not in self.stable[module_name]["class_nodes"][class_name]["methods"] and \
                            not isinstance(method_name, jsondiff.Symbol):
                        continue  # this is a new method/additive change in current version so skip checks

                    stable_methods_node = self.stable[module_name]["class_nodes"][class_name]["methods"]
                    self.check_class_method_removed_or_renamed(module_name, class_name, method_name, method_components, stable_methods_node)

                    if not isinstance(method_name, jsondiff.Symbol):  # skip param checks if method was deleted
                        stable_parameters_node = self.stable[module_name]["class_nodes"][class_name]["methods"][method_name]["parameters"]
                        self.run_parameter_level_diff_checks(module_name, method_name, method_components, stable_parameters_node, class_name=class_name)

    def run_function_level_diff_checks(self):
        for module_name, module in self.diff.items():
            for function_name, function_components in module.get("function_nodes", {}).items():
                if function_name not in self.stable[module_name]["function_nodes"] and \
                        not isinstance(function_name, jsondiff.Symbol):
                    continue  # this is a new function/additive change in current version so skip checks
                self.check_module_level_function_removed_or_renamed(module_name, function_name, function_components)

                if not isinstance(function_name, jsondiff.Symbol):  # skip param checks if function was deleted
                    stable_parameters_node = self.stable[module_name]["function_nodes"][function_name]["parameters"]
                    self.run_parameter_level_diff_checks(module_name, function_name, function_components, stable_parameters_node)

    def run_parameter_level_diff_checks(self, module_name, function_name, function_components, stable_parameters_node, class_name=None):
        for param_type, params in function_components.get("parameters", {}).items():
            if param_type == "positional_or_keyword":
                for param_name, default in params.items():
                    if isinstance(param_name, jsondiff.Symbol):
                        self.check_positional_parameter_removed_or_renamed(
                            module_name, param_name, param_type, default, function_name, stable_parameters_node, class_name
                        )
                    elif param_name not in stable_parameters_node[param_type]:
                        self.check_positional_parameter_added(
                            module_name, param_name, param_type, function_name, class_name
                        )
                    else:
                        stable_default = stable_parameters_node[param_type][param_name]
                        self.check_positional_parameter_default_value_changed(
                            module_name, function_name, param_name, default, stable_default, class_name
                        )

    def check_positional_parameter_ordering(self):
        keys = self.stable.keys() & self.current.keys()

        for key in keys:
            stable_cls = self.stable[key]["class_nodes"]
            current_cls = self.current[key]["class_nodes"]
            class_keys = stable_cls.keys() & current_cls.keys()
            for cls in class_keys:
                stable_method_nodes = stable_cls[cls]["methods"]
                current_method_nodes = current_cls[cls]["methods"]
                method_keys = stable_method_nodes.keys() & current_method_nodes.keys()
                for method in method_keys:
                    stable_params = stable_method_nodes[method]["parameters"]["positional_or_keyword"].keys()
                    current_params = current_method_nodes[method]["parameters"]["positional_or_keyword"].keys()
                    if len(stable_params) != len(current_params):
                        # a parameter was deleted and that breaking change was already reported so skip
                        continue
                    for key1, key2 in zip(stable_params, current_params):
                        if key1 != key2:
                            self.breaking_changes.append(
                                self.CHANGED_PARAMETER_ORDERING.format(
                                    f"{key}.{cls}", method, list(stable_params), list(current_params)
                                ))
                            break

            stable_funcs = self.stable[key]["function_nodes"]
            current_funcs = self.current[key]["function_nodes"]
            func_nodes = stable_funcs.keys() & current_funcs.keys()
            for func in func_nodes:
                stable_params = stable_funcs[func]["parameters"]["positional_or_keyword"].keys()
                current_params = current_funcs[func]["parameters"]["positional_or_keyword"].keys()
                if len(stable_params) != len(current_params):
                    # a parameter was deleted and that breaking change was already reported so skip
                    continue
                for key1, key2 in zip(stable_params, current_params):
                    if key1 != key2:
                        self.breaking_changes.append(
                            self.CHANGED_PARAMETER_ORDERING_OF_FUNCTION.format(
                                f"{key}.{func}", list(stable_params), list(current_params)
                            ))
                        break

    def check_positional_parameter_default_value_changed(self, module_name, function_name, param_name, default, stable_default, class_name=None):
        if default is not None:  # a default was added in the current version
            if default != stable_default:
                if stable_default is not None:  # There is a stable default
                    if stable_default == "none":  # the case in which the stable default was None
                        stable_default = None  # set back to actual None for the message
                    if class_name:
                        self.breaking_changes.append(
                            self.CHANGED_PARAMETER_DEFAULT_VALUE.format(
                                f"{module_name}.{class_name}", function_name, param_name, stable_default, default
                            ))
                    else:
                        self.breaking_changes.append(
                            self.CHANGED_PARAMETER_DEFAULT_VALUE_OF_FUNCTION.format(
                                f"{module_name}.{function_name}", param_name, stable_default, default
                            ))

    def check_positional_parameter_added(self, module_name, param_name, param_type, function_name, class_name=None):
        if class_name:
            self.breaking_changes.append(self.ADDED_POSITIONAL_PARAM_TO_METHOD.format(f"{module_name}.{class_name}", function_name, param_type, param_name))
        else:
            self.breaking_changes.append(self.ADDED_POSITIONAL_PARAM_TO_FUNCTION.format(f"{module_name}.{function_name}", param_type, param_name))

    def check_positional_parameter_removed_or_renamed(self, module_name, param_name, param_type, deleted, function_name, stable_parameters_node, class_name=None):
        deleted_params = []
        if param_name.label == "delete":
            deleted_params = deleted
        elif param_name.label == "replace":  # replace means all positional parameters were removed
            deleted_params = stable_parameters_node[param_type]

        for deleted in deleted_params:
            if deleted != "self":
                if class_name:
                    self.breaking_changes.append(self.REMOVE_OR_RENAME_POSITIONAL_PARAM_OF_METHOD.format(
                            f"{module_name}.{class_name}", function_name, param_type, deleted
                        ))
                else:
                    self.breaking_changes.append(self.REMOVE_OR_RENAME_POSITIONAL_PARAM_OF_FUNCTION.format(
                            f"{module_name}.{function_name}", param_type, deleted
                        ))

    def check_class_instance_attribute_removed_or_renamed(self, module_name, class_name, components):
        for prop in components.get("properties", []):
            if isinstance(prop, jsondiff.Symbol):
                deleted_props = []
                if prop.label == "delete":
                    deleted_props = components["properties"][prop]
                elif prop.label == "replace":
                    deleted_props = self.stable[module_name]["class_nodes"][class_name]["properties"]

                for property in deleted_props:
                    if property.endswith("Client"):
                        bc = self.REMOVE_OR_RENAME_INSTANCE_ATTRIBUTE_FROM_CLIENT.format(f"{module_name}.{class_name}", property)
                    elif self.stable[module_name]["class_nodes"][class_name]["type"] == "Enum":
                        bc = self.REMOVE_OR_RENAME_ENUM_VALUE.format(f"{module_name}.{class_name}", property)
                    else:
                        bc = self.REMOVE_OR_RENAME_INSTANCE_ATTRIBUTE_FROM_MODEL.format(f"{module_name}.{class_name}", property)
                    self.breaking_changes.append(bc)

    def check_class_removed_or_renamed(self, module_name, model_name, class_components):
        if isinstance(model_name, jsondiff.Symbol):
            deleted_classes = []
            if model_name.label == "delete":
                deleted_classes = class_components
            elif model_name.label == "replace":
                deleted_classes = self.stable[module_name]["class_nodes"]

            for name in deleted_classes:
                if name.endswith("Client"):
                    bc = self.REMOVE_OR_RENAME_CLIENT.format(f"{module_name}.{name}")
                else:
                    bc = self.REMOVE_OR_RENAME_MODEL.format(f"{module_name}.{name}")
                self.breaking_changes.append(bc)

    def check_class_method_removed_or_renamed(self, module_name, class_name, method_name, method_components, stable_methods_node):
        if isinstance(method_name, jsondiff.Symbol):
            methods_deleted = []
            if method_name.label == "delete":
                methods_deleted = method_components
            elif method_name.label == "replace":
                methods_deleted = stable_methods_node

            for method in methods_deleted:
                if class_name.endswith("Client"):
                    bc = self.REMOVE_OR_RENAME_CLIENT_METHOD.format(f"{module_name}.{class_name}", method)
                else:
                    bc = self.REMOVE_OR_RENAME_MODEL_METHOD.format(f"{module_name}.{class_name}", method)
                self.breaking_changes.append(bc)

    def check_module_level_function_removed_or_renamed(self, module_name, function_name, function_components):
        if isinstance(function_name, jsondiff.Symbol):
            deleted_functions = []
            if function_name.label == "delete":
                deleted_functions = function_components
            elif function_name.label == "replace":
                deleted_functions = self.stable[module_name]["function_nodes"]

            for function in deleted_functions:
                self.breaking_changes.append(self.REMOVE_OR_RENAME_MODULE_LEVEL_FUNCTION.format(f"{module_name}.{function}"))

# "C:\\Users\\krpratic\\azure-sdk-for-python\\sdk\\formrecognizer\\azure-ai-formrecognizer"
# "C:\\Users\\krpratic\\azure-sdk-for-python\\sdk\\storage\\azure-storage-blob"
def test_compare(pkg_dir="C:\\Users\\krpratic\\azure-sdk-for-python\\sdk\\storage\\azure-storage-blob", version=None):

    with open(os.path.join(pkg_dir, "stable.json"), "r") as fd:
        stable = json.load(fd)
    with open(os.path.join(pkg_dir, "current.json"), "r") as fd:
        current = json.load(fd)
    diff = jsondiff.diff(stable, current)

    bc = BreakingChangesTracker(stable, current, diff)
    bc.run_checks()

    if bc.breaking_changes:
        print(bc)
        exit(1)

    package_name = os.path.basename(pkg_dir)
    print(f"\nNo breaking changes found for {package_name} between stable version {version} and current version.")



def main(package_name, target_module, version, in_venv, pkg_dir):
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

    try:
        public_api = test_detect_breaking_changes(target_module)

        if in_venv:
            with open("stable.json", "w") as fd:
                json.dump(public_api, fd, indent=2)
            _LOGGER.info("stable.json is written.")
            return

        with open("current.json", "w") as fd:
            json.dump(public_api, fd, indent=2)
        _LOGGER.info("current.json is written.")

    except Exception as err:  # catch any issues with capturing the public API and building the report
        print("\n*****See aka.ms/breaking-changes-tool to resolve any build issues*****\n")
        raise err
    # test_compare(pkg_dir, version)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run breaking changes checks against target folder."
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
        _LOGGER.info(f"{package_name} opted out of breaking changes checks. See aka.ms/breaking-changes-tool to opt-in.")
        exit(0)

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


