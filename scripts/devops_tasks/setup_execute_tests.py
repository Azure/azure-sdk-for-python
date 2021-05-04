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
coverage_dir = os.path.join(root_dir, "_coverage/")
dev_setup_script_location = os.path.join(root_dir, "scripts/dev_setup.py")

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

def collect_pytest_coverage_files(targeted_packages):
    coverage_files = []
    # generate coverage files
    for package_dir in [package for package in targeted_packages]:
        coverage_file = os.path.join(
            coverage_dir, ".coverage_{}".format(os.path.basename(package_dir))
        )
        if os.path.isfile(coverage_file):
            coverage_files.append(coverage_file)

    logging.info("Visible uncombined .coverage files: {}".format(coverage_files))

    if len(coverage_files):
        cov_cmd_array = ["coverage", "combine"]
        cov_cmd_array.extend(coverage_files)

        # merge them with coverage combine and copy to root
        run_check_call(cov_cmd_array, coverage_dir)

        source = os.path.join(coverage_dir, "./.coverage")
        dest = os.path.join(root_dir, ".coverage")

        shutil.move(source, dest)


def prep_tests(targeted_packages):
    logging.info("running test setup for {}".format(targeted_packages))
    run_check_call(
        [
            sys.executable,
            dev_setup_script_location,
            "--disabledevelop",
            "-p",
            ",".join([os.path.basename(p) for p in targeted_packages])
        ],
        root_dir,
    )


def run_tests(targeted_packages, test_output_location, test_res, parsed_args):
    err_results = []

    clean_coverage(coverage_dir)

    # base command array without a targeted package
    command_array = [sys.executable, "-m", "pytest"]
    command_array.extend(test_res)

    # loop through the packages
    logging.info("Running pytest for {}".format(targeted_packages))

    for index, target_package in enumerate(targeted_packages):
        logging.info(
            "Running pytest for {}. {} of {}.".format(
                target_package, index, len(targeted_packages)
            )
        )

        package_name = os.path.basename(target_package)
        source_coverage_file = os.path.join(root_dir, ".coverage")
        target_coverage_file = os.path.join(
            coverage_dir, ".coverage_{}".format(package_name)
        )
        target_package_options = []
        allowed_return_codes = []

        local_command_array = command_array[:]

        # Get code coverage params for current package
        coverage_commands = create_code_coverage_params(parsed_args, package_name)
        # Create local copy of params to pass to execute
        local_command_array.extend(coverage_commands)

        # if we are targeting only packages that are management plane, it is a possibility
        # that no tests running is an acceptable situation
        # we explicitly handle this here.
        if is_error_code_5_allowed(target_package, package_name):
            allowed_return_codes.append(5)

        # format test result output location
        if test_output_location:
            target_package_options.extend(
                [
                    "--junitxml",
                    os.path.join(
                        "TestResults/{}/".format(package_name), test_output_location
                    ),
                ]
            )

        target_package_options.append(target_package)
        err_result = run_check_call(
            local_command_array + target_package_options,
            root_dir,
            allowed_return_codes,
            True,
            False,
        )
        if err_result:
            logging.error("Errors present in {}".format(package_name))
            err_results.append(err_result)

        if os.path.isfile(source_coverage_file):
            shutil.move(source_coverage_file, target_coverage_file)

    if not parsed_args.disablecov:
        collect_pytest_coverage_files(targeted_packages)

    # if any of the packages failed, we should get exit with errors
    if err_results:
        exit(1)


def execute_global_install_and_test(
    parsed_args, targeted_packages, extended_pytest_args
):
    if parsed_args.mark_arg:
        extended_pytest_args.extend(["-m", '"{}"'.format(parsed_args.mark_arg)])

    if parsed_args.runtype == "setup" or parsed_args.runtype == "all":
        prep_tests(targeted_packages)

    if parsed_args.runtype == "execute" or parsed_args.runtype == "all":
        run_tests(
            targeted_packages,
            parsed_args.test_results,
            extended_pytest_args,
            parsed_args,
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Install Dependencies, Install Packages, Test Azure Packages, Called from DevOps YAML Pipeline"
    )

    parser.add_argument(
        "glob_string",
        nargs="?",
        help=(
            "A comma separated list of glob strings that will target the top level directories that contain packages."
            'Examples: All = "azure-*", Single = "azure-keyvault", Targeted Multiple = "azure-keyvault,azure-mgmt-resource"'
        ),
    )

    parser.add_argument(
        "--junitxml",
        dest="test_results",
        help=(
            "The folder where the test results will be stored in xml format."
            'Example: --junitxml="junit/test-results.xml"'
        ),
    )

    parser.add_argument(
        "--mark_arg",
        dest="mark_arg",
        help=(
            'The complete argument for `pytest -m "<input>"`. This can be used to exclude or include specific pytest markers.'
            '--mark_arg="not cosmosEmulator"'
        ),
    )

    parser.add_argument(
        "--disablecov", help=("Flag that disables code coverage."), action="store_true"
    )

    parser.add_argument(
        "--tparallel",
        default=False,
        help=("Flag that enables parallel tox invocation."),
        action="store_true",
    )

    parser.add_argument(
        "--tenvparallel",
        default=False,
        help=("Run individual tox env for each package in parallel."),
        action="store_true",
    )

    parser.add_argument(
        "--service",
        help=(
            "Name of service directory (under sdk/) to test."
            "Example: --service applicationinsights"
        ),
    )

    parser.add_argument(
        "-r", "--runtype", choices=["setup", "execute", "all", "none"], default="none"
    )

    parser.add_argument(
        "-t",
        "--toxenv",
        dest="tox_env",
        help="Specific set of named environments to execute",
    )

    parser.add_argument(
        "-w",
        "--wheel_dir",
        dest="wheel_dir",
        help="Location for prebuilt artifacts (if any)",
    )

    parser.add_argument(
        "-x",
        "--xdist",
        default=False,
        help=("Flag that enables xdist (requires pip install)"),
        action="store_true"
    )

    parser.add_argument(
        "-i",
        "--injected-packages",
        dest="injected_packages",
        default="",
        help="Comma or space-separated list of packages that should be installed prior to dev_requirements. If local path, should be absolute.",
    )

    parser.add_argument(
        "--filter-type",
        dest="filter_type",
        default='Build',
        help="Filter type to identify eligible packages. for e.g. packages filtered in Build can pass filter type as Build,",
        choices=['Build', "Docs", "Regression", "Omit_management"]
    )


    args = parser.parse_args()

    # We need to support both CI builds of everything and individual service
    # folders. This logic allows us to do both.
    if args.service:
        service_dir = os.path.join("sdk", args.service)
        target_dir = os.path.join(root_dir, service_dir)
    else:
        target_dir = root_dir

    targeted_packages = process_glob_string(args.glob_string, target_dir, "", args.filter_type)
    extended_pytest_args = []

    if len(targeted_packages) == 0:
        exit(0)

    if args.xdist:
        extended_pytest_args.extend(["-n", "8", "--dist=loadscope"])

    if args.runtype != "none":
        execute_global_install_and_test(args, targeted_packages, extended_pytest_args)
    else:
        prep_and_run_tox(targeted_packages, args, extended_pytest_args)
