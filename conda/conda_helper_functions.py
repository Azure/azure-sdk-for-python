"""
Helper functions for updating conda files.
"""

import os
import glob
from typing import Dict, List, Optional, Tuple
import csv
import json
from ci_tools.logging import logger
import urllib.request
from datetime import datetime
from ci_tools.parsing import ParsedSetup

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SDK_DIR = os.path.join(ROOT_DIR, "sdk")

AZURE_SDK_CSV_URL = "https://raw.githubusercontent.com/Azure/azure-sdk/main/_data/releases/latest/python-packages.csv"
PACKAGE_COL = "Package"
LATEST_GA_DATE_COL = "LatestGADate"
VERSION_GA_COL = "VersionGA"
FIRST_GA_DATE_COL = "FirstGADate"
DISPLAY_NAME_COL = "DisplayName"
SERVICE_NAME_COL = "ServiceName"
REPO_PATH_COL = "RepoPath"
TYPE_COL = "Type"
SUPPORT_COL = "Support"

# =====================================
# Helpers for handling bundled releases
# =====================================

def get_package_path(package_name: str) -> Optional[str]:
    """Get the filesystem path of an SDK package given its name."""
    pattern = os.path.join(SDK_DIR, "**", package_name)
    matches = glob.glob(pattern, recursive=True)
    if not matches:
        logger.error(f"Package path not found for package: {package_name}")
        return None
    return matches[0]

def get_bundle_name(package_name: str) -> Optional[str]:
    """
    Check bundled release config from package's pyproject.toml file.

    If bundled, return the bundle name; otherwise, return None.
    """
    package_path = get_package_path(package_name)
    if not package_path:
        logger.warning(f"Cannot determine package path for {package_name}")
        return None
    parsed = ParsedSetup.from_path(package_path)
    if not parsed:
        # TODO raise something 
        logger.error(f"Failed to parse setup for package {package_name}")
        return None
        
    conda_config = parsed.get_conda_config()

    if not conda_config:
        if parsed.is_stable_release():
            # TODO raise something
            logger.warning(f"Stable release package {package_name} needs a conda config")
        return None

    if conda_config and "bundle_name" in conda_config:
        return conda_config["bundle_name"]
    
    return None

def map_bundle_to_packages(package_names: List[str]) -> Dict[str, List[str]]:
    """Create a mapping of bundle names to their constituent package names."""
    logger.info("Mapping bundle names to packages...")
    all_paths = glob.glob(os.path.join(SDK_DIR, "*", "*"))
    # Exclude temp directories like .tox, .venv, __pycache__, etc.
    path_lookup = {
        os.path.basename(p): p
        for p in all_paths
        if os.path.isdir(p) and not os.path.basename(p).startswith((".", "__"))
    }
    
    bundle_map = {}
    for package_name in package_names:
        logger.debug(f"Processing package for bundle mapping: {package_name}")
        package_path = path_lookup.get(package_name)
        if not package_path:
            logger.warning(f"Package path not found for {package_name}")
            continue
        
        # Skip directories without pyproject.toml
        if not os.path.exists(os.path.join(package_path, "pyproject.toml")):
            logger.warning(f"Skipping {package_name}: no pyproject.toml found")
            continue
        
        parsed = ParsedSetup.from_path(package_path)
        if not parsed:
            logger.error(f"Failed to parse setup for package {package_name}")
            continue
        
        conda_config = parsed.get_conda_config()
        if conda_config and "bundle_name" in conda_config:
            bundle_name = conda_config["bundle_name"]
            logger.debug(f"Bundle name for package {package_name}: {bundle_name}")
            bundle_map.setdefault(bundle_name, []).append(package_name)

    return bundle_map

# =====================================
# Utility functions for parsing data
# =====================================

def parse_csv() -> List[Dict[str, str]]:
    """Download and parse the Azure SDK Python packages CSV file."""
    try:
        logger.info(f"Downloading CSV from {AZURE_SDK_CSV_URL}")

        with urllib.request.urlopen(AZURE_SDK_CSV_URL) as response:
            csv_content = response.read().decode("utf-8")

        # Parse the CSV content
        csv_reader = csv.DictReader(csv_content.splitlines())
        packages = list(csv_reader)

        logger.info(f"Successfully parsed {len(packages)} packages from CSV")

        return packages

    except Exception as e:
        logger.error(f"Failed to download or parse CSV: {e}")
        return []


def is_mgmt_package(pkg: Dict[str, str]) -> bool:
    pkg_name = pkg.get(PACKAGE_COL, "")
    _type = pkg.get(TYPE_COL, "")
    if _type == "mgmt":
        return True
    elif _type == "client":
        return False
    else:
        return pkg_name != "azure-mgmt-core" and (
            "mgmt" in pkg_name or "cognitiveservices" in pkg_name
        )


def separate_packages_by_type(
    packages: List[Dict[str, str]],
) -> Tuple[List[Dict[str, str]], List[Dict[str, str]]]:
    """Separate packages into data plane and management plane libraries."""
    data_plane_packages = []
    mgmt_plane_packages = []

    for pkg in packages:
        if is_mgmt_package(pkg):
            mgmt_plane_packages.append(pkg)
        else:
            data_plane_packages.append(pkg)

    logger.debug(
        f"Separated {len(data_plane_packages)} data plane and {len(mgmt_plane_packages)} management plane packages"
    )

    return (data_plane_packages, mgmt_plane_packages)


def package_needs_update(
    package_row: Dict[str, str], prev_release_date: str, is_new=False
) -> bool:
    """
    Check if the package is new or needs version update (i.e., FirstGADate or LatestGADate is after the last release).

    :param package_row: The parsed CSV row for the package.
    :param prev_release_date: The date of the previous release in "mm/dd/yyyy" format.
    :param is_new: Whether to check for new package (FirstGADate) or outdated package (LatestGADate).
    :return: if the package is new or needs an update.
    """
    compare_date = (
        package_row.get(FIRST_GA_DATE_COL)
        if is_new
        else package_row.get(LATEST_GA_DATE_COL)
    )

    logger.debug(
        f"Checking {'new package' if is_new else 'outdated package'} for package {package_row.get(PACKAGE_COL)} with against date: {compare_date}"
    )

    if not compare_date:
        if not is_new and package_row.get(PACKAGE_COL) == "uamqp":
            return True  # uamqp is an exception

        logger.debug(
            f"Package {package_row.get(PACKAGE_COL)} is skipped due to missing {FIRST_GA_DATE_COL if is_new else LATEST_GA_DATE_COL}."
        )

        # TODO need to verify that this is the desired behavior / we're not skipping needed packages

        return False

    try:
        # Convert string dates to datetime objects for proper comparison
        compare_date = datetime.strptime(compare_date, "%m/%d/%Y")
        prev_date = datetime.strptime(prev_release_date, "%m/%d/%Y")
        logger.debug(
            f"Comparing {package_row.get(PACKAGE_COL)} CompareDate {compare_date} with previous release date {prev_date}"
        )
        return compare_date > prev_date
    except ValueError as e:
        logger.error(
            f"Date parsing error for package {package_row.get(PACKAGE_COL)}: {e}"
        )
        return False


def get_package_data_from_pypi(
    package_name: str,
) -> Tuple[Optional[str], Optional[str]]:
    """Fetch the latest version and download URI for a package from PyPI."""
    pypi_url = f"https://pypi.org/pypi/{package_name}/json"
    try:
        with urllib.request.urlopen(pypi_url, timeout=10) as response:
            data = json.loads(response.read().decode("utf-8"))

            # Get the latest version
            latest_version = data["info"]["version"]
            if latest_version in data["releases"] and data["releases"][latest_version]:
                # Get the source distribution (sdist) if available
                files = data["releases"][latest_version]
                source_dist = next(
                    (f for f in files if f["packagetype"] == "sdist"), None
                )
                if source_dist:
                    download_url = source_dist["url"]
                    logger.info(
                        f"Found download URL for {package_name}=={latest_version}: {download_url}"
                    )
                    return latest_version, download_url

    except Exception as e:
        logger.error(f"Failed to fetch download URI from PyPI for {package_name}: {e}")
    return None, None


def build_package_index(conda_artifacts: List[Dict]) -> Dict[str, Tuple[int, int]]:
    """Build an index of package name -> (artifact_idx, checkout_idx) for fast lookups in conda-sdk-client.yml."""
    package_index = {}

    for artifact_idx, artifact in enumerate(conda_artifacts):
        if "checkout" in artifact:
            for checkout_idx, checkout_item in enumerate(artifact["checkout"]):
                package_name = checkout_item.get("package")
                if package_name:
                    package_index[package_name] = (artifact_idx, checkout_idx)
    return package_index
