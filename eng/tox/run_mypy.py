#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# This script is used to execute mypy within a tox environment. Packages can opt in to fail CI job if mypy fails.

from subprocess import check_call, CalledProcessError
import argparse
import os
import logging
import sys

from mypy_hard_failure_packages import MYPY_HARD_FAILURE_OPTED

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

    try:
        check_call(
            [sys.executable, "-m", "mypy", os.path.join(args.target_package, "azure")]
        )
    except CalledProcessError as e:
        logging.error("{} exited with mypy error {}".format(package_name, e.returncode))

        # return failure if package has opted in mark mypy failure as hard error
        if package_name in MYPY_HARD_FAILURE_OPTED:
            logging.error(
                "Package {} has opted to fail CI when mypy fails".format(package_name)
            )
            exit(1)
