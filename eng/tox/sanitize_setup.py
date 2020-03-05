#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# This script can process and update setup.py for e.g. update required version to dev

import argparse
import sys
import os
import logging
import glob
from packaging.specifiers import SpecifierSet
from pkg_resources import Requirement
from pypi_tools.pypi import PyPIClient

root_dir = os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "..", ".."))
setup_parser_path = os.path.abspath(os.path.join(root_dir, "eng", "versioning"))

sys.path.append(setup_parser_path)
from setup_parser import get_install_requires, parse_setup


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
    versions = [str(v) for v in client.get_ordered_versions(package_name) if str(v) in spec]
    return versions


def get_version(pkg_name):
    # find version for the package from source. This logic should be revisited to find version from devops feed
    glob_path = os.path.join(root_dir, "sdk", "*", pkg_name, "setup.py")
    paths = glob.glob(glob_path)
    if paths:
        setup_py_path = paths[0]
        _, version, _ = parse_setup(setup_py_path)
        return version
    else:
        logging.error("setyp.py is not found for package {} to identify current version".format(pkg_name))
        exit(1)

def process_requires(setup_py_path):
    # This method process package requirement to verify if all required packages are available on PyPI
    # If any azure sdk package is not available on PyPI then requirement will be updated to refer dev version
    requires = [
        Requirement.parse(r)
        for r in get_install_requires(setup_py_path)
        if r.startswith("azure") and "-nspkg" not in r
    ]
    # Find package requirements that are not available on PyPI
    requirement_to_update = {}
    for req in requires:
        pkg_name = req.key
        spec = SpecifierSet(str(req).replace(pkg_name, ""))
        if not is_required_version_on_pypi(pkg_name, spec):
            old_req = str(req)
            version = get_version(pkg_name)
            new_req = old_req.replace(version, "{}.dev".format(version))
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
