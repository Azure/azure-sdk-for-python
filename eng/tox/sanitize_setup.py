#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# This script can process and update setup.py for e.g. update required version to dev

import argparse
import sys
import re
import os
import logging
import glob
from packaging.specifiers import SpecifierSet
from packaging.version import Version
from pkg_resources import Requirement

root_dir = os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "..", ".."))
setup_parser_path = os.path.abspath(os.path.join(root_dir, "eng", "versioning"))
pypi_tools_path = os.path.join(root_dir, "tools", "azure-sdk-tools", "pypi_tools")

sys.path += [setup_parser_path, pypi_tools_path]
from setup_parser import get_install_requires, parse_setup
from pypi import PyPIClient

DEV_BUILD_IDENTIFIER = "a"

def update_requires(setup_py_path, requires_dict):
    # This method changes package requirement by overriding the specifier
    contents = []
    with open(setup_py_path, "r") as setup_file:
        contents = setup_file.readlines()

    # find and replace all existing package requirement with new requirement
    for i in range(0, len(contents) - 1):
        keys = [k for k in requires_dict.keys() if k in contents[i]]
        for key in keys:
            contents[i] = contents[i].replace(key, requires_dict[key])

    with open(setup_py_path, "w") as setup_file:
        setup_file.writelines(contents)


def is_required_version_on_pypi(package_name, spec):
    client = PyPIClient()
    try:
        pypi_results = client.get_ordered_versions(package_name)
    except:
        pypi_results = []

    versions = [str(v) for v in pypi_results if str(v) in spec]
    return versions


def get_version(pkg_name):
    # find version for the package from source. This logic should be revisited to find version from devops feed
    glob_path = os.path.join(root_dir, "sdk", "*", pkg_name, "setup.py")
    paths = glob.glob(glob_path)
    if paths:
        setup_py_path = paths[0]
        _, version, _ = parse_setup(setup_py_path)
        # Remove dev build part if version for this package is already updated to dev build
        # When building package with dev build version, version for packages in same service is updated to dev build 
        # and other packages will not have dev build number
        # strip dev build number so we can check if package exists in PyPI and replace
        
        version_obj = Version(version)
        if version_obj.pre:
            if version_obj.pre[0] == DEV_BUILD_IDENTIFIER:
                version = version_obj.base_version

        return version
    else:
        logging.error("setup.py is not found for package {} to identify current version".format(pkg_name))
        exit(1)


def get_base_version(pkg_name):
    # find version for the package from source. This logic should be revisited to find version from devops feed
    glob_path = os.path.join(root_dir, "sdk", "*", pkg_name, "setup.py")
    paths = glob.glob(glob_path)
    if paths:
        setup_py_path = paths[0]
        _, version, _ = parse_setup(setup_py_path)
        version_obj = Version(version)
        return version_obj.base_version
    else:
        logging.error("setup.py is not found for package {} to identify current version".format(pkg_name))
        exit(1)


def process_requires(setup_py_path):
    # This method process package requirement to verify if all required packages are available on PyPI
    # If any azure sdk package is not available on PyPI then requirement will be updated to refer dev version
    requires = [
        Requirement.parse(r)
        for r in get_install_requires(setup_py_path)
        if r.startswith("azure")
    ]
    # Find package requirements that are not available on PyPI
    requirement_to_update = {}
    for req in requires:
        pkg_name = req.key
        spec = SpecifierSet(str(req).replace(pkg_name, ""))

        if not is_required_version_on_pypi(pkg_name, spec):
            old_req = str(req)
            version = get_version(pkg_name)
            base_version = get_base_version(pkg_name)
            logging.info("Updating version {0} in requirement {1} to dev build version".format(version, old_req))
            # to properly replace the version, we must replace the entire version, not a partial piece of it
            rx = r'{}(((a|b|rc)\d+)?(\.post\d+)?)?'.format(base_version)
            new_req = re.sub(rx, "{}{}".format(base_version, DEV_BUILD_IDENTIFIER), str(req), flags=re.IGNORECASE)
            logging.info("New requirement for package {0}: {1}".format(pkg_name, new_req))
            requirement_to_update[old_req] = new_req

    if not requirement_to_update:
        logging.info("All required packages are available on PyPI")
    else:
        logging.info("Packages not available on PyPI:{}".format(requirement_to_update))
        update_requires(setup_py_path, requirement_to_update)
        logging.info("Package requirement is updated in setup.py")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Verify and update package requirements in setup.py"
    )

    parser.add_argument(
        "-t", "--target", help="The target package directory on disk.", required=True,
    )

    args = parser.parse_args()
    # get target package name from target package path
    setup_py_path = os.path.abspath(os.path.join(args.target, "setup.py"))
    if not os.path.exists(setup_py_path):
        logging.error("setup.py is not found in {}".format(args.target))
        exit(1)
    else:
        process_requires(setup_py_path)
