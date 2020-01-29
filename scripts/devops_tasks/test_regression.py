#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# This script will run regression test for packages which are added as required package by other packages
# Regression test ensures backword compatibility with released dependent package versions

import argparse
import glob
import sys
import os
import logging
from common_tasks import (
    process_glob_string,
    parse_setup,
    run_check_call,
    parse_require,
    install_package_from_whl,
    filter_dev_requirements,
    OmmitType,
)
from git_helper import get_release_tag, checkout_code_repo, clone_repo

AZURE_GLOB_STRING = "azure*"

root_dir = os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "..", ".."))
test_tools_req_file = os.path.abspath(os.path.join(root_dir, "eng", "test_tools.txt"))

GIT_REPO_NAME = "azure-sdk-for-python"
GIT_MASTER_BRANCH = "master"
VENV_NAME = "regressionenv"
AZURE_SDK_FOR_PYTHON_GIT_URL = "https://github.com/Azure/azure-sdk-for-python.git"
TEMP_FOLDER_NAME = ".tmp_code_path"
COSMOS_TEST_ARG = "not cosmosEmulator"

RELEASE_TAGS_TO_EXCLUDE = ['azure-storage-file-share_12.0.0','azure-storage-file-share_12.0.0b5']

logging.getLogger().setLevel(logging.INFO)


class CustomVirtualEnv:
    def __init__(self, path):
        self.path = os.path.join(path, VENV_NAME)

    def create(self):
        logging.info("Creating virtual environment [{}]".format(self.path))
        run_check_call([sys.executable, "-m", "venv", "ENV_DIR", self.path], root_dir)

    def _process_venv(self, activate_env):
        if activate_env:
            # clear any previously installed packages
            run_check_call(
                [sys.executable, "-m", "venv", "--clear", "ENV_DIR", self.path],
                root_dir,
            )

        scriptName = "activate.bat" if activate_env else "deactivate.bat"
        venv_script = os.path.join(self.path, "Scripts", scriptName)
        operation_type = "Activating" if activate_env else "Deactivating"

        if os.path.exists(venv_script):
            logging.info(
                "{0} virtual environment {1}".format(operation_type, venv_script)
            )
            run_check_call([venv_script,], root_dir)
        else:
            logging.error(
                "Script to process virtualenv is missing. path [{}]".format(venv_script)
            )
            sys.exit(1)

    def activate(self):
        self._process_venv(True)

    def deactivate(self):
        self._process_venv(False)


class RegressionContext:
    def __init__(self, whl_dir, tmp_path, is_latest):
        self.whl_directory = whl_dir
        self.temp_path = tmp_path
        self.is_latest_depend_test = is_latest
        self.venv = CustomVirtualEnv(self.temp_path)
        self.venv.create()
        self.python_symlink = os.path.abspath(
            os.path.join(self.venv.path, "Scripts", "python")
        )

    def init_for_pkg(self, pkg_root):
        # This method is called each time context is switched to test regression for new package
        self.package_root_path = pkg_root
        self.package_name, _, _, _ = parse_setup(self.package_root_path)

    def activate(self, dep_pkg_root_path):
        self.dep_pkg_root_path = dep_pkg_root_path
        self.venv.activate()

    def deactivate(self, dep_pkg_root_path):
        # This function can be used to reset code repo to master branch and also to deactivate virtual env
        # Revert to master branch
        run_check_call(["git", "clean", "-fd"], dep_pkg_root_path)
        run_check_call(["git", "checkout", GIT_MASTER_BRANCH], dep_pkg_root_path)
        self.venv.deactivate()


class RegressionTest:
    def __init__(self, context, package_dependency_dict):
        self.context = context
        self.package_dependency_dict = package_dependency_dict

    def run(self):
        pkg_name = self.context.package_name
        if pkg_name in self.package_dependency_dict:
            dep_packages = self.package_dependency_dict[pkg_name]
            logging.info("Running regression test for {}".format(pkg_name))
            logging.info(
                "Dependent packages for [{0}]: {1}".format(pkg_name, dep_packages)
            )

            for dep_pkg_path in dep_packages:
                dep_pkg_name, _, _, _ = parse_setup(dep_pkg_path)
                logging.info(
                    "Starting regression test of {0} against released {1}".format(
                        pkg_name, dep_pkg_name
                    )
                )
                self._run_test(dep_pkg_path)
                logging.info(
                    "Completed regression test of {0} against released {1}".format(
                        pkg_name, dep_pkg_name
                    )
                )
            logging.info("Completed regression test for {}".format(pkg_name))
        else:
            logging.info(
                "Package {} is not added as required by any package".format(pkg_name)
            )

    def _run_test(self, dep_pkg_path):
        # find GA released tags for package and run test using that code base
        dep_pkg_name, _, _, _ = parse_setup(dep_pkg_path)
        release_tag = get_release_tag(dep_pkg_name, self.context.is_latest_depend_test)
        if not release_tag:
            logging.error(
                "Release tag is not avaiable. Skipping package {} from test".format(
                    dep_pkg_name
                )
            )
            sys.exit(1)

        # Ommit based on package name and release tag
        if release_tag in RELEASE_TAGS_TO_EXCLUDE:
            logging.info("Release tag {0} is excluded from regression test".format(release_tag))
            return

        # Get code repo with released tag of dependent package
        checkout_code_repo(release_tag, dep_pkg_path)

        try:
            # activate virtual env
            self.context.activate(dep_pkg_path)
            # install packages required to run tests after updating relative reference to abspath
            run_check_call(
                [
                    self.context.python_symlink,
                    "-m",
                    "pip",
                    "install",
                    "-r",
                    test_tools_req_file,
                ],
                self.context.package_root_path,
            )
            # Install pre-built whl for current package
            install_package_from_whl(
                self.context.package_name,
                self.context.whl_directory,
                self.context.temp_path,
                self.context.python_symlink,
            )
            # install package to be tested and run pytest
            self._execute_test(dep_pkg_path)
        finally:
            # deactivate virtual env and revert repo
            self.context.deactivate(dep_pkg_path)


    def _execute_test(self, dep_pkg_path):
        # install dependent package from source
        self._install_packages(dep_pkg_path, self.context.package_name)
        logging.info("Running test for {}".format(dep_pkg_path))
        pkg_test_dir = self._get_package_test_dir(dep_pkg_path)
        run_check_call(
            [
                self.context.python_symlink,
                "-m",
                "pytest",
                "--verbose",
                "-m",
                COSMOS_TEST_ARG,
                pkg_test_dir,
            ],
            self.context.temp_path,
        )

    def _get_package_test_dir(self, pkg_root_path):
        # Returns path to test or tests folder within package root directory.
        paths = glob.glob(os.path.join(pkg_root_path, "test*"))
        if paths is None:
            logging.error("'test' folder is not found in {}".format(pkg_root_path))
            sys.exit(1)
        return paths[0]

    def _install_packages(self, dependent_pkg_path, pkg_to_exclude):
        python_executable = self.context.python_symlink
        working_dir = self.context.package_root_path
        temp_dir = self.context.temp_path

        # install dev requirement but skip already installed package which is being tested
        filtered_dev_req_path = filter_dev_requirements(
            dependent_pkg_path, [pkg_to_exclude,], dependent_pkg_path
        )
        logging.info(
            "Installing filtered dev requirements from {}".format(filtered_dev_req_path)
        )
        run_check_call(
            [python_executable, "-m", "pip", "install", "-r", filtered_dev_req_path],
            dependent_pkg_path,
        )
        # install dependent package which is being verified
        run_check_call(
            [python_executable, "-m", "pip", "install", dependent_pkg_path], temp_dir
        )


# This method identifies package dependency map for all packages in azure sdk
def find_package_dependency(glob_string, repo_root_dir):
    package_paths = process_glob_string(
        glob_string, repo_root_dir, "", OmmitType.Regression
    )
    dependency_map = {}
    for pkg_root in package_paths:
        _, _, _, requires = parse_setup(pkg_root)

        # Get a list of package names from install requires
        required_pkgs = [parse_require(r)[0] for r in requires]
        required_pkgs = [p for p in required_pkgs if p.startswith("azure")]

        for req_pkg in required_pkgs:
            if req_pkg not in dependency_map:
                dependency_map[req_pkg] = []
            dependency_map[req_pkg].append(pkg_root)

    logging.info("Package dependency: {}".format(dependency_map))
    return dependency_map


# This is the main function which identifies packages to test, find dependency matrix and trigger test
def run_main(args):

    temp_dir = ""
    if args.temp_dir:
        temp_dir = args.temp_dir
    else:
        temp_dir = os.path.abspath(os.path.join(root_dir, "..", TEMP_FOLDER_NAME))

    core_repo_root = os.path.join(temp_dir, GIT_REPO_NAME)
    # Make sure root_dir where script is running is not same as code repo which will be reverted to old released branch to run test
    if root_dir == core_repo_root:
        logging.error(
            "Invalid path to clone github code repo. Temporary path can not be same as current source root directory"
        )
        exit(1)

    # Make sure temp path exists
    if not os.path.exists(temp_dir):
        os.mkdir(temp_dir)

    if args.service:
        service_dir = os.path.join("sdk", args.service)
        target_dir = os.path.join(root_dir, service_dir)
    else:
        target_dir = root_dir

    targeted_packages = process_glob_string(args.glob_string, target_dir)
    if len(targeted_packages) == 0:
        exit(0)

    # clone code repo only if it doesn't exists
    if not os.path.exists(core_repo_root):
        clone_repo(temp_dir, AZURE_SDK_FOR_PYTHON_GIT_URL)
    else:
        logging.info(
            "Path {} already exists. Skipping step to clone github repo".format(
                core_repo_root
            )
        )

    # find package dependency map for azure sdk
    pkg_dependency = find_package_dependency(AZURE_GLOB_STRING, core_repo_root)
    logging.info("Regression test will run for: {}".format(pkg_dependency.keys()))

    # Create regression text context. One context object will be reused for all packages
    context = RegressionContext(args.whl_dir, temp_dir, args.verify_latest)

    for pkg_path in targeted_packages:
        context.init_for_pkg(pkg_path)
        RegressionTest(context, pkg_dependency).run()
    logging.info("Regression test is completed successfully")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run regression test for a package against released dependent packages"
    )

    parser.add_argument(
        "glob_string",
        nargs="?",
        help=(
            "A comma separated list of glob strings that will target the top level directories that contain packages."
            'Examples: All = "azure*", Single = "azure-keyvault", Targeted Multiple = "azure-keyvault,azure-mgmt-resource"'
        ),
    )

    parser.add_argument(
        "--service",
        help=(
            "Name of service directory (under sdk/) to test."
            "Example: --service applicationinsights"
        ),
    )

    parser.add_argument(
        "--whl-dir",
        required=True,
        help=("Directory in which whl is pre built for all eligible package"),
    )

    parser.add_argument(
        "--verify-latest",
        default=True,
        help=(
            "Set this parameter to true to verify regression against latest released version."
            "Default behavior is to test regression for oldest released version of dependent packages"
        ),
    )

    parser.add_argument(
        "--temp-dir",
        help=(
            "Temporary path to clone github repo of azure-sdk-for-python to run tests. Any changes in this path will be overwritten"
        ),
    )

    args = parser.parse_args()
    run_main(args)
