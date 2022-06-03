#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# This script is used to verify that root directory in whl is azure and to verify manifest so all directories in soruce is included in sdist
import argparse
import logging
import os
import glob
import shutil
from tox_helper_tasks import (
    get_package_details,
    unzip_sdist_to_directory,
    move_and_rename,
    unzip_file_to_directory,
)

logging.getLogger().setLevel(logging.INFO)

# Excluding auto generated applicationinsights and loganalytics
EXCLUDED_PACKAGES = [
    "azure",
    "azure-mgmt",
    "azure-common",
    "azure-applicationinsights",
    "azure-loganalytics",
]


def extract_whl(dist_dir, version):
    # Find whl for the package
    path_to_whl = glob.glob(os.path.join(dist_dir, "*{}*.whl".format(version)))[0]

    # Cleanup any existing stale files if any and rename whl file to tar.gz
    zip_file = path_to_whl.replace(".whl", ".tar.gz")
    cleanup(zip_file)
    os.rename(path_to_whl, zip_file)

    # Extrat renamed gz file to unzipped folder
    extract_location = os.path.join(dist_dir, "unzipped")
    cleanup(extract_location)
    unzip_file_to_directory(zip_file, extract_location)
    return extract_location


def verify_whl_root_directory(dist_dir, expected_top_level_module, version):
    # This method ensures root directory in whl is the directoy indicated by our top level namespace
    extract_location = extract_whl(dist_dir, version)
    root_folders = os.listdir(extract_location)

    # check for non 'azure' folder as root folder
    non_azure_folders = [
        d for d in root_folders if d != expected_top_level_module and not d.endswith(".dist-info")
    ]
    if non_azure_folders:
        logging.error(
            "whl has following incorrect directory at root level [%s]",
            non_azure_folders,
        )
        return False
    else:
        return True


def cleanup(path):
    # This function deletes all files and cleanup the directory if it exists
    if os.path.exists(path):
        if os.path.isdir(path):
            shutil.rmtree(path)
        else:
            os.remove(path)


def should_verify_package(package_name):
    return (
        package_name not in EXCLUDED_PACKAGES
        and "nspkg" not in package_name
        and "-mgmt" not in package_name
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Verify directories included in whl and contents in manifest file"
    )

    parser.add_argument(
        "-t",
        "--target",
        dest="target_package",
        help="The target package directory on disk.",
        required=True,
    )

    parser.add_argument(
        "-d",
        "--dist_dir",
        dest="dist_dir",
        help="The dist location on disk. Usually /tox/dist.",
        required=True,
    )

    args = parser.parse_args()

    # get target package name from target package path
    pkg_dir = os.path.abspath(args.target_package)
    pkg_name, namespace, ver, _, _ = get_package_details(os.path.join(pkg_dir, "setup.py"))

    top_level_module = namespace.split('.')[0]

    if should_verify_package(pkg_name):
        logging.info("Verifying root directory in whl for package: [%s]", pkg_name)
        if verify_whl_root_directory(args.dist_dir, top_level_module, ver):
            logging.info("Verified root directory in whl for package: [%s]", pkg_name)
        else:
            logging.info(
                "Failed to verify root directory in whl for package: [%s]", pkg_name
            )
            exit(1)
