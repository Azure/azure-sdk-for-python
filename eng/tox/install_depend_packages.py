#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import argparse
import logging
import os
import sys

from ci_tools.scenario.dependency_resolution import install_dependent_packages

logging.getLogger().setLevel(logging.INFO)


def main() -> None:
    parser = argparse.ArgumentParser(description="Install either latest or minimum version of dependent packages.")

    parser.add_argument(
        "-t",
        "--target",
        dest="target_package",
        help="The target package directory on disk.",
        required=True,
    )

    parser.add_argument(
        "-d",
        "--dependency-type",
        dest="dependency_type",
        choices=["Latest", "Minimum"],
        help="Dependency type to install. Dependency type is either 'Latest' or 'Minimum'",
        required=True,
    )

    parser.add_argument(
        "-w",
        "--work-dir",
        dest="work_dir",
        help="Temporary working directory to create new dev requirements file",
        required=True,
    )

    args = parser.parse_args()

    setup_path = os.path.abspath(args.target_package)

    if not (os.path.exists(setup_path) and os.path.exists(args.work_dir)):
        logging.error("Invalid arguments. Please make sure target directory and working directory are valid path")
        sys.exit(1)

    install_dependent_packages(setup_path, args.dependency_type, args.work_dir, python_executable=sys.executable)


if __name__ == "__main__":
    main()
