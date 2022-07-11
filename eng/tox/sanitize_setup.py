a#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# This script can process and update setup.py for e.g. update required version to dev

import argparse
import os
import logging
from ci_tools.functions import process_requires


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Verify and update package requirements in setup.py"
    )

    parser.add_argument(
        "-t", "--target", help="The target package directory on disk.", required=True,
    )

    args = parser.parse_args()
    # get target package name from target package path
    setup_py_path = os.path.abspath(os.path.join(args.target, "setup.py"))
    if not os.path.exists(setup_py_path):
        logging.error("setup.py is not found in {}".format(args.target))
        exit(1)
    else:
        process_requires(setup_py_path)
