#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# This script is used to execute bandit within a tox environment. Depending on which package is being executed against,
# a failure may be suppressed.

from subprocess import check_call, CalledProcessError
import argparse
import os
import logging
import sys

from ci_tools.environment_exclusions import (
    is_check_enabled
)
from ci_tools.variables import in_ci

logging.getLogger().setLevel(logging.INFO)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run bandit against target folder.")

    parser.add_argument(
        "-t",
        "--target",
        dest="target_package",
        help="The target package directory on disk. The target module passed to bandit will be <target_package>/azure.",
        required=True,
    )

    args = parser.parse_args()
    package_name = os.path.basename(os.path.abspath(args.target_package))

    if in_ci():
        if not is_check_enabled(args.target_package, "bandit"):
            logging.error("Bandit is disabled.")
            exit(1)

    try:
        check_call(
            [
                sys.executable,
                "-m",
                "bandit",
                "-r",
                os.path.join(args.target_package, "azure"),
                "-ll",
            ]
        )
    except CalledProcessError as e:
        logging.error("{} exited with error {}".format(package_name, e.returncode))
        exit(1)
