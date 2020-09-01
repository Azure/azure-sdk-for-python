#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.

from subprocess import check_call
import argparse
import os
import logging

from tox_helper_tasks import find_whl, get_package_details

logging.getLogger().setLevel(logging.INFO)

root_dir = os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "..", ".."))


def get_package_wheel_path(pkg_root):
    # parse setup.py to get package name and version
    pkg_name, _, version = get_package_details(os.path.join(pkg_root, "setup.py"))
    # Check if wheel is already built and available for current package
    prebuilt_dir = os.getenv("PREBUILT_WHEEL_DIR")
    if prebuilt_dir:
        prebuilt_package_path = find_whl(prebuilt_dir, pkg_name, version)
    else:
        return None


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run apistubgen against target folder. "
    )

    parser.add_argument(
        "-t",
        "--target",
        dest="target_package",
        help="The target package directory on disk.",
        required=True,
    )

    parser.add_argument(
        "-w",
        "--work_dir",
        dest="work_dir",
        help="Working directory to run apistubgen",
        required=True,
    )

    args = parser.parse_args()

    # Check if a wheel is already built for current package and install from wheel when available
    # If wheel is not available then install package from source
    pkg_path = get_package_wheel_path(args.target_package)
    if not pkg_path:
        pkg_path = args.target_package

    check_call(["apistubgen", "--pkg-path", pkg_path,], cwd=args.work_dir)
