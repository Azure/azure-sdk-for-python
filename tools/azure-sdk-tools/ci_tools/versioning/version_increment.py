#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# Below are common methods for the devops build steps. This is the common location that will be updated with
# package targeting during release.
import os
import argparse
from packaging.version import parse
import logging

from ci_tools.versioning.version_shared import (
    get_packages,
    set_version_py,
    set_dev_classifier,
    update_change_log,
)
from ci_tools.variables import discover_repo_root

logging.getLogger().setLevel(logging.INFO)


def increment_version(old_version):
    parsed_version = parse(old_version)
    release = parsed_version.release

    if parsed_version.is_prerelease:
        prerelease_version = parsed_version.pre[1]
        return "{0}.{1}.{2}b{3}".format(release[0], release[1], release[2], prerelease_version + 1)

    return "{0}.{1}.{2}".format(release[0], release[1], release[2] + 1)

def version_increment_main():
    parser = argparse.ArgumentParser(
        description="Increments version for a given package name based on the released version"
    )
    parser.add_argument(
        "--package-name",
        required=True,
        help="name of package (accetps both formats: azure-service-package and azure_service_pacage)",
    )
    parser.add_argument(
        dest="glob_string",
        nargs="?",
        help=(
            "A comma separated list of glob strings that will target the top level directories that contain packages."
            'Examples: All = "azure-*", Single = "azure-keyvault", Targeted Multiple = "azure-keyvault,azure-mgmt-resource"'
        ),
    )
    parser.add_argument(
        "--service",
        required=True,
        help="name of the service for which to set the dev build id (e.g. keyvault)",
    )
    parser.add_argument(
        "--repo",
        default=None,
        dest="repo",
        help=(
            "Where is the start directory that we are building against? If not provided, the current working directory will be used. Please ensure you are within the azure-sdk-for-python repository."
        ),
    )

    args = parser.parse_args()
    root_dir = args.repo or discover_repo_root()

    package_name = args.package_name.replace("_", "-")

    packages = get_packages(args, package_name, additional_excludes=["mgmt", "-nspkg"], root_dir=root_dir)

    package_map = {pkg[1][0]: pkg for pkg in packages}

    if package_name not in package_map:
        raise ValueError("Package name not found: {}".format(package_name))

    target_package = package_map[package_name]

    new_version = increment_version(target_package[1][1])
    print("{0}: {1} -> {2}".format(package_name, target_package[1][1], new_version))

    set_version_py(target_package[0], new_version)
    set_dev_classifier(target_package[0], new_version)
    update_change_log(target_package[0], new_version, args.service, args.package_name, True, False, root_dir=root_dir)
