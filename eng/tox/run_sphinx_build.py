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

def in_ci():
    return os.getenv('TF_BUILD', False)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run sphinx-build against target folder. Zips and moves resulting files to a root location as well."
    )

    parser.add_argument(
        "-w",
        "--workingdir",
        dest="working_directory",
        help="The unzipped package directory on disk. Usually {distdir}/unzipped/",
        required=True,
    )

    parser.add_argument(
        "-o",
        "--outputdir",
        dest="output_directory",
        help="",
        required=True,
    )

    args = parser.parse_args()

    output_dir = os.path.abspath(args.output_directory)
    target_dir = os.path.abspath(args.working_directory)


    # sphinx-build -b html {distdir}/unzipped/docgen {distdir}/site
    command_array = [
                "sphinx-build",
                "-b",
                "html",
                target_dir,
                output_dir
            ]

    try:
        logging.info("Sphinx build command: {}".format(command_array))

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
