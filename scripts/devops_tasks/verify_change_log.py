#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# Normally, this module will be executed as referenced as part of the devops build definitions.
# An enterprising user can easily glance over this and leverage for their own purposes.

import argparse
import sys
import os
import logging

from common_tasks import process_glob_string, parse_setup, run_check_call

excluded_packages = ["azure"]

logging.getLogger().setLevel(logging.INFO)

root_dir = os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "..", ".."))
psscript = os.path.join(root_dir, "scripts", "devops_tasks", "find_change_log.ps1")


def find_change_log(targeted_package, version):
    # Execute powershell script to find a matching version in history.md
    command_array = ["pwsh"]
    command_array.append("-File {}".format(psscript))
    command_array.append("-workingDir {}".format(targeted_package))
    command_array.append("-version {}".format(version))
    command_array.append("set-ExecutionPolicy Unrestricted")

    allowed_return_codes = []

    # Execute powershell script to verify version
    er_result = run_check_call(
        command_array, root_dir, allowed_return_codes, True, False
    )

    if er_result:
        logging.error(
            "Failed to find version in change log for package {}".format(
                targeted_package
            )
        )
        return False

    return True


def verify_packages(targeted_packages):
    # run the build and distribution
    change_log_missing = {}

    for package in targeted_packages:
        # Parse setup.py using common helper method to get version and package name
        pkg_name, version, _, _ = parse_setup(package)

        # Skip management packages
        if "-mgmt" in pkg_name or pkg_name in excluded_packages:
            continue

        if not find_change_log(package, version):
            logging.error(
                "Change log is not updated for package {0}, version {1}".format(
                    pkg_name, version
                )
            )
            change_log_missing[pkg_name] = version

    return change_log_missing


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Verifies latest version is updated in history.md file, Called from DevOps YAML Pipeline"
    )

    parser.add_argument(
        "glob_string",
        nargs="?",
        help=(
            "A comma separated list of glob strings that will target the top level directories that contain packages. "
            'Examples: All == "azure-*", Single = "azure-keyvault"'
        ),
    )

    parser.add_argument(
        "--service",
        help=(
            "Name of service directory (under sdk/) to build."
            "Example: --service applicationinsights"
        ),
    )

    parser.add_argument(
        "--pkgfilter",
        default="",
        dest="package_filter_string",
        help=(
            "An additional string used to filter the set of artifacts by a simple CONTAINS clause."
        ),
    )

    args = parser.parse_args()

    # We need to support both CI builds of everything and individual service
    # folders. This logic allows us to do both.
    if args.service:
        service_dir = os.path.join("sdk", args.service)
        target_dir = os.path.join(root_dir, service_dir)
    else:
        target_dir = root_dir

    targeted_packages = process_glob_string(
        args.glob_string, target_dir, args.package_filter_string
    )
    change_missing = verify_packages(targeted_packages)
    if len(change_missing) > 0:
        logging.error("Below packages do not have change log in history.md")
        logging.error("***************************************************")
        for pkg_name in change_missing.keys():
            logging.error("{0} - {1}".format(pkg_name, change_missing[pkg_name]))

        sys.exit(1)
