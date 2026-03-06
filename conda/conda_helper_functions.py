"""
Helper functions for updating conda files.
"""

import os
import glob
from functools import lru_cache
from typing import Optional
import csv
from ci_tools.logging import logger
import urllib.request
from datetime import datetime
from ci_tools.parsing import ParsedSetup
from packaging.version import Version
from pypi_tools.pypi import PyPIClient, retrieve_versions_from_pypi


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


@lru_cache(maxsize=None)
def _build_package_path_index() -> dict[str, str]:
    """
    Build a one-time index mapping package names to their filesystem paths.

    This scans the sdk/ directory once and caches the result for all subsequent lookups.
    """
    all_paths = glob.glob(os.path.join(SDK_DIR, "*", "*"))
    # Exclude temp directories like .tox, .venv, __pycache__, etc.
    return {
        os.path.basename(p): p
        for p in all_paths
        if os.path.isdir(p) and not os.path.basename(p).startswith((".", "__"))
    }


def get_package_path(package_name: str) -> Optional[str]:
    """Get the filesystem path of an SDK package given its name."""
    path_index = _build_package_path_index()
    package_path = path_index.get(package_name)
    if not package_path:
        logger.warning(f"Package path not found for package: {package_name}")
        return None
    return package_path


def get_bundle_name(package_name: str) -> Optional[str]:
    """
    Check bundled release config from package's pyproject.toml file given the package name.

    If bundled, return the bundle name; otherwise, return None.
    """
    package_path = get_package_path(package_name)
    if not package_path:
        logger.warning(f"Cannot determine package path for {package_name}")
        return None
    parsed = ParsedSetup.from_path(package_path)
    if not parsed:
        # can't proceed, need to know if it's bundled or not
        logger.error(f"Failed to parse setup for package {package_name}")
        raise Exception(f"Failed to parse setup for package {package_name}")

    conda_config = parsed.get_conda_config()

    if not conda_config:
        if is_stable_on_pypi(package_name):
            raise Exception(
                f"Stable release package {package_name} needs a conda config"
            )

        logger.warning(
            f"No conda config found for package {package_name}, which may be a pre-release"
        )
        return None

    if conda_config and "bundle_name" in conda_config:
        return conda_config["bundle_name"]

    return None


def map_bundle_to_packages(
    package_names: list[str],
) -> tuple[dict[str, list[str]], list[str]]:
    """Create a mapping of bundle names to their constituent package names.

    :return: Tuple of (bundle_map, failed_packages) where failed_packages are packages that threw exceptions.
    """
    logger.info("Mapping bundle names to packages...")

    bundle_map = {}
    failed_packages = []
    for package_name in package_names:
        logger.debug(f"Processing package for bundle mapping: {package_name}")
        try:
            bundle_name = get_bundle_name(package_name)
            if bundle_name:
                logger.debug(f"Bundle name for package {package_name}: {bundle_name}")
                bundle_map.setdefault(bundle_name, []).append(package_name)
        except Exception as e:
            logger.error(f"Failed to get bundle name for {package_name}: {e}")
            failed_packages.append(package_name)
            continue

    return bundle_map, failed_packages


# =====================================
# Utility functions for parsing data
# =====================================


def parse_csv() -> list[dict[str, str]]:
    """Download and parse the Azure SDK Python packages CSV file."""
    try:
        logger.info(f"Downloading CSV from {AZURE_SDK_CSV_URL}")

        with urllib.request.urlopen(AZURE_SDK_CSV_URL, timeout=10) as response:
            csv_content = response.read().decode("utf-8")

        # Parse the CSV content
        csv_reader = csv.DictReader(csv_content.splitlines())
        packages = list(csv_reader)

        logger.info(f"Successfully parsed {len(packages)} packages from CSV")

        return packages

    except Exception as e:
        logger.error(f"Failed to download or parse CSV: {e}")
        return []


def is_mgmt_package(pkg: dict[str, str]) -> bool:
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
    packages: list[dict[str, str]],
) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
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
    package_row: dict[str, str], prev_release_date: str, is_new=False
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
        logger.debug(
            f"Package {package_row.get(PACKAGE_COL)} is skipped due to missing {FIRST_GA_DATE_COL if is_new else LATEST_GA_DATE_COL}."
        )

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


def is_stable_on_pypi(package_name: str) -> bool:
    """
    Check if a package has any stable (GA) release on PyPI.

    :param package_name: The name of the package to check.
    :return: True if any stable version exists on PyPI, False otherwise.
    """
    try:
        versions = retrieve_versions_from_pypi(package_name)
        if not versions:
            logger.warning(f"No versions found on PyPI for {package_name}")
            return False

        # Check if any version is stable (not a prerelease)
        for v in versions:
            if not Version(v).is_prerelease:
                logger.debug(f"Package {package_name} has stable version {v}")
                return True

        logger.debug(f"Package {package_name} has no stable versions")
        return False

    except Exception as e:
        logger.warning(f"Failed to check PyPI for {package_name}: {e}")
        return False


def get_package_data_from_pypi(
    package_name: str,
) -> tuple[Optional[str], Optional[str]]:
    """Fetch the latest version and download URI for a package from PyPI."""
    try:
        client = PyPIClient()
        data = client.project(package_name)

        # Get the latest version
        latest_version = data["info"]["version"]
        if latest_version in data["releases"] and data["releases"][latest_version]:
            # Get the source distribution (sdist) if available
            files = data["releases"][latest_version]
            source_dist = next((f for f in files if f["packagetype"] == "sdist"), None)
            if source_dist:
                download_url = source_dist["url"]
                logger.info(
                    f"Found download URL for {package_name}=={latest_version}: {download_url}"
                )
                return latest_version, download_url

    except Exception as e:
        logger.error(f"Failed to fetch download URI from PyPI for {package_name}: {e}")
    return None, None


def build_package_index(conda_artifacts: list[dict]) -> dict[str, tuple[int, int]]:
    """Build an index of package name -> (artifact_idx, checkout_idx) for fast lookups in conda-sdk-client.yml."""
    package_index = {}

    for artifact_idx, artifact in enumerate(conda_artifacts):
        if "checkout" in artifact:
            for checkout_idx, checkout_item in enumerate(artifact["checkout"]):
                package_name = checkout_item.get("package")
                if package_name:
                    package_index[package_name] = (artifact_idx, checkout_idx)
    return package_index


def get_valid_package_imports(package_name: str) -> list[str]:
    """
    Inspect the package's actual module structure and return only valid imports.

    :param package_name: The name of the package (e.g., "azure-mgmt-advisor" or "azure-eventgrid").
    :return: List of valid module names for import (e.g., ["azure.eventgrid", "azure.eventgrid.aio"]).
    """
    package_path = get_package_path(package_name)
    if not package_path:
        logger.warning(
            f"Could not find package path for {package_name} to determine imports, using fallback"
        )
        return [package_name.replace("-", ".")]
    else:
        parsed = ParsedSetup.from_path(package_path)
        if not parsed or not parsed.namespace:
            logger.warning(
                f"Could not parse namespace for {package_name}, using fallback"
            )
            module_name = package_name.replace("-", ".")
        else:
            module_name = parsed.namespace

    imports = [module_name]

    # Construct the path to the actual module directory
    module_parts = module_name.split(".")
    module_dir = os.path.join(package_path, *module_parts)

    if not os.path.isdir(module_dir):
        logger.warning(
            f"Module directory not found for {package_name} at {module_dir}, using base import only"
        )
        return imports

    # Check for common submodules and only add if they exist
    submodules_to_check = ["aio", "models", "operations"]

    for submodule_name in submodules_to_check:
        submodule_path = os.path.join(module_dir, submodule_name)
        if os.path.isdir(submodule_path) and os.path.exists(
            os.path.join(submodule_path, "__init__.py")
        ):
            imports.append(f"{module_name}.{submodule_name}")

    # Check for aio.operations (nested submodule)
    aio_operations_path = os.path.join(module_dir, "aio", "operations")
    if os.path.isdir(aio_operations_path) and os.path.exists(
        os.path.join(aio_operations_path, "__init__.py")
    ):
        imports.append(f"{module_name}.aio.operations")

    return imports
