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

from ci_tools.environment_exclusions import is_check_enabled, is_typing_ignored
from ci_tools.variables import in_ci

logging.getLogger().setLevel(logging.INFO)


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
    setup_path = os.path.abspath(args.target_package)

    if in_ci():
        if not is_check_enabled(args.target_package, "verifytypes") or is_typing_ignored(package_name):
            logging.info(
                f"{package_name} opts-out of verifytypes check. See https://aka.ms/python/typing-guide for information."
            )
            exit(0)

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
