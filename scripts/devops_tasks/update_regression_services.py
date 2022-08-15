#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import os
import argparse
import pdb
import json

import pkg_resources
from test_regression import find_package_dependency, AZURE_GLOB_STRING

from ci_tools.functions import discover_targeted_packages

root_dir = os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "..", ".."))


def parse_service(pkg_path):
    path = os.path.normpath(pkg_path)
    path = path.split(os.sep)

    current_segment = ""

    for path_segment in reversed(path):
        if path_segment == "sdk":
            return current_segment
        current_segment = path_segment

    return pkg_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Updates a given regression json file with a narrowed set of services that are dependent on the targeted service/glob string."
    )

    parser.add_argument(
        "glob_string",
        nargs="?",
        help=(
            "A comma separated list of glob strings that will target the top level directories that contain packages."
            'Examples: All = "azure*", Single = "azure-keyvault", Targeted Multiple = "azure-keyvault,azure-mgmt-resource"'
        ),
    )

    parser.add_argument(
        "--service",
        help=("Name of service directory (under sdk/) to test." "Example: --service applicationinsights"),
    )

    parser.add_argument(
        "--json",
        help=("Location of the matrix configuration which has a DependentServices dimension object."),
    )

    args = parser.parse_args()

    if args.service:
        service_dir = os.path.join("sdk", args.service)
        target_dir = os.path.join(root_dir, service_dir)
    else:
        service_dir = "sdk"
        target_dir = root_dir

    targeted_packages = [
        os.path.basename(path_name) for path_name in discover_targeted_packages(args.glob_string, target_dir, "", "Regression")
    ]
    deps = find_package_dependency(AZURE_GLOB_STRING, root_dir, service_dir)
    package_set = []

    for key in list(deps.keys()):
        if key not in targeted_packages:
            deps.pop(key)
        else:
            package_set.extend(deps[key])

    service_list = set([parse_service(pkg) for pkg in package_set])

    try:
        with open(args.json, "r") as f:
            settings_json = f.read()
    except FileNotFoundError as f:
        print("The json file {} cannot be loaded.".format(args.json))
        exit(1)

    if len(service_list) > 0: 
        settings = json.loads(settings_json)
        settings["matrix"]["DependentService"] = list(service_list)
        json_result = json.dumps(settings)

        with open(args.json, "w") as f:
            f.write(json_result)
    else:
        with open(args.json, "w") as f:
            f.write("{}")