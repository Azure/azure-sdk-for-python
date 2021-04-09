#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import argparse
import os
import sys
import logging
from os import path

# import common_task module
root_dir = path.abspath(path.join(path.abspath(__file__), "..", "..", ".."))
common_task_path = path.abspath(path.join(root_dir, "scripts", "devops_tasks"))
sys.path.append(common_task_path)
from common_tasks import get_installed_packages

def verify_packages(package_file_path):
    # this method verifies packages installed on machine is matching the expected package version
    # packages.txt file expects to have list of packages and version in format <package-name>==<version>

    packages = []
    with open(package_file_path, "r") as packages_file:
        packages = packages_file.readlines()
    packages = [p.replace('\n', '') for p in packages]

    # packages.txt is created by package installation script. But this script can be reused to verify installed packages
    # Add a sanity check to ensure content in file is in expected format
    invalid_lines = [p for p in packages if '==' not in p]
    if invalid_lines:
        logging.error("packages.txt has package details in invalid format. Expected format is <package-name>==<version>")
        sys.exit(1)

    # find installed and expected packages
    installed = dict(p.split('==') for p in get_installed_packages() if "==" in p)
    expected = dict(p.split('==') for p in packages)

    missing_packages = [pkg for pkg in expected.keys() if installed.get(pkg) != expected.get(pkg)]

    if missing_packages:
        logging.error("Version is incorrect for following package[s]")
        for package in missing_packages:
            logging.error("%s, Expected[%s], Installed[%s]", package, expected[package], installed[package])
        sys.exit(1)
    else:
        logging.info("Verified package version")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Install either latest or minimum version of dependent packages."
    )

    parser.add_argument(
        "-f",
        "--packages-file",
        dest="packages_file",
        help="Path to a file that has list of packages and version to verify",
        required=True,
    )

    args = parser.parse_args()
    if os.path.exists(args.packages_file):
        verify_packages(args.packages_file)
