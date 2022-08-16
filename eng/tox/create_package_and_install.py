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
import pdb
from pkg_resources import parse_version

from tox_helper_tasks import find_whl, find_sdist, get_pip_list_output
from ci_tools.parsing import ParsedSetup, parse_require
from ci_tools.build import create_package

logging.getLogger().setLevel(logging.INFO)

from ci_tools.parsing import ParsedSetup

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
        packages = build_and_discover_package(
            setuppy_path,
            args.distribution_directory,
            args.target_setup,
            args.package_type,
        )
    return packages


def discover_prebuilt_package(dist_directory, setuppy_path, package_type):
    packages = []
    pkg = ParsedSetup.from_path(setuppy_path)
    if package_type == "wheel":
        prebuilt_package = find_whl(dist_directory, pkg.name, pkg.version)
    else:
        prebuilt_package = find_sdist(dist_directory, pkg.name, pkg.version)

    if prebuilt_package is None:
        logging.error(
            "Package is missing in prebuilt directory {0} for package {1} and version {2}".format(
                dist_directory, pkg.name, pkg.version
            )
        )
        exit(1)
    packages.append(prebuilt_package)
    return packages


def in_ci():
    return os.getenv("TF_BUILD", False)


def build_and_discover_package(setuppy_path, dist_dir, target_setup, package_type):
    if package_type == "wheel":
        create_package(setuppy_path, dist_dir, enable_sdist=False)
    else:
        create_package(setuppy_path, dist_dir, enable_wheel=False)

    prebuilt_packages = [
        f for f in os.listdir(args.distribution_directory) if f.endswith(".whl" if package_type == "wheel" else ".zip")
    ]

    if not in_ci():
        logging.info("Cleaning up build directories and files")
        cleanup_build_artifacts(target_setup)
    return prebuilt_packages


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Build a package directory into wheel or sdist. Then install it. To install dev dependencies, set environment variable "SetDevVersion" to "true" and set "PIP_INDEX_URL" to a python feed.'
    )
    parser.add_argument(
        "-d",
        "--distribution-directory",
        dest="distribution_directory",
        help="The path to the distribution directory. This is the temporary location where packages will be built. Most commonly tox {envtmpdir}.",
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

    parser.add_argument(
        "--pre-download-disabled",
        dest="pre_download_disabled",
        help="During a dev build, we will restore package dependencies from a dev feed before installing them. The presence of this flag disables that behavior.",
        action="store_true",
    )

    args = parser.parse_args()

    commands_options = []
    built_pkg_path = ""
    setup_py_path = os.path.join(args.target_setup, "setup.py")
    additional_downloaded_reqs = []

    if not os.path.exists(args.distribution_directory):
        os.mkdir(args.distribution_directory)

    tmp_dl_folder = os.path.join(args.distribution_directory, "dl")
    if not os.path.exists(tmp_dl_folder):
        os.mkdir(tmp_dl_folder)

    # preview version is enabled when installing dev build so pip will install dev build version from devpos feed
    if os.getenv("SetDevVersion", 'false') == 'true':
        commands_options.append("--pre")

    if args.cache_dir:
        commands_options.extend(["--cache-dir", args.cache_dir])

    discovered_packages = discover_packages(setup_py_path, args)

    if args.skip_install:
        logging.info("Flag to skip install whl is passed. Skipping package installation")
    else:
        for built_package in discovered_packages:
            if os.getenv("PREBUILT_WHEEL_DIR") is not None and not args.force_create:
                # find the prebuilt package in the set of prebuilt wheels
                package_path = os.path.join(os.environ["PREBUILT_WHEEL_DIR"], built_package)
                if os.path.isfile(package_path):
                    built_pkg_path = package_path
                    logging.info("Installing {w} from directory".format(w=built_package))
                # it does't exist, so we need to error out
                else:
                    logging.error("{w} not present in the prebuilt package directory. Exiting.".format(w=built_package))
                    exit(1)
            else:
                built_pkg_path = os.path.abspath(os.path.join(args.distribution_directory, built_package))
                logging.info("Installing {w} from fresh built package.".format(w=built_package))

            if not args.pre_download_disabled:
                requirements = ParsedSetup.from_path(os.path.join(os.path.abspath(args.target_setup), "setup.py")).requires
                azure_requirements = [req.split(";")[0] for req in requirements if req.startswith("azure")]

                if azure_requirements:
                    logging.info(
                        "Found {} azure requirement(s): {}".format(len(azure_requirements), azure_requirements)
                    )

                    download_command = [
                        sys.executable,
                        "-m",
                        "pip",
                        "download",
                        "-d",
                        tmp_dl_folder,
                        "--no-deps",
                    ]

                    installation_additions = []

                    # only download a package if the requirement is not already met, so walk across
                    # direct install_requires
                    for req in azure_requirements:
                        addition_necessary = True
                        # get all installed packages
                        installed_pkgs = get_pip_list_output()

                        # parse the specifier
                        req_name, req_specifier = parse_require(req)

                        # if we have the package already present...
                        if req_name in installed_pkgs:
                            # if there is no specifier for the requirement, we can ignore it
                            if req_specifier is None:
                                addition_necessary = False

                            # if the package we're installing doesn't require a specific version (indicated by req_specifier) for the requiremeent (req_name)
                            # then its presence is enough. No reason to add it to necessary installations.
                            if req_specifier is None:
                                addition_necessary = False

                            # ...do we need to install the new version? if the existing specifier matches, we're fine
                            if req_specifier is not None and installed_pkgs[req_name] in req_specifier:
                                addition_necessary = False

                        if addition_necessary:
                            installation_additions.append(req)

                    if installation_additions:
                        download_command.extend(installation_additions)
                        download_command.extend(commands_options)

                        check_call(download_command, env=dict(os.environ, PIP_EXTRA_INDEX_URL=""))
                        additional_downloaded_reqs = [
                            os.path.abspath(os.path.join(tmp_dl_folder, pth)) for pth in os.listdir(tmp_dl_folder)
                        ]

            commands = [sys.executable, "-m", "pip", "install", built_pkg_path]

            commands.extend(additional_downloaded_reqs)
            commands.extend(commands_options)

            if args.work_dir and os.path.exists(args.work_dir):
                logging.info("Executing command from {0}:{1}".format(args.work_dir, commands))
                check_call(commands, cwd=args.work_dir)
            else:
                check_call(commands)
            logging.info("Installed {w}".format(w=built_package))
