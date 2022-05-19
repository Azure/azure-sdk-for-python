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
from unicodedata import name
from xmlrpc.client import Boolean
from tox_helper_tasks import (
    get_package_details,
    unzip_file_to_directory,
)
from verify_whl import cleanup, should_verify_package
from typing import List, Mapping, Any

logging.getLogger().setLevel(logging.INFO)

ALLOWED_ROOT_DIRECTORIES = ["azure", "tests", "samples", "examples"]

EXCLUDED_PYTYPE_PACKAGES = ["azure-keyvault", "azure", "azure-common"]


def get_root_directories_in_source(package_dir: str) -> List[str]:
    """
    Find all allowed directories in source path.
    """
    source_folders = [d for d in os.listdir(package_dir) if os.path.isdir(d) and d in ALLOWED_ROOT_DIRECTORIES]
    return source_folders


def get_root_directories_in_sdist(dist_dir: str, version: str) -> List[str]:
    """
    Given an unzipped sdist directory, extract which directories are present.
    """
    # find sdist zip file
    # extract sdist and find list of directories in sdist
    path_to_zip = glob.glob(os.path.join(dist_dir, "*{}*.zip".format(version)))[0]
    extract_location = os.path.join(dist_dir, "unzipped")
    # Cleanup any files in unzipped
    cleanup(extract_location)
    unzipped_dir = unzip_file_to_directory(path_to_zip, extract_location)
    sdist_folders = [d for d in os.listdir(unzipped_dir) if os.path.isdir(d)]
    return sdist_folders


def verify_sdist(package_dir: str, dist_dir: str, version: str) -> bool:
    """
    Compares the root directories in source against root directories present within a sdist.
    """

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


def verify_sdist_pytyped(
    pkg_dir: str, namespace: str, package_metadata: Mapping[str, Any], include_package_data: bool
) -> bool:
    """
    Takes a package directory and ensures that the setup.py within is correctly configured for py.typed files.
    """
    result = True
    manifest_location = os.path.join(pkg_dir, "MANIFEST.in")

    if include_package_data is None or False:
        logging.info(
            "Ensure that the setup.py present in directory {} has kwarg 'include_package_data' defined and set to 'True'."
        )
        result = False

    if package_metadata:
        if not any([key for key in package_metadata if "py.typed" in str(package_metadata[key])]):
            logging.info(
                "At least one value in the package_metadata map should include a reference to the py.typed file."
            )
            result = False

    if os.path.exists(manifest_location):
        with open(manifest_location, "r") as f:
            lines = f.readlines()
            result = any([include for include in lines if "py.typed" in include])

            if not result:
                logging.info("Ensure that the MANIFEST.in includes at least one path that leads to a py.typed file.")

    pytyped_file_path = os.path.join(pkg_dir, *namespace.split("."), "py.typed")
    if not os.path.exists(pytyped_file_path):
        logging.info(
            "The py.typed file must exist in the base namespace for your package. Traditionally this would mean the furthest depth, EG 'azure/storage/blob/py.typed'."
        )
        result = False

    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Verify directories included in sdist and contents in manifest file. Also ensures that py.typed configuration is correct within the setup.py."
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
    pkg_name, namespace, ver, package_data, include_package_data = get_package_details(
        os.path.join(pkg_dir, "setup.py")
    )

    if should_verify_package(pkg_name):
        logging.info("Verifying sdist for package [%s]", pkg_name)
        if verify_sdist(pkg_dir, args.dist_dir, ver):
            logging.info("Verified sdist for package [%s]", pkg_name)
        else:
            logging.info("Failed to verify sdist for package [%s]", pkg_name)
            exit(1)

    if pkg_name not in EXCLUDED_PYTYPE_PACKAGES and "-nspkg" not in pkg_name:
        logging.info("Verifying presence of py.typed: [%s]", pkg_name)
        if verify_sdist_pytyped(pkg_dir, namespace, package_data, include_package_data):
            logging.info("Py.typed setup.py kwargs are set properly: [%s]", pkg_name)
        else:
            logging.info("Verified py.typed [%s]. Check messages above.", pkg_name)
            exit(1)
