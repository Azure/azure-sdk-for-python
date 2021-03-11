#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# Normally, this module will be executed as referenced as part of the devops build definitions.
# An enterprising user can easily glance over this and leverage for their own purposes.

import argparse
import sys
import os

from common_tasks import process_glob_string, run_check_call, str_to_bool

root_dir = os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "..", ".."))
build_packing_script_location = os.path.join(root_dir, "build_package.py")

# Import method to update package requirement if it is dev build package
tox_path = os.path.abspath(os.path.join(root_dir, "eng", "tox"))
sys.path.append(tox_path)
from sanitize_setup import process_requires

def build_packages(targeted_packages, distribution_directory, is_dev_build=False):
    # run the build and distribution
    for package_root in targeted_packages:
        service_hierarchy = os.path.join(os.path.basename(package_root))
        if is_dev_build:
            verify_update_package_requirement(package_root)
        print("Generating Package Using Python {}".format(sys.version))
        run_check_call(
            [
                sys.executable,
                build_packing_script_location,
                "--dest",
                os.path.join(distribution_directory, service_hierarchy),
                package_root,
            ],
            root_dir,
        )


def verify_update_package_requirement(pkg_root):
    setup_py_path = os.path.abspath(os.path.join(pkg_root, "setup.py"))
    process_requires(setup_py_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Build Azure Packages, Called from DevOps YAML Pipeline"
    )
    parser.add_argument(
        "-d",
        "--distribution-directory",
        dest="distribution_directory",
        help="The path to the distribution directory. Should be passed $(Build.ArtifactStagingDirectory) from the devops yaml definition.",
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
            "Name of service directory (under sdk/) to build."
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

    parser.add_argument(
        "--devbuild",
        default=False,
        dest="is_dev_build",
        help=(
            "Set build type to dev build so package requirements will be updated if required package is not available on PyPI"
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
        targeted_packages, args.distribution_directory, str_to_bool(args.is_dev_build)
    )
