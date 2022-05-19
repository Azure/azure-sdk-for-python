import importlib
import inspect
import json
import logging
import glob
import os
import pkgutil
from pathlib import Path
import subprocess
import sys
import types
import tempfile
from typing import Dict, Any, Optional

# Because I'm subprocessing myself, I need to do weird thing as import.
try:
    # If I'm started as a module __main__
    from .venvtools import create_venv_with_package
except (ModuleNotFoundError, ImportError) as e:
    # If I'm started by my main directly
    from venvtools import create_venv_with_package


_LOGGER = logging.getLogger(__name__)


def parse_input(input_parameter):
    """From a syntax like package_name#submodule, build a package name
    and complete module name.
    """
    split_package_name = input_parameter.split("#")
    package_name = split_package_name[0]
    module_name = package_name.replace("-", ".")
    if len(split_package_name) >= 2:
        module_name = ".".join([module_name, split_package_name[1]])
    return package_name, module_name


def create_empty_report():
    return {"client": {}, "models": {"enums": {}, "exceptions": {}, "models": {}}, "operations": {}}


def create_report(module_name: str) -> Dict[str, Any]:
    module_to_generate = importlib.import_module(module_name)
    client_name = getattr(module_to_generate, '__all__')

    report = create_empty_report()

    try:
        report["client"] = client_name
    except:
        report["client"] = []
        
    # Look for models first
    model_names = [model_name for model_name in dir(module_to_generate.models) if model_name[0].isupper()]
    for model_name in model_names:
        model_cls = getattr(module_to_generate.models, model_name)
        if hasattr(model_cls, "_attribute_map"):
            report["models"]["models"][model_name] = create_model_report(model_cls)
        elif issubclass(model_cls, Exception):  # If not, might be an exception
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
        op_content = {"name": op_name}
        op_cls = getattr(module_to_generate.operations, op_name)
        for op_attr_name in dir(op_cls):
            op_attr = getattr(op_cls, op_attr_name)
            if isinstance(op_attr, types.FunctionType) and not op_attr_name.startswith("_"):
                # Keep it
                func_content = create_report_from_func(op_attr)
                op_content.setdefault("functions", {})[op_attr_name] = func_content
        report["operations"][op_name] = op_content

    return report


def create_model_report(model_cls):
    result = {
        "name": model_cls.__name__,
    }
    # If _attribute_map, it's a model
    if hasattr(model_cls, "_attribute_map"):
        result["type"] = "Model"
        for attribute, conf in model_cls._attribute_map.items():
            attribute_validation = getattr(model_cls, "_validation", {}).get(attribute, {})

            result.setdefault("parameters", {})[attribute] = {
                "name": attribute,
                "properties": {
                    "type": conf["type"],
                    "required": attribute_validation.get("required", False),
                    "readonly": attribute_validation.get("readonly", False),
                },
            }
    elif issubclass(model_cls, Exception):  # If not, might be an exception
        result["type"] = "Exception"
    else:  # If not, it's an enum
        result["type"] = "Enum"
        result["values"] = list(model_cls.__members__)

    return result


def create_report_from_func(function_attr):
    func_content = {
        "name": function_attr.__name__,
        "metadata": getattr(function_attr, "metadata", {}),
        "parameters": [],
    }
    signature = inspect.signature(function_attr)
    for parameter_name in signature.parameters:
        if parameter_name == "self":
            continue
        if parameter_name == "custom_headers":
            break  # We reach Autorest generic
        parameter = signature.parameters[parameter_name]
        func_content["parameters"].append(
            {
                "name": parameter.name,
                "type": str(parameter.kind),
                "has_default_value": not (parameter.default is parameter.empty)
            }
        )
    return func_content


# given an input of a name, we need to return the appropriate relative diff between the sdk_root and the actual package directory
def resolve_package_directory(package_name):
    packages = [
        os.path.dirname(p)
        for p in (glob.glob("{}/setup.py".format(package_name)) + glob.glob("sdk/*/{}/setup.py".format(package_name)))
    ]

    if len(packages) > 1:
        print(
            "There should only be a single package matched in either repository structure. The following were found: {}".format(
                packages
            )
        )
        sys.exit(1)

    return packages[0]


def merge_report(report_paths):
    """Merge report on the given paths list."""
    if len(report_paths) == 1:
        raise ValueError("Doesn't make sense to merge a report if there is only one report....")

    merged_report = create_empty_report()
    for report in sorted(report_paths):
        with open(report, "r") as report_fd:
            report_json = json.load(report_fd)

        merged_report["models"]["enums"].update(report_json["models"]["enums"])
        merged_report["models"]["exceptions"].update(report_json["models"]["exceptions"])
        merged_report["models"]["models"].update(report_json["models"]["models"])
        merged_report["operations"].update(report_json["operations"])
    return merged_report


def main(
    input_parameter: str,
    version: Optional[str] = None,
    no_venv: bool = False,
    pypi: bool = False,
    last_pypi: bool = False,
    output: Optional[str] = None,
    metadata_path: Optional[str] = None,
):

    output_msg = output if output else "default folder"
    _LOGGER.info(
        f"Building code report of {input_parameter} for version {version} in {output_msg} ({no_venv}/{pypi}/{last_pypi})"
    )
    package_name, module_name = parse_input(input_parameter)
    path_to_package = resolve_package_directory(package_name)

    output_filename = ""
    result = []
    if (version or pypi or last_pypi) and not no_venv:
        if version:
            versions = [version]
        else:
            _LOGGER.info(f"Download versions of {package_name} on PyPI")
            from pypi_tools.pypi import PyPIClient

            client = PyPIClient()
            versions = [str(v) for v in client.get_ordered_versions(package_name)]
            _LOGGER.info(f"Got {versions}")
            if last_pypi:
                _LOGGER.info(f"Only keep last PyPI version")
                versions = [versions[-1]]

        for version in versions:
            _LOGGER.info(f"Installing version {version} of {package_name} in a venv")
            with create_venv_with_package(
                [f"{package_name}=={version}"]
            ) as venv, tempfile.TemporaryDirectory() as temp_dir:
                metadata_path = str(Path(temp_dir, f"metadata_{version}.json"))
                args = [
                    venv.env_exe,
                    __file__,
                    "--no-venv",
                    "--version",
                    version,
                    "--metadata",
                    metadata_path,
                    input_parameter,
                ]
                if output is not None:
                    args.append("--output=" + output)
                try:
                    subprocess.check_call(args)
                except subprocess.CalledProcessError:
                    # If it fail, just assume this version is too old to get an Autorest report
                    _LOGGER.warning(
                        f"Version {version} seems to be too old to build a report (probably not Autorest based)"
                    )
                # Files have been written by the subprocess
                with open(metadata_path, "r") as metadata_fd:
                    result.extend(json.load(metadata_fd)["reports_path"])
        # Files have been written by the subprocess
        return result

    modules = find_autorest_generated_folder(module_name)
    version = version or "latest"
    output_folder = Path(path_to_package) / Path("code_reports") / Path(version)
    output_folder.mkdir(parents=True, exist_ok=True)

    for module_name in modules:
        _LOGGER.info(f"Working on {module_name}")

        report = create_report(module_name)

        module_for_path = get_sub_module_part(package_name, module_name)
        if module_for_path:
            output_filename = output_folder / Path(module_for_path + ".json")
        else:
            if output is not None:
                output_filename = output
            else:
                output_filename = output_folder / Path("report.json")

        with open(output_filename, "w") as fd:
            json.dump(report, fd, indent=2)
            _LOGGER.info(f"Report written to {output_filename}")
        result.append(str(output_filename))

    if len(result) > 1:
        merged_report = merge_report(result)
        if output is not None:
            output_filename = output
        else:
            output_filename = output_folder / Path("merged_report.json")
        with open(output_filename, "w") as fd:
            json.dump(merged_report, fd, indent=2)
            _LOGGER.info(f"Merged report written to {output_filename}")
        result = [str(output_filename)]

    if metadata_path:
        metadata = {"reports_path": result}  # Prepare metadata
        with open(metadata_path, "w") as metadata_fd:
            _LOGGER.info(f"Writing metadata: {metadata}")
            json.dump(metadata, metadata_fd)

    return result


def find_autorest_generated_folder(module_prefix="azure"):
    """Find all Autorest generated code in that module prefix.
    This actually looks for a "models" package only (not file). We could be smarter if necessary.
    """
    _LOGGER.info(f"Looking for Autorest generated package in {module_prefix}")

    # Manually skip some namespaces for now
    if module_prefix in ["azure.cli", "azure.storage", "azure.servicemanagement", "azure.servicebus"]:
        _LOGGER.info(f"Skip {module_prefix}")
        return []

    result = []
    try:
        _LOGGER.debug(f"Try {module_prefix}")
        model_module = importlib.import_module(".models", module_prefix)
        # If not exception, we MIGHT have found it, but cannot be a file.
        # Keep continue to try to break it, file module have no __path__
        model_module.__path__
        _LOGGER.info(f"Found {module_prefix}")
        result.append(module_prefix)
    except (ModuleNotFoundError, AttributeError):
        # No model, might dig deeper
        prefix_module = importlib.import_module(module_prefix)
        for _, sub_package, ispkg in pkgutil.iter_modules(prefix_module.__path__, module_prefix + "."):
            if ispkg:
                result += find_autorest_generated_folder(sub_package)
    return result


def get_sub_module_part(package_name, module_name):
    """Assuming package is azure-mgmt-compute and module name is azure.mgmt.compute.v2018-08-01
    will return v2018-08-01
    """
    sub_module_from_package = package_name.replace("-", ".")
    if not module_name.startswith(sub_module_from_package):
        _LOGGER.warning(f"Submodule {module_name} does not start with package name {package_name}")
        return
    return module_name[len(sub_module_from_package) + 1 :]


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Code fingerprint building",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument("package_name", help="Package name.")
    parser.add_argument(
        "--version",
        "-v",
        dest="version",
        help="The version of the package you want. By default, latest and current branch.",
    )
    parser.add_argument(
        "--no-venv",
        dest="no_venv",
        action="store_true",
        help="If version is provided, this will assume the current accessible package is already this version. You should probably not use it.",
    )
    parser.add_argument(
        "--pypi",
        dest="pypi",
        action="store_true",
        help="If provided, build report for all versions on pypi of this package.",
    )
    parser.add_argument(
        "--last-pypi",
        dest="last_pypi",
        action="store_true",
        help="If provided, build report for last version on pypi of this package.",
    )
    parser.add_argument("--debug", dest="debug", action="store_true", help="Verbosity in DEBUG mode")
    parser.add_argument("--output", dest="output", help="Override output path.")
    parser.add_argument(
        "--metadata-path", dest="metadata", help="Write a metadata file about what happen. Mostly used for automation."
    )
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO)

    main(args.package_name, args.version, args.no_venv, args.pypi, args.last_pypi, args.output, args.metadata)
