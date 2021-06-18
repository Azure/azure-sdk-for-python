#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import argparse
import os
import logging
import sys

from common_tasks import run_check_call

logging.getLogger().setLevel(logging.INFO)

root_dir = os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "..", ".."))
sdk_dir = os.path.join(root_dir, "sdk")

SWAGGER_FOLDER = "swagger"


def run_black(service_dir):
    logging.info("Running black for {}".format(service_dir))

    command = [sys.executable, "-m", "black", "-l", "120", "sdk/{}".format(service_dir)]

    run_check_call(command, root_dir)


def check_diff(folder):
    # We don't care about changes to txt files (dev_requirements change)
    run_check_call(["git", "status"], sdk_dir, always_exit=False)

    dir_changed = folder.split("/")[:-2]
    command = [
        "git",
        "diff",
        "--exit-code",
        "{}".format("/".join(dir_changed)),
    ]
    result = run_check_call(command, sdk_dir, always_exit=False)
    if result:
        command = ["git", "status"]
        run_check_call(command, root_dir)
        raise ValueError(
            "Found difference between formatted code and current commit. Please re-generate with the latest autorest."
        )

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run black to verify formatted code."
    )
    parser.add_argument(
        "--service_directory", help="Directory of the package being tested"
    )

    parser.add_argument(
        "--validate", help=("Flag that enables formatting validation.")
    )

    args = parser.parse_args()

    if bool(args.validate):
        run_black(args.service_directory)
    else:
        print("Skipping formatting validation")