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

from type_checking_opt_out_packages import TYPE_CHECKING_OPT_OUT

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

    if package_name not in TYPE_CHECKING_OPT_OUT:
        logging.info("Package {} has opted to run mypy".format(package_name))
        check_call(
            [
                sys.executable,
                "-m",
                "mypy",
                "--python-version",
                "3.10",
                "--show-error-codes",
                "--ignore-missing-imports",
                os.path.join(args.target_package, "azure"),
                os.path.join(args.target_package, "samples")
            ]
        )
