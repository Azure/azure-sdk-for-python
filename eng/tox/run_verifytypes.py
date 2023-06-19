#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# This script is used to execute verifytypes within a tox environment. It additionally installs
# the package from main and compares its type completeness score with
# that of the current code. If type completeness worsens from the code in main, the check fails.

import subprocess
import json
import argparse
import os
import logging
import sys

from ci_tools.environment_exclusions import is_check_enabled, is_typing_ignored
from ci_tools.variables import in_ci

logging.getLogger().setLevel(logging.INFO)


def install_from_main(subdirectory, package_name):
    main_url = f"git+https://github.com/Azure/azure-sdk-for-python@main#subdirectory={subdirectory}&egg={package_name}"

    commands = [
        sys.executable,
        "-m",
        "pip",
        "install",
        main_url,
        "--force-reinstall"
    ]

    subprocess.check_call(commands, stdout=subprocess.DEVNULL)



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
        pass  # we don't fail on verifytypes, only if type completeness score worsens from main

    # get type completeness score from main
    try:
        install_from_main(setup_path.split("azure-sdk-for-python")[1].lstrip("/\\"), package_name)
    except subprocess.CalledProcessError:
        exit(0)  # there is no code in main yet, nothing to compare

    score_from_main = get_type_complete_score(commands)

    score_from_main_rounded = round(score_from_main * 100, 1)
    score_from_current_rounded = round(score_from_current * 100, 1)
    print("\n-----Type completeness score comparison-----\n")
    print(f"Score in main: {score_from_main_rounded}%")
    if score_from_current_rounded < score_from_main_rounded:
        print(
            f"\nERROR: The type completeness score of {package_name} has decreased compared to main. "
            f"See the above output for areas to improve. See https://aka.ms/python/typing-guide for information."
        )
        exit(1)
