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
from pkg_resources import parse_version
from pypi_tools.pypi import PyPIClient

from ci_tools.parsing import ParsedSetup, parse_require

DEV_REQ_FILE = "dev_requirements.txt"
NEW_DEV_REQ_FILE = "new_dev_requirements.txt"
PKGS_TXT_FILE = "packages.txt"

logging.getLogger().setLevel(logging.INFO)

# both min and max overrides are *inclusive* of the version targeted
MINIMUM_VERSION_SUPPORTED_OVERRIDE = {
    "azure-common": "1.1.10",
    "msrest": "0.6.10",
    "typing-extensions": "3.6.5",
    "opentelemetry-api": "1.3.0",
    "opentelemetry-sdk": "1.3.0",
    "azure-core": "1.11.0",
    "requests": "2.19.0",
    "six": "1.12.0",
    "cryptography": "3.3.2"
}

MAXIMUM_VERSION_SUPPORTED_OVERRIDE = {"cryptography": "4.0.0"}


def install_dependent_packages(setup_py_file_path, dependency_type, temp_dir):
    # This method identifies latest/ minimal version of dependent packages and installs them from pyPI
    # dependency type must either be latest or minimum
    # Latest dependency will find latest released package that satisfies requires of given package name
    # Minimum type will find minimum version on PyPI that satisfies requires of given package name

    released_packages = find_released_packages(setup_py_file_path, dependency_type)
    logging.info("%s released packages: %s", dependency_type, released_packages)
    # filter released packages from dev_requirements and create a new file "new_dev_requirements.txt"
    dev_req_file_path = filter_dev_requirements(setup_py_file_path, released_packages, temp_dir)

    # install released dependent packages
    if released_packages or dev_req_file_path:
        install_packages(released_packages, dev_req_file_path)

    if released_packages:
        # create a file with list of packages and versions found based on minimum or latest check on PyPI
        # This file can be used to verify if we have correct version installed
        pkgs_file_path = os.path.join(temp_dir, PKGS_TXT_FILE)
        with open(pkgs_file_path, "w") as pkgs_file:
            for package in released_packages:
                pkgs_file.write(package + "\n")
        logging.info("Created file %s to track azure packages found on PyPI", pkgs_file_path)


def find_released_packages(setup_py_path, dependency_type):
    # this method returns list of required available package on PyPI in format <package-name>==<version>

    # parse setup.py and find install requires
    requires = [r for r in ParsedSetup.from_path(setup_py_path).requires if "-nspkg" not in r]

    # Get available version on PyPI for each required package
    avlble_packages = [x for x in map(lambda x: process_requirement(x, dependency_type), requires) if x]
    return avlble_packages


def process_requirement(req, dependency_type):
    # this method finds either latest or minimum version of a package that is available on PyPI

    # find package name and requirement specifier from requires
    pkg_name, spec = parse_require(req)

    # get available versions on PyPI
    client = PyPIClient()
    versions = [str(v) for v in client.get_ordered_versions(pkg_name, True)]
    logging.info("Versions available on PyPI for %s: %s", pkg_name, versions)

    if pkg_name in MINIMUM_VERSION_SUPPORTED_OVERRIDE:
        versions = [
            v for v in versions if parse_version(v) >= parse_version(MINIMUM_VERSION_SUPPORTED_OVERRIDE[pkg_name])
        ]

    if pkg_name in MAXIMUM_VERSION_SUPPORTED_OVERRIDE:
        versions = [
            v for v in versions if parse_version(v) <= parse_version(MAXIMUM_VERSION_SUPPORTED_OVERRIDE[pkg_name])
        ]

    # Search from lowest to latest in case of finding minimum dependency
    # Search from latest to lowest in case of finding latest required version
    # reverse the list to get latest version first
    if dependency_type == "Latest":
        versions.reverse()

    # return first version that matches specifier in <package-name>==<version> format
    for version in versions:
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

    :param req: An incoming "req" looks like a requirement that appears in a dev_requirements file. EG: [ "../../../tools/azure-devtools",
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


def filter_dev_requirements(setup_py_path, released_packages, temp_dir):
    # This method returns list of requirements from dev_requirements by filtering out packages in given list
    dev_req_path = os.path.join(os.path.dirname(setup_py_path), DEV_REQ_FILE)
    requirements = []
    with open(dev_req_path, "r") as dev_req_file:
        requirements = dev_req_file.readlines()

    # filter out any package available on PyPI (released_packages)
    # include packages without relative reference and packages not available on PyPI
    released_packages = [p.split("==")[0] for p in released_packages]
    # find prebuilt whl paths in dev requiremente
    prebuilt_dev_reqs = [os.path.basename(req.replace("\n", "")) for req in requirements if os.path.sep in req]
    # filter any req if wheel is for a released package
    req_to_exclude = [req for req in prebuilt_dev_reqs if req.split("-")[0].replace("_", "-") in released_packages]
    req_to_exclude.extend(released_packages)

    filtered_req = [
        req
        for req in requirements
        if os.path.basename(req.replace("\n", "")) not in req_to_exclude
        and not any([check_req_against_exclusion(req, i) for i in req_to_exclude])
    ]

    logging.info("Filtered dev requirements: %s", filtered_req)

    new_dev_req_path = ""
    if filtered_req:
        # create new dev requirements file with different name for filtered requirements
        new_dev_req_path = os.path.join(temp_dir, NEW_DEV_REQ_FILE)
        with open(new_dev_req_path, "w") as dev_req_file:
            dev_req_file.writelines(filtered_req)

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
