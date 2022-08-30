#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# Below are common methods for the devops build steps. This is the common location that will be updated with
# package targeting during release.
import argparse
import re
from os import path
import sys

from ci_tools.versioning.version_shared import get_packages, get_version_py
from ci_tools.variables import discover_repo_root


def find_invalid_versions_main():
    parser = argparse.ArgumentParser(description="")
    parser.add_argument(
        "--always-succeed",
        action="store_true",
        help="return exit code 0 even if incorrect versions are detected",
    )
    parser.add_argument("--service", help="name of a service directory to target packages")
    parser.add_argument(
        dest="glob_string",
        nargs="?",
        help=(
            "A comma separated list of glob strings that will target the top level directories that contain packages."
            'Examples: All = "azure-*", Single = "azure-keyvault", Targeted Multiple = "azure-keyvault,azure-mgmt-resource"'
        ),
    )

    parser.add_argument(
        "--repo",
        default=None,
        dest="repo",
        help=(
            "Where is the start directory that we are building against? If not provided, the current working directory will be used. Please ensure you are within the azure-sdk-for-python repository."
        ),
    )

    args = parser.parse_args()
    root_dir = args.repo or discover_repo_root()

    always_succeed = args.always_succeed

    packages = get_packages(args, root_dir=root_dir)

    invalid_packages = []
    for package in packages:
        package_name = package.name
        try:
            try:
                version_py_path = get_version_py(package.setup_filename)
            except:
                invalid_packages.append((package_name, "Could not find _version.py file"))
                continue

            if not version_py_path:
                invalid_packages.append((package_name, "Could not find _version.py file"))
                continue

            with open(version_py_path, "r") as version_py_file:
                version_contents = version_py_file.read()

                version = re.search(
                    r'^VERSION\s*=\s*[\'"]([^\'"]*)[\'"]', version_contents, re.MULTILINE  # type: ignore
                ).group(1)

                if version != package.version:
                    invalid_packages.append(
                        (
                            package_name,
                            f"Version evaluation mismatch: setup.py: {package.version} _version.py: {version}",
                        )
                    )
                    continue

            version_py_folder, _ = path.split(version_py_path)
            package_dunder_init = path.join(version_py_folder, "__init__.py")

            with open(package_dunder_init, "r") as package_dunder_init_file:
                version = re.search(
                    r"^__version__\s*=\s*VERSION",
                    package_dunder_init_file.read(),
                    re.MULTILINE,
                )

                if not bool(version):
                    invalid_packages.append(
                        (
                            package_name,
                            "Could not find __version__ = VERSION in package __init__.py",
                        )
                    )
                    continue
        except:
            invalid_packages.append((package_name, "Unknown error {}".format(sys.exc_info())))

    if invalid_packages:
        print("=================\nInvalid Packages:\n=================")

        for invalid_package in invalid_packages:
            print(f"{invalid_package[0]}\t{invalid_package[1]}")

        if not always_succeed:
            exit(1)
    else:
        print("No invalid packages found")


if __name__ == "__main__":
    find_invalid_versions_main()
