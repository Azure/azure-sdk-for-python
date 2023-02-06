#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# This script is used to execute verifytypes within a tox environment. It additionally installs
# the latest release of a package (if it exists) and compares its type completeness score with
# that of the current code. If type completeness worsens from the last release, the check fails.

import subprocess
import json
import argparse
import os
import logging
import sys
import fnmatch
import tempfile
from packaging.version import parse
from ci_tools.environment_exclusions import is_ignored_package, is_check_enabled
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


def install_latest_release(package_name):
    from pypi_tools.pypi import PyPIClient

    client = PyPIClient()

    try:
        latest_version = str(client.get_ordered_versions(package_name)[-1])
    except (IndexError, KeyError):
        logging.info(f"No released packages for {package_name} on PyPi yet.")
        latest_version = None

    if latest_version:
        packages = [f"{package_name}=={latest_version}"]
        commands = [
            sys.executable,
            "-m",
            "pip",
            "install",
        ]

        commands.extend(packages)
        subprocess.check_call(commands, stdout=subprocess.DEVNULL)
    return latest_version


def get_type_complete_score(commands, check_pytyped=False):
    try:
        response = subprocess.run(
            commands,
            check=True,
            capture_output=True,
        )
    except subprocess.CalledProcessError as e:
        if e.returncode != 1:
            logging.info(
                f"Running verifytypes failed: {e.stderr}. See https://aka.ms/python/typing-guide for information."
            )
            exit(1)

        report = json.loads(e.output)
        if check_pytyped:
            pytyped_present = report["typeCompleteness"].get("pyTypedPath", None)
            if not pytyped_present:
                print(
                    f"No py.typed file was found. See aka.ms/python/typing-guide for information."
                )
                exit(1)
        return report["typeCompleteness"]["completenessScore"]

    # library scores 100%
    report = json.loads(response.stdout)
    return report["typeCompleteness"]["completenessScore"]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run pyright verifytypes against target folder. "
    )

    parser.add_argument(
        "-t",
        "--target",
        dest="target_package",
        help="The target package directory on disk. The target module passed to run pyright will be <target_package>/azure.",
        required=True,
    )

    args = parser.parse_args()
    package_name = os.path.basename(os.path.abspath(args.target_package))
    module = package_name.replace("-", ".")
    package_root = os.path.abspath(args.target_package)

    if not is_check_enabled(args.target_package, "verifytypes") or is_ignored_package(package_name):
        logging.info(
            f"{package_name} opts-out of verifytypes check. See https://aka.ms/python/typing-guide for information."
        )
        exit(0)

    if not in_ci():
        # when we run tox locally, we use editable installs for a package's dependencies.
        # verifytypes doesn't work with editable installed dependencies. so here we
        # create whls for the package's dependencies locally, install, and clean up.
        with tempfile.TemporaryDirectory() as tmp_dir_name:
            dev_reqs = os.path.join(package_root, "dev_requirements.txt")
            install_dev_reqs(dev_reqs, args.target_package, tmp_dir_name)

    commands = [
        sys.executable,
        "-m",
        "pyright",
        "--verifytypes",
        module,
        "--ignoreexternal",
        "--outputjson",
    ]

    # get type completeness score from current code
    score_from_current = get_type_complete_score(commands, check_pytyped=True)
    try:
        subprocess.check_call(commands[:-1])
    except subprocess.CalledProcessError:
        pass  # we don't fail on verifytypes, only if type completeness score worsens from last release

    # get type completeness score from latest release
    latest_version = install_latest_release(package_name)
    if latest_version:
        score_from_released = get_type_complete_score(commands)
    else:
        score_from_released = None

    if score_from_released is not None:
        score_from_released_rounded = round(score_from_released * 100, 1)
        score_from_current_rounded = round(score_from_current * 100, 1)
        print("\n-----Type completeness score comparison-----\n")
        print(f"Previous release ({latest_version}): {score_from_released_rounded}%")
        if score_from_current_rounded < score_from_released_rounded:
            print(
                f"\nERROR: The type completeness score of {package_name} has decreased since the last release. "
                f"See the above output for areas to improve. See https://aka.ms/python/typing-guide for information."
            )
            exit(1)
