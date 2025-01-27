#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# This script is used to execute pylint within a tox environment. Depending on which package is being executed against,
# a failure may be suppressed.

import subprocess
import argparse
import os
import logging
import sys

from ci_tools.environment_exclusions import is_check_enabled
from ci_tools.parsing import ParsedSetup
from ci_tools.variables import in_ci

logging.getLogger().setLevel(logging.INFO)

root_dir = os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "..", ".."))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run black against target folder. Uses the black config in eng/black-pyproject.toml."
    )

    parser.add_argument(
        "-t",
        "--target",
        dest="target_package",
        help="The target package directory on disk.",
        required=True,
    )

    args = parser.parse_args()

    pkg_dir = os.path.abspath(args.target_package)
    pkg_details = ParsedSetup.from_path(pkg_dir)
    configFileLocation = os.path.join(root_dir, "eng/black-pyproject.toml")

    if in_ci():
        if not is_check_enabled(args.target_package, "black"):
            logging.info(
                f"Package {pkg_details.name} opts-out of black check."
            )
            exit(0)

    try:
        run_result = subprocess.run(
            [
                sys.executable,
                "-m",
                "black",
                f"--config={configFileLocation}",
                args.target_package,
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        if run_result.stderr and "reformatted" in run_result.stderr.decode("utf-8"):
            if in_ci():
                logging.info(f"The package {pkg_details.name} needs reformat. Run the `black` tox env locally to reformat.")
                exit(1)
            else:
                logging.info(f"The package {pkg_details.name} was reformatted.")

    except subprocess.CalledProcessError as e:
        logging.error(
            f"Unable to invoke black for {pkg_details.name}. Ran into exception {e}."
        )

