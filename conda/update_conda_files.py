"""Update package versions, yml files, release-logs, and changelogs for conda packages."""

import os
import argparse
import json
import csv
import yaml
import urllib.request
import re
import glob
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from ci_tools.logging import logger, configure_logging
from ci_tools.parsing import get_install_requires, ParsedSetup
from typing import Dict, List, Optional, Tuple

# paths
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SDK_DIR = os.path.join(ROOT_DIR, "sdk")
CONDA_DIR = os.path.join(ROOT_DIR, "conda")
CONDA_RECIPES_DIR = os.path.join(CONDA_DIR, "conda-recipes")
CONDA_RELEASE_LOGS_DIR = os.path.join(CONDA_DIR, "conda-releaselogs")
CONDA_ENV_PATH = os.path.join(CONDA_RECIPES_DIR, "conda_env.yml")
CONDA_CLIENT_YAML_PATH = os.path.join(
    ROOT_DIR, "eng", "pipelines", "templates", "stages", "conda-sdk-client.yml"
)

# constants
RELEASE_PERIOD_MONTHS = 3
AZURE_SDK_CSV_URL = "https://raw.githubusercontent.com/Azure/azure-sdk/main/_data/releases/latest/python-packages.csv"
PACKAGE_COL = "Package"
LATEST_GA_DATE_COL = "LatestGADate"
VERSION_GA_COL = "VersionGA"
FIRST_GA_DATE_COL = "FirstGADate"

# packages that should be shipped but are known to be missing from the csv
PACKAGES_WITH_DOWNLOAD_URI = [
    "msal",
    "msal-extensions",
]


class quoted(str):
    pass


def quoted_presenter(dumper, data):
    """YAML presenter to force quotes around a string."""
    return dumper.represent_scalar("tag:yaml.org,2002:str", data, style="'")


def update_conda_version() -> (
    Tuple[datetime, str]
):  # TODO do i need the new date anywhere else? i think i may
    """Update the AZURESDK_CONDA_VERSION in conda_env.yml and return the old and new versions."""

    with open(CONDA_ENV_PATH, "r") as file:
        conda_env_data = yaml.safe_load(file)

    old_version = conda_env_data["variables"]["AZURESDK_CONDA_VERSION"]
    old_date = datetime.strptime(old_version, "%Y.%m.%d")

    new_date = old_date + relativedelta(months=RELEASE_PERIOD_MONTHS)

    # bump version
    new_version = new_date.strftime("%Y.%m.%d")
    conda_env_data["variables"]["AZURESDK_CONDA_VERSION"] = quoted(new_version)

    yaml.add_representer(quoted, quoted_presenter)

    with open(CONDA_ENV_PATH, "w") as file:
        yaml.dump(conda_env_data, file, default_flow_style=False, sort_keys=False)

    logger.info(f"Updated AZURESDK_CONDA_VERSION from {old_version} to {new_version}")

    return old_date, new_version


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
        package_name = pkg.get(PACKAGE_COL, "")
        if is_mgmt_package(package_name):
            mgmt_plane_packages.append(pkg)
        else:
            data_plane_packages.append(pkg)

    logger.info(
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


def update_package_versions(
    packages: List[Dict[str, str]], prev_release_date: str
) -> None:
    """
    Update outdated package versions in the conda-sdk-client.yml file

    :param packages: List of package rows from the CSV.
    :param prev_release_date: The date of the previous release in "mm/dd/yyyy" format.
    """
    packages_to_update = []

    for package in packages:
        if package_needs_update(package, prev_release_date, is_new=False):
            packages_to_update.append(
                (package.get(PACKAGE_COL), package.get(VERSION_GA_COL))
            )

    if not packages_to_update:
        logger.info("No packages need version updates")
        return

    logger.info(
        f"Detected {len(packages_to_update)} outdated package versions to update"
    )

    with open(CONDA_CLIENT_YAML_PATH, "r") as file:
        conda_client_data = yaml.safe_load(file)

    updated_count = 0

    # Navigate to the CondaArtifacts section
    conda_artifacts = conda_client_data["extends"]["parameters"]["stages"][0]["jobs"][
        0
    ]["steps"][0]["parameters"]["CondaArtifacts"]
    package_index = build_package_index(conda_artifacts)

    for pkg_name, new_version in packages_to_update:
        if pkg_name in package_index:
            artifact_idx, checkout_idx = package_index[pkg_name]
            checkout_item = conda_artifacts[artifact_idx]["checkout"][checkout_idx]

            if "version" in checkout_item:
                old_version = checkout_item.get("version", "")
                checkout_item["version"] = new_version
                logger.info(f"Updated {pkg_name}: {old_version} -> {new_version}")
                updated_count += 1
            else:
                logger.warning(
                    f"Package {pkg_name} has no 'version' field, skipping update"
                )
        else:
            logger.warning(
                f"Package {pkg_name} not found in conda-sdk-client.yml, skipping update"
            )

    # handle download_uri for packages known to be missing from the csv
    for pkg_name in PACKAGES_WITH_DOWNLOAD_URI:
        if pkg_name in package_index:
            artifact_idx, checkout_idx = package_index[pkg_name]
            checkout_item = conda_artifacts[artifact_idx]["checkout"][checkout_idx]

            curr_download_uri = checkout_item.get("download_uri", "")
            latest_version, download_uri = get_package_data_from_pypi(pkg_name)

            if not latest_version or not download_uri:
                logger.warning(
                    f"Could not retrieve latest version or download URI for {pkg_name} from PyPI, skipping"
                )
                continue

            if curr_download_uri != download_uri:
                # version needs update
                logger.info(
                    f"Package {pkg_name} download_uri mismatch with PyPi, updating {curr_download_uri} to {download_uri}"
                )
                checkout_item["version"] = latest_version
                checkout_item["download_uri"] = download_uri
                logger.info(
                    f"Updated download_uri for {pkg_name} with version {latest_version}: {download_uri}"
                )
                updated_count += 1
        else:
            logger.warning(
                f"Package {pkg_name} not found in conda-sdk-client.yml, skipping download_uri update"
            )

    if updated_count > 0:
        with open(CONDA_CLIENT_YAML_PATH, "w") as file:
            yaml.dump(
                conda_client_data,
                file,
                default_flow_style=False,
                sort_keys=False,
                width=float("inf"),
            )
        logger.info(
            f"Successfully updated {updated_count} package versions in conda-sdk-client.yml"
        )
    else:
        logger.warning("No packages were found in the YAML file to update")


def get_package_path(package_name: str) -> Optional[str]:
    """Get the filesystem path of an SDK package given its name."""
    pattern = os.path.join(SDK_DIR, "**", package_name)
    matches = glob.glob(pattern, recursive=True)
    if matches:
        return matches[0]


def format_requirement(req: str) -> str:
    """Format a requirement string for conda meta.yaml."""
    name_unpinned = re.split(r"[>=<!]", req)[0].strip()

    # TODO idk if this is right, certain reqs never seem to have pinned versions like aiohttp or isodate

    if name_unpinned.startswith("azure-") or name_unpinned in ["msrest"]:
        return f"{name_unpinned} >={{{{ environ.get('AZURESDK_CONDA_VERSION', '0.0.0') }}}}"
    return req


def get_package_requirements(package_name: str) -> Tuple[List[str], List[str]]:
    """Retrieve the host and run requirements for a data plane package meta.yaml."""
    host_requirements = ["python", "pip"]
    run_requirements = ["python"]

    package_path = get_package_path(package_name)
    if not package_path:
        logger.error(f"Could not find package path for {package_name}")
        return host_requirements, run_requirements

    # get requirements from setup.py or pyproject.toml
    try:
        install_reqs = get_install_requires(package_path)
    except ValueError as e:
        logger.error(f"No setup.py or pyproject.toml found for {package_name}: {e}")
        return host_requirements, run_requirements

    for req in install_reqs:
        # TODO ?? is this correct behavior??????
        req_name = format_requirement(req)
        host_requirements.append(req_name)
        run_requirements.append(req_name)

    # make sure essential reqs are added if they weren't in install_reqs
    # TODO finalize actual list of essentials
    for essential_req in [
        "azure-identity",
        "azure-core",
        "aiohttp",
        "requests-oauthlib >=0.5.0",
        "cryptography",
    ]:
        req_name = format_requirement(essential_req)
        if req_name not in host_requirements:
            host_requirements.append(req_name)
            run_requirements.append(req_name)

    # TODO there are other requirements to consider...

    return host_requirements, run_requirements


def generate_data_plane_meta_yaml(
    package_name: str, download_uri: Optional[str] = None
) -> str:
    """Generate the meta.yaml content for a data plane package."""

    # TODO is it correct that the env var name is arbitrary and replaced in conda_functions.py?
    src_distr_name = package_name.split("-")[-1].upper()
    src_distribution_env_var = f"{src_distr_name}_SOURCE_DISTRIBUTION"

    # TODO there can be subdirectory packages..... e.g. azure-ai-ml
    pkg_name_normalized = package_name.replace("-", ".")

    host_reqs, run_reqs = get_package_requirements(package_name)

    # Format requirements with proper YAML indentation
    host_reqs_str = "\n    - ".join(host_reqs)
    run_reqs_str = "\n    - ".join(run_reqs)

    # TODO ... check import
    # TODO get about info

    meta_yaml_content = f"""{{% set name = "{package_name}" %}}

package:
  name: "{{{{ name|lower }}}}"
  version: {{{{ environ.get('AZURESDK_CONDA_VERSION', '0.0.0') }}}}

source:
  url: {{{{ environ.get('{src_distribution_env_var}', '') }}}}

build:
  noarch: python
  number: 0
  script: "{{{{ PYTHON }}}} -m pip install . -vv"

requirements:
  host:
    - {host_reqs_str}
  run:
    - {run_reqs_str}

test:
  imports:
    - {pkg_name_normalized}

about:
  home: "https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/ai/azure-ai-agents"
  license: MIT
  license_family: MIT
  license_file: 
  summary: "Microsoft Azure AI Agents Client Library for Python"
  description: |
    This is the Microsoft Azure AI Agents Client Library.
    Please see https://aka.ms/azsdk/conda/releases/agents for version details.
  doc_url: 
  dev_url: 

extra:
  recipe-maintainers:
    - xiangyan99
"""
    return meta_yaml_content


def add_new_data_plane_packages(new_packages: List[Dict[str, str]]) -> None:
    """Create meta.yaml files for new data plane packages and add import tests."""
    logger.info(f"Adding {len(new_packages)} new data plane packages")

    for pkg in new_packages:
        package_name = pkg.get(PACKAGE_COL)
        if not package_name:
            logger.warning("Skipping package with missing name")
            continue

        logger.info(f"Adding new data plane package: {package_name}")

        pkg_yaml_path = os.path.join(CONDA_RECIPES_DIR, package_name, "meta.yaml")
        os.makedirs(os.path.dirname(pkg_yaml_path), exist_ok=True)

        meta_yml = generate_data_plane_meta_yaml(package_name)

        try:
            with open(pkg_yaml_path, "w") as f:
                f.write(meta_yml)
            logger.info(f"Created meta.yaml for {package_name} at {pkg_yaml_path}")
        except Exception as e:
            logger.error(f"Failed to create meta.yaml for {package_name}: {e}")


def add_new_mgmt_plane_packages(new_packages: List[Dict[str, str]]) -> None:
    """Update azure-mgmt/meta.yaml with new management libraries, and add import tests."""
    # TODO implement logic to add new management plane packages
    logger.info(f"Adding {len(new_packages)} new management plane packages")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Update conda package files and versions for release."
    )

    args = parser.parse_args()
    args.debug = True
    configure_logging(args)

    old_date, new_version = update_conda_version()

    # convert to mm/dd/yyyy format for comparison with CSV dates
    old_version = old_date.strftime("%m/%d/%Y")

    # Parse CSV data
    packages = parse_csv()

    if not packages:
        logger.error("No packages found in CSV data.")
        exit(1)

    # Only ship GA packages
    packages = [pkg for pkg in packages if pkg.get(VERSION_GA_COL)]
    logger.info(f"Filtered to {len(packages)} GA packages")

    # update existing package versions
    # TODO handle packages missing from conda-sdk-client that aren't new relative to the last release...
    update_package_versions(packages, old_version)

    # handle new packages
    new_packages = [
        pkg for pkg in packages if package_needs_update(pkg, old_version, is_new=True)
    ]
    new_data_plane_packages, new_mgmt_plane_packages = separate_packages_by_type(
        new_packages
    )

    # handle new data plane libraries
    if len(new_data_plane_packages) > 0:
        add_new_data_plane_packages(new_data_plane_packages)

    # handle new mgmt plane libraries
    # if len(new_mgmt_plane_packages) > 0:
    #     add_new_mgmt_plane_packages(new_mgmt_plane_packages)

    # update conda-sdk-client

    # add/update release logs
