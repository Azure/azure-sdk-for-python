#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


import argparse
import sys
import os
import logging
from common_tasks import (
    run_check_call,
    process_glob_string,
)


logging.getLogger().setLevel(logging.INFO)

root_dir = os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "..", ".."))

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
        help=("Flag  that enables parallel tox invocation."),
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

    parser.add_argument(
        "--test-samples",
        dest="test_samples",
        default=False,
        help="Whether or not to execute library samples as tests."
    )


    args = parser.parse_args()

    if args.test_samples is False:
        logging.info("User opted to not run samples")
        exit(0)

    if args.service:
        service_dir = os.path.join("sdk", args.service)
        target_dir = os.path.join(root_dir, service_dir)
    else:
        target_dir = root_dir

    targeted_packages = process_glob_string(args.glob_string, target_dir, "", args.filter_type)

    if len(targeted_packages) == 0:
        exit(0)


    logging.info("User opted to run samples")
    logging.info("Root dir is {}".format(root_dir))
    logging.info("Glog string is {}".format(args.glob_string))
    logging.info("service dir is {}".format(service_dir))
    logging.info("target dir is {}".format(target_dir))
    logging.info("targeted packages are {}".format(targeted_packages))

    one_sample = os.path.abspath(os.path.join(target_dir, args.glob_string, "samples/sample_recognize_receipts_from_url.py"))

    logging.info(
        "Testing {}".format(one_sample)
    )
    samples_errors = []
    command_array = [sys.executable, one_sample]
    errors = run_check_call(command_array, root_dir, always_exit=False)
    if errors:
        samples_errors.append(errors)

    if samples_errors:
        logging.error(samples_errors)
        exit(1)

        logging.info(
            "All samples ran successfully"
        )
        exit(0)
