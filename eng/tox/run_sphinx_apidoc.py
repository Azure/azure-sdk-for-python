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


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run sphinx-apidoc against target folder. Handles management generation if necessary."
    )

    parser.add_argument(
        "-w",
        "--workingdir",
        dest="working_directory",
        help="The unzipped package directory on disk. Usually {distdir}/unzipped/",
        required=True,
    )

    args = parser.parse_args()

    dist_location = os.path.abspath(args.target_package)

    default_command_array = [
        sys.executable,
        "-m",
        "sphinx-apidoc",
        "--no-toc",
        "-o",
        os.path.join(output_directory, "unzipped/docgen"),
        os.path.join(output_directory, "unzipped/"),
        os.path.join(output_directory, "unzipped/test*"),
        os.path.join(output_directory, "unzipped/example*"),
        os.path.join(output_directory, "unzipped/sample*"),
        os.path.join(output_directory, "unzipped/setup.py"),
    ]

    try:
        check_call()
    except CalledProcessError as e:
        logging.error(
            "{} exited with linting error {}".format(package_name, e.returncode)
        )
        exit(1)
