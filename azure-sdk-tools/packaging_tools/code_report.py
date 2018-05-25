import importlib
import inspect
import json
import logging
import types
from typing import Dict, Any

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
    operations_classes = [op_name for op_name in dir(module_to_generate.operations) if op_name[0].isupper()]
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

def main(input_parameter: str, output_filename: str):
    _, module_name = parse_input(input_parameter)
    report = create_report(module_name)

    with open(output_filename, "w") as fd:
        json.dump(report, fd, indent=2)

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description='Code fingerprint building',
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument('package_name',
                        help='Package name')
    parser.add_argument('--output-file', '-o',
                        dest='output_file', default='./report.json',
                        help='Output file. [default: %(default)s]')
    parser.add_argument("--debug",
                        dest="debug", action="store_true",
                        help="Verbosity in DEBUG mode")

    args = parser.parse_args()

    main_logger = logging.getLogger()
    logging.basicConfig()
    main_logger.setLevel(logging.DEBUG if args.debug else logging.INFO)

    main(args.package_name, args.output_file)
