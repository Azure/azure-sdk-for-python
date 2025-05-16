#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import argparse
import os
import sys
import logging
import re

from subprocess import check_call
from typing import TYPE_CHECKING, Callable, Optional
from pkg_resources import parse_version, Requirement
from pypi_tools.pypi import PyPIClient
from packaging.specifiers import SpecifierSet
from packaging.version import Version

from ci_tools.parsing import ParsedSetup, parse_require
from ci_tools.functions import compare_python_version, handle_incompatible_minimum_dev_reqs

from typing import List

DEV_REQ_FILE = "dev_requirements.txt"
NEW_DEV_REQ_FILE = "new_dev_requirements.txt"
PKGS_TXT_FILE = "packages.txt"

logging.getLogger().setLevel(logging.INFO)

# GENERIC_OVERRIDES dictionaries pair a specific dependency with a MINIMUM or MAXIMUM inclusive bound.
# During LATEST and MINIMUM dependency checks, we sometimes need to ignore versions for various compatibility
# reasons.
MINIMUM_VERSION_GENERIC_OVERRIDES = {
    "azure-common": "1.1.10",
    "msrest": "0.6.10",
    "typing-extensions": "4.6.0",
    "opentelemetry-api": "1.3.0",
    "opentelemetry-sdk": "1.3.0",
    "azure-core": "1.11.0",
    "requests": "2.19.0",
    "six": "1.12.0",
    "cryptography": "38.0.3",
    "msal": "1.23.0",
    "azure-storage-file-datalake": "12.2.0",
}

MAXIMUM_VERSION_GENERIC_OVERRIDES = {}

# SPECIFIC OVERRIDES provide additional filtering of upper and lower bound by
# binding an override to the specific package being processed. As an example, when
# processing the latest or minimum deps for "azure-eventhub", the minimum version of "azure-core"
# will be overridden to 1.25.0.
MINIMUM_VERSION_SPECIFIC_OVERRIDES = {
    "azure-eventhub": {"azure-core": "1.25.0"},
    "azure-eventhub-checkpointstoreblob-aio": {"azure-core": "1.25.0", "azure-eventhub": "5.11.0"},
    "azure-eventhub-checkpointstoreblob": {"azure-core": "1.25.0", "azure-eventhub": "5.11.0"},
    "azure-eventhub-checkpointstoretable": {"azure-core": "1.25.0", "azure-eventhub": "5.11.0"},
    "azure-identity": {"msal": "1.23.0"},
    "azure-core-tracing-opentelemetry": {"azure-core": "1.28.0"},
    "azure-storage-file-datalake": {"azure-storage-blob": "12.22.0"},
    "azure-cosmos": {"azure-core": "1.30.0"},
    "azure-appconfiguration-provider": {"azure-appconfiguration": "1.7.2"},
    "azure-ai-evaluation": {"aiohttp": "3.8.6"}
}

MAXIMUM_VERSION_SPECIFIC_OVERRIDES = {}

# PLATFORM SPECIFIC OVERRIDES provide additional generic (EG not tied to the package whos dependencies are being processed)
# filtering on a _per platform_ basis. Primarily used to limit certain packages due to platform compat
PLATFORM_SPECIFIC_MINIMUM_OVERRIDES = {
    ">=3.12.0": {
        "azure-core": "1.23.1",
        "aiohttp": "3.9.0",
        "six": "1.16.0",
        "requests": "2.30.0"
    },
    ">=3.13.0": {
        "typing-extensions": "4.12.0",
        "aiohttp": "3.10.6"
    }
}

PLATFORM_SPECIFIC_MAXIMUM_OVERRIDES = {}

# This is used to actively _add_ requirements to the install set. These are used to actively inject
# a new requirement specifier to the set of packages being installed.
SPECIAL_CASE_OVERRIDES = {
    # this package has an override
    "azure-core": {
        # if the version being installed matches this specifier, add the listed packages to the install list
        "<1.24.0": ["msrest<0.7.0"]
    }
}


def install_dependent_packages(setup_py_file_path, dependency_type, temp_dir):
    # This method identifies latest/ minimal version of dependent packages and installs them from pyPI
    # dependency type must either be latest or minimum
    # Latest dependency will find latest released package that satisfies requires of given package name
    # Minimum type will find minimum version on PyPI that satisfies requires of given package name
    released_packages = find_released_packages(setup_py_file_path, dependency_type)
    override_added_packages = []

    # new section added to account for difficulties with msrest
    for pkg_spec in released_packages:
        override_added_packages.extend(check_pkg_against_overrides(pkg_spec))

    logging.info("%s released packages: %s", dependency_type, released_packages)

    additional_filter_fn = None
    if dependency_type == "Minimum":
        additional_filter_fn = handle_incompatible_minimum_dev_reqs

    # before september 2024, filter_dev_requirements only would remove any packages present in released_packages from the dev_requirements,
    # then create a new file "new_dev_requirements.txt" without the problematic packages.
    # after september 2024, filter_dev_requirements will also check for **compatibility** with the packages being installed when filtering the dev_requirements.
    dev_req_file_path = filter_dev_requirements(setup_py_file_path, released_packages, temp_dir, additional_filter_fn)

    if override_added_packages:
        logging.info(f"Expanding the requirement set by the packages {override_added_packages}.")

    install_set = released_packages + list(set(override_added_packages))

    # install released dependent packages
    if released_packages or dev_req_file_path:
        install_packages(install_set, dev_req_file_path)

    if released_packages:
        # create a file with list of packages and versions found based on minimum or latest check on PyPI
        # This file can be used to verify if we have correct version installed
        pkgs_file_path = os.path.join(temp_dir, PKGS_TXT_FILE)
        with open(pkgs_file_path, "w") as pkgs_file:
            for package in released_packages:
                pkgs_file.write(package + "\n")
        logging.info("Created file %s to track azure packages found on PyPI", pkgs_file_path)


def check_pkg_against_overrides(pkg_specifier: str) -> List[str]:
    """
    Checks a set of package specifiers of form "[A==1.0.0, B=2.0.0]". Used to inject additional package installations
    as indicated by the SPECIAL_CASE_OVERRIDES dictionary.

    :param str pkg_specifier: A specifically targeted package that is about to be passed to install_packages.
    """
    additional_installs = []
    target_package, target_version = pkg_specifier.split("==")

    target_version = Version(target_version)
    if target_package in SPECIAL_CASE_OVERRIDES:
        special_case_specifiers = SPECIAL_CASE_OVERRIDES[target_package]

        for specifier_set in special_case_specifiers.keys():
            spec = SpecifierSet(specifier_set)
            if target_version in spec:
                additional_installs.extend(special_case_specifiers[specifier_set])

    return additional_installs


def find_released_packages(setup_py_path, dependency_type):
    # this method returns list of required available package on PyPI in format <package-name>==<version>
    pkg_info = ParsedSetup.from_path(setup_py_path)

    # parse setup.py and find install requires
    requires = [r for r in pkg_info.requires if "-nspkg" not in r]

    # Get available version on PyPI for each required package
    avlble_packages = [x for x in map(lambda x: process_requirement(x, dependency_type, pkg_info.name), requires) if x]

    return avlble_packages


def process_bounded_versions(originating_pkg_name: str, pkg_name: str, versions: List[str]) -> List[str]:
    """
    Processes a target package based on an originating package (target is a dep of originating) and the versions available from pypi for the target package.

    Returns the set of versions AFTER general, platform, and package-specific overrides have been applied.

    :param str originating_pkg_name: The name of the package whos requirements are being processed.
    :param str pkg_name: A specific requirement of the originating package being processed.
    :param List[str] versions: All the versions available on pypi for pkg_name.
    """

    # lower bound general
    if pkg_name in MINIMUM_VERSION_GENERIC_OVERRIDES:
        versions = [
            v for v in versions if parse_version(v) >= parse_version(MINIMUM_VERSION_GENERIC_OVERRIDES[pkg_name])
        ]

    # lower bound platform-specific
    for platform_bound in PLATFORM_SPECIFIC_MINIMUM_OVERRIDES.keys():
        if compare_python_version(platform_bound):
            restrictions = PLATFORM_SPECIFIC_MINIMUM_OVERRIDES[platform_bound]

            if pkg_name in restrictions:
                versions = [v for v in versions if parse_version(v) >= parse_version(restrictions[pkg_name])]

    # lower bound package-specific
    if (
        originating_pkg_name in MINIMUM_VERSION_SPECIFIC_OVERRIDES
        and pkg_name in MINIMUM_VERSION_SPECIFIC_OVERRIDES[originating_pkg_name]
    ):
        versions = [
            v
            for v in versions
            if parse_version(v) >= parse_version(MINIMUM_VERSION_SPECIFIC_OVERRIDES[originating_pkg_name][pkg_name])
        ]

    # upper bound general
    if pkg_name in MAXIMUM_VERSION_GENERIC_OVERRIDES:
        versions = [
            v for v in versions if parse_version(v) <= parse_version(MAXIMUM_VERSION_GENERIC_OVERRIDES[pkg_name])
        ]

    # upper bound platform
    for platform_bound in PLATFORM_SPECIFIC_MAXIMUM_OVERRIDES.keys():
        if compare_python_version(platform_bound):
            restrictions = PLATFORM_SPECIFIC_MAXIMUM_OVERRIDES[platform_bound]

            if pkg_name in restrictions:
                versions = [v for v in versions if parse_version(v) <= parse_version(restrictions[pkg_name])]

    # upper bound package-specific
    if (
        originating_pkg_name in MAXIMUM_VERSION_SPECIFIC_OVERRIDES
        and pkg_name in MAXIMUM_VERSION_SPECIFIC_OVERRIDES[originating_pkg_name]
    ):
        versions = [
            v
            for v in versions
            if parse_version(v) <= parse_version(MAXIMUM_VERSION_SPECIFIC_OVERRIDES[originating_pkg_name][pkg_name])
        ]

    return versions


def process_requirement(req, dependency_type, orig_pkg_name):
    # this method finds either latest or minimum version of a package that is available on PyPI

    # find package name and requirement specifier from requires
    requirement = parse_require(req)
    pkg_name = requirement.key
    spec = requirement.specifier if len(requirement.specifier) else None

    # Filter out requirements with environment markers that don't match the current environment
    # e.g. `; python_version > 3.10` when running on Python3.9
    if not (requirement.marker is None or requirement.marker.evaluate()):
        logging.info(
            f"Skipping requirement {req!r}. Environment marker {str(requirement.marker)!r} "
            + "does not apply to current environment."
        )
        return ""

    # get available versions on PyPI
    client = PyPIClient()
    versions = [str(v) for v in client.get_ordered_versions(pkg_name, True)]
    logging.info("Versions available on PyPI for %s: %s", pkg_name, versions)

    # think of the various versions that come back from pypi as the top of a funnel
    # We apply generic overrides -> platform specific overrides -> package specific overrides
    versions = process_bounded_versions(orig_pkg_name, pkg_name, versions)

    # Search from lowest to latest in case of finding minimum dependency
    # Search from latest to lowest in case of finding latest required version
    # reverse the list to get latest version first
    if dependency_type == "Latest":
        versions.reverse()

    # return first version that matches specifier in <package-name>==<version> format
    for version in versions:
        # if there IS NO specifier, then we should take the first entry. we have already sorted for latest/minimum.
        if spec is None:
            return pkg_name + "==" + version

        if version in spec:
            logging.info(
                "Found %s version %s that matches specifier %s",
                dependency_type,
                version,
                spec,
            )
            return pkg_name + "==" + version

    logging.error(
        "No version is found on PyPI for package %s that matches specifier %s",
        pkg_name,
        spec,
    )
    return ""


def check_req_against_exclusion(req, req_to_exclude):
    """
    This function evaluates a requirement from a dev_requirements file against a file name. Returns True
    if the requirement is for the same package listed in "req_to_exclude". False otherwise.

    :param req: An incoming "req" looks like a requirement that appears in a dev_requirements file. EG: [ "../../../tools/azure-sdk-tools",
        "https://docsupport.blob.core.windows.net/repackaged/cffi-1.14.6-cp310-cp310-win_amd64.whl; sys_platform=='win32' and python_version >= '3.10'",
        "msrestazure>=0.4.11", "pytest" ]

    :param req_to_exclude: A valid and complete python package name. No specifiers.
    """
    req_id = ""
    for c in req:
        if re.match(r"[A-Za-z0-9_-]", c):
            req_id += c
        else:
            break

    return req_id == req_to_exclude


def filter_dev_requirements(
    setup_py_path,
    released_packages,
    temp_dir,
    additional_filter_fn: Optional[Callable[[str, List[str], List[Requirement]], List[str]]] = None,
):
    """
    This function takes an existing package path, a list of specific package specifiers that we have resolved, a temporary directory to write
    the modified dev_requirements to, and an optional additional_filter_fn that can be used to further filter the dev_requirements file if necessary.

    The function will filter out any requirements present in the dev_requirements file that are present in the released_packages list (aka are required
    by the package).
    """
    # This method returns list of requirements from dev_requirements by filtering out packages in given list
    dev_req_path = os.path.join(os.path.dirname(setup_py_path), DEV_REQ_FILE)
    requirements = []
    with open(dev_req_path, "r") as dev_req_file:
        requirements = dev_req_file.readlines()

    # filter out any package available on PyPI (released_packages)
    # include packages without relative reference and packages not available on PyPI
    released_packages = [parse_require(p) for p in released_packages]
    released_package_names = [p.key for p in released_packages]
    # find prebuilt whl paths in dev requiremente
    prebuilt_dev_reqs = [os.path.basename(req.replace("\n", "")) for req in requirements if os.path.sep in req]
    # filter any req if wheel is for a released package
    req_to_exclude = [req for req in prebuilt_dev_reqs if req.split("-")[0].replace("_", "-") in released_package_names]
    req_to_exclude.extend(released_package_names)

    filtered_req = [
        req
        for req in requirements
        if os.path.basename(req.replace("\n", "")) not in req_to_exclude
        and not any([check_req_against_exclusion(req, i) for i in req_to_exclude])
    ]

    if additional_filter_fn:
        # this filter function handles the case where a dev requirement is incompatible with the current set of targeted packages
        filtered_req = additional_filter_fn(setup_py_path, filtered_req, released_packages)

    logging.info("Filtered dev requirements: %s", filtered_req)

    new_dev_req_path = ""
    if filtered_req:
        # create new dev requirements file with different name for filtered requirements
        new_dev_req_path = os.path.join(temp_dir, NEW_DEV_REQ_FILE)
        with open(new_dev_req_path, "w") as dev_req_file:
            dev_req_file.writelines(line if line.endswith("\n") else line + "\n" for line in filtered_req)

    return new_dev_req_path


def install_packages(packages, req_file):
    # install list of given packages from PyPI
    commands = [
        sys.executable,
        "-m",
        "pip",
        "install",
    ]

    if packages:
        commands.extend(packages)

    if req_file:
        commands.extend(["-r", req_file])

    logging.info("Installing packages. Command: %s", commands)
    check_call(commands)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Install either latest or minimum version of dependent packages.")

    parser.add_argument(
        "-t",
        "--target",
        dest="target_package",
        help="The target package directory on disk.",
        required=True,
    )

    parser.add_argument(
        "-d",
        "--dependency-type",
        dest="dependency_type",
        choices=["Latest", "Minimum"],
        help="Dependency type to install. Dependency type is either 'Latest' or 'Minimum'",
        required=True,
    )

    parser.add_argument(
        "-w",
        "--work-dir",
        dest="work_dir",
        help="Temporary working directory to create new dev requirements file",
        required=True,
    )

    args = parser.parse_args()
    setup_path = os.path.join(os.path.abspath(args.target_package), "setup.py")

    if not (os.path.exists(setup_path) and os.path.exists(args.work_dir)):
        logging.error("Invalid arguments. Please make sure target directory and working directory are valid path")
        sys.exit(1)

    install_dependent_packages(setup_path, args.dependency_type, args.work_dir)
