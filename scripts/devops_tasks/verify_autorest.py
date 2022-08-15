#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import argparse
import os
import logging

from common_tasks import run_check_call

logging.getLogger().setLevel(logging.INFO)

root_dir = os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "..", ".."))
sdk_dir = os.path.join(root_dir, "sdk")

SWAGGER_FOLDER = "swagger"


def run_autorest(service_dir):
    logging.info("Running autorest for {}".format(service_dir))

    service_dir = os.path.join(sdk_dir, service_dir)

    swagger_folders = find_swagger_folders(service_dir)

    for working_dir in swagger_folders:
        os.chdir(working_dir)
        f = os.path.abspath(os.path.join(working_dir, "README.md"))
        if os.path.exists(f):
            reset_command = ["autorest", "--reset"]
            run_check_call(reset_command, root_dir)

            command = ["autorest", "--python", f, "--verbose"]
            logging.info("Command: {}\nLocation: {}\n".format(command, working_dir))
            run_check_call(command, working_dir)
    return swagger_folders


def find_swagger_folders(directory):
    logging.info("Searching for swagger files in: {}".format(directory))

    ret = []
    for root, subdirs, files in os.walk(directory):
        for d in subdirs:
            if d == SWAGGER_FOLDER:
                if os.path.exists(os.path.join(root, d, "README.md")):
                    ret.append(os.path.join(root, d))

    logging.info("Found swagger files at: {}".format(ret))
    return ret


def check_diff(folder):
    # We don't care about changes to txt files (dev_requirements change)
    run_check_call(["git", "status"], sdk_dir, always_exit=False)

    command = [
        "git",
        "checkout",
        "--",
        "**/*.txt",
    ]
    result = run_check_call(command, sdk_dir, always_exit=False)

    # Remove the whl dirs
    command = [
        "rm",
        "-r",
        "**/.tmp_whl_dir/"
    ]
    result = run_check_call(command, sdk_dir, always_exit=False)

    # Next we need to move the autorest and _tox_logs directories and then replace them

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
            "Found difference between re-generated code and current commit. Please re-generate with the latest autorest."
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run autorest to verify generated code."
    )
    parser.add_argument(
        "--service_directory", help="Directory of the package being tested"
    )

    args = parser.parse_args()
    folders = run_autorest(args.service_directory)

    if len(folders):
        for folder in folders:
            check_diff(folder)
