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
from prep_sphinx_env import get_package_details, should_build_docs
import sys

logging.getLogger().setLevel(logging.INFO)

root_dir = os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "..", ".."))
generate_mgmt_script = os.path.join(root_dir, "doc/sphinx/generate_doc.py")

def is_mgmt_package(package_dir):
    return "mgmt"  in pkg_name or "cognitiveservices" in pkg_name

def sphinx_apidoc(working_directory):
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

def mgmt_apidoc(working_directory, package_name):
    command_array = [
        sys.executable,
        generate_mgmt_script,
        "-p",
        package_name.replace("-","."),
        "-o",
        working_directory,
        "--verbose"
        ]

    try:
        logging.info("Command to generate management sphinx sources: {}".format(command_array))

        check_call(
            command_array
        )
    except CalledProcessError as e:
        logging.error(
            "script failed for path {} exited with error {}".format(
                args.working_directory, e.returncode
            )
        )
        exit(1)

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

    parser.add_argument(
        "-r",
        "--root",
        dest="package_root",
        help="",
        required=True,
    )

    args = parser.parse_args()

    target_dir = os.path.abspath(args.working_directory)
    package_dir = os.path.abspath(args.package_root)
    output_directory = os.path.join(target_dir, "unzipped/docgen")

    pkg_name, pkg_version = get_package_details(os.path.join(package_dir, 'setup.py'))

    if should_build_docs(pkg_name):
        if is_mgmt_package(pkg_name):
            mgmt_apidoc(output_directory, pkg_name)
        else:
            sphinx_apidoc(args.working_directory)
    else:
        logging.info("Skipping sphinx source generation for {}".format(pkg_name))