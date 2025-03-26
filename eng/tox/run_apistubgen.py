#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.

from subprocess import check_call
import argparse
import os
import logging

from ci_tools.functions import find_whl
from ci_tools.parsing import ParsedSetup

logging.getLogger().setLevel(logging.INFO)

root_dir = os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "..", ".."))

def get_package_wheel_path(pkg_root, out_path):
    # parse setup.py to get package name and version
    pkg_details = ParsedSetup.from_path(pkg_root)

    # Check if wheel is already built and available for current package
    prebuilt_dir = os.getenv("PREBUILT_WHEEL_DIR")
    out_token_path = None
    if prebuilt_dir:
        pkg_path = os.path.join(prebuilt_dir, find_whl(prebuilt_dir, pkg_details.name, pkg_details.version))
        if not pkg_path:
            raise FileNotFoundError(
                "No prebuilt wheel found for package {} version {} in directory {}".format(
                    pkg_details.name, pkg_details.version, prebuilt_dir)
            )
        # If the package is a wheel and out_path is given, the token file output path should be the parent directory of the wheel
        if out_path:
            out_token_path = os.path.join(out_path, os.path.basename(os.path.dirname(pkg_path)))
        return pkg_path, out_token_path
    pkg_path = pkg_root
    # If the package is not a wheel and out_path is given, the token file output path should be the same as the target package path
    if out_path:
        out_token_path = os.path.join(out_path, os.path.basename(pkg_path))
    return  pkg_path, out_token_path

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
        "--work-dir",
        dest="work_dir",
        help="Working directory to run apistubgen",
        required=True,
    )

    parser.add_argument(
        "-o",
        "--out-path",
        dest="out_path",
        help="Output directory to generate json token file"
    )

    args = parser.parse_args()

    # Check if a wheel is already built for current package and install from wheel when available
    # If wheel is not available then install package from source
    pkg_path, out_token_path = get_package_wheel_path(args.target_package, args.out_path)

    cmds = ["apistubgen", "--pkg-path", pkg_path]
    if out_token_path:
        cmds.extend(["--out-path", out_token_path])

    logging.info("Running apistubgen {}.".format(cmds))
    check_call(cmds, cwd=args.work_dir)
