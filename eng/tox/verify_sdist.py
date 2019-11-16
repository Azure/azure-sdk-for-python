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
from verify_whl import cleanup, should_verify_package

logging.getLogger().setLevel(logging.INFO)

ALLOWED_ROOT_DIRECTORIES = ["azure", "tests", "samples", "examples"]


def get_root_directories_in_source(package_dir):
    # find all allowed directories in source path
    source_folders = [
        d
        for d in os.listdir(package_dir)
        if os.path.isdir(d) and d in ALLOWED_ROOT_DIRECTORIES
    ]
    return source_folders


def get_root_directories_in_sdist(dist_dir, version):
    # find sdist zip file
    # extract sdist and find list of directories in sdist
    path_to_zip = glob.glob(os.path.join(dist_dir, "*{}*.zip".format(version)))[0]
    extract_location = os.path.join(dist_dir, "unzipped")
    # Cleanup any files in unzipped
    cleanup(extract_location)
    unzipped_dir = unzip_file_to_directory(path_to_zip, extract_location)
    sdist_folders = [d for d in os.listdir(unzipped_dir) if os.path.isdir(d)]
    return sdist_folders


def verify_sdist(package_dir, dist_dir, version):
    # This function compares the root directories in source against root directories sdist

    source_folders = get_root_directories_in_source(package_dir)
    sdist_folders = get_root_directories_in_sdist(dist_dir, version)

    # compare folders in source directory against unzipped sdist
    missing_folders = set(source_folders) - set(sdist_folders)
    for folder in missing_folders:
        logging.error("Source folder [%s] is not included in sdist", folder)

    if missing_folders:
        logging.info("Directories in source: %s", source_folders)
        logging.info("Directories in sdist: %s", sdist_folders)
        return False
    else:
        return True


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
    pkg_name, _, ver = get_package_details(os.path.join(pkg_dir, "setup.py"))

    if should_verify_package(pkg_name):
        logging.info("Verifying sdist for package [%s]", pkg_name)
        if verify_sdist(pkg_dir, args.dist_dir, ver):
            logging.info("Verified sdist for package [%s]", pkg_name)
        else:
            logging.info("Failed to verify sdist for package [%s]", pkg_name)
            exit(1)
