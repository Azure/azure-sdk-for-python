"""Update package versions, yml files, release-logs, and changelogs for conda packages."""

import os
import argparse
import yaml
import re
import glob
from datetime import datetime
from dateutil.relativedelta import relativedelta
from ci_tools.logging import logger, configure_logging
from ci_tools.parsing import ParsedSetup
from typing import Optional
from conda_helper_functions import (
    parse_csv,
    separate_packages_by_type,
    package_needs_update,
    get_package_data_from_pypi,
    build_package_index,
    get_package_path,
    get_bundle_name,
    map_bundle_to_packages,
    get_valid_package_imports,
    PACKAGE_COL,
    VERSION_GA_COL,
    LATEST_GA_DATE_COL,
    REPO_PATH_COL,
    SUPPORT_COL,
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

# packages that should be shipped but are known to be missing from the csv - store version here
PACKAGES_WITH_DOWNLOAD_URI = {
    "msal": "",
    "msal-extensions": "",
}


# =====================================
# Helpers for updating conda_env.yml
# =====================================


class quoted(str):
    pass


def quoted_presenter(dumper, data):
    """YAML presenter to force quotes around a string."""
    return dumper.represent_scalar("tag:yaml.org,2002:str", data, style="'")


def update_conda_version(
    target_release_date: Optional[datetime] = None,
) -> tuple[datetime, str]:
    """Update the AZURESDK_CONDA_VERSION in conda_env.yml and return the old and new versions.

    Args:
        target_release_date: Optional specific release date to use. If None, calculates
                            the next release date by adding RELEASE_PERIOD_MONTHS to the old version.
    """

    with open(CONDA_ENV_PATH, "r") as file:
        conda_env_data = yaml.safe_load(file)

    old_version = conda_env_data["variables"]["AZURESDK_CONDA_VERSION"]
    old_date = datetime.strptime(old_version, "%Y.%m.%d")

    if target_release_date:
        new_date = target_release_date
    else:
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
    package_dict: dict[str, dict[str, str]],
    packages_to_update: list[str],
    new_data_plane_packages: list[str],
    new_mgmt_plane_packages: list[str],
) -> list[str]:
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

            # store retrieved version for release log
            PACKAGES_WITH_DOWNLOAD_URI[pkg_name] = latest_version

            if curr_download_uri != download_uri:
                # version needs update
                logger.info(
                    f"Package {pkg_name} download_uri mismatch with PyPi, updating {curr_download_uri} to {download_uri}"
                )
                # checkout for these packages only has download_uri, no version field
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

    parameters = conda_client_data["parameters"]

    # quick look up for handling bundled package releases
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

        # bundle info is based on pyproject.toml
        bundle_name = get_bundle_name(package_name)

        if bundle_name:
            # package is part of a bundle
            logger.info(
                f"Package {package_name} belongs to release bundle {bundle_name}"
            )
            release_name = f"release_{bundle_name.replace('-', '_')}"
            display_name = bundle_name
        else:
            # package is released individually
            release_name = f"release_{package_name.replace('-', '_')}"
            display_name = package_name

        # add new release parameter if not exists
        if release_name not in existing_parameter_names:
            logger.info(f"Adding new release parameter: {release_name}")
            new_parameter = {
                "name": release_name,
                "displayName": display_name,
                "type": "boolean",
                "default": True,
            }
            parameters.append(new_parameter)
            existing_parameter_names.append(release_name)

        # add to CondaArtifacts
        curr_version = pkg.get(VERSION_GA_COL)

        if not curr_version:
            logger.error(
                f"Package {package_name} is missing version info, skipping addition"
            )
            result.append(package_name)
            continue

        checkout_package = {"package": package_name, "version": curr_version}
        common_root, service_name = determine_service_info(pkg, bundle_name)

        if package_name in existing_artifact_names:
            # individual released package already exists
            logger.warning(
                f"New package {package_name} already exists in conda-sdk-client.yml, skipping addition"
            )
            result.append(package_name)
            continue

        if bundle_name and bundle_name in existing_artifact_names:
            # bundle already exists, will append packages to it
            logger.info(
                f"Release bundle {bundle_name} already exists in conda-sdk-client.yml, will append package {package_name} to it"
            )
            conda_artifacts[existing_artifact_names[bundle_name]]["checkout"].append(
                checkout_package
            )
        else:
            # no existing artifact, whether bundle or not -> create
            new_artifact_entry = {
                "name": bundle_name if bundle_name else package_name,
                "common_root": common_root,
                "service": service_name,
                "in_batch": f"${{{{ parameters.{release_name} }}}}",
                "checkout": [checkout_package],
            }
            # append before azure-mgmt entry
            conda_artifacts.insert(len(conda_artifacts) - 1, new_artifact_entry)

            added_count += 1
            logger.info(f"Added new data plane package: {package_name}")

            existing_artifact_names[bundle_name if bundle_name else package_name] = (
                len(conda_artifacts) - 2
            )  # new index

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


def determine_service_info(
    pkg: dict[str, str], bundle_name: Optional[str]
) -> tuple[str, str]:
    """
    Returns the common root and service name for the given package.

    :param package_name: The name of the package (e.g., "azure-ai-textanalytics").
    :param bundle_name: The name of the bundle/release group the package belongs to, if any.
    """
    # defaults
    package_name = pkg.get(PACKAGE_COL, "")
    service_name = pkg.get(REPO_PATH_COL, "").lower()
    common_root = "azure"

    package_path = get_package_path(package_name)
    if not service_name and package_path:
        service_name = os.path.basename(os.path.dirname(package_path))

    if bundle_name and service_name:
        common_root = f"azure/{service_name}"

    return common_root, service_name


def format_requirement(req: str) -> str:
    """Format a requirement string for conda meta.yaml."""
    name_unpinned = re.split(r"[>=<!~]", req)[0].strip()

    # assuming this always applies to all azure-* reqs
    if name_unpinned.startswith("azure-") or name_unpinned in ["msrest"]:
        return f"{name_unpinned} >={{{{ environ.get('AZURESDK_CONDA_VERSION', '0.0.0') }}}}"

    # translate compatible release (~=) to >= for yml
    req = req.replace("~=", ">=")
    return req


def get_package_requirements(parsed: ParsedSetup) -> tuple[list[str], list[str]]:
    """Retrieve the host and run requirements for a data plane package meta.yaml."""
    host_requirements = set(["pip", "python"])
    run_requirements = set(["python"])

    # reqs commonly seen in existing meta.yaml files that aren't always in setup.py or pyproject.toml
    for essential_req in ["azure-core", "aiohttp"]:
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

    return list(host_requirements), list(run_requirements)


def get_package_metadata(
    package_name: str, package_path: str, is_bundle: bool = False
) -> tuple[str, str, str]:
    """Extract package metadata for about section in meta.yaml.

    :param package_name: The name of the package or bundle.
    :param package_path: The filesystem path to the package.
    :param is_bundle: Whether this is a release bundle (affects URL structure).
    """
    service_dir = os.path.basename(os.path.dirname(package_path))

    # For bundles, URL points to service directory; for individual packages, include package name
    if is_bundle:
        home_url = (
            f"https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/{service_dir}"
        )
    else:
        home_url = f"https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/{service_dir}/{package_name}"

    summary = f"Microsoft Azure {service_dir.replace('-', ' ').title()} Client Library for Python"

    conda_url = f"https://aka.ms/azsdk/conda/releases/{service_dir}"
    description = (
        f"This is the {summary}.\n    Please see {conda_url} for version details."
    )

    return home_url, summary, description


def generate_data_plane_meta_yaml(
    bundle_map: dict[str, list[str]],
    package_name: str,
    bundle_name: Optional[str],
) -> str:
    """
    Generate the meta.yaml content for a data plane package or release group.
    """
    # Use bundle_name if available for recipe name and env var derivation
    # however, env var name is arbitrary and replaced in conda_functions.py
    recipe_name = bundle_name if bundle_name else package_name
    src_distr_name = recipe_name.split("-")[-1].upper()
    src_distribution_env_var = f"{src_distr_name}_SOURCE_DISTRIBUTION"

    if bundle_name:
        # handle grouped packages
        logger.info(
            f"Generating meta.yaml for release group {bundle_name} including packages: {bundle_map[bundle_name]}"
        )
        host_reqs = set()
        run_reqs = set()
        pkg_imports = []

        for pkg in bundle_map[bundle_name]:
            package_path = get_package_path(pkg)
            parsed_setup = ParsedSetup.from_path(package_path)

            pkg_host_reqs, pkg_run_reqs = get_package_requirements(parsed_setup)
            host_reqs.update(pkg_host_reqs)
            run_reqs.update(pkg_run_reqs)

            # Get valid imports for this package (including .aio if it exists)
            pkg_imports.extend(get_valid_package_imports(pkg))
        host_reqs = list(host_reqs)
        run_reqs = list(run_reqs)
        pkg_imports = list(set(pkg_imports))  # deduplicate

        package_path = get_package_path(bundle_map[bundle_name][0])

        if not package_path:
            logger.error(
                f"Could not find package path for {bundle_name} to extract metadata, skipping meta.yaml generation"
            )
            return ""

        home_url, summary, description = get_package_metadata(
            bundle_name, package_path, is_bundle=True
        )
    else:
        logger.info(f"Generating meta.yaml for package {package_name}")
        package_path = get_package_path(package_name)

        if not package_path:
            logger.error(
                f"Could not find package path for {package_name} to extract metadata, skipping meta.yaml generation"
            )
            return ""
        parsed_setup = ParsedSetup.from_path(package_path)

        host_reqs, run_reqs = get_package_requirements(parsed_setup)
        # Get valid imports for this package (including .aio if it exists)
        pkg_imports = get_valid_package_imports(package_name)

        home_url, summary, description = get_package_metadata(
            package_name, package_path
        )

    # Format requirements with proper YAML indentation
    host_reqs_str = "\n    - ".join(host_reqs)
    run_reqs_str = "\n    - ".join(run_reqs)
    pkg_imports_str = "\n    - ".join(pkg_imports)
    meta_yaml_content = f"""{{% set name = "{recipe_name}" %}}

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
    bundle_map: dict[str, list[str]],
    new_data_plane_names: list[str],
) -> list[str]:
    """Create meta.yaml files for new data plane packages and add import tests."""
    if len(new_data_plane_names) == 0:
        return []

    logger.info(f"Adding {len(new_data_plane_names)} new data plane packages")
    result = []

    # bundles are processed once when encountering the first package in that group
    bundles_processed = set()
    for package_name in new_data_plane_names:
        logger.info(f"Adding new data plane meta.yaml for: {package_name}")

        folder_name = package_name
        bundle_name = get_bundle_name(package_name)
        if bundle_name:
            if bundle_name in bundles_processed:
                logger.info(
                    f"Meta.yaml for bundle {bundle_name} already created, skipping {package_name}"
                )
                continue
            folder_name = bundle_name

        pkg_yaml_path = os.path.join(CONDA_RECIPES_DIR, folder_name, "meta.yaml")
        os.makedirs(os.path.dirname(pkg_yaml_path), exist_ok=True)

        try:
            meta_yml = generate_data_plane_meta_yaml(
                bundle_map, package_name, bundle_name
            )
            if bundle_name:
                bundles_processed.add(bundle_name)
        except Exception as e:
            logger.error(
                f"Failed to generate meta.yaml content for {package_name} and skipping, error: {e}"
            )
            result.append(package_name)
            continue

        if not meta_yml:
            logger.error(
                f"Meta.yaml content for {package_name} is empty, skipping file creation"
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


def add_new_mgmt_plane_packages(new_mgmt_plane_names: list[str]) -> list[str]:
    """Update azure-mgmt/meta.yaml with new management libraries, and add import tests."""
    if len(new_mgmt_plane_names) == 0:
        return []
    logger.info(f"Adding {len(new_mgmt_plane_names)} new management plane packages")
    result = []

    # can't use pyyaml due to jinja2
    with open(CONDA_MGMT_META_YAML_PATH, "r") as file:
        content = file.read()

    test_match = re.search(
        r"^test:\s*\n\s*imports:(.*?)^(?=\w)", content, re.MULTILINE | re.DOTALL
    )
    if not test_match:
        logger.error("Could not find 'test: imports:' section in meta.yaml")
        result.extend(new_mgmt_plane_names)
        return result

    existing_imports_text = test_match.group(1)
    existing_imports = [
        line.strip()
        for line in existing_imports_text.strip().split("\n")
        if line.strip().startswith("-")
    ]

    new_imports = []
    for package_name in new_mgmt_plane_names:
        if not package_name:
            logger.warning("Skipping package with missing name")
            continue

        imports = get_valid_package_imports(package_name)
        # Format imports for YAML with "- " prefix
        formatted = [f"- {imp}" for imp in imports]
        new_imports.extend(formatted)
        logger.info(
            f"Generated {len(imports)} import statements for {package_name}: {formatted}"
        )

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
        result.extend(new_mgmt_plane_names)

    logger.info(
        f"Added {len(new_mgmt_plane_names)} new management plane packages to meta.yaml"
    )
    return result


# =====================================
# Helpers for updating release logs
# =====================================


def update_data_plane_release_logs(
    package_dict: dict,
    bundle_map: dict[str, list[str]],
    new_data_plane_names: list[str],
    release_date: str,
) -> list[str]:
    """
    Add and update release logs for data plane conda packages. Release log includes versions of all packages for the release
    """
    result = []

    # Update all existing data plane release logs by file

    existing_release_logs = glob.glob(os.path.join(CONDA_RELEASE_LOGS_DIR, "*.md"))
    for release_log_path in existing_release_logs:
        curr_service_name = os.path.basename(release_log_path).replace(".md", "")
        # skip azure-mgmt here
        if curr_service_name == "azure-mgmt":
            continue
        if (
            curr_service_name not in package_dict
            and curr_service_name not in bundle_map
            and curr_service_name not in PACKAGES_WITH_DOWNLOAD_URI
        ):
            logger.warning(
                f"Existing release log service {curr_service_name} was not found in CSV data, skipping update. It may be deprecated."
            )
            result.append(curr_service_name)
            continue

        pkg_updates = []
        if curr_service_name in bundle_map:
            # handle grouped packages
            pkg_names_in_bundle = bundle_map[curr_service_name]
            for pkg_name in pkg_names_in_bundle:
                pkg = package_dict.get(pkg_name, {})
                version = pkg.get(VERSION_GA_COL)
                if version:
                    pkg_updates.append(f"- {pkg_name}-{version}")
                else:
                    # shouldn't happen, but fallback
                    logger.error(
                        f"Package {pkg_name} in group {curr_service_name} is missing version info, it may be deprecated. Skipping in release log update"
                    )
                    result.append(pkg_name)
        else:
            # handle exception for packages with download_uri
            if curr_service_name in PACKAGES_WITH_DOWNLOAD_URI:
                version = PACKAGES_WITH_DOWNLOAD_URI[curr_service_name]
                if not version:
                    logger.error(
                        f"Package {curr_service_name} with download_uri is missing version info, it may be deprecated. Skipping in release log update"
                    )
                    result.append(curr_service_name)
                    continue
            else:
                pkg = package_dict.get(curr_service_name, {})
                version = pkg.get(VERSION_GA_COL)

            if version:
                pkg_updates.append(f"- {curr_service_name}-{version}")
            else:
                logger.error(
                    f"Package {curr_service_name} is missing version info, it may be deprecated. Skipping in release log update"
                )
                result.append(curr_service_name)
        try:
            with open(release_log_path, "r") as f:
                existing_content = f.read()

            lines = existing_content.split("\n")

            new_release = f"\n## {release_date}\n\n"

            # check if release is already logged
            if new_release in existing_content:
                logger.info(
                    f"Release log for {curr_service_name} already contains entry for {release_date}, overwriting"
                )
                # remove existing release section to overwrite
                release_idx = lines.index(new_release.strip())

                ## find next release heading or end of file
                next_release_idx = next(
                    (
                        i
                        for i in range(release_idx + 1, len(lines))
                        if lines[i].startswith("## ")
                    ),
                    len(lines),
                )
                del lines[release_idx:next_release_idx]

            new_release += "### Packages included\n\n"
            new_release += "\n".join(pkg_updates)
            lines.insert(1, new_release)

            updated_content = "\n".join(lines)

            with open(release_log_path, "w") as f:
                f.write(updated_content)

            logger.info(f"Updated release log for {os.path.basename(release_log_path)}")
        except Exception as e:
            logger.error(
                f"Failed to update release log {os.path.basename(release_log_path)}: {e}"
            )
            result.append(curr_service_name)

    # Handle brand new packages
    for package_name in new_data_plane_names:
        pkg = package_dict.get(package_name, {})
        version = pkg.get(VERSION_GA_COL)

        if not version:
            logger.warning(f"Skipping {package_name} with missing version")
            result.append(package_name)
            continue

        bundle_name = get_bundle_name(package_name)
        # check for bundle
        if bundle_name:
            display_name = bundle_name
        else:
            display_name = package_name

        release_log_path = os.path.join(CONDA_RELEASE_LOGS_DIR, f"{display_name}.md")

        if not os.path.exists(release_log_path):
            # Add brand new release log file
            logger.info(f"Creating new release log for: {display_name}")

            title_parts = display_name.replace("azure-", "").split("-")
            title = " ".join(word.title() for word in title_parts)

            content = f"# Azure {title} client library for Python (conda)\n\n"
            content += f"## {release_date}\n\n"
            content += "### Packages included\n\n"

            pkg_updates = []
            if bundle_name:
                pkg_names_in_log = bundle_map.get(bundle_name, [])
                for pkg_name in pkg_names_in_log:
                    pkg = package_dict.get(pkg_name, {})
                    version = pkg.get(VERSION_GA_COL)
                    pkg_updates.append(f"- {pkg_name}-{version}")
            else:
                pkg = package_dict.get(package_name, {})
                version = pkg.get(VERSION_GA_COL)
                pkg_updates.append(f"- {package_name}-{version}")
            content += "\n".join(pkg_updates)

            try:
                with open(release_log_path, "w") as f:
                    f.write(content)
                logger.info(f"Created new release log for {display_name}")
            except Exception as e:
                logger.error(f"Failed to create release log for {display_name}: {e}")
                result.append(display_name)

        else:
            logger.info(
                f"Release log for {display_name} already exists, check that new package {package_name} is included"
            )

    return result


def update_mgmt_plane_release_log(
    package_dict: dict,
    all_mgmt_plane_names: list[str],
    release_date: str,
) -> list[str]:
    """
    Update azure-mgmt release log.
    """
    result = []

    mgmt_log_path = os.path.join(CONDA_RELEASE_LOGS_DIR, "azure-mgmt.md")
    if not os.path.exists(mgmt_log_path):
        logger.error("Management plane release log azure-mgmt.md does not exist.")
        return all_mgmt_plane_names  # all new packages need attention

    pkg_updates = []
    for package_name in all_mgmt_plane_names:
        pkg = package_dict.get(package_name, {})
        version = pkg.get(VERSION_GA_COL)

        if not version:
            logger.warning(
                f"Skipping release log update of {package_name} with missing version"
            )
            result.append(package_name)
            continue

        pkg_updates.append(f"- {package_name}-{version}")

    try:
        with open(mgmt_log_path, "r") as f:
            existing_content = f.read()

        lines = existing_content.split("\n")

        new_release = f"\n## {release_date}\n\n"

        # check if release is already logged
        if new_release in existing_content:
            logger.info(
                f"Release log for azure-mgmt already contains entry for {release_date}, overwriting"
            )
            # remove existing release section to overwrite
            release_idx = lines.index(new_release.strip())

            ## find next release heading or end of file
            next_release_idx = next(
                (
                    i
                    for i in range(release_idx + 1, len(lines))
                    if lines[i].startswith("## ")
                ),
                len(lines),
            )
            del lines[release_idx:next_release_idx]

        new_release += "### Packages included\n\n"

        new_release += "\n".join(pkg_updates)
        lines.insert(1, new_release)
        updated_content = "\n".join(lines)

        with open(mgmt_log_path, "w") as f:
            f.write(updated_content)
    except Exception as e:
        logger.error(f"Failed to update azure-mgmt release log: {e}")
        return all_mgmt_plane_names

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
    parser.add_argument(
        "--release-date",
        type=str,
        default=None,
        help="Release date in 'MM.DD' format (e.g., '03.01', '12.01'). "
        "Year is determined automatically. If not provided, the next release date is calculated.",
    )

    args = parser.parse_args()
    configure_logging(args)

    # Handle release date
    if args.release_date:
        try:
            current_year = datetime.now().year
            target_release_date = datetime.strptime(
                f"{current_year}.{args.release_date}", "%Y.%m.%d"
            )
            logger.info(
                f"Using provided release date: {target_release_date.strftime('%Y.%m.%d')}"
            )
        except ValueError as e:
            logger.error(f"Invalid release date format '{args.release_date}': {e}")
            logger.error("Expected format: 'MM.DD' (e.g., '03.01', '12.01')")
            exit(1)
    else:
        logger.info(
            "No release date provided, auto bumping old date by {} months.".format(
                RELEASE_PERIOD_MONTHS
            )
        )
        target_release_date = None

    old_date, new_version = update_conda_version(target_release_date)

    # Output version as Azure DevOps pipeline variable to use in PR
    print(f"##vso[task.setvariable variable=CondaReleaseVersion]{new_version}")

    # convert to mm/dd/yyyy format for comparison with CSV dates
    old_version = old_date.strftime("%m/%d/%Y")

    packages = parse_csv()
    if not packages:
        logger.error("No packages found in CSV data.")
        exit(1)

    # Only ship GA packages that are not deprecated
    packages = [
        pkg
        for pkg in packages
        if (
            (pkg.get(VERSION_GA_COL) and pkg.get(LATEST_GA_DATE_COL))
            and not pkg.get(SUPPORT_COL) == "deprecated"
        )
    ]
    logger.info(f"Filtered to {len(packages)} GA packages")

    data_pkgs, mgmt_pkgs = separate_packages_by_type(packages)

    outdated_data_plane_names = [
        pkg.get(PACKAGE_COL, "")
        for pkg in data_pkgs
        if package_needs_update(pkg, old_version, is_new=False)
    ]
    new_data_plane_names = [
        pkg.get(PACKAGE_COL, "")
        for pkg in data_pkgs
        if package_needs_update(pkg, old_version, is_new=True)
    ]
    outdated_mgmt_plane_names = [
        pkg.get(PACKAGE_COL, "")
        for pkg in mgmt_pkgs
        if package_needs_update(pkg, old_version, is_new=False)
    ]
    new_mgmt_plane_names = [
        pkg.get(PACKAGE_COL, "")
        for pkg in mgmt_pkgs
        if package_needs_update(pkg, old_version, is_new=True)
    ]

    # don't overlap new packages with outdated packages
    outdated_data_plane_names = [
        name for name in outdated_data_plane_names if name not in new_data_plane_names
    ]
    outdated_mgmt_plane_names = [
        name for name in outdated_mgmt_plane_names if name not in new_mgmt_plane_names
    ]

    # map package name to csv row for easy lookup
    package_dict = {pkg.get(PACKAGE_COL, ""): pkg for pkg in packages}

    outdated_package_names = outdated_data_plane_names + outdated_mgmt_plane_names

    # update conda-sdk-client.yml
    conda_sdk_client_pkgs_result = update_conda_sdk_client_yml(
        package_dict, outdated_package_names, new_data_plane_names, new_mgmt_plane_names
    )

    # pre-process bundled data packages to minimize file writes for new data plane packages,
    # and release logs (mgmt packages are always bundled together)
    bundle_map, bundle_failed_pkgs = map_bundle_to_packages(
        [pkg.get(PACKAGE_COL, "") for pkg in data_pkgs]
    )
    logger.info(
        f"Identified {len(bundle_map)} release bundles from package data: {bundle_map}"
    )

    # handle new data plane libraries
    new_data_plane_results = add_new_data_plane_packages(
        bundle_map, new_data_plane_names
    )

    # handle new mgmt plane libraries
    new_mgmt_plane_results = add_new_mgmt_plane_packages(new_mgmt_plane_names)

    # add/update release logs
    data_plane_release_log_results = update_data_plane_release_logs(
        package_dict, bundle_map, new_data_plane_names, new_version
    )

    all_mgmt_plane_names = [pkg.get(PACKAGE_COL, "") for pkg in mgmt_pkgs]

    mgmt_plane_release_log_results = update_mgmt_plane_release_log(
        package_dict, all_mgmt_plane_names, new_version
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

    if data_plane_release_log_results:
        print(
            "\nThe following data plane packages may require manual adjustments in release logs:"
        )
        for pkg_name in data_plane_release_log_results:
            print(f"- {pkg_name}")

    if mgmt_plane_release_log_results:
        print(
            "\nThe following management plane packages may require manual adjustments in azure-mgmt release log:"
        )
        for pkg_name in mgmt_plane_release_log_results:
            print(f"- {pkg_name}")

    if bundle_failed_pkgs:
        print(
            "\nThe following packages errored when constructing bundle map, they may need a [tool.azure-sdk-conda] section in their pyproject.toml for proper release grouping, and may have been improperly individually processed."
        )
        for pkg_name in bundle_failed_pkgs:
            print(f"- {pkg_name}")

    if len(new_data_plane_names) > 0:
        print("\n=== Manual Steps for New Data Plane Packages ===")
        print(
            "- A dummy placeholder library needs to be requested on Conda for new data plane packages."
        )
        print("- A new AKA link needs to be created for each new release log.")
        print(
            "\nSee the generated PR description for further details. The new data plane package names are:"
        )
        for pkg_name in new_data_plane_names:
            print(f"{pkg_name}")
