import ast
import os
import enum
import tokenize
import argparse
import logging
import inspect
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
    REMOVE_OR_RENAME_ATTR_FROM_MODEL = "RemoveOrRenameAttrFromModel"


def test_tokenize(ignore_dict, file_path, source):
    for token in tokenize.generate_tokens(lambda: source.readline()):
        if token.type == tokenize.COMMENT:
            if token.string.find("breaking-changes") != -1:
                if file_path not in ignore_dict:
                    ignore_dict[file_path] = []
                ignore_dict[file_path].append(token.start[0])


class BreakingChange:

    def __init__(self):
        self.line_number = None
        self.file_name = None
        self.breaking_change_type = None
        self.message = None
        self.ignore = False


class BreakingChangesChecker(ast.NodeVisitor):

    def __init__(self):
        self.function_nodes = {}
        self.class_nodes = {}

    def visit_ClassDef(self, node):
        if not node.name.startswith("_"):
            self.class_nodes[node.name] = node
        self.generic_visit(node)

    def visit_FunctionDef(self, node):
        if not node.name.startswith("_"):
            self.function_nodes[node.name] = node
        self.generic_visit(node)


class Analyzer(ast.NodeVisitor):
    def __init__(self):
        self.function_nodes = {}
        self.class_nodes = {}

    def visit_Module(self, module):
        for node in module.body:
            if isinstance(node, ast.FunctionDef):
                if not node.name.startswith("_"):
                    self.function_nodes[node.name] = node
            if isinstance(node, ast.ClassDef):
                if not node.name.startswith("_"):
                    self.class_nodes[node.name] = node


    # def visit_Assign(self, node):
    #     if node.targets[0].id == '__all__':
    #         for elt in node.value.elts:
    #             self.in_all.append(elt.value)
    #     self.generic_visit(node)
    #
    # def visit_ImportFrom(self, node):
    #     for api in node.names:
    #         node_module = "/".join(node.module.split('.'))
    #         if node_module not in self.public_api:
    #             self.public_api[node_module] = []
    #         self.public_api[node_module].append({api.name: None})
    #     self.generic_visit(node)


def test_install_pkg(package_name):
    import subprocess
    import sys
    import time
    from pypi_tools.pypi import PyPIClient

    client = PyPIClient()

    try:
        version = client.get_relevant_versions(package_name)
    except IndexError:
        exit(0)  # means there is no stable version available on PyPi

    stable_package_path = os.path.join(root_dir, "eng", "tox", "temp")
    commands = [sys.executable, "-m", "pip", "install", "--no-deps", "-q", f"--target={tmpdir}", f"{package_name}=={version[1]}"]
    subprocess.check_call(commands)
    while not os.path.isdir(tmpdir):
        time.sleep(5)

    return stable_package_path



def check_positional_params(stable, current):
    print(stable)


def added_positional_parameter(stable, current):

    for module, stable_nodes in stable.items():
        current_nodes = current[module]
        for cls, stable_cls_node in stable_nodes["class_nodes"].items():
            current_cls_node = current_nodes["class_nodes"][cls]
            check_positional_params(stable_cls_node, current_cls_node)



def apply_rules(stable, current):
    breaking_changes = []

    added_positional_parameter(stable, current)

    pass



def test_breaking_changes(pkg_dir="C:\\Users\\krpratic\\azure-sdk-for-python\\sdk\\formrecognizer\\azure-ai-formrecognizer", package_name="azure-ai-formrecognizer", namespace="azure.ai.formrecognizer"):
    import shutil
    stable_package_path = test_install_pkg(package_name)
    stable_tree = test_detect_breaking_changes(pkg_dir=stable_package_path, namespace=namespace)

    current_tree = test_detect_breaking_changes(pkg_dir=pkg_dir, namespace=namespace)

    apply_rules(stable_tree, current_tree)
    shutil.rmtree(tmpdir)



def test_find_modules(pkg_root_path):
    """Find modules within the package to import and parse
    :param str: pkg_root_path
        Package root path
    :rtype: list
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
    # source_lines = inspect.getsourcelines(f)[0]
    # if source_lines[0].find("ignore") != -1 and source_lines[0].find("breaking-changes") != -1:
    #     func_obj["ignore"] = True
    #     return func_obj

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



def create_class_report(name, cls):
    print(cls)
    cls_info = {
        "name": name,
        "type": None,
        "ignore": False,
        "methods": {},
        "properties": None
    }

    source_lines = inspect.getsourcelines(cls)[0]
    if source_lines[0].find("ignore") != -1 and source_lines[0].find("breaking-changes") != -1:
        cls_info["ignore"] = True
        return cls_info

    base_classes = inspect.getmro(cls)
    is_enum = True if "Enum" in str(base_classes) else False
    if is_enum:
        cls_info["type"] = "Enum"
        cls_info["properties"] = [value for value in dir(cls) if not value.startswith("_")]
        return cls_info

    # we can't get the class instance variables without instantiating the class since these are dynamic, so this is the best we can do
    try:
        props = cls.__init__.__code__.co_names
        cls_info["properties"] = list(props)
    except AttributeError:
        cls_info["properties"] = [value for value in dir(cls) if not value.startswith("_")]

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


def test_detect_breaking_changes(pkg_dir="C:\\Users\\krpratic\\azure-sdk-for-python\\sdk\\formrecognizer\\azure-ai-formrecognizer", package_name="azure-ai-formrecognizer", namespace="azure.ai.formrecognizer"):
    from pathlib import Path
    import importlib
    import inspect
    import types
    folders = "/".join(namespace.split('.'))

    modules = test_find_modules(pkg_dir)

    public_api = {}
    for key, val in modules.items():
        public_api[key] = {"class_nodes": {}, "clients": {}, "function_nodes": {}}
        module = importlib.import_module(key)
        model_names = [model_name for model_name in dir(module)]
        for model_name in model_names:
            # if model_name.startswith("_"):
            #     try:
            #         module = importlib.import_module(f"{key}.{model_name}")
            #         model_names = [model_name for model_name in dir(module)]
            #         for model_name in model_names:
            #             if not model_name.startswith("_"):
            #                 thing = getattr(module, model_name)
            #                 if isinstance(thing, types.FunctionType):
            #                     public_api[key]["function_nodes"].update({model_name: create_function_report(model_name, thing)})
            #                 else:
            #                     public_api[key]["class_nodes"].update({model_name: create_class_report(thing)})
            #     except Exception:
            #         continue
            if not model_name.startswith("_"):
                thing = getattr(module, model_name)
                if inspect.isfunction(thing):
                    public_api[key]["function_nodes"].update({model_name: create_function_report(model_name, thing)})
                elif inspect.isclass(thing) and model_name.endswith("Client"):
                    public_api[key]["clients"].update({model_name: create_class_report(model_name, thing)})
                elif inspect.isclass(thing):
                    public_api[key]["class_nodes"].update({model_name: create_class_report(model_name, thing)})

    # public_api = {}
    # for key, val in modules.items():
    #     public_api[key] = {"class_nodes": {}, "function_nodes": {}}
    #     for v in val:
    #         with open(v, "r") as source:
    #             module = ast.parse(source.read())
    #
    #         analyzer = Analyzer()
    #         analyzer.visit(module)
    #         if analyzer.class_nodes:
    #             public_api[key]["class_nodes"].update(analyzer.class_nodes)
    #         if analyzer.function_nodes:
    #             public_api[key]["function_nodes"].update(analyzer.function_nodes)

    import json
    with open("current.json", "w") as fd:
        json.dump(public_api, fd, indent=2)

    return public_api

    # ignore_dict = {}
    # for module in public_api:
    #     for key, value_list in module.public_api.items():
    #         for value_dict in value_list:
    #             for api in value_dict:
    #                 if api not in module.in_all:
    #                     module.public_api[key].remove(value_dict)
    #                 if api.startswith("_"):
    #                     module.public_api[key].remove(value_dict)
    #
    #         bc = BreakingChangesChecker(module.public_api[key], module.in_all)
    #         try:
    #             with open(module.path.replace("__init__", key), "r") as source:
    #                 tree = ast.parse(source.read())
    #                 test_tokenize(ignore_dict, key, source)
    #             bc.visit(tree)
    #         except FileNotFoundError:
    #             pass  # FIXME: need to work out how to open for module imports

    # return public_api, ignore_dict


# if __name__ == "__main__":
#     parser = argparse.ArgumentParser(
#         description="Run pylint against target folder. Add a local custom plugin to the path prior to execution. "
#     )
#
#     parser.add_argument(
#         "-t",
#         "--target",
#         dest="target_package",
#         help="The target package directory on disk. The target module passed to pylint will be <target_package>/azure.",
#         required=True,
#     )
#
#     args = parser.parse_args()
#
#
#     pkg_dir = os.path.abspath(args.target_package)
#     package_name, namespace, ver = get_package_details(os.path.join(pkg_dir, "setup.py"))
#     test_breaking_changes(pkg_dir, package_name, namespace)




def test_create_report():
    import importlib
    import inspect
    import types
    import importlib.util

    # for module in module_names:
        # spec = importlib.util.spec_from_file_location(module, package_path[0])
        # module_to_generate = importlib.util.module_from_spec(spec)
        # spec.loader.exec_module(module_to_generate)
        # foo.MyClass()
    module_to_generate = importlib.import_module("azure.ai.formrecognizer")


    print(module_to_generate)
    # Look for models first
    l = module_to_generate._api_versions
    model_names = [model_name for model_name in dir(module_to_generate)]
    for model_name in model_names:
        if not model_name.startswith("_"):
            thing = getattr(module_to_generate, model_name)
            ff = inspect.getsourcelines(thing)[1]
            if isinstance(thing, types.FunctionType):

                create_function_report(thing.name)
            create_empty_class_report(ff)


class StableAPI:

    def __init__(self):
        self.my_stable_api = {}

my_api = StableAPI()


def write_to_object(public_api):
    my_api.my_stable_api = public_api
    print(f"in write to object {public_api}")
    return

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

    args = parser.parse_args()
    print(args)
    # pkg_dir = os.path.abspath(args.target_package)
    # package_name, namespace, ver = get_package_details(os.path.join(pkg_dir, "setup.py"))


def client_removed_or_renamed(stable, diff):

    pass

def check_for_breaking_changes(stable, diff):
    breaking_changes = []
    client_removed_or_renamed(stable, diff)


def test_compare():
    import json_delta
    import json
    import jsondiff
    with open("stable.json", "r") as fd:
        l = json.load(fd)
    with open("current.json", "r") as fd:
        r = json.load(fd)
    results1 = json_delta.diff(l, r)
    results2 = jsondiff.diff(l, r)

    return l, results2


def test_startrr(package_name="azure-ai-formrecognizer", module_name="azure.ai.formrecognizer"):
    import subprocess
    import sys
    import time
    from pypi_tools.pypi import PyPIClient

    client = PyPIClient()

    try:
        version = client.get_relevant_versions(package_name)
    except IndexError:
        exit(0)  # means there is no stable version available on PyPi

    # from pathlib import Path
    # namespaces = []
    # folders = "/".join(module_name.split('.'))
    stable_package_path = os.path.join(root_dir, "eng", "tox", "temp")
    # for path in Path(os.path.join(stable_package_path, folders)).rglob('*__init__.py'):
    #     if any(p.startswith("_") and p != "__init__.py" for p in path.parts):
    #         continue
    #     namespaces.append(str(path))

    namespaces1 = "azure-ai-formrecognizer"
    # create_report(namespaces1, namespaces)

    f = __file__
    with create_venv_with_package([f"{package_name}=={str(version[1])}"]) as venv:
        args = [
            venv.env_exe,
            "C:\\Users\krpratic\\azure-sdk-for-python\\eng\\tox\\find_changes.py",
            "-t",
            namespaces1,
            "-p",
            stable_package_path
        ]
        try:
            subprocess.check_call(args)
        except subprocess.CalledProcessError:
            # If it fail, just assume this version is too old to get an Autorest report
            _LOGGER.warning(f"Version {version} seems to be too old to build a report (probably not Autorest based)")

    test_detect_breaking_changes()

    #
    # commands = [sys.executable, "-m", "pip", "install", "--no-deps", "-q", f"--target={tmpdir}", f"{package_name}=={version[1]}"]
    # subprocess.check_call(commands)
    # while not os.path.isdir(tmpdir):
    #     time.sleep(5)
    #
