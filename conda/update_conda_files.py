"""Update package versions, yml files, release-logs, and changelogs for conda packages."""

import os
import argparse
import csv
import yaml
import urllib.request
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from ci_tools.logging import logger, configure_logging
from typing import Dict, List, Optional, Tuple

# paths
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CONDA_DIR = os.path.join(ROOT_DIR, "conda")
CONDA_RECIPES_DIR = os.path.join(CONDA_DIR, "conda-recipes")
CONDA_RELEASE_LOGS_DIR = os.path.join(CONDA_DIR, "conda-releaselogs")
CONDA_ENV_PATH = os.path.join(CONDA_RECIPES_DIR, "conda_env.yml")

# constants
RELEASE_PERIOD_MONTHS = 3
AZURE_SDK_CSV_URL = "https://raw.githubusercontent.com/Azure/azure-sdk/main/_data/releases/latest/python-packages.csv"
PACKAGE_COL_NAME = "Package"


def update_conda_version() -> str:
    """Update the AZURESDK_CONDA_VERSION in conda_env.yml and return the new version."""

    with open(CONDA_ENV_PATH, "r") as file:
        conda_env_data = yaml.safe_load(file)

    current_version = conda_env_data["variables"]["AZURESDK_CONDA_VERSION"]
    current_date = datetime.strptime(current_version, "%Y.%m.%d")

    new_date = current_date + relativedelta(months=RELEASE_PERIOD_MONTHS)

    # bump version
    new_version = new_date.strftime("%Y.%m.%d")
    conda_env_data["variables"]["AZURESDK_CONDA_VERSION"] = new_version

    with open(CONDA_ENV_PATH, "w") as file:
        yaml.dump(conda_env_data, file, default_flow_style=False, sort_keys=False)

    logger.info(
        f"Updated AZURESDK_CONDA_VERSION from {current_version} to {new_version}"
    )

    return new_version


# read from csv
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

        # Log some sample data for debugging
        if packages:
            logger.debug(f"Sample package data: {packages[0]}")
            logger.debug(f"CSV headers: {list(packages[0].keys())}")

        return packages

    except Exception as e:
        logger.error(f"Failed to download or parse CSV: {e}")
        return []


def is_mgmt_package(pkg_name: str) -> bool:
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
        package_name = pkg.get(PACKAGE_COL_NAME, "")
        if is_mgmt_package(package_name):
            mgmt_plane_packages.append(pkg)
        else:
            data_plane_packages.append(pkg)

    logger.info(
        f"Separated {len(data_plane_packages)} data plane and {len(mgmt_plane_packages)} management plane packages"
    )

    return (data_plane_packages, mgmt_plane_packages)


# get new data plane libraries

# get outdated versions

# handle data yml

# mgmt yml

# import tests for data

# import tests for mgmt

# update conda-sdk-client

# release logs

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Update conda package files and versions."
    )

    args = parser.parse_args()

    configure_logging(args)

    new_version = update_conda_version()

    # Parse CSV data
    packages = parse_csv()
    if not packages:
        logger.error("No packages found in CSV data.")
        exit(1)

    data_plane_packages, mgmt_plane_packages = separate_packages_by_type(packages)
