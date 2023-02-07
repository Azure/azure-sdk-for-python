#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# This script creates wheels for dependencies of a package and installs them.

import subprocess
import argparse
import os
import logging
import sys
import fnmatch
import tempfile
from packaging.version import parse
from ci_tools.parsing import ParsedSetup
from ci_tools.build import create_package
from ci_tools.variables import in_ci
logging.getLogger().setLevel(logging.INFO)


def install_dev_reqs(file, pkg_root, temp_dir):
    """Copied/edited from scripts/tox_harness.py"""

    adjusted_req_lines = []

    with open(file, "r") as f:
        for line in f:
            args = [part.strip() for part in line.split() if part and not part.strip() == "-e"]
            amended_line = " ".join(args)

            if amended_line.endswith("]"):
                trim_amount = amended_line[::-1].index("[") + 1
                amended_line = amended_line[0: (len(amended_line) - trim_amount)]

            adjusted_req_lines.append(amended_line)

    adjusted_req_lines = list(map(lambda x: build_whl_for_req(x, pkg_root, temp_dir), adjusted_req_lines))
    install_deps_commands = [
        sys.executable,
        "-m",
        "pip",
        "install",
    ]
    print(f"Installing dev requirements from freshly built packages: {adjusted_req_lines}")
    install_deps_commands.extend(adjusted_req_lines)
    subprocess.check_call(install_deps_commands)


def find_whl(package_name, version, whl_directory):
    """Copied/edited from scripts/tox_harness.py"""

    if not os.path.exists(whl_directory):
        logging.error("Whl directory is incorrect")
        exit(1)

    parsed_version = parse(version)

    logging.info("Searching whl for package {0}-{1}".format(package_name, parsed_version.base_version))
    whl_name_format = "{0}-{1}*.whl".format(package_name.replace("-", "_"), parsed_version.base_version)
    whls = []
    for root, dirnames, filenames in os.walk(whl_directory):
        for filename in fnmatch.filter(filenames, whl_name_format):
            whls.append(os.path.join(root, filename))

    whls = [os.path.relpath(w, whl_directory) for w in whls]

    if not whls:
        logging.error(
            "whl is not found in whl directory {0} for package {1}-{2}".format(
                whl_directory, package_name, parsed_version.base_version
            )
        )
        exit(1)

    return whls[0]


def build_whl_for_req(req, package_path, temp_dir):
    """Copied/edited from scripts/tox_harness.py"""

    if ".." in req:
        req_pkg_path = os.path.abspath(os.path.join(package_path, req.replace("\n", "")))
        parsed = ParsedSetup.from_path(req_pkg_path)

        logging.info("Building wheel for package {}".format(parsed.name))
        create_package(req_pkg_path, temp_dir, enable_sdist=False)

        whl_path = os.path.join(temp_dir, find_whl(parsed.name, parsed.version, temp_dir))
        logging.info("Wheel for package {0} is {1}".format(parsed.name, whl_path))
        return whl_path
    else:
        return req


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Create dependencies and install. "
    )

    parser.add_argument(
        "-p",
        "--path-to-setup",
        dest="target_setup",
        help="The path to the setup.py (not including the file) for the package we want to package into a wheel/sdist and install.",
        required=True,
    )

    args = parser.parse_args()
    package_root = os.path.abspath(args.target_setup)
    if not in_ci():
        # when we run tox locally, we use editable installs for a package's dependencies.
        # Some static analyzers (pyright/verifytypes) don't resolve dependencies
        # like azure-core when it is installed via editable install.
        # Here we create whls for the package's dependencies locally, install, and clean up.
        with tempfile.TemporaryDirectory() as tmp_dir_name:
            dev_reqs = os.path.join(package_root, "dev_requirements.txt")
            install_dev_reqs(dev_reqs, package_root, tmp_dir_name)
