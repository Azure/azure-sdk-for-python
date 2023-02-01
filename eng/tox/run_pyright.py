#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# This script is used to execute pyright within a tox environment.

from subprocess import check_call, CalledProcessError
import argparse
import os
import logging
import sys

from ci_tools.environment_exclusions import (
    is_ignored_package,
    is_check_enabled,
)

logging.getLogger().setLevel(logging.INFO)

root_dir = os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "..", ".."))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run pyright against target folder. ")

    parser.add_argument(
        "-t",
        "--target",
        dest="target_package",
        help="The target package directory on disk. The target module passed to run pyright will be <target_package>/azure.",
        required=True,
    )

    args = parser.parse_args()
    package_name = os.path.basename(os.path.abspath(args.target_package))
    if not is_check_enabled(args.target_package, "pyright") or is_ignored_package(package_name):
        logging.info(
            f"Package {package_name} opts-out of pyright check. See https://aka.ms/python/typing-guide for information."
        )
        exit(0)

    paths = [
        os.path.join(args.target_package, "azure"),
        os.path.join(args.target_package, "samples"),
    ]
    if not is_check_enabled(args.target_package, "type_check_samples"):
        logging.info(
            f"Package {package_name} opts-out of pyright check on samples."
        )
        paths = paths[:-1]

    commands = [
        sys.executable,
        "-m",
        "pyright",
    ]
    commands.extend(paths)
    try:
        check_call(commands)
    except CalledProcessError as error:
        print("See https://aka.ms/python/typing-guide for information.\n\n")
        raise error
