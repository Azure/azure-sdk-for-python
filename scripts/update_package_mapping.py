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


def create_package_service_mapping(service_info, autorest_options):
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

def main(package_name):

    service_info = {
        "is_arm": package_name.startswith("azure-mgmt"),
        "pretty_name": package_name  # FIXME
    }
    autorest_options = {
        "package-name": package_name,
        "namespace": package_name.replace("-", ".")
    }

    package_service_mapping = Path("package_service_mapping.json")
    if package_service_mapping:
        _LOGGER.info("Updating package_service_mapping.json")
        entry = create_package_service_mapping(service_info, autorest_options)
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