#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import json
import logging
import os.path
from pathlib import Path
import sys

import requests
from cookiecutter.main import cookiecutter
from swaggertosdk.SwaggerToSdkNewCLI import generate_code

_LOGGER = logging.getLogger(__name__)

def guess_service_info_from_path(spec_path):
    """Guess Python Autorest options based on the spec path.

    Expected path:
    specification/compute/resource-manager/readme.md
    """
    spec_path = spec_path.lower()
    spec_path = spec_path[spec_path.index("specification"):] # Might raise and it's ok
    split_spec_path = spec_path.split("/")

    rp_name = split_spec_path[1]
    is_arm = split_spec_path[2] == "resource-manager"

    return {
        "rp_name": rp_name,
        "is_arm": is_arm
    }

def get_data(spec_path):
    if spec_path.startswith("http"):
        response = requests.get(spec_path)
        response.raise_for_status()
        return response.text
    else:
        with open(spec_path, "r") as fd:
            return fd.read()        

def guess_service_info_from_content(spec_path):
    data = get_data(spec_path)

    lines = data.splitlines()
    while lines:
        line = lines.pop(0)
        if line.startswith("# "):
            pretty_name = line[2:]
            break
    else:
        raise ValueError("Unable to find main title in this README")
    return {
        'pretty_name': pretty_name
    }        

def guess_service_info(spec_path):
    result = guess_service_info_from_content(spec_path)
    result.update(guess_service_info_from_path(spec_path))
    return result

def create_swagger_to_sdk_conf(spec_path, service_info, autorest_options):
    type_str = ".mgmt" if service_info["is_arm"] else ".data"
    return {
        "{}{}".format(service_info["rp_name"], type_str): {
            "markdown": spec_path[spec_path.index("specification"):],
            "autorest_options": {
                "namespace": autorest_options["namespace"],
                "package-version": autorest_options["package-version"],
                "package-name": autorest_options["package-name"]
            },
            "output_dir": "{}/{}".format(autorest_options["package-name"], autorest_options["package-name"].replace("-","/")),
            "build_dir": autorest_options["package-name"]
        }
    }

def create_package_service_mapping(spec_path, service_info, autorest_options):
    type_str = "Management" if service_info["is_arm"] else "Client"
    return {
        autorest_options["package-name"]: {
            "service_name": service_info["pretty_name"],
            "category": type_str,
            "namespaces": [
                autorest_options["namespace"]
            ]
        }
    }

def main(spec_path):
    service_info = guess_service_info(spec_path)

    autorest_options = {}
    if service_info["is_arm"]:
        autorest_options["azure-arm"] = True
        namespace = "azure.mgmt." + service_info["rp_name"]
        package_name = "azure-mgmt-" + service_info["rp_name"]
    else:
        autorest_options["add-credentials"] = True
        namespace = "azure." + service_info["rp_name"]
        package_name = "azure-" + service_info["rp_name"]

    # Create output folder
    output_dir = Path(".").resolve() / Path(package_name)
    output_dir.mkdir(exist_ok=True)
    _LOGGER.info("Output folder: %s", output_dir)

    _LOGGER.info("Calling Autorest")
    autorest_options.update({
        "use": "@microsoft.azure/autorest.python@preview",
        "license-header": "MICROSOFT_MIT_NO_VERSION",
        "payload-flattening-threshold": 2,
        "python": "",
        "package-version": "0.1.0",
        "python.output-folder": output_dir
    })

    autorest_options["namespace"] = namespace
    autorest_options["package-name"] = package_name

    generate_code(
        input_file=Path(spec_path) if not spec_path.startswith("http") else spec_path,
        output_dir=output_dir,
        global_conf={"autorest_options": autorest_options},
        local_conf={}
    )

    _LOGGER.info("Rebuilding packaging with Cookiecutter")
    pretty_name = service_info["pretty_name"]
    cookiecutter('gh:Azure/cookiecutter-azuresdk-pypackage',
                 no_input=True,
                 extra_context={
                     'package_name': package_name,
                     'package_pprint_name': pretty_name
                 },
                 overwrite_if_exists=True
    )

    swagger_to_sdk = Path("swagger_to_sdk_config.json")
    if swagger_to_sdk.exists():
        _LOGGER.info("Updating swagger_to_sdk_config.json")
        entry = create_swagger_to_sdk_conf(spec_path, service_info, autorest_options)
        with swagger_to_sdk.open() as fd:
            data_conf = json.load(fd)
            data_conf["projects"].update(entry)
        with swagger_to_sdk.open("w") as fd:
            json.dump(data_conf, fd, indent=2, sort_keys=True)

    package_service_mapping = Path("package_service_mapping.json")
    if package_service_mapping:
        _LOGGER.info("Updating package_service_mapping.json")
        entry = create_package_service_mapping(spec_path, service_info, autorest_options)
        with package_service_mapping.open() as fd:
            data_conf = json.load(fd)
            data_conf.update(entry)
        with package_service_mapping.open("w") as fd:
            json.dump(data_conf, fd, indent=2, sort_keys=True)

    _LOGGER.info("Done! Enjoy your Python SDK!!")

if __name__ == "__main__":
    logging.basicConfig()
    logging.getLogger().setLevel(logging.INFO)

    main(sys.argv[1])