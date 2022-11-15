#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# Below are common methods for the devops build steps. This is the common location that will be updated with
# package targeting during release.

import argparse
from os import path
from packaging.version import parse

from ci_tools.versioning.version_shared import (
    get_packages,
    set_version_py,
    set_dev_classifier,
)

from ci_tools.variables import discover_repo_root
from ci_tools.functions import process_requires

MAX_R_DIGITS = 3


def format_build_id(build_id: str) -> str:
    split_build_id = build_id.split(".", 1)
    r = split_build_id[1]
    if len(r) > MAX_R_DIGITS or int(r) < 0 or int(r) > 1000:
        raise ValueError("Build number suffix is out of acceptable range for package sorting (0 < r < 1000)")
    return "".join([split_build_id[0], r.zfill(MAX_R_DIGITS)])


def get_dev_version(current_version: str, build_id: str) -> str:
    parsed_version = parse(current_version)
    return "{0}a{1}".format(parsed_version.base_version, build_id)


def is_in_service(sdk_path: str, setup_py_location: str, service_name: str) -> bool:
    sdk_prefix = path.normpath(sdk_path)
    normalized_setup = path.normpath(setup_py_location)

    return normalized_setup.startswith(path.join(sdk_prefix, service_name))


def version_set_dev_main() -> None:
    parser = argparse.ArgumentParser(
        description="Increments version for a given package name based on the released version"
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
        help="name of the service for which to set the dev build id (e.g. keyvault)",
    )
    parser.add_argument(
        "-b",
        "--build-id",
        required=True,
        help="id of the build (generally of the form YYYYMMDD.r) dot characters(.) will be removed",
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

    target_packages = get_packages(args, root_dir=root_dir)
    build_id = format_build_id(args.build_id)

    if not target_packages:
        print("No packages found")

    for target_package in target_packages:
        try:
            new_version = get_dev_version(target_package.version, build_id)
            print("{0}: {1} -> {2}".format(target_package.name, target_package.version, new_version))

            process_requires(target_package.setup_filename)
            set_version_py(target_package.setup_filename, new_version)
            set_dev_classifier(target_package.setup_filename, new_version)
        except:
            print("Could not set dev version for package: {0}".format(target_package.name))
