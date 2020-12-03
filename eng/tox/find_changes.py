import argparse
import os
from detect_breaking_changes import test_find_modules, create_function_report, create_class_report
from tox_helper_tasks import get_package_details


stable_api = {}

class StableAPI:

    def __init__(self, pr):
        self.my_stable_api = pr

my_api = StableAPI("f")

def create_ot(api):
    my_api.my_stable_api = api

def create_empty_function_report(name):
    return {
        "name": name,
        "positional_parameters": {},
        "optional_parameters": {}
    }


def create_empty_class_report(lineno):
    return {
        "is_client": False,
        "lineno": lineno,
        "methods": {},
        "properties": {}
    }



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
        "-p",
        "--package_path",
        dest="package_path",
        help="The target package directory on disk. The target module passed to pylint will be <target_package>/azure.",
        required=True,
    )

    args = parser.parse_args()
    pkg_dir = os.path.abspath(args.target_package)
    # package_name, namespace, ver = get_package_details(os.path.join(pkg_dir, "setup.py"))
    print(args.package_path)

    import importlib
    import inspect

    modules = test_find_modules(args.package_path)
    print(modules)
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

    import json
    with open("stable.json", "w") as fd:
        json.dump(public_api, fd, indent=2)