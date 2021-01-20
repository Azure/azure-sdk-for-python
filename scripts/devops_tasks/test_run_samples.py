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

IGNORED_SAMPLES = {
    "azure-eventgrid": [
        "__init__.py",
        "consume_cloud_events_from_eventhub.py",
        "consume_cloud_events_from_service_bus_queue.py",
        "consume_cloud_events_from_storage_queue.py"]
}


def run_samples(targeted_package):
    logging.info("running samples for {}".format(targeted_package))

    samples_errors = []
    sample_paths = []
    samples_dir_path = os.path.abspath(os.path.join(targeted_package, "samples"))
    package_name = os.path.basename(targeted_package)

    for path, subdirs, files in os.walk(samples_dir_path):
        for name in files:
            if fnmatch(name, "*.py") and name not in IGNORED_SAMPLES.get(package_name, []):
                sample_paths.append(os.path.abspath(os.path.join(path, name)))

    if not sample_paths:
        logging.info(
            "No samples found in {}".format(targeted_package)
        )
        exit(0)

    for sample in sample_paths:
        if sys.version_info < (3, 5) and sample.endswith("_async.py"):
            continue

        logging.info(
            "Testing {}".format(sample)
        )
        command_array = [sys.executable, sample]
        errors = run_check_call(command_array, root_dir, always_exit=False)

        sample_name = os.path.basename(sample)
        if errors:
            samples_errors.append(sample_name)
            logging.info(
                "ERROR: {}".format(sample_name)
            )
        else:
            logging.info(
                "SUCCESS: {}.".format(sample_name)
            )

    if samples_errors:
        logging.error("Sample(s) that ran with errors: {}".format(samples_errors))
        exit(1)

    logging.info(
        "All samples ran successfully in {}".format(targeted_package)
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Install Dependencies, Install Packages, Test Azure Packages' Samples, Called from DevOps YAML Pipeline"
    )

    parser.add_argument(
        "-t",
        "--target",
        dest="target_package",
        help="The target package directory on disk. The target module passed to run mypy will be <target_package>/azure.",
        required=True,
    )

    args = parser.parse_args()

    service_dir = os.path.join("sdk", args.target_package)
    target_dir = os.path.join(root_dir, service_dir)

    logging.info("User opted to run samples")

    run_samples(target_dir)
