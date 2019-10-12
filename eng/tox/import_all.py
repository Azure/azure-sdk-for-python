#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# This script is used to verify package dependency by importing all modules
import argparse
import logging
import os

logging.getLogger().setLevel(logging.INFO)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Import all modules in package"
    )

    parser.add_argument(
        "-t",
        "--target",
        dest="target_package",
        help="The target package directory on disk.",
        required=True,
    )

    args = parser.parse_args()

    #get target package name from target package path
    target_pkg = os.path.basename(os.path.abspath(args.target_package))
    package_name = target_pkg.replace('-','.')

    #import all modules from current package
    logging.info("Importing all modules from package [{0}] to verify dependency".format(package_name))
    import_script_all = 'from {0} import *'.format(package_name)
    exec(import_script_all)
    logging.info("Verified module dependency, no issues found")
