#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# This script is used to execute pylint within a tox environment. Depending on which package is being executed against,
# a failure may be suppressed.

from subprocess import check_call, CalledProcessError
import argparse
import os
import logging
import sys

from allowed_pylint_failures import PYLINT_ACCEPTABLE_FAILURES

logging.getLogger().setLevel(logging.INFO)

root_dir = os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "..", ".."))
rcFileLocation = os.path.join(root_dir, "pylintrc")
lint_plugin_path = os.path.join(root_dir, "scripts/pylint_custom_plugin")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run pylint against target folder. Add a local custom plugin to the path prior to execution."
    )

    parser.add_argument(
        "-t",
        "--target",
        dest="target_package",
        help="The target module on disk.",
        required=True,
    )

    args = parser.parse_args()

    package_name = os.path.basename(args.target_package)

    try:
        if "mgmt" not in package_name:
            check_call(
                [
                    sys.executable,
                    "-m",
                    "pylint",
                    "--rcfile={}".format(rcFileLocation),
                    "--output-format=parseable",
                    os.path.join(args.target_package, "azure"),
                ]
            )
    except CalledProcessError as e:
        logging.error(
            "{} exited with linting error {}".format(package_name, e.returncode)
        )
        if package_name not in PYLINT_ACCEPTABLE_FAILURES:
            exit(1)
        else:
            logging.info(
                "Ignoring failure for pylint run against package {}".format(
                    package_name
                )
            )
