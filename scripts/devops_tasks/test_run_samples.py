#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


import argparse
import sys
import os
import logging
from fnmatch import fnmatch
from common_tasks import (
    run_check_call,
    process_glob_string,
)


logging.getLogger().setLevel(logging.INFO)

root_dir = os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "..", ".."))
dev_setup_script_location = os.path.join(root_dir, "scripts/dev_setup.py")


def prep_samples(targeted_packages):
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


def run_samples(targeted_packages_directories):
    logging.info("running samples for {}".format(targeted_packages))
    samples_errors = []

    for pkg_dir in targeted_packages_directories:

        sample_paths = []
        samples_dir_path = os.path.abspath(os.path.join(pkg_dir, "samples"))
        for path, subdirs, files in os.walk(samples_dir_path):
            for name in files:
                if fnmatch(name, "*.py"):
                    sample_paths.append(os.path.abspath(os.path.join(path, name)))

        if not sample_paths:
            logging.info(
                "No samples found in {}".format(targeted_packages_directories)
            )
            continue

        for sample in sample_paths:
            if sys.version_info < (3, 5) and sample.endswith("_async.py"):
                continue

            logging.info(
                "Testing {}".format(sample)
            )
            command_array = [sys.executable, sample]
            errors = run_check_call(command_array, root_dir, always_exit=False)

            if errors:
                samples_errors.append(sample)
                logging.info(
                    "ERROR: {}".format(sample)
                )
            else:
                logging.info(
                    "SUCCESS: {}.".format(sample)
                )

    if samples_errors:
        logging.error("Sample(s) that ran with errors: {}".format(samples_errors))
        exit(1)

    logging.info(
        "All samples ran successfully in {}".format(targeted_packages_directories)
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
        "--service",
        help=(
            "Name of service directory (under sdk/) to test."
            "Example: --service applicationinsights"
        ),
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

    targeted_packages = process_glob_string(args.glob_string, target_dir)

    if len(targeted_packages) == 0:
        exit(0)

    logging.info("User opted to run samples")

    prep_samples(targeted_packages)
    run_samples(targeted_packages)
