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
from ci_tools.parsing import ParsedSetup, extract_package_metadata
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
CONDA_MGMT_META_YAML_PATH = os.path.join(CONDA_RECIPES_DIR, "azure-mgmt", "meta.yaml")

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


class IndentDumper(yaml.SafeDumper):
    """Used to preserve indentation levels in conda-sdk-client.yml."""

    def increase_indent(self, flow=False, indentless=False):
        return super().increase_indent(flow, False)


def update_conda_sdk_client_yml(
    packages_to_update: List[Dict[str, str]],
    new_data_plane_packages: List[Dict[str, str]],
    new_mgmt_plane_packages: List[Dict[str, str]],
) -> None:
    """
    Update outdated package versions and add new entries in conda-sdk-client.yml file

    :param packages_to_update: List of package rows from the CSV that need updates.
    :param new_data_plane_packages: List of new data plane package rows from the CSV.
    :param new_mgmt_plane_packages: List of new management plane package rows from the CSV.
    """
    updated_count = 0
    added_count = 0

    with open(CONDA_CLIENT_YAML_PATH, "r") as file:
        conda_client_data = yaml.safe_load(file)

    conda_artifacts = conda_client_data["extends"]["parameters"]["stages"][0]["jobs"][
        0
    ]["steps"][0]["parameters"]["CondaArtifacts"]

    # update outdated package versions

    logger.info(
        f"Detected {len(packages_to_update)} outdated package versions to update in conda-sdk-client.yml"
    )
    package_index = build_package_index(conda_artifacts)

    for pkg in packages_to_update:
        pkg_name = pkg.get(PACKAGE_COL)
        new_version = pkg.get(VERSION_GA_COL)
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

    # add new data plane packages

    logger.info(
        f"Detected {len(new_data_plane_packages)} new data plane packages to add to conda-sdk-client.yml"
    )

    parameters = conda_client_data["parameters"]

    for pkg in new_data_plane_packages:
        package_name = pkg.get(PACKAGE_COL)

        if not package_name:
            logger.warning("Skipping package with missing name")
            continue

        # TODO commented out for testing purposes only
        # if package_name in package_index:
        #     logger.warning(
        #         f"Package {package_name} already exists in conda-sdk-client.yml, skipping addition"
        #     )
        #     continue

        release_name = f"release_{package_name.replace('-', '_')}"
        new_parameter = {
            "name": release_name,
            "displayName": package_name,
            "type": "boolean",
            "default": True,
        }

        parameters.append(new_parameter)

        # also add to CondaArtifacts
        common_root, service_name = determine_service_info(package_name)

        new_artifact_entry = {
            "name": package_name,
            "common_root": common_root,
            "service": service_name,
            "in_batch": f"${{{{ parameters.{release_name} }}}}",
            "checkout": [{"package": package_name, "version": pkg.get(VERSION_GA_COL)}],
        }

        # append before azure-mgmt entry
        conda_artifacts.insert(len(conda_artifacts) - 1, new_artifact_entry)

        added_count += 1
        logger.info(f"Added new data plane package: {package_name}")

    # add new mgmt plane packages

    logger.info(
        f"Detected {len(new_mgmt_plane_packages)} new management plane packages to add to conda-sdk-client.yml"
    )

    # TODO

    # TODO note this dump doesn't preserve some quotes like around
    #    displayName: 'azure-developer-loadtesting' but i don't think those functionally necessary?

    if updated_count > 0 or added_count > 0:
        with open(CONDA_CLIENT_YAML_PATH, "w") as file:
            yaml.dump(
                conda_client_data,
                file,
                Dumper=IndentDumper,
                default_flow_style=False,
                sort_keys=False,
                indent=2,
                width=float("inf"),
            )
        logger.info(
            f"Successfully updated {updated_count} package versions in conda-sdk-client.yml"
        )
    else:
        logger.warning("No packages were found in the YAML file to update")


def get_package_path(package_name: str) -> str:
    """Get the filesystem path of an SDK package given its name."""
    pattern = os.path.join(SDK_DIR, "**", package_name)
    matches = glob.glob(pattern, recursive=True)
    return matches[0]


def determine_service_info(package_name: str) -> Tuple[str, str]:
    # TODO how to actually determine, this is mostly placeholder
    """
    Dynamically determine the common_root and service name based on package name and directory structure.

    :param package_name: The name of the package (e.g., "azure-ai-textanalytics").
    Returns:
        Tuple of (common_root, service_name)
    """
    # Multi-package services that should have common_root like "azure/servicename"
    multi_package_services = {
        "azure-storage",
        "azure-communication",
        "azure-keyvault",
        "azure-eventhub",
        "azure-schemaregistry",
        "azure-ai-vision",
    }

    # TODO not all existing packages follow this pattern tho,
    # e.g. azure-ai-metricsadvisor has service cognitivelanguage <- does this one even exist anymore?
    # e.g. azure-ai-translation-text has service translation
    # e.g. azure-digitaltwins-core has service digitaltwins
    # e.g. azure-monitor-ingestion has service monitor

    # and some packages don't have a common_root field at all??

    # TODO idk how to properly get the service name, e.g. azure-ai-voicelive is projects?
    service_name = os.path.basename(os.path.dirname(get_package_path(package_name)))
    print("!!!")
    print(service_name)

    # Determine common_root
    if package_name in multi_package_services:
        base_service = package_name[6:]  # Remove "azure-" prefix
        common_root = f"azure/{base_service}"
    else:
        common_root = "azure"

    return common_root, service_name


def format_requirement(req: str) -> str:
    """Format a requirement string for conda meta.yaml."""
    name_unpinned = re.split(r"[>=<!]", req)[0].strip()

    # TODO idk if this is right, certain reqs never seem to have pinned versions like aiohttp or isodate

    if name_unpinned.startswith("azure-") or name_unpinned in ["msrest"]:
        return f"{name_unpinned} >={{{{ environ.get('AZURESDK_CONDA_VERSION', '0.0.0') }}}}"
    return req


def get_package_requirements(parsed: ParsedSetup) -> Tuple[List[str], List[str]]:
    """Retrieve the host and run requirements for a data plane package meta.yaml."""
    host_requirements = set(["pip"])
    run_requirements = set()

    # TODO finalize actual list of essentials, this is more of a placeholder with reqs idk how to find dynamically
    for essential_req in [
        "azure-identity",
        "azure-core",
        "python",
        "aiohttp",
        "requests-oauthlib >=0.5.0",
        "cryptography",
    ]:
        req_name = format_requirement(essential_req)
        host_requirements.add(req_name)
        run_requirements.add(req_name)

    package_path = get_package_path(parsed.name)
    if not package_path:
        logger.error(f"Could not find package path for {parsed.name}")
        return list(host_requirements), list(run_requirements)

    # get requirements from setup.py or pyproject.toml
    install_reqs = parsed.requires

    for req in install_reqs:
        req_name = format_requirement(req)
        host_requirements.add(req_name)
        run_requirements.add(req_name)

    # TODO there are other requirements to consider...

    return list(host_requirements), list(run_requirements)


def get_package_metadata(package_name: str, package_path: str) -> Dict[str, str]:
    """Extract metadata for the about section from package."""
    metadata = extract_package_metadata(package_path)

    service_dir = os.path.basename(os.path.dirname(package_path))

    home_url = f"https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/{service_dir}/{package_name}"

    # TODO check this
    if metadata and metadata.get("description"):
        summary = metadata["description"]
    else:
        summary = f"Microsoft Azure {package_name.replace('azure-', '').replace('-', ' ').title()} Client Library for Python"

    # TODO definitely need to check if this is actually correct
    conda_url = f"https://aka.ms/azsdk/conda/releases/{service_dir}"

    return {
        "home": home_url,
        "summary": summary,
        "description": f"This is the {summary}.\n    Please see {conda_url} for version details.",
    }


def generate_data_plane_meta_yaml(
    package_name: str, download_uri: Optional[str] = None
) -> str:
    """Generate the meta.yaml content for a data plane package."""

    # TODO is it correct that the env var name is arbitrary and replaced in conda_functions.py?
    src_distr_name = package_name.split("-")[-1].upper()
    src_distribution_env_var = f"{src_distr_name}_SOURCE_DISTRIBUTION"

    package_path = get_package_path(package_name)

    parsed_setup = ParsedSetup.from_path(package_path)
    host_reqs, run_reqs = get_package_requirements(parsed_setup)

    # Format requirements with proper YAML indentation
    host_reqs_str = "\n    - ".join(host_reqs)
    run_reqs_str = "\n    - ".join(run_reqs)

    # TODO there can be subdirectory packages..... e.g. azure-ai-ml, may need more import logic
    pkg_name_normalized = package_name.replace("-", ".")

    # Get package metadata for about section
    metadata = get_package_metadata(package_name, package_path)

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
  home: "{metadata['home']}"
  license: MIT
  license_family: MIT
  license_file: 
  summary: "{metadata['summary']}"
  description: |
    {metadata['description']}
  doc_url: 
  dev_url: 

extra:
  recipe-maintainers:
    - xiangyan99
"""
    return meta_yaml_content


def add_new_data_plane_packages(new_packages: List[Dict[str, str]]) -> None:
    """Create meta.yaml files for new data plane packages and add import tests."""
    if len(new_packages) == 0:
        return

    logger.info(f"Adding {len(new_packages)} new data plane packages")

    for pkg in new_packages:
        package_name = pkg.get(PACKAGE_COL)
        if not package_name:
            logger.warning("Skipping package with missing name")
            continue

        logger.info(f"Adding new data plane meta.yaml for: {package_name}")

        pkg_yaml_path = os.path.join(CONDA_RECIPES_DIR, package_name, "meta.yaml")
        os.makedirs(os.path.dirname(pkg_yaml_path), exist_ok=True)

        try:
            # TODO maybe compile list of failed packages to report at end
            meta_yml = generate_data_plane_meta_yaml(package_name)
        except Exception as e:
            logger.error(
                f"Failed to generate meta.yaml content for {package_name} and skipping, error: {e}"
            )
            continue

        try:
            with open(pkg_yaml_path, "w") as f:
                f.write(meta_yml)
            logger.info(f"Created meta.yaml for {package_name} at {pkg_yaml_path}")
        except Exception as e:
            logger.error(f"Failed to create meta.yaml for {package_name}: {e}")

        # TODO AKA link stuff needs to happen, either do it or return packages that need action


def add_new_mgmt_plane_packages(new_packages: List[Dict[str, str]]) -> None:
    """Update azure-mgmt/meta.yaml with new management libraries, and add import tests."""
    if len(new_packages) == 0:
        return
    logger.info(f"Adding {len(new_packages)} new management plane packages")

    # with open(CONDA_MGMT_META_YAML_PATH, "r") as file:
    #     mgmt_meta_data = yaml.safe_load(file)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Update conda package files and versions for release."
    )

    args = parser.parse_args()
    args.debug = True  # TODO remove this
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

    outdated_packages = [
        pkg for pkg in packages if package_needs_update(pkg, old_version, is_new=False)
    ]
    new_packages = [
        pkg for pkg in packages if package_needs_update(pkg, old_version, is_new=True)
    ]
    new_data_plane_packages, new_mgmt_plane_packages = separate_packages_by_type(
        new_packages
    )

    # update conda-sdk-client.yml
    # TODO handle packages missing from conda-sdk-client that aren't new relative to the last release...
    update_conda_sdk_client_yml(
        outdated_packages, new_data_plane_packages, new_mgmt_plane_packages
    )

    # handle new data plane libraries
    add_new_data_plane_packages(new_data_plane_packages)

    # handle new mgmt plane libraries
    add_new_mgmt_plane_packages(new_mgmt_plane_packages)

    # add/update release logs
