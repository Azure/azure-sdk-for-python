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

from common_tasks import process_glob_string, run_check_call

root_dir = os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "..", ".."))
dev_setup_script_location = os.path.join(root_dir, "scripts/dev_setup.py")

MANAGEMENT_PACKAGE_IDENTIFIERS = [
    "mgmt",
    "azure-cognitiveservices",
    "azure-servicefabric",
]


def prep_tests(targeted_packages, python_version):
    print("running test setup for {}".format(targeted_packages))
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
    # if we are targeting only packages that are management plane, it is a possibility
    # that no tests running is an acceptable situation
    # we explicitly handle this here.

    # base command array without a targeted package
    command_array = [python_version, "-m", "pytest"]
    command_array.extend(test_res)

    # loop through the packages
    print("Running pytest for {}".format(targeted_packages))

    for target_package in targeted_packages:
        target_package_options = []
        allowed_return_codes = []

        if all(
            map(
                lambda x: any(
                    [pkg_id in x for pkg_id in MANAGEMENT_PACKAGE_IDENTIFIERS]
                ),
                [target_package],
            )
        ):
            allowed_return_codes.append(5)

        if test_output_location:
            target_package_options.extend(
                [
                    "--junitxml",
                    os.path.join(
                        "results/{}/".format(os.path.basename(target_package)),
                        test_output_location,
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
            err_results.append(err_result)

    print(err_results)

    # if any of the packages failed, we should get exit with errors
    if err_results:
        print("nooo")
        exit(1)


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
        "-r", "--runtype", choices=["setup", "execute", "all"], default="all"
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
    test_results_arg = []

    if args.disablecov:
        test_results_arg.append("--no-cov")
    else:
        test_results_arg.extend(["--durations=10", "--cov-append", "--cov-report="])

    if args.mark_arg:
        test_results_arg.extend(["-m", '"{}"'.format(args.mark_arg)])

    print(targeted_packages)

    if args.runtype == "setup" or args.runtype == "all":
        prep_tests(targeted_packages, args.python_version)

    if args.runtype == "execute" or args.runtype == "all":
        run_tests(
            targeted_packages, args.python_version, args.test_results, test_results_arg
        )
