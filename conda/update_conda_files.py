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
from conda_helper_functions import (
    parse_csv,
    separate_packages_by_type,
    package_needs_update,
    get_package_data_from_pypi,
    build_package_index,
)

from conda_release_groups import (
    get_package_group_data,
    get_release_group,
    get_package_to_group_mapping,
)

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
DISPLAY_NAME_COL = "DisplayName"
SERVICE_NAME_COL = "ServiceName"
REPO_PATH_COL = "RepoPath"
TYPE_COL = "Type"

# packages that should be shipped but are known to be missing from the csv
PACKAGES_WITH_DOWNLOAD_URI = [
    "msal",
    "msal-extensions",
]

# =====================================
# Helpers for updating conda_env.yml
# =====================================


class quoted(str):
    pass


def quoted_presenter(dumper, data):
    """YAML presenter to force quotes around a string."""
    return dumper.represent_scalar("tag:yaml.org,2002:str", data, style="'")


def update_conda_version() -> Tuple[datetime, str]:
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


# =====================================
# Helpers for updating conda-sdk-client.yml
# =====================================


class IndentDumper(yaml.SafeDumper):
    """Used to preserve indentation levels in conda-sdk-client.yml."""

    def increase_indent(self, flow=False, indentless=False):
        return super().increase_indent(flow, False)


def update_conda_sdk_client_yml(
    package_dict: Dict[str, Dict[str, str]],
    packages_to_update: List[str],
    new_data_plane_packages: List[str],
    new_mgmt_plane_packages: List[str],
) -> List[str]:
    """
    Update outdated package versions and add new entries in conda-sdk-client.yml file

    :param package_dict: Dictionary mapping package names to their CSV row data.
    :param packages_to_update: List of package names that need version updates.
    :param new_data_plane_packages: List of new data plane package names.
    :param new_mgmt_plane_packages: List of new management plane package names.
    :return: List of package names that were not updated or added and may require manual action.
    """
    updated_count = 0
    added_count = 0
    result = []

    with open(CONDA_CLIENT_YAML_PATH, "r") as file:
        conda_client_data = yaml.safe_load(file)

    conda_artifacts = conda_client_data["extends"]["parameters"]["stages"][0]["jobs"][
        0
    ]["steps"][0]["parameters"]["CondaArtifacts"]

    # === Update outdated package versions ===

    logger.info(
        f"Detected {len(packages_to_update)} outdated package versions to update in conda-sdk-client.yml"
    )
    package_index = build_package_index(conda_artifacts)

    for pkg_name in packages_to_update:
        pkg = package_dict.get(pkg_name, {})
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
                result.append(pkg_name)
        else:
            logger.warning(
                f"Package {pkg_name} not found in conda-sdk-client.yml, skipping update"
            )
            result.append(pkg_name)

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
                result.append(pkg_name)
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
            result.append(pkg_name)

    # === Add new data plane packages ===

    logger.info(
        f"Detected {len(new_data_plane_packages)} new data plane packages to add to conda-sdk-client.yml"
    )

    package_to_group = get_package_to_group_mapping()
    parameters = conda_client_data["parameters"]

    # quick look up for handling grouped package releases
    existing_parameter_names = [p.get("name") for p in parameters]
    existing_artifact_names = {
        a.get("name"): idx for idx, a in enumerate(conda_artifacts)
    }

    for package_name in new_data_plane_packages:
        pkg = package_dict.get(package_name, {})

        if package_name in package_index:
            logger.warning(
                f"New package {package_name} already exists in conda-sdk-client.yml, skipping addition"
            )
            result.append(package_name)
            continue

        # check if package belongs to a release group
        group_name = get_release_group(package_name, package_to_group)
        group_data = get_package_group_data(group_name)

        if group_data:
            # package is part of a release group
            logger.info(f"Package {package_name} belongs to release group {group_name}")
            release_name = f"release_{group_name.replace('-', '_')}"
            display_name = group_name
        else:
            # package is released individually
            release_name = f"release_{package_name.replace('-', '_')}"
            display_name = package_name

        # add new release parameter if not exists
        if release_name not in existing_parameter_names:
            new_parameter = {
                "name": release_name,
                "displayName": display_name,
                "type": "boolean",
                "default": True,
            }
            parameters.append(new_parameter)

        # add to CondaArtifacts
        common_root, service_name = determine_service_info(pkg, package_to_group)

        # build checkout packages
        if group_data:
            checkout_packages = []
            for grouped_pkg_name in group_data["packages"]:
                curr_pkg = package_dict.get(grouped_pkg_name, {})
                if not curr_pkg:
                    logger.error(
                        f"Package {grouped_pkg_name} listed in group {group_name} not found in CSV data, skipping"
                    )
                    result.append(grouped_pkg_name)
                    continue
                curr_version = curr_pkg.get(VERSION_GA_COL)
                if curr_version:
                    checkout_packages.append(
                        {"package": grouped_pkg_name, "version": curr_version}
                    )
                else:
                    logger.error(
                        f"Package {grouped_pkg_name} in group {group_name} is missing version info, skipping"
                    )
                    result.append(grouped_pkg_name)
        else:
            checkout_packages = [
                {"package": package_name, "version": pkg.get(VERSION_GA_COL)}
            ]

        if group_name not in existing_artifact_names:
            new_artifact_entry = {
                "name": group_name if group_data else package_name,
                "common_root": common_root,
                "service": service_name,
                "in_batch": f"${{{{ parameters.{release_name} }}}}",
                "checkout": checkout_packages,
            }

            # append before azure-mgmt entry
            conda_artifacts.insert(len(conda_artifacts) - 1, new_artifact_entry)

            added_count += 1
            logger.info(f"Added new data plane package: {package_name}")
        else:
            logger.info(
                f"CondaArtifact for {group_name if group_data else package_name} already exists in conda-sdk-client.yml"
            )
            curr_artifact_checkout = conda_artifacts[
                existing_artifact_names[group_name]
            ]["checkout"]
            packages_in_artifact = {item["package"] for item in curr_artifact_checkout}

            # account for adding new packages to an existing group
            for pkg_entry in checkout_packages:
                if pkg_entry["package"] not in packages_in_artifact:
                    curr_artifact_checkout.append(pkg_entry)
                    added_count += 1
                    logger.info(
                        f"Added package {pkg_entry['package']} to existing CondaArtifact {group_name}"
                    )

    # === Add new mgmt plane packages ===

    logger.info(
        f"Detected {len(new_mgmt_plane_packages)} new management plane packages to add to conda-sdk-client.yml"
    )

    # assumes azure-mgmt will always be the last CondaArtifacts entry
    azure_mgmt_artifact_checkout = conda_artifacts[-1]["checkout"]

    for package_name in new_mgmt_plane_packages:
        pkg = package_dict.get(package_name, {})

        if package_name in package_index:
            logger.warning(
                f"New package {package_name} already exists in conda-sdk-client.yml, skipping addition"
            )
            result.append(package_name)
            continue

        new_mgmt_entry = {
            "package": package_name,
            "version": pkg.get(VERSION_GA_COL),
        }

        azure_mgmt_artifact_checkout.append(new_mgmt_entry)

        added_count += 1
        logger.info(f"Added new management plane package: {package_name}")

    # sort mgmt packages alphabetically
    azure_mgmt_artifact_checkout.sort(key=lambda x: x["package"])

    # TODO note this dump doesn't preserve some quotes like around
    #    displayName: 'azure-developer-loadtesting' but i don't think those functionally necessary?
    #   double check that this is ok, esp for URLs... ^

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
    return result


# =====================================
# Helpers for creating conda-recipes/<service>/meta.yaml files
# =====================================


def get_package_path(package_name: str) -> str:
    """Get the filesystem path of an SDK package given its name."""
    pattern = os.path.join(SDK_DIR, "**", package_name)
    matches = glob.glob(pattern, recursive=True)
    return matches[0]


def determine_service_info(
    pkg: Dict[str, str], package_to_group: dict
) -> Tuple[str, str]:
    """
    Returns the common root and service name for the given package.

    :param package_name: The name of the package (e.g., "azure-ai-textanalytics").
    :param package_to_group: Mapping of package names to release group names.
    """
    # defaults
    package_name = pkg.get(PACKAGE_COL, "")
    service_name = pkg.get(REPO_PATH_COL, "").lower()
    common_root = "azure"

    # check for exceptions to the pattern
    group_name = get_release_group(package_name, package_to_group)
    group_data = get_package_group_data(group_name)

    if group_data:
        if group_data.get("service"):
            service_name = group_data["service"]
        if group_data.get("common_root"):
            common_root = group_data["common_root"]

    if not service_name:
        service_name = os.path.basename(os.path.dirname(get_package_path(package_name)))

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


def get_package_metadata(package_name: str, package_path: str) -> Tuple[str, str, str]:
    """Extract package metadata for about section in meta.yaml."""
    pkg_metadata = extract_package_metadata(package_path)

    service_dir = os.path.basename(os.path.dirname(package_path))
    home_url = f"https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/{service_dir}/{package_name}"

    # TODO check correctness of this
    if pkg_metadata and pkg_metadata.get("description"):
        summary = pkg_metadata["description"]
    else:
        summary = f"Microsoft Azure {package_name.replace('azure-', '').replace('-', ' ').title()} Client Library for Python"

    # TODO definitely need to check if this is actually always correct
    conda_url = f"https://aka.ms/azsdk/conda/releases/{service_dir}"
    description = (
        f"This is the {summary}.\n    Please see {conda_url} for version details."
    )

    return home_url, summary, description


def generate_data_plane_meta_yaml(
    package_dict: Dict[str, Dict[str, str]],
    package_name: str,
    group_name: Optional[str],
    group_data: Optional[dict],
) -> str:
    """
    Generate the meta.yaml content for a data plane package or release group.

    :param package_dict: Dictionary mapping package names to their CSV row data.
    :param package_name: The name of the package to generate meta.yaml for.
    :param group: Whether the meta.yaml is for a single package or group.
    """

    # TODO is it correct that the env var name is arbitrary and replaced in conda_functions.py?
    src_distr_name = package_name.split("-")[-1].upper()
    src_distribution_env_var = f"{src_distr_name}_SOURCE_DISTRIBUTION"

    # TODO not sure if this is the best way to get these requirements
    # TODO don't think this covers all possible import tests, e.g. azure.eventgrid, azure.eventgrid.aio <- when would I add that?
    if group_name and group_data:
        # handle grouped packages
        logger.info(
            f"Generating meta.yaml for release group {group_name} including packages: {group_data['packages']}"
        )
        host_reqs = set()
        run_reqs = set()
        pkg_imports = []

        for pkg in group_data["packages"]:
            package_path = get_package_path(pkg)
            parsed_setup = ParsedSetup.from_path(package_path)

            pkg_host_reqs, pkg_run_reqs = get_package_requirements(parsed_setup)
            host_reqs.update(pkg_host_reqs)
            run_reqs.update(pkg_run_reqs)

            pkg_imports.append(pkg.replace("-", "."))
        host_reqs = list(host_reqs)
        run_reqs = list(run_reqs)

        home_url, summary, description = get_package_metadata(
            group_name, get_package_path(group_data["packages"][0])
        )
    else:
        logger.info(f"Generating meta.yaml for package {package_name}")
        package_path = get_package_path(package_name)
        parsed_setup = ParsedSetup.from_path(package_path)

        host_reqs, run_reqs = get_package_requirements(parsed_setup)
        pkg_imports = [package_name.replace("-", ".")]

        home_url, summary, description = get_package_metadata(
            package_name, package_path
        )

    # Format requirements with proper YAML indentation
    host_reqs_str = "\n    - ".join(host_reqs)
    run_reqs_str = "\n    - ".join(run_reqs)
    pkg_imports_str = "\n    - ".join(pkg_imports)
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
    - {pkg_imports_str}

about:
  home: "{home_url}"
  license: MIT
  license_family: MIT
  license_file: 
  summary: "{summary}"
  description: |
    {description}
  doc_url: 
  dev_url: 

extra:
  recipe-maintainers:
    - xiangyan99
"""
    return meta_yaml_content


def add_new_data_plane_packages(
    package_dict: Dict[str, Dict[str, str]], new_data_plane_names: List[str]
) -> List[str]:
    """Create meta.yaml files for new data plane packages and add import tests."""
    if len(new_data_plane_names) == 0:
        return []

    logger.info(f"Adding {len(new_data_plane_names)} new data plane packages")
    result = []

    group_names_processed = set()
    for package_name in new_data_plane_names:
        logger.info(f"Adding new data plane meta.yaml for: {package_name}")

        pkg_yaml_path = os.path.join(CONDA_RECIPES_DIR, package_name, "meta.yaml")
        os.makedirs(os.path.dirname(pkg_yaml_path), exist_ok=True)

        group_name = get_release_group(package_name, get_package_to_group_mapping())
        group_data = get_package_group_data(group_name)

        if group_data and group_name in group_names_processed:
            logger.info(
                f"Meta.yaml for group {group_name} already created, skipping {package_name}"
            )
            continue

        try:
            meta_yml = generate_data_plane_meta_yaml(
                package_dict, package_name, group_name, group_data
            )
            if group_data:
                group_names_processed.add(group_name)
        except Exception as e:
            logger.error(
                f"Failed to generate meta.yaml content for {package_name} and skipping, error: {e}"
            )
            result.append(package_name)
            continue

        try:
            with open(pkg_yaml_path, "w") as f:
                f.write(meta_yml)
            logger.info(f"Created meta.yaml for {package_name} at {pkg_yaml_path}")
        except Exception as e:
            logger.error(f"Failed to create meta.yaml for {package_name}: {e}")
            result.append(package_name)

    return result


# =====================================
# Helpers for adding new mgmt plane packages to azure-mgmt/meta.yaml
# =====================================


def add_new_mgmt_plane_packages(new_packages: List[Dict[str, str]]) -> List[str]:
    """Update azure-mgmt/meta.yaml with new management libraries, and add import tests."""
    if len(new_packages) == 0:
        return []
    logger.info(f"Adding {len(new_packages)} new management plane packages")
    result = []

    # can't use pyyaml due to jinja2
    with open(CONDA_MGMT_META_YAML_PATH, "r") as file:
        content = file.read()

    test_match = re.search(
        r"^test:\s*\n\s*imports:(.*?)^(?=\w)", content, re.MULTILINE | re.DOTALL
    )
    if not test_match:
        logger.error("Could not find 'test: imports:' section in meta.yaml")
        result.extend([pkg.get(PACKAGE_COL) for pkg in new_packages])
        return result

    existing_imports_text = test_match.group(1)
    existing_imports = [
        line.strip()
        for line in existing_imports_text.strip().split("\n")
        if line.strip().startswith("-")
    ]

    new_imports = []
    for pkg in new_packages:
        package_name = pkg.get(PACKAGE_COL)
        if not package_name:
            logger.warning("Skipping package with missing name")
            continue

        # TODO there are some existing packages that have hyphens instead of . which seems wrong?
        # ^ should manually edit these before running this script coz it messes with alphabetical sort

        module_name = package_name.replace("-", ".")

        imports = [
            f"- {module_name}",
            f"- {module_name}.aio",
            f"- {module_name}.aio.operations",
            f"- {module_name}.models",
            f"- {module_name}.operations",
        ]

        new_imports.extend(imports)
        logger.info(f"Generated import statements for {package_name}")

    all_imports = list(set(existing_imports + new_imports))

    # sort alphabetically
    all_imports.sort()

    # format imports with proper indentation
    formatted_imports = "\n".join(f"    {imp}" for imp in all_imports)

    # replace the imports section
    new_imports_section = f"test:\n  imports:\n{formatted_imports}\n\n"
    updated_content = re.sub(
        r"^test:\s*\n\s*imports:.*?^(?=\w)",
        new_imports_section,
        content,
        flags=re.MULTILINE | re.DOTALL,
    )

    try:
        with open(CONDA_MGMT_META_YAML_PATH, "w") as file:
            file.write(updated_content)
    except Exception as e:
        logger.error(f"Failed to update {CONDA_MGMT_META_YAML_PATH}: {e}")
        result.extend([pkg.get(PACKAGE_COL) for pkg in new_packages])

    logger.info(f"Added {len(new_packages)} new management plane packages to meta.yaml")
    return result


# =====================================
# Helpers for updating release logs
# =====================================


def update_release_logs(
    package_dict: Dict,
    new_data_plane_names: List[str],
    new_mgmt_plane_names: List[str],
    release_date: str,
) -> List[str]:
    """
    Add and update release logs for conda packages. Release log includes versions of all packages for the release
    """
    result = []

    # TODO update mgmt release log separately
    mgmt_release_log_path = os.path.join(CONDA_RELEASE_LOGS_DIR, "azure-mgmt.md")

    # TODO update all existing data plane release logs

    # TODO update release logs for new packages
    for package_name in new_data_plane_names:
        pkg = package_dict.get(package_name, {})
        version = pkg.get(VERSION_GA_COL)

        if not version:
            logger.warning(f"Skipping {package_name} with missing version")
            result.append(package_name)
            continue

        # check for group
        group_name = get_release_group(package_name, get_package_to_group_mapping())
        group_data = get_package_group_data(group_name)
        if group_data:
            release_log_path = os.path.join(CONDA_RELEASE_LOGS_DIR, f"{group_name}.md")
        else:
            release_log_path = os.path.join(
                CONDA_RELEASE_LOGS_DIR, f"{package_name}.md"
            )

        if not os.path.exists(release_log_path):
            # Add new release log
            logger.info(f"Creating new release log for: {package_name}")

            try:
                title_parts = package_name.replace("azure-", "").split("-")
                title = " ".join(word.title() for word in title_parts)

                content = f"# Azure {title} client library for Python (conda)\n\n"
                content += f"## {release_date}\n\n"
                content += "### Packages included\n\n"

                content += f"- {package_name}-{version}\n"

                with open(release_log_path, "w") as f:
                    f.write(content)
                logger.info(f"Created new release log for {package_name}")
            except Exception as e:
                logger.error(f"Failed to create release log for {package_name}: {e}")
                result.append(package_name)

        else:
            # Update existing release log
            try:
                with open(release_log_path, "r") as f:
                    existing_content = f.read()

                lines = existing_content.split("\n")

                new_release = f"\n## {release_date}\n\n"
                new_release += "### Packages included\n\n"
                new_release += f"- {package_name}-{version}\n"

                lines.insert(1, new_release)
                updated_content = "\n".join(lines)

                with open(release_log_path, "w") as f:
                    f.write(updated_content)

                logger.info(f"Updated release log for {package_name}")
            except Exception as e:
                logger.error(f"Failed to update release log for {package_name}: {e}")
                result.append(package_name)

    # TODO AKA link pointing to new release logs needs to happen

    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Update conda package files and versions for release."
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable debug logging",
    )

    args = parser.parse_args()
    configure_logging(args)

    old_date, new_version = update_conda_version()

    # convert to mm/dd/yyyy format for comparison with CSV dates
    old_version = old_date.strftime("%m/%d/%Y")

    # Parse CSV data
    packages = parse_csv()

    if not packages:
        logger.error("No packages found in CSV data.")
        exit(1)

    # Only ship GA packages that are not deprecated
    packages = [
        pkg
        for pkg in packages
        if (pkg.get(VERSION_GA_COL) and pkg.get(LATEST_GA_DATE_COL))
    ]
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

    # Extract package names from the filtered lists
    outdated_package_names = [
        pkg.get(PACKAGE_COL, "") for pkg in outdated_packages if pkg.get(PACKAGE_COL)
    ]
    new_data_plane_names = [
        pkg.get(PACKAGE_COL, "")
        for pkg in new_data_plane_packages
        if pkg.get(PACKAGE_COL)
    ]
    new_mgmt_plane_names = [
        pkg.get(PACKAGE_COL, "")
        for pkg in new_mgmt_plane_packages
        if pkg.get(PACKAGE_COL)
    ]

    # map package name to csv row for easy lookup
    package_dict = {pkg.get(PACKAGE_COL, ""): pkg for pkg in packages}

    # update conda-sdk-client.yml
    # TODO handle packages missing from conda-sdk-client that aren't new relative to the last release...
    conda_sdk_client_pkgs_result = update_conda_sdk_client_yml(
        package_dict, outdated_package_names, new_data_plane_names, new_mgmt_plane_names
    )

    # handle new data plane libraries
    new_data_plane_results = add_new_data_plane_packages(
        package_dict, new_data_plane_names
    )

    # handle new mgmt plane libraries
    new_mgmt_plane_results = add_new_mgmt_plane_packages(new_mgmt_plane_packages)

    # add/update release logs
    release_log_results = update_release_logs(
        package_dict, new_data_plane_names, new_mgmt_plane_names, new_version
    )

    print("=== REPORT ===")

    if conda_sdk_client_pkgs_result:
        print(
            "The following packages may require manual adjustments in conda-sdk-client.yml:"
        )
        for pkg_name in conda_sdk_client_pkgs_result:
            print(f"- {pkg_name}")

    if new_data_plane_results:
        print(
            "\nThe following new data plane packages may require manual meta.yaml creation or adjustments:"
        )
        for pkg_name in new_data_plane_results:
            print(f"- {pkg_name}")

    if new_mgmt_plane_results:
        print(
            "\nThe following new management plane packages may require manual adjustments in azure-mgmt/meta.yaml:"
        )
        for pkg_name in new_mgmt_plane_results:
            print(f"- {pkg_name}")

    if release_log_results:
        print(
            "\nThe following packages may require manual adjustments in release logs:"
        )
        for pkg_name in release_log_results:
            print(f"- {pkg_name}")
