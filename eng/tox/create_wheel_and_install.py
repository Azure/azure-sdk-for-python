#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# This script is used to create and install the appropriate wheel for a tox environment.
# it should be executed from tox with `{toxenvdir}/python` to ensure that the wheel
# can be successfully tested from within a tox environment.

from subprocess import check_call
import argparse
import os
import logging
import sys
import glob
import shutil

from tox_helper_tasks import find_whl, get_package_details
logging.getLogger().setLevel(logging.INFO)


def cleanup_build_artifacts(build_folder):
    # clean up egginfo
    results = glob.glob(os.path.join(build_folder, "*.egg-info"))

    if results:
        print(results[0])
        shutil.rmtree(results[0])

    # clean up build results
    shutil.rmtree(os.path.join(build_folder, "build"))


def discover_whls(setuppy_path, dist_dir, target_setup):
    wheels = []
    if os.getenv("PREBUILT_WHEEL_DIR") is not None:
        wheels = discover_prebuilt_whl(os.getenv("PREBUILT_WHEEL_DIR"), setuppy_path)
    else:
        wheels = build_and_discover_whl(setuppy_path, dist_dir, target_setup)
    return wheels


def discover_prebuilt_whl(whl_directory, setuppy_path):
    wheels = []
    pkg_name, _, version = get_package_details(setuppy_path)
    whl_name = find_whl(whl_directory, pkg_name, version)
    if whl_name is None:
        logging.error("whl is missing in prebuilt whl directory {0} for package {1} and version {2}".format(whl_directory, pkg_name, version))
        exit(1)
    wheels.append(whl_name)
    return wheels


def build_and_discover_whl(setuppy_path, dist_dir, target_setup):
    check_call(
        [
            sys.executable,
            setuppy_path,
            "bdist_wheel",
            "-d",
            dist_dir,
        ]
    )

    wheels = [
        f for f in os.listdir(args.distribution_directory) if f.endswith(".whl")
    ]

    cleanup_build_artifacts(target_setup)
    return wheels


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Build a package directory into a wheel. Then install it."
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
        help="The path to the setup.py (not including the file) for the package we want to package into a wheel and install.",
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

    args = parser.parse_args()

    setup_py_path = os.path.join(args.target_setup, "setup.py")
    discovered_wheels = discover_whls(setup_py_path, args.distribution_directory, args.target_setup)

    if args.skip_install:
        logging.info(
            "Flag to skip install whl is passed. Skipping package installation"
        )
    else:
        for wheel in discovered_wheels:
            # if the environment variable is set, that means that this is running where we
            # want to use the pre-built wheels
            pkg_wheel_path = ""
            if os.getenv("PREBUILT_WHEEL_DIR") is not None:
                # find the wheel in the set of prebuilt wheels
                whl_path = os.path.join(os.environ["PREBUILT_WHEEL_DIR"], wheel)
                if os.path.isfile(whl_path):
                    pkg_wheel_path = whl_path
                    logging.info("Installing {w} from wheel directory".format(w=wheel))
                # it does't exist, so we need to error out
                else:
                    logging.error(
                        "{w} not present in the prebuilt wheels directory. Exiting.".format(
                            w=wheel
                        )
                    )
                    exit(1)
            else:
                pkg_wheel_path = os.path.join(args.distribution_directory, wheel)
                logging.info("Installing {w} from fresh wheel.".format(w=wheel))

            commands = [
                sys.executable,
                "-m",
                "pip",
                "install",
                pkg_wheel_path
            ]

            # force install package when installing from prebuilt whl to make sure whl is installed on running environment
            if os.getenv("PREBUILT_WHEEL_DIR") is not None:
                commands.append("--force")

            # If extra index URL is passed then set it as argument to pip command
            if args.extra_index_url:
                commands.extend(["--extra-index-url", args.extra_index_url])

            # preview version is enabled when installing dev build so pip will install dev build version from devpos feed
            if args.install_preview:
                commands.append("--pre")

            if args.cache_dir:
                commands.extend(["--cache-dir", args.cache_dir])


            check_call(commands)
            logging.info("Installed {w}".format(w=wheel))
