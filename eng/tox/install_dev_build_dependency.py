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
from subprocess import check_call

# import common_task module
root_dir = path.abspath(path.join(path.abspath(__file__), "..", "..", ".."))
common_task_path = path.abspath(path.join(root_dir, "scripts", "devops_tasks"))
sys.path.append(common_task_path)

from common_tasks import get_installed_packages
from ci_tools.functions import discover_targeted_packages
from ci_tools.parsing import ParsedSetup

EXCLUDED_PKGS = [
    "azure-common",
]

# index URL to devops feed
DEV_INDEX_URL = "https://pkgs.dev.azure.com/azure-sdk/public/_packaging/azure-sdk-for-python/pypi/simple"

logging.getLogger().setLevel(logging.INFO)

# This script verifies installed package version and ensure all installed pacakges are dev build version


def get_installed_azure_packages(pkg_name_to_exclude):
    # This method returns a list of installed azure sdk packages
    installed_pkgs = [
        p.split("==")[0] for p in get_installed_packages() if p.startswith("azure-")
    ]

    # Get valid list of Azure SDK packages in repo
    pkgs = discover_targeted_packages("", root_dir)
    valid_azure_packages = [
        path.basename(p) for p in pkgs if "mgmt" not in p and "-nspkg" not in p
    ]

    # Filter current package and any exlcuded package
    pkg_names = [
        p
        for p in installed_pkgs
        if p in valid_azure_packages
        and p != pkg_name_to_exclude
        and p not in EXCLUDED_PKGS
    ]

    logging.info("Installed azure sdk packages: %s", pkg_names)
    return pkg_names


def uninstall_packages(packages):
    # This method uninstall list of given packages so dev build version can be reinstalled
    commands = [
        sys.executable,
        "-m",
        "pip",
        "uninstall",
    ]

    logging.info("Uninstalling packages: %s", packages)
    commands.extend(packages)
    # Pass Uninstall confirmation
    commands.append("--yes")
    check_call(commands)
    logging.info("Uninstalled packages")


def install_packages(packages):
    # install list of given packages from devops feed

    commands = [
        sys.executable,
        "-m",
        "pip",
        "install",
    ]

    logging.info("Installing dev build version for packages: %s", packages)
    commands.extend(packages)
    commands.extend(
        [
            "--index-url",
            DEV_INDEX_URL,
        ]
    )
    # install dev build of azure packages
    check_call(commands)


def install_dev_build_packages(pkg_name_to_exclude):
    # Uninstall GA version and reinstall dev build version of dependent packages
    azure_pkgs = get_installed_azure_packages(pkg_name_to_exclude)
    uninstall_packages(azure_pkgs)
    install_packages(azure_pkgs)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Install dev build version of dependent packages for current package"
    )

    parser.add_argument(
        "-t",
        "--target",
        dest="target_package",
        help="The target package directory on disk.",
        required=True,
    )

    args = parser.parse_args()

    if args.target_package:
        pkg_dir = path.abspath(args.target_package)
        pkg_details = ParsedSetup.from_path(pkg_dir)
        install_dev_build_packages(pkg_details.name)


