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

logging.getLogger().setLevel(logging.INFO)


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

    command_array = [
                "sphinx-apidoc",
                "--no-toc",
                "-o",
                os.path.join(args.working_directory, "unzipped/docgen"),
                os.path.join(args.working_directory, "unzipped/"),
                os.path.join(args.working_directory, "unzipped/test*"),
                os.path.join(args.working_directory, "unzipped/example*"),
                os.path.join(args.working_directory, "unzipped/sample*"),
                os.path.join(args.working_directory, "unzipped/setup.py"),
            ]

    try:
        logging.info("Sphinx api-doc command: {}".format(command_array))

        check_call(
            command_array
        )
    except CalledProcessError as e:
        logging.error(
            "sphinx-apidoc failed for path {} exited with error {}".format(
                args.working_directory, e.returncode
            )
        )
        exit(1)
