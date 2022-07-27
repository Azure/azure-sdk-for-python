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
from prep_sphinx_env import should_build_docs
import sys
import shutil

from ci_tools.parsing import ParsedSetup

logging.getLogger().setLevel(logging.INFO)

root_dir = os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "..", ".."))
generate_mgmt_script = os.path.join(root_dir, "doc/sphinx/generate_doc.py")

def is_mgmt_package(package_dir):
    return "mgmt"  in pkg_name or "cognitiveservices" in pkg_name

def copy_existing_docs(source, target):
    for file in os.listdir(source):
        logging.info("Copying {}".format(file))
        shutil.copy(os.path.join(source, file), target)

def sphinx_apidoc(working_directory):
    working_doc_folder = os.path.join(args.working_directory, "unzipped", "doc")
    command_array = [
            "sphinx-apidoc",
            "--no-toc",
            "--module-first",
            "-o",
            os.path.join(args.working_directory, "unzipped/docgen"),
            os.path.join(args.working_directory, "unzipped/"),
            os.path.join(args.working_directory, "unzipped/test*"),
            os.path.join(args.working_directory, "unzipped/example*"),
            os.path.join(args.working_directory, "unzipped/sample*"),
            os.path.join(args.working_directory, "unzipped/setup.py"),
        ]

    try:
        # if a `doc` folder exists, just leverage the sphinx sources found therein.
        if os.path.exists(working_doc_folder): 
            logging.info("Copying files into sphinx source folder.")
            copy_existing_docs(working_doc_folder, os.path.join(args.working_directory, "unzipped/docgen"))

        # otherwise, we will run sphinx-apidoc to generate the sources
        else: 
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

def mgmt_apidoc(working_directory, namespace):
    command_array = [
        sys.executable,
        generate_mgmt_script,
        "-p",
        namespace,
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

    pkg_details = ParsedSetup.from_path(package_dir)

    if should_build_docs(pkg_details.name):
        if is_mgmt_package(pkg_details.name):
            mgmt_apidoc(output_directory, pkg_details.namespace)
        else:
            sphinx_apidoc(args.working_directory)
    else:
        logging.info("Skipping sphinx source generation for {}".format(pkg_details.name))