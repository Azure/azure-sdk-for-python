#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# Normally, this module will be executed as referenced as part of the devops build definitions.
# An enterprising user can easily glance over this and leverage for their own purposes.


import argparse
import sys
from pathlib import Path
import os
import errno
import glob
import shutil
import logging
from common_tasks import process_glob_string, run_check_call, cleanup_folder

logging.getLogger().setLevel(logging.INFO)

root_dir = os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "..", ".."))
coverage_dir = os.path.join(root_dir, "_coverage/")
dev_setup_script_location = os.path.join(root_dir, "scripts/dev_setup.py")

DEFAULT_TOX_INI_LOCATION = os.path.join(root_dir, "eng/tox/tox.ini")

MANAGEMENT_PACKAGE_IDENTIFIERS = [
    "mgmt",
    "azure-cognitiveservices",
    "azure-servicefabric",
    "azure-nspkg",
]


def clean_coverage():
    try:
        os.mkdir(coverage_dir)
    except OSError as e:
        if e.errno == errno.EEXIST:
            logging.info("Coverage dir already exists. Cleaning.")
            cleanup_folder(coverage_dir)
        else:
            raise
        

def prep_tests(targeted_packages, python_version):
    logging.info("running test setup for {}".format(targeted_packages))
    run_check_call(
        [
            python_version,
            dev_setup_script_location,
            "-p",
            ",".join([os.path.basename(p) for p in targeted_packages]),
        ],
        root_dir,
    )


def run_tests(targeted_packages, python_version, test_output_location, test_res):
    err_results = []

    clean_coverage()

    # base command array without a targeted package
    command_array = [python_version, "-m", "pytest"]
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

        # if we are targeting only packages that are management plane, it is a possibility
        # that no tests running is an acceptable situation
        # we explicitly handle this here.
        if all(
            map(
                lambda x: any(
                    [pkg_id in x for pkg_id in MANAGEMENT_PACKAGE_IDENTIFIERS]
                ),
                [target_package],
            )
        ):
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
            command_array + target_package_options,
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

    collect_pytest_coverage_files(targeted_packages)

    # if any of the packages failed, we should get exit with errors
    if err_results:
        exit(1)


def prep_and_run_tox(targeted_packages, tox_env, options_array=[]):
    for package_dir in [package for package in targeted_packages]:
        destination_tox_ini = os.path.join(package_dir, "tox.ini")
        allowed_return_codes = []
        tox_execution_array = ["tox"]

        # if we are targeting only packages that are management plane, it is a possibility
        # that no tests running is an acceptable situation
        # we explicitly handle this here.
        if all(
            map(
                lambda x: any(
                    [pkg_id in x for pkg_id in MANAGEMENT_PACKAGE_IDENTIFIERS]
                ),
                [package_dir],
            )
        ):
            options_array.append("--suppress-no-test-exit-code")

        # # if not present, copy it
        if not os.path.exists(destination_tox_ini):
            logging.info("No customized tox.ini present, using common eng/tox/tox.ini.")
            tox_execution_array.extend(["-c", DEFAULT_TOX_INI_LOCATION])

        if tox_env:
            tox_execution_array.extend(["-e", tox_env])

        if options_array:
            tox_execution_array.extend(["--"] + options_array)

        run_check_call(tox_execution_array, package_dir)

    if not tox_env:
        collect_tox_coverage_files(targeted_packages)


# TODO, dedup this function with collect_tox
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


# TODO, dedup this function with collect_pytest
def collect_tox_coverage_files(targeted_packages):
    root_coverage_dir = os.path.join(root_dir, "_coverage/")

    clean_coverage()

    coverage_files = []
    # generate coverage files
    for package_dir in [package for package in targeted_packages]:
        coverage_file = os.path.join(package_dir, ".coverage")
        if os.path.isfile(coverage_file):
            destination_file = os.path.join(
                root_coverage_dir, ".coverage_{}".format(os.path.basename(package_dir))
            )
            shutil.copyfile(coverage_file, destination_file)
            coverage_files.append(destination_file)

    logging.info("Visible uncombined .coverage files: {}".format(coverage_files))

    if len(coverage_files):
        cov_cmd_array = ["coverage", "combine"]
        cov_cmd_array.extend(coverage_files)

        # merge them with coverage combine and copy to root
        run_check_call(cov_cmd_array, os.path.join(root_dir, "_coverage/"))

        source = os.path.join(coverage_dir, "./.coverage")
        dest = os.path.join(root_dir, ".coverage")

        shutil.move(source, dest)


def execute_global_install_and_test(parsed_args, targeted_packages, extended_pytest_args):
    if args.runtype == "setup" or args.runtype == "all":
        prep_tests(targeted_packages, args.python_version)

    if args.mark_arg:
        extended_pytest_args.extend(["-m", "\"{}\"".format(args.mark_arg)])

    if args.runtype == "execute" or args.runtype == "all":
        run_tests(
            targeted_packages,
            args.python_version,
            args.test_results,
            extended_pytest_args,
        )


def execute_tox_harness(parsed_args, targeted_packages, extended_pytest_args):
    if args.wheel_dir:
        os.environ["PREBUILT_WHEEL_DIR"] = args.wheel_dir

    if args.mark_arg:
        extended_pytest_args.extend(["-m", "'{}'".format(args.mark_arg)])

    prep_and_run_tox(targeted_packages, args.tox_env, extended_pytest_args)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Install Dependencies, Install Packages, Test Azure Packages, Called from DevOps YAML Pipeline"
    )
    parser.add_argument(
        "-p",
        "--python-version",
        dest="python_version",
        default="python",
        help='The name of the python that should run the build. This is for usage in special cases like the "Special_Python_Distro_Tests" Job in /.azure-pipelines/client.yml. Defaults to "python"',
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

    args = parser.parse_args()

    # We need to support both CI builds of everything and individual service
    # folders. This logic allows us to do both.
    if args.service:
        service_dir = os.path.join("sdk", args.service)
        target_dir = os.path.join(root_dir, service_dir)
    else:
        target_dir = root_dir

    targeted_packages = process_glob_string(args.glob_string, target_dir)
    extended_pytest_args = []

    # common argument handling
    if args.disablecov:
        extended_pytest_args.append("--no-cov")
    else:
        extended_pytest_args.extend(["--durations=10", "--cov", "--cov-report="])

    if args.runtype != "none":
        execute_tox_harness(args, targeted_packages, extended_pytest_args)
    else:
        execute_global_install_and_test(args, targeted_packages, extended_pytest_args)