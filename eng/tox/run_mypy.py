#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# This script is used to execute mypy within a tox environment.

from subprocess import check_call
import argparse
import os
import logging
import sys

from allowed_type_checking_failures import (
    is_ignored_package,
    MYPY_OPT_OUT,
    TYPE_CHECK_SAMPLES_OPT_OUT,
)

logging.getLogger().setLevel(logging.INFO)

root_dir = os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "..", ".."))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run mypy against target folder. ")

    parser.add_argument(
        "-t",
        "--target",
        dest="target_package",
        help="The target package directory on disk. The target module passed to run mypy will be <target_package>/azure.",
        required=True,
    )

    args = parser.parse_args()
    package_name = os.path.basename(os.path.abspath(args.target_package))
    if package_name in MYPY_OPT_OUT or is_ignored_package(package_name):
        logging.info(
            f"Package {package_name} opts-out of mypy check. See https://aka.ms/python/typing-guide for information."
        )
        exit(0)

    paths = [
        os.path.join(args.target_package, "azure"),
        os.path.join(args.target_package, "samples"),
    ]
    if package_name in TYPE_CHECK_SAMPLES_OPT_OUT:
        logging.info(
            f"Package {package_name} opts-out of mypy check on samples. See https://aka.ms/python/typing-guide for information."
        )
        paths = paths[:-1]

    commands = [
        sys.executable,
        "-m",
        "mypy",
        "--python-version",
        "3.10",
        "--show-error-codes",
        "--ignore-missing-imports",
    ]
    commands.extend(paths)
    check_call(commands)
    print("See https://aka.ms/python/typing-guide for information.")
