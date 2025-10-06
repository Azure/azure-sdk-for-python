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
import tempfile
import subprocess
from unicodedata import name
from xmlrpc.client import Boolean
from packaging.version import Version
from tox_helper_tasks import (
    unzip_file_to_directory,
)
from verify_whl import cleanup, should_verify_package, get_prior_version, verify_prior_version_metadata, get_path_to_zip
from typing import List, Mapping, Any, Dict, Optional

from ci_tools.parsing import ParsedSetup, extract_package_metadata
from ci_tools.functions import verify_package_classifiers
from pypi_tools.pypi import retrieve_versions_from_pypi

logging.getLogger().setLevel(logging.INFO)

ALLOWED_ROOT_DIRECTORIES = ["azure", "tests", "samples", "examples"]

EXCLUDED_PYTYPE_PACKAGES = ["azure-keyvault", "azure", "azure-common"]

EXCLUDED_CLASSIFICATION_PACKAGES = []


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
    path_to_zip = get_path_to_zip(dist_dir, version, package_type="*.tar.gz")
    # extract sdist and find list of directories in sdist
    extract_location = os.path.join(dist_dir, "unzipped")
    # Cleanup any files in unzipped
    cleanup(extract_location)
    unzipped_dir = unzip_file_to_directory(path_to_zip, extract_location)
    sdist_folders = [d for d in os.listdir(unzipped_dir) if os.path.isdir(d)]
    return sdist_folders


def verify_sdist(package_dir: str, dist_dir: str, parsed_pkg: ParsedSetup) -> bool:
    """
    Compares the root directories in source against root directories present within a sdist.
    Also verifies metadata compatibility with prior stable version.
    """
    version = parsed_pkg.version
    # Extract metadata from zip file to ensure we're checking the built package metadata
    metadata: Dict[str, Any] = extract_package_metadata(get_path_to_zip(dist_dir, version, package_type="*.tar.gz"))

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

    # Verify metadata compatibility with prior version
    prior_version = get_prior_version(parsed_pkg.name, version)
    if prior_version:
        if not verify_prior_version_metadata(parsed_pkg.name, prior_version, metadata, package_type="*.tar.gz"):
            return False

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
            if not any([include for include in lines if "py.typed" in include]):
                logging.info("Ensure that the MANIFEST.in includes at least one path that leads to a py.typed file.")
                result = False

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
    pkg_details = ParsedSetup.from_path(pkg_dir)

    error_occurred = False

    if should_verify_package(pkg_details.name):
        logging.info(f"Verifying sdist folders and metadata for package {pkg_details.name}")
        if verify_sdist(pkg_dir, args.dist_dir, pkg_details):
            logging.info(f"Verified sdist folders and metadata for package {pkg_details.name}")
        else:
            logging.error(f"Failed to verify sdist folders and metadata for package {pkg_details.name}")
            error_occurred = True

    if pkg_details.name not in EXCLUDED_PYTYPE_PACKAGES and "-nspkg" not in pkg_details.name and "-mgmt" not in pkg_details.name:
        logging.info(f"Verifying presence of py.typed: {pkg_details.name}")
        if verify_sdist_pytyped(pkg_dir, pkg_details.namespace, pkg_details.package_data, pkg_details.include_package_data):
            logging.info(f"Py.typed setup.py kwargs are set properly: {pkg_details.name}")
        else:
            logging.error(f"Py.typed verification failed for package {pkg_details.name}. Check messages above.")
            error_occurred = True

    if pkg_details.name not in EXCLUDED_CLASSIFICATION_PACKAGES and "-nspkg" not in pkg_details.name:
        logging.info(f"Verifying package classifiers: {pkg_details.name}")

        status, message = verify_package_classifiers(pkg_details.name, pkg_details.version, pkg_details.classifiers)
        if status:
            logging.info(f"Package classifiers are set properly: {pkg_details.name}")
        else:
            logging.error(f"{message}")
            error_occurred = True

    if error_occurred:
        logging.error(f"{pkg_details.name} failed sdist verification. Check outputs above.")
        exit(1)