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

from ci_tools.environment_exclusions import is_check_enabled
from ci_tools.parsing import ParsedSetup
from ci_tools.variables import in_ci

logging.getLogger().setLevel(logging.INFO)

root_dir = os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "..", ".."))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run pylint against target folder. Add a local custom plugin to the path prior to execution. "
    )

    parser.add_argument(
        "-t",
        "--target",
        dest="target_package",
        help="The target package directory on disk. The target module passed to pylint will be <target_package>/azure.",
        required=True,
    )

    parser.add_argument(
        "--next",
        default=False,
        help="Next version of pylint is being tested.",
        required=False,      
    )

    args = parser.parse_args()

    pkg_dir = os.path.abspath(args.target_package)
    pkg_details = ParsedSetup.from_path(pkg_dir)
    rcFileLocation = os.path.join(root_dir, "eng/pylintrc") if args.next else os.path.join(root_dir, "pylintrc")

    top_level_module = pkg_details.namespace.split('.')[0]

    if in_ci():
        if not is_check_enabled(args.target_package, "pylint"):
            logging.info(
                f"Package {pkg_details.name} opts-out of pylint check."
            )
            exit(0)

    exit_code = 0

    # Run pylint on main package
    try:
        main_pylint_targets = [os.path.join(args.target_package, top_level_module)]
        
        check_call(
            [
                sys.executable,
                "-m",
                "pylint",
                "--rcfile={}".format(rcFileLocation),
                "--output-format=parseable",
            ] + main_pylint_targets
        )
    except CalledProcessError as e:
        logging.error(
            "{} main package exited with linting error {}. Please see this link for more information https://aka.ms/azsdk/python/pylint-guide".format(pkg_details.name, e.returncode)
        )
        exit_code = max(exit_code, e.returncode)
        
    # Run pylint on tests and samples with appropriate pylintrc if they exist and next pylint is being used
    if args.next:
        logging.info("Running with --next flag, checking for tests and samples directories")
        tests_dir = os.path.join(args.target_package, "tests")
        samples_dir = os.path.join(args.target_package, "samples")
        
        logging.info(f"Checking tests directory: {tests_dir}")
        logging.info(f"Tests directory exists: {os.path.exists(tests_dir)}")
        
        # Run tests with test_pylintrc
        if os.path.exists(tests_dir):
            try:
                test_rcfile = os.path.join(root_dir, "eng/test_pylintrc")
                logging.info(f"Running pylint on tests with config: {test_rcfile}")
                check_call(
                    [
                        sys.executable,
                        "-m",
                        "pylint",
                        "--rcfile={}".format(test_rcfile),
                        "--output-format=parseable",
                        tests_dir
                    ]
                )
            except CalledProcessError as e:
                logging.error(
                    "{} tests exited with linting error {}. Please see this link for more information https://aka.ms/azsdk/python/pylint-guide".format(pkg_details.name, e.returncode)
                )
                exit_code = max(exit_code, e.returncode)
            
        # Run samples with samples_pylintrc
        logging.info(f"Checking samples directory: {samples_dir}")
        logging.info(f"Samples directory exists: {os.path.exists(samples_dir)}")
        if os.path.exists(samples_dir):
            try:
                samples_rcfile = os.path.join(root_dir, "eng/samples_pylintrc")
                logging.info(f"Running pylint on samples with config: {samples_rcfile}")
                check_call(
                    [
                        sys.executable,
                        "-m",
                        "pylint",
                        "--rcfile={}".format(samples_rcfile),
                        "--output-format=parseable",
                        samples_dir
                    ]
                )
            except CalledProcessError as e:
                logging.error(
                    "{} samples exited with linting error {}. Please see this link for more information https://aka.ms/azsdk/python/pylint-guide".format(pkg_details.name, e.returncode)
                )
                exit_code = max(exit_code, e.returncode)
    else:
        logging.info("Not running with --next flag, skipping tests and samples")

    if exit_code > 0:
        if args.next and in_ci():
            from gh_tools.vnext_issue_creator import create_vnext_issue
            create_vnext_issue(pkg_dir, "pylint")
        exit(exit_code)

    if args.next and in_ci():
        from gh_tools.vnext_issue_creator import close_vnext_issue
        close_vnext_issue(pkg_details.name, "pylint")
