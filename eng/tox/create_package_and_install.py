#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# This script is used to create and install the appropriate package for a tox environment.
# it should be executed from tox with `{toxenvdir}/python` to ensure that the package
# can be successfully tested from within a tox environment.

import argparse
import logging

logging.getLogger().setLevel(logging.INFO)

from ci_tools.scenario.generation import create_package_and_install

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Build a package directory into wheel or sdist. Then install it. To install dev dependencies, set environment variable "SETDEVVERSION" to "true" and set "PIP_INDEX_URL" to a python feed.'
    )
    parser.add_argument(
        "-d",
        "--distribution-directory",
        dest="distribution_directory",
        help="The path to the distribution directory. This is the temporary location where packages will be built. Most commonly tox {envtmpdir}.",
        required=True,
    )

    parser.add_argument(
        "-p",
        "--path-to-setup",
        dest="target_setup",
        help="The path to the setup.py (not including the file) for the package we want to package into a wheel/sdist and install.",
        required=True,
    )

    parser.add_argument(
        "-s",
        "--skip-install",
        dest="skip_install",
        help="Create whl in distribution directory and skip installing it",
        default=False,
    )

    parser.add_argument(
        "--cache-dir",
        dest="cache_dir",
        help="Location that, if present, will be used as the pip cache directory.",
        default=None
    )

    parser.add_argument(
        "-w",
        "--work-dir",
        dest="work_dir",
        help="Location that, if present, will be used as working directory to run pip install.",
        default=None
    )

    parser.add_argument(
        "--force-create",
        dest="force_create",
        help="Force recreate whl even if it is prebuilt",
        default=False
    )

    parser.add_argument(
        "--package-type",
        dest="package_type",
        help="Package type to build",
        default="wheel",
    )

    parser.add_argument(
        "--pre-download-disabled",
        dest="pre_download_disabled",
        help="During a dev build, we will restore package dependencies from a dev feed before installing them. The presence of this flag disables that behavior.",
        action="store_true",
    )

    args = parser.parse_args()

    create_package_and_install(
        distribution_directory=args.distribution_directory,
        target_setup=args.target_setup,
        skip_install=args.skip_install,
        cache_dir=args.cache_dir,
        work_dir=args.work_dir,
        force_create=args.force_create,
        package_type=args.package_type,
        pre_download_disabled=args.pre_download_disabled,
    )


    
