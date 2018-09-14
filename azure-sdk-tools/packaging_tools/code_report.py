import importlib
import inspect
import json
import logging
import pkgutil
from pathlib import Path
import types
from typing import Dict, Any, Optional

_LOGGER = logging.getLogger(__name__)

def parse_input(input_parameter):
    """From a syntax like package_name#submodule, build a package name
    and complete module name.
    """
    split_package_name = input_parameter.split('#')
    package_name = split_package_name[0]
    module_name = package_name.replace("-", ".")
    if len(split_package_name) >= 2:
        module_name = ".".join([module_name, split_package_name[1]])
    return package_name, module_name


def create_report(module_name: str) -> Dict[str, Any]:
    module_to_generate = importlib.import_module(module_name)

    report = {}
    report["models"] = {
        "enums": {},
        "exceptions": {},
        "models": {}
    }
    # Look for models first
    model_names = [model_name for model_name in dir(module_to_generate.models) if model_name[0].isupper()]
    for model_name in model_names:
        model_cls = getattr(module_to_generate.models, model_name)
        if hasattr(model_cls, "_attribute_map"):
            report["models"]["models"][model_name] = create_model_report(model_cls)
        elif issubclass(model_cls, Exception): # If not, might be an exception
            report["models"]["exceptions"][model_name] = create_model_report(model_cls)
        else:
            report["models"]["enums"][model_name] = create_model_report(model_cls)
    # Look for operation groups
    try:
        operations_classes = [op_name for op_name in dir(module_to_generate.operations) if op_name[0].isupper()]
    except AttributeError:
        # This guy has no "operations", this is possible (Cognitive Services). Just skip it then.
        operations_classes = []

    for op_name in operations_classes:
        op_content = {'name': op_name}
        op_cls = getattr(module_to_generate.operations, op_name)
        for op_attr_name in dir(op_cls):
            op_attr = getattr(op_cls, op_attr_name)
            if isinstance(op_attr, types.FunctionType) and not op_attr_name.startswith("_"):
                # Keep it
                func_content = create_report_from_func(op_attr)
                op_content.setdefault("functions", {})[op_attr_name] = func_content
        report.setdefault("operations", {})[op_name] = op_content

    return report

def create_model_report(model_cls):
    result = {
        'name': model_cls.__name__,
    }
    # If _attribute_map, it's a model
    if hasattr(model_cls, "_attribute_map"):
        result['type'] = "Model"
        for attribute, conf in model_cls._attribute_map.items():
            attribute_validation = getattr(model_cls, "_validation", {}).get(attribute, {})

            result.setdefault('parameters', {})[attribute] = {
                'name': attribute,
                'properties': {
                    'type': conf['type'],
                    'required': attribute_validation.get('required', False),
                    'readonly': attribute_validation.get('readonly', False)
                }
            }
    elif issubclass(model_cls, Exception): # If not, might be an exception
        result['type'] = "Exception"
    else: # If not, it's an enum
        result['type'] = "Enum"
        result['values'] = list(model_cls.__members__)

    return result

def create_report_from_func(function_attr):
    func_content = {
        'name': function_attr.__name__,
        'metadata': getattr(function_attr, "metadata", {}),
        'parameters': []
    }
    signature = inspect.signature(function_attr)
    for parameter_name in signature.parameters:
        if parameter_name == "self":
            continue
        if parameter_name =="custom_headers":
            break # We reach Autorest generic
        parameter = signature.parameters[parameter_name]
        func_content["parameters"].append({
            'name': parameter.name,
        })
    return func_content

def main(input_parameter: str, output_filename: Optional[str] = None, version: Optional[str] = None):
    package_name, module_name = parse_input(input_parameter)
    report = create_report(module_name)

    version = version or "latest"

    if not output_filename:
        split_package_name = input_parameter.split('#')
        output_filename = Path(package_name) / Path("code_reports") / Path(version)
        if len(split_package_name) == 2:
            output_filename /= Path(split_package_name[1]+".json")
        else:
            output_filename /= Path("report.json")
    else:
        output_filename = Path(output_filename)

    output_filename.parent.mkdir(parents=True, exist_ok=True)

    with open(output_filename, "w") as fd:
        json.dump(report, fd, indent=2)

def find_autorest_generated_folder(module_prefix="azure"):
    """Find all Autorest generated code in that module prefix.
    This actually looks for a "models" package only (not file). We could be smarter if necessary.
    """
    _LOGGER.info(f"Looking for Autorest generated package in {module_prefix}")

    # Manually skip some namespaces for now
    if module_prefix in ["azure.cli", "azure.storage"]:
        _LOGGER.info(f"Skip {module_prefix}")
        return []

    result = []
    prefix_module = importlib.import_module(module_prefix)
    for _, sub_package, ispkg in pkgutil.iter_modules(prefix_module.__path__, module_prefix+"."):
        try:
            # ASM has a "models", but is not autorest. Patch it widly for now.
            if sub_package in ["azure.servicemanagement", "azure.storage", "azure.servicebus"]:
                continue

            _LOGGER.debug(f"Try {sub_package}")
            model_module = importlib.import_module(".models", sub_package)

            # If not exception, we MIGHT have found it, but cannot be a file.
            # Keep continue to try to break it, file module have no __path__
            model_module.__path__
            _LOGGER.info(f"Found {sub_package}")
            result.append(sub_package)
        except (ModuleNotFoundError, AttributeError):
            # No model, might dig deeper
            if ispkg:
                result += find_autorest_generated_folder(sub_package)
    return result

def build_them_all():
    """Build all reports for all packages.
    """
    root = Path(__file__).parent.parent.parent # Root of the repo

    packages = dict()
    for module_name in find_autorest_generated_folder():

        main_module = importlib.import_module(module_name)

        package_name = list(Path(main_module.__path__[0]).relative_to(root).parents)[-2]
        packages.setdefault(package_name, set()).add(module_name)

    for package_name, sub_module_list in packages.items():
        _LOGGER.info(f"Processing {package_name}")
        package_name_str = str(package_name)
        if len(sub_module_list) == 1:
            main(package_name_str)
        else:
            for sub_module in sub_module_list:
                _LOGGER.info(f"\tProcessing sub-module {sub_module}")
                sub_module_from_package = package_name_str.replace("-", ".")
                if not sub_module.startswith(sub_module_from_package):
                    _LOGGER.warning(f"Submodule {sub_module} does not package name {package_name}")
                    continue
                sub_module_last_part = sub_module[len(sub_module_from_package)+1:]
                _LOGGER.info(f"Calling main with {package_name}#{sub_module_last_part}")
                main(f"{package_name}#{sub_module_last_part}")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description='Code fingerprint building',
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument('package_name',
                        help='Package name.')
    parser.add_argument('--output-file', '-o',
                        dest='output_file',
                        help='Output file. [default: ./<package_name>/code_reports/<version>/<module_name>.json]')
    parser.add_argument('--version', '-v',
                        dest='version',
                        help='The version of the package you want. By default, latest and current branch.')
    parser.add_argument("--debug",
                        dest="debug", action="store_true",
                        help="Verbosity in DEBUG mode")

    args = parser.parse_args()

    main_logger = logging.getLogger()
    logging.basicConfig()
    main_logger.setLevel(logging.DEBUG if args.debug else logging.INFO)

    if args.package_name == "all":
        build_them_all()
    else:
        main(args.package_name, args.output_file, args.version)
