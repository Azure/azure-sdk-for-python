#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# This script is used to execute mypy within a tox environment.

from subprocess import check_call, CalledProcessError
import argparse
import os
import logging
import sys

from ci_tools.environment_exclusions import (
    is_check_enabled, is_typing_ignored
)
from ci_tools.variables import in_ci

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
    if in_ci():
        if not is_check_enabled(args.target_package, "mypy", True) or is_typing_ignored(package_name):
            logging.info(
                f"Package {package_name} opts-out of mypy check. See https://aka.ms/python/typing-guide for information."
            )
            exit(0)

    commands = [
        sys.executable,
        "-m",
        "mypy",
        "--python-version",
        "3.10",
        "--show-error-codes",
        "--ignore-missing-imports",
    ]
    src_code = [*commands, os.path.join(args.target_package, "azure")]
    src_code_error = None
    sample_code_error = None
    try:
        logging.info(
            f"Running mypy commands on src code: {src_code}"
        )
        check_call(src_code)
    except CalledProcessError as src_err:
        src_code_error = src_err

    if in_ci() and not is_check_enabled(args.target_package, "type_check_samples", True):
        logging.info(
            f"Package {package_name} opts-out of mypy check on samples."
        )
    else:
        sample_code = [
            *commands,
            "--check-untyped-defs",
            "--follow-imports=silent",
            os.path.join(args.target_package, "samples")
        ]
        try:
            logging.info(
                f"Running mypy commands on sample code: {sample_code}"
            )
            check_call(sample_code)
        except CalledProcessError as sample_err:
            sample_code_error = sample_err

    print("See https://aka.ms/python/typing-guide for information.\n\n")
    if src_code_error and sample_code_error:
        raise Exception(
            [
                src_code_error,
                sample_code_error,
            ],
        )
    if src_code_error:
        raise src_code_error
    if sample_code_error:
        raise sample_code_error
