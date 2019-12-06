#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import argparse
import os
import sys
import logging
from pip._internal.operations import freeze


def verify_packages(package_file_path):
    # this method verifies packages installed on machine is matching the expected package version
    # packages.txt file expects to have list of packages and version in format <package-name>==<version>

    packages = []
    with open(package_file_path, "r") as packages_file:
        packages = packages_file.readlines()
    packages = [p.replace('\n', '') for p in packages]

    # find installed packages
    installed_pkgs = [
        p for p in freeze.freeze() if p.startswith("azure-")
    ]

    missing_packages = [p for p in packages if p not in installed_pkgs]
    if missing_packages:
        logging.error("Version is not correct for packages: %s", missing_packages)
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
