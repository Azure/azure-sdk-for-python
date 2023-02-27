#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# This script creates wheels for dependencies of a package and installs them.

import argparse
import os
import logging
from ci_tools.variables import in_ci
from ci_tools.functions import build_and_install_dev_reqs
logging.getLogger().setLevel(logging.INFO)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Create dependencies and install. "
    )

    parser.add_argument(
        "-p",
        "--path-to-setup",
        dest="target_setup",
        help="The path to the setup.py (not including the file) for the package we want to package into a wheel/sdist and install.",
        required=True,
    )

    args = parser.parse_args()
    package_root = os.path.abspath(args.target_setup)
    dev_reqs = os.path.join(package_root, "dev_requirements.txt")
    if not in_ci():
        # when we run tox locally, we use editable installs for a package's dependencies.
        # Some static analyzers (pyright/verifytypes) don't resolve dependencies
        # like azure-core when it is installed via editable install.
        # Here we create whls for the package's dependencies locally, install, and clean up.
        build_and_install_dev_reqs(dev_reqs, package_root)
