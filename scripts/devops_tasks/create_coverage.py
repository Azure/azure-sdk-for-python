#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# This script is the primary entry point for the azure-sdk-for-python Devops CI commands
# Primarily, it figures out which packages need to be built by combining the targeting string with the servicedir argument.
# After this, it either executes a global install of all packages followed by a test, or a tox invocation per package collected.


import argparse
import sys
import os
import errno
import shutil
import glob
import logging
import pdb
import re
from common_tasks import (
    process_glob_string,
    run_check_call,
    cleanup_folder,
    clean_coverage,
    is_error_code_5_allowed,
    create_code_coverage_params,
)
from tox_harness import prep_and_run_tox

logging.getLogger().setLevel(logging.INFO)

root_dir = os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "..", ".."))
coverage_dir = os.path.join(root_dir, "_all_coverage_files/")
dev_setup_script_location = os.path.join(root_dir, "scripts/dev_setup.py")


def collect_tox_coverage_files():#targeted_packages):
    logging.info("Running collect tox coverage files...")
    root_coverage_dir = os.path.join(root_dir, "_coverage/")

    coverage_files = []
    for root, _, files in os.walk(coverage_dir):
        for f in files:
            if re.match(".coverage_*", f):
                coverage_files.append(os.path.join(root, f))

    logging.info(".coverage files: {}".format(coverage_files))

    if len(coverage_files):
        cov_cmd_array = [sys.executable, "-m", "coverage", "combine", "--append"]
        cov_cmd_array.extend(coverage_files)

        # merge them with coverage combine and copy to root
        run_check_call(cov_cmd_array, coverage_dir)

        logging.info("after running coverage combine: ")

        generate_coverage_xml()

    # clean_coverage(coverage_dir)

    # # coverage report has paths starting .tox and azure
    # # coverage combine fixes this with the help of tox.ini[coverage:paths]
    # # combine_coverage_files(targeted_packages) # Skipping this, upload all .coverage-{package-name} files

    # coverage_files = []
    # # generate coverage files
    # for package_dir in [package for package in targeted_packages]:
    #     coverage_file = os.path.join(package_dir, ".coverage")
    #     if os.path.isfile(coverage_file):
    #         destination_file = os.path.join(
    #             root_coverage_dir, ".coverage_{}".format(os.path.basename(package_dir))
    #         )
    #         shutil.copyfile(coverage_file, destination_file)
    #         coverage_files.append(destination_file)

    # logging.info("Visible uncombined .coverage files: {}".format(coverage_files))

    # if len(coverage_files):
    #     cov_cmd_array = [sys.executable, "-m", "coverage", "combine", "--append"]
    #     cov_cmd_array.extend(coverage_files)

    #     # merge them with coverage combine and copy to root
    #     # run_check_call(cov_cmd_array, os.path.join(root_dir, "_coverage/")) # Don't run a coverage combine

    #     # Don't move to root and generate XML, this will be done at a later step.
    #     # source = os.path.join(coverage_dir, "./.coverage")
    #     # dest = os.path.join(root_dir, ".coverage")

    #     # shutil.move(source, dest)
    #     # # Generate coverage XML
    #     generate_coverage_xml()


def generate_coverage_xml():
    # coverage_path = os.path.join(root_dir, ".coverage")
    if os.path.exists(coverage_dir):
        logging.info("Generating coverage XML")
        commands = ["coverage", "xml", "-i", "--omit", '"*test*,*example*"']
        run_check_call(commands, root_dir, always_exit = False)
    else:
        logging.error("Coverage file is not available in {} to generate coverage XML".format(coverage_dir))


def combine_coverage_files(coverage_files):
    # find tox.ini file. tox.ini is used to combine coverage paths to generate formatted report
    tox_ini_file = os.path.join(root_dir, "eng", "tox", "tox.ini")
    config_file_flag = "--rcfile={}".format(tox_ini_file)

    if os.path.isfile(tox_ini_file):
        # for every individual coverage file, run coverage combine to combine path
        for coverage_file in coverage_files:
            cov_cmd_array = [sys.executable, "-m", "coverage", "combine", "--append"]
            # tox.ini file has coverage paths to combine
            # Pas tox.ini as coverage config file
            cov_cmd_array.extend([config_file_flag, coverage_file])
            run_check_call(cov_cmd_array, root_dir)
    else:
        # not a hard error at this point
        # this combine step is required only for modules if report has package name starts with .tox
        logging.error("tox.ini is not found in path {}".format(root_dir))



if __name__ == "__main__":
    collect_tox_coverage_files()