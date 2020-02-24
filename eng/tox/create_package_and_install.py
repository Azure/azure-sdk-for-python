#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# This script is used to create and install the appropriate package for a tox environment.
# it should be executed from tox with `{toxenvdir}/python` to ensure that the package
# can be successfully tested from within a tox environment.

from subprocess import check_call
import argparse
import os
import logging
import sys
import glob
import shutil

from tox_helper_tasks import find_whl, find_sdist, get_package_details
logging.getLogger().setLevel(logging.INFO)


def cleanup_build_artifacts(build_folder):
    # clean up egginfo
    results = glob.glob(os.path.join(build_folder, "*.egg-info"))

    if results:
        print(results[0])
        shutil.rmtree(results[0])

    # clean up build results
    build_path = os.path.join(build_folder, "build")
    if os.path.exists(build_path):
        shutil.rmtree(build_path)


def discover_packages(setuppy_path, args):
    packages = []
    if os.getenv("PREBUILT_WHEEL_DIR") is not None and not args.force_create:
        packages = discover_prebuilt_package(os.getenv("PREBUILT_WHEEL_DIR"), setuppy_path, args.package_type)
    else:
        packages = build_and_discover_package(setuppy_path, args.distribution_directory, args.target_setup, args.package_type)
    return packages


def discover_prebuilt_package(dist_directory, setuppy_path, package_type):
    packages = []
    pkg_name, _, version = get_package_details(setuppy_path)
    if package_type == "wheel":
        prebuilt_package = find_whl(dist_directory, pkg_name, version)
    else:
        prebuilt_package = find_sdist(dist_directory, pkg_name, version)

    if prebuilt_package is None:
        logging.error("Package is missing in prebuilt directory {0} for package {1} and version {2}".format(dist_directory, pkg_name, version))
        exit(1)
    packages.append(prebuilt_package)
    return packages


def in_ci():
    return os.getenv("TF_BUILD", False)


def build_and_discover_package(setuppy_path, dist_dir, target_setup, package_type):

    if package_type == "wheel":
        check_call(
            [
                sys.executable,
                setuppy_path,
                "bdist_wheel",
                "-d",
                dist_dir,
            ]
        )
    else:
        check_call(
            [
                sys.executable,
                setuppy_path,
                "sdist",
                "--format",
                "zip",
                "-d",
                dist_dir,
            ]
        )

    prebuilt_packages = [
        f for f in os.listdir(args.distribution_directory) if f.endswith(".whl" if package_type == "wheel" else ".zip")
    ]

    if not in_ci():
        logging.info("Cleaning up build directories and files")
        cleanup_build_artifacts(target_setup)
    return prebuilt_packages


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Build a package directory into wheel or sdist. Then install it."
    )
    parser.add_argument(
        "-d",
        "--distribution-directory",
        dest="distribution_directory",
        help="The path to the distribution directory. Should be passed $(Build.ArtifactStagingDirectory) from the devops yaml definition.",
        required=True,
    )

    parser.add_argument(
        "-p",
        "--path-to-setup",
        dest="target_setup",
        help="The path to the setup.py (not including the file) for the package we want to package into a wheel/sdist and install.",
        required=True,
    )

    parser.add_argument(
        "-s",
        "--skip-install",
        dest="skip_install",
        help="Create whl in distribution directory and skip installing it",
        default=False,
    )

    parser.add_argument(
        "-e",
        "--extra-index-url",
        dest="extra_index_url",
        help="Index URL to search for packages. This can be set to install package from azure devops feed",
    )

    parser.add_argument(
        "--install-preview",
        dest="install_preview",
        help="Install preview version of dependent packages. This is helpful when installing dev build version of packages from alternate package location",
    )

    parser.add_argument(
        "--cache-dir",
        dest="cache_dir",
        help="Location that, if present, will be used as the pip cache directory.",
    )

    parser.add_argument(
        "-w",
        "--work-dir",
        dest="work_dir",
        help="Location that, if present, will be used as working directory to run pip install.",
    )

    parser.add_argument(
        "--force-create",
        dest="force_create",
        help="Force recreate whl even if it is prebuilt",
    )

    parser.add_argument(
        "--package-type",
        dest="package_type",
        help="Package type to build",
        default="wheel",
    )


    args = parser.parse_args()

    setup_py_path = os.path.join(args.target_setup, "setup.py")
    discovered_packages = discover_packages(setup_py_path, args)

    if args.skip_install:
        logging.info(
            "Flag to skip install whl is passed. Skipping package installation"
        )
    else:
        for built_package in discovered_packages:
            # if the environment variable is set, that means that this is running where we
            # want to use the pre-built packages
            built_pkg_path = ""
            if os.getenv("PREBUILT_WHEEL_DIR") is not None and not args.force_create:
                # find the prebuilt package in the set of prebuilt wheels
                package_path = os.path.join(os.environ["PREBUILT_WHEEL_DIR"], built_package)
                if os.path.isfile(package_path):
                    built_pkg_path = package_path
                    logging.info("Installing {w} from directory".format(w=built_package))
                # it does't exist, so we need to error out
                else:
                    logging.error(
                        "{w} not present in the prebuilt package directory. Exiting.".format(
                            w=built_package
                        )
                    )
                    exit(1)
            else:
                built_pkg_path = os.path.abspath(os.path.join(args.distribution_directory, built_package))
                logging.info("Installing {w} from fresh built package.".format(w=built_package))

            commands = [
                sys.executable,
                "-m",
                "pip",
                "install",
                built_pkg_path
            ]


            # If extra index URL is passed then set it as argument to pip command
            if args.extra_index_url:
                commands.extend(["--extra-index-url", args.extra_index_url])

            # preview version is enabled when installing dev build so pip will install dev build version from devpos feed
            if args.install_preview:
                commands.append("--pre")

            if args.cache_dir:
                commands.extend(["--cache-dir", args.cache_dir])

            if args.work_dir and os.path.exists(args.work_dir):
                logging.info("Executing command from {0}:{1}".format(args.work_dir, commands))
                check_call(commands, cwd= args.work_dir)
            else:
                check_call(commands)
            logging.info("Installed {w}".format(w=built_package))
