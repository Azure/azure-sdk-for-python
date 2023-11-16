#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import argparse
import os
import logging
import sys
import subprocess

logging.getLogger().setLevel(logging.INFO)
from ci_tools.functions import discover_targeted_packages
from ci_tools.environment_exclusions import is_check_enabled

root_dir = os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "..", ".."))
sdk_dir = os.path.join(root_dir, "sdk")


def run_black(glob_string, service_dir):
    results = []
    logging.info("Running black for {}".format(service_dir))

    discovered_packages = discover_targeted_packages(
        glob_string, os.path.join(root_dir, "sdk", service_dir)
    )

    for package in discovered_packages:
        package_name = os.path.basename(package)

        if is_check_enabled(package, "black", True):
            out = subprocess.Popen(
                [
                    "tox",
                    "-qqq",
                    "--conf",
                    os.path.join(root_dir, "eng", "tox", "tox.ini"),
                    "--root",
                    root_dir,
                    "run",
                    "-e",
                    "black",
                    "--",
                    os.path.join("sdk", service_dir, package_name),
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                cwd=root_dir,
            )

            stdout, stderr = out.communicate()

            if stderr:
                results.append((package_name, stderr))

            if out.returncode > 0:
                print(
                    f"black ran into an unexpected failure while analyzing the code for {package_name}"
                )
                if stdout:
                    print(stdout.decode("utf-8"))
                exit(out.returncode)

            if stdout and "reformatted" in stdout.decode("utf-8"):
                results.append((package_name, False))
            else:
                print(f"black succeeded against {package_name}")

    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run black to verify formatted code.")

    parser.add_argument(
        "glob_string",
        nargs="?",
        help=(
            "A comma separated list of glob strings that will target the top level directories that contain packages."
            'Examples: All = "azure*", Single = "azure-keyvault", Targeted Multiple = "azure-keyvault,azure-mgmt-resource"'
        ),
    )
    parser.add_argument(
        "--service_directory", help="Directory of the package being tested"
    )

    parser.add_argument("--validate", help=("Flag that enables formatting validation."))

    args = parser.parse_args()
    if args.validate != "False":
        results = run_black(args.glob_string, args.service_directory)

        if len(results) > 0:
            for result in results:
                error = "Code needs reformat." if result[1] == False else error
                logging.error(f"Black run for {result[0]} ran into an issue: {error}")

            raise ValueError(
                "Found difference between formatted code and current commit. Check https://aka.ms/azsdk/python/black for how to fix it."
            )
    else:
        print("Skipping formatting validation")
