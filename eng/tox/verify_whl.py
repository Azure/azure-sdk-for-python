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
from packaging.version import Version
from typing import Dict, Any, Optional
from tox_helper_tasks import (
    unzip_file_to_directory,
)

from ci_tools.parsing import ParsedSetup
from pypi_tools.pypi import retrieve_versions_from_pypi

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

    # Cleanup any existing stale files if any and rename whl file to zip for extraction later
    zip_file = path_to_whl.replace(".whl", ".zip")
    cleanup(zip_file)
    os.rename(path_to_whl, zip_file)

    # Extrat renamed gz file to unzipped folder
    extract_location = os.path.join(dist_dir, "unzipped")
    cleanup(extract_location)
    unzip_file_to_directory(zip_file, extract_location)
    return extract_location


def verify_whl_root_directory(dist_dir, expected_top_level_module, version):
    # This method ensures root directory in whl is the directory indicated by our top level namespace
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


def get_prior_stable_version(package_name: str, current_version: str) -> Optional[str]:
    """Get the latest stable version from PyPI that is prior to the current version."""
    try:
        all_versions = retrieve_versions_from_pypi(package_name)
        current_ver = Version(current_version)
        stable_versions = [Version(v) for v in all_versions
                          if not Version(v).is_prerelease and Version(v) < current_ver]
        return str(max(stable_versions)) if stable_versions else None
    except Exception:
        return None


def download_and_parse_prior_version(package_name: str, prior_version: str) -> Optional[ParsedSetup]:
    """Download the prior version wheel and parse it with ParsedSetup."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        try:
            subprocess.run([
                "pip", "download", "--no-deps", "--only-binary=:all:",
                f"{package_name}=={prior_version}", "--dest", tmp_dir
            ], check=True, capture_output=True)
            whl_files = glob.glob(os.path.join(tmp_dir, "*.whl"))
            return ParsedSetup.from_path(whl_files[0]) if whl_files else None
        except Exception:
            return None


def verify_metadata_compatibility(current_metadata: Dict[str, Any], prior_metadata: Dict[str, Any]) -> bool:
    """Verify that all keys from prior version metadata are present in current version."""
    if not prior_metadata:
        return True
    if not current_metadata:
        return False
    return set(prior_metadata.keys()).issubset(set(current_metadata.keys()))


def verify_whl(dist_dir: str, expected_top_level_module: str, parsed_pkg: ParsedSetup) -> bool:
    """
    Verifies root directory in whl and metadata compatibility with prior stable version.
    """
    # Verify root directory
    if not verify_whl_root_directory(dist_dir, expected_top_level_module, parsed_pkg.version):
        return False

    # Verify metadata compatibility with prior version
    metadata: Dict[str, Any] = parsed_pkg.metadata
    prior_version = get_prior_stable_version(parsed_pkg.name, parsed_pkg.version)
    if prior_version:
        prior_parsed_pkg = download_and_parse_prior_version(parsed_pkg.name, prior_version)
        if prior_parsed_pkg:
            prior_metadata: Dict[str, Any] = prior_parsed_pkg.metadata
            if not verify_metadata_compatibility(metadata, prior_metadata):
                return False

    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Verify directories included in whl, contents in manifest file, and metadata compatibility"
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
    top_level_module = pkg_details.namespace.split('.')[0]

    if should_verify_package(pkg_details.name):
        logging.info("Verifying whl for package: [%s]", pkg_details.name)
        if verify_whl(args.dist_dir, top_level_module, pkg_details):
            logging.info("Verified whl for package: [%s]", pkg_details.name)
        else:
            logging.error("Failed to verify whl for package: [%s]", pkg_details.name)
            exit(1)
