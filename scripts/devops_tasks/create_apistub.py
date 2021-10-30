#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import argparse
import sys
import os

from common_tasks import process_glob_string, run_check_call


def build_stub(targeted_packages, dest_directory):
    # run the apistubgen for each package
    for package_root in targeted_packages:
        service_hierarchy = os.path.join(os.path.basename(package_root))
        print("Generating Package API stub file Using apistubgen")
        run_check_call(
            [
                "apistubgen",
                "--pkg-path",
                package_root,
                "--out-path",
                os.path.join(dest_directory, service_hierarchy),
                "--hide-report"
            ],
            root_dir,
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Build API stub file for APIView, Called from DevOps YAML Pipeline"
    )
    parser.add_argument(
        "-d",
        "--dest-dir",
        dest="dest_dir",
        help="The path to the destination directory. Should be passed $(Build.ArtifactStagingDirectory) from the devops yaml definition.",
        required=True,
    )

    parser.add_argument(
        "glob_string",
        nargs="?",
        help=(
            "A comma separated list of glob strings that will target the top level directories that contain packages. "
            'Examples: All == "azure-*", Single = "azure-keyvault"'
        ),
    )

    parser.add_argument(
        "--service",
        help=(
            "Name of service directory (under sdk/)."
            "Example: --service applicationinsights"
        ),
    )

    parser.add_argument(
        "--pkgfilter",
        default="",
        dest="package_filter_string",
        help=(
            "An additional string used to filter the set of artifacts by a simple CONTAINS clause. This filters packages AFTER the set is built with compatibility and omission lists accounted."
        ),
    )

    args = parser.parse_args()

    # We need to support both CI builds of everything and individual service
    # folders. This logic allows us to do both.
    if args.service:
        service_dir = os.path.join("sdk", args.service)
        target_dir = os.path.join(root_dir, service_dir)
    else:
        target_dir = root_dir

    targeted_packages = process_glob_string(
        args.glob_string, target_dir, args.package_filter_string
    )
    build_packages(
        targeted_packages, args.dest_dir
    )
