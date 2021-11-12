#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import argparse
import sys
import os
import glob
import shutil

from common_tasks import process_glob_string, run_check_call
root_dir = os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "..", ".."))

def stage_apistubs(targeted_packages, dest_directory):
    # run the apistubgen for each package
    for package_root in targeted_packages:
        path_to_search = os.path.join(package_root, ".tox", "dist", "*python.json")
        globs = glob.glob(path_to_search)
        if globs:
            json_file_path = globs[0]
            target_path = os.path.join(dest_directory, os.path.basename(package_root))
            print("Copying Package API stub file from path {0} to {1}".format(json_file_path, target_path))
            shutil.copy(json_file_path, target_path)
        else:
            print("APIView stub file is not present at {}.".format(path_to_search))
        

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
    stage_apistubs(
        targeted_packages, args.dest_dir
    )
