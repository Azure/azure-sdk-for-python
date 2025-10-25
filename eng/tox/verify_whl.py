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

from ci_tools.parsing import ParsedSetup, extract_package_metadata
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


def verify_whl_root_directory(dist_dir: str, expected_top_level_module: str, parsed_pkg: ParsedSetup) -> bool:
    # Verify metadata compatibility with prior version
    version: str = parsed_pkg.version
    metadata: Dict[str, Any] = extract_package_metadata(get_path_to_zip(dist_dir, version))
    prior_version = get_prior_version(parsed_pkg.name, version)
    if prior_version:
        if not verify_prior_version_metadata(parsed_pkg.name, prior_version, metadata):
            return False

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
    )


def get_prior_version(package_name: str, current_version: str) -> Optional[str]:
    """Get prior stable version if it exists, otherwise get prior preview version, else return None."""
    try:
        all_versions = retrieve_versions_from_pypi(package_name)
        current_ver = Version(current_version)
        prior_versions = [Version(v) for v in all_versions if Version(v) < current_ver]
        if not prior_versions:
            return None

        # Try stable versions first
        stable_versions = [v for v in prior_versions if not v.is_prerelease]
        if stable_versions:
            return str(max(stable_versions))

        # Fall back to preview versions
        preview_versions = [v for v in prior_versions if v.is_prerelease]
        return str(max(preview_versions)) if preview_versions else None
    except Exception:
        return None


def verify_prior_version_metadata(package_name: str, prior_version: str, current_metadata: Dict[str, Any], package_type: str = "*.whl") -> bool:
    """Download prior version and verify metadata compatibility."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        try:
            is_binary = "--only-binary=:all:" if package_type == "*.whl" else "--no-binary=:all:"
            subprocess.run([
                "pip", "download", "--no-deps", is_binary,
                f"{package_name}=={prior_version}", "--dest", tmp_dir
            ], check=True, capture_output=True)
            zip_files = glob.glob(os.path.join(tmp_dir, package_type))
            # If no match and we're not constrained to wheel-only, attempt legacy sdist (zip) once.
            if not zip_files and package_type != "*.whl":
                zip_files = glob.glob(os.path.join(tmp_dir, "*.zip"))
            if not zip_files:  # Still nothing -> treat as no prior artifact to compare.
                return True

            prior_metadata: Dict[str, Any] = extract_package_metadata(zip_files[0])
            is_compatible = verify_metadata_compatibility(current_metadata, prior_metadata)
            return is_compatible
        except Exception:
            return True


def verify_metadata_compatibility(current_metadata: Dict[str, Any], prior_metadata: Dict[str, Any]) -> bool:
    """Verify that all keys from prior version metadata are present in current version.

    Special handling: homepage/repository keys are exempt from prior compatibility check,
    but current version must have at least one of them.
    """
    if not current_metadata:
        return False
    # Check that current version has at least one homepage or repository URL
    repo_urls = ['homepage', 'repository']
    current_keys_lower = {k.lower() for k in current_metadata.keys()}
    if not any(key in current_keys_lower for key in repo_urls):
        logging.error(f"Current metadata must contain at least one of: {repo_urls}")
        return False

    if not prior_metadata:
        return True

    # For backward compatibility check, exclude homepage/repository from prior requirements
    prior_keys_filtered = {k for k in prior_metadata.keys() if k.lower() not in repo_urls}
    current_keys = set(current_metadata.keys())

    is_compatible = prior_keys_filtered.issubset(current_keys)
    if not is_compatible:
        missing_keys = prior_keys_filtered - current_keys
        logging.error("Metadata compatibility failed. Missing keys: %s", missing_keys)
    return is_compatible


def get_path_to_zip(dist_dir: str, version: str, package_type: str = "*.whl") -> str:
    return glob.glob(os.path.join(dist_dir, "**", "*{}{}".format(version, package_type)), recursive=True)[0]


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
        if verify_whl_root_directory(args.dist_dir, top_level_module, pkg_details):
            logging.info("Verified whl for package: [%s]", pkg_details.name)
        else:
            logging.error("Failed to verify whl for package: [%s]", pkg_details.name)
            exit(1)
