#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# This script is used to execute verifytypes within a tox environment. It additionally installs
# the package from main and compares its type completeness score with
# that of the current code. If type completeness worsens from the code in main, the check fails.

import typing
import pathlib
import subprocess
import json
import argparse
import os
import logging
import sys
import tempfile

from ci_tools.parsing import ParsedSetup
from ci_tools.environment_exclusions import is_check_enabled, is_typing_ignored
from ci_tools.variables import in_ci

logging.getLogger().setLevel(logging.INFO)
root_dir = os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "..", ".."))


def install_from_main(setup_path: str) -> None:
    path = pathlib.Path(setup_path)
    subdirectory = path.relative_to(root_dir)
    cwd = os.getcwd()
    with tempfile.TemporaryDirectory() as temp_dir_name:
        os.chdir(temp_dir_name)
        try:
            subprocess.check_call(['git', 'init'], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
            subprocess.check_call(
                ['git', 'clone', '--no-checkout', 'https://github.com/Azure/azure-sdk-for-python.git', '--depth', '1'],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.STDOUT
            )
            os.chdir("azure-sdk-for-python")
            subprocess.check_call(['git', 'sparse-checkout', 'init', '--cone'], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
            subprocess.check_call(['git', 'sparse-checkout', 'set', subdirectory], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
            subprocess.check_call(['git', 'checkout', 'main'], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)

            if not os.path.exists(os.path.join(os.getcwd(), subdirectory)):
                # code is not checked into main yet, nothing to compare
                exit(0)

            os.chdir(subdirectory)

            command = [
                sys.executable,
                "-m",
                "pip",
                "install",
                ".",
                "--force-reinstall"
            ]

            subprocess.check_call(command, stdout=subprocess.DEVNULL)
        finally:
            os.chdir(cwd)  # allow temp dir to be deleted



def get_type_complete_score(commands: typing.List[str], check_pytyped: bool = False) -> float:
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
    setup_path = os.path.abspath(args.target_package)
    pkg_details = ParsedSetup.from_path(setup_path)
    module = pkg_details.namespace

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

    # show output
    try:
        subprocess.check_call(commands[:-1])
    except subprocess.CalledProcessError:
        pass  # we don't fail on verifytypes, only if type completeness score worsens from main

    if in_ci():
        # get type completeness score from main
        logging.info(
            "Getting the type completeness score from the code in main..."
        )
        install_from_main(setup_path)
        score_from_main = get_type_complete_score(commands)

        score_from_main_rounded = round(score_from_main * 100, 1)
        score_from_current_rounded = round(score_from_current * 100, 1)
        print("\n-----Type completeness score comparison-----\n")
        print(f"Score in main: {score_from_main_rounded}%")
        # Give a 5% buffer for type completeness score to decrease
        if score_from_current_rounded < score_from_main_rounded - 5:
            print(
                f"\nERROR: The type completeness score of {package_name} has significantly decreased compared to the score in main. "
                f"See the above output for areas to improve. See https://aka.ms/python/typing-guide for information."
            )
            exit(1)
