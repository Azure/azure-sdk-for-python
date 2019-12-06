#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# Normally, this module will be executed as referenced as part of the devops build definitions.
# An enterprising user can easily glance over this and leverage for their own purposes.
import sys
import argparse
import logging
from os import path
from pip._internal.operations import freeze

# import common_task module
root_dir = path.abspath(path.join(path.abspath(__file__), "..", "..", ".."))
common_task_path = path.abspath(path.join(root_dir, "scripts", "devops_tasks"))
sys.path.append(common_task_path)
from common_tasks import process_glob_string
from tox_helper_tasks import get_package_details

EXCLUDED_PKGS = [
    "azure-common",
]

logging.getLogger().setLevel(logging.INFO)

# This script verifies installed package version and ensure all installed pacakges are dev build version


def get_installed_packages():
    # returns a map of installed azure sdk packages and version
    installed_pkgs = [p for p in freeze.freeze() if p.startswith("azure-")]
    valid_azure_packages = get_azure_packages()
    pkg_version_dict = dict(
        p.split("==")
        for p in installed_pkgs
        if p.split("==")[0] in valid_azure_packages
    )

    logging.info("Installed azure sdk packages: {}".format(pkg_version_dict))
    return pkg_version_dict


def get_azure_packages():
    # returns list of Azure SDK packages
    pkgs = process_glob_string("", root_dir)
    pkg_names = [
        path.basename(p) for p in pkgs if "mgmt" not in p and "-nspkg" not in p
    ]

    # exclude filtepre defined exclusion list of packages
    pkg_names = [p for p in pkg_names if p not in EXCLUDED_PKGS]
    return pkg_names


def is_dependent_pkg_dev_version(pkg_name):
    # Verify that all installed dependent packages of given package are of dev build version
    azure_pkgs = get_installed_packages()

    # filter for any package other than given package with non dev version
    non_devbuild = []
    for pkg, version in azure_pkgs.items():
        if pkg != pkg_name and ".dev" not in version:
            non_devbuild.append({pkg, version})

    if non_devbuild:
        logging.error("Found package[s] with non dev build version.")
        for p, v in non_devbuild:
            logging.error("{0} - {1}".format(p, v))
        return False

    logging.info("All azure sdk dependent packages are using dev build version")
    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Verify version of installed packages")

    parser.add_argument(
        "-t",
        "--target",
        dest="target_package",
        help="The target package directory on disk.",
        required=True,
    )

    args = parser.parse_args()
    # get target package name from target package path
    pkg_dir = path.abspath(args.target_package)
    pkg_name, _, ver = get_package_details(path.join(pkg_dir, "setup.py"))
    if not is_dependent_pkg_dev_version(pkg_name):
        sys.exit(1)
