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
    find_packages_missing_on_pypi,
    find_whl,
    find_tools_packages,
    get_installed_packages,
    extend_dev_requirements,
    str_to_bool
)
from git_helper import get_release_tag, git_checkout_tag, git_checkout_branch, clone_repo

AZURE_GLOB_STRING = "azure*"

root_dir = os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "..", ".."))
test_tools_req_file = os.path.abspath(os.path.join(root_dir, "eng", "test_tools.txt"))

GIT_REPO_NAME = "azure-sdk-for-python"
GIT_MASTER_BRANCH = "master"
VENV_NAME = "regressionenv"
AZURE_SDK_FOR_PYTHON_GIT_URL = "https://github.com/Azure/azure-sdk-for-python.git"
TEMP_FOLDER_NAME = ".tmp_code_path"

OLDEST_EXTENSION_PKGS = ['msrestazure','adal']

logging.getLogger().setLevel(logging.INFO)

class CustomVirtualEnv:
    def __init__(self, path):
        self.path = os.path.join(path, VENV_NAME)

    def create(self):
        logging.info("Creating virtual environment [{}]".format(self.path))
        run_check_call([sys.executable, "-m", "venv", "ENV_DIR", self.path], root_dir)
        self.python_executable = self._find_python_executable()
        self.lib_paths = self._find_lib_paths()

    def clear_venv(self):
        # clear any previously installed packages
        run_check_call(
            [sys.executable, "-m", "venv", "--clear", "ENV_DIR", self.path], root_dir
        )

    def _find_python_executable(self):
        paths = glob.glob(os.path.join(self.path, "*", "python")) + glob.glob(os.path.join(self.path, "*", "python.exe"))
        if not paths:
            logging.error("Failed to find path to python executable in virtual env:{}".format(self.path))
            sys.exit(1)
        return paths[0]

    def _find_lib_paths(self):
        paths = glob.glob(os.path.join(self.path, "*", "site-packages")) + glob.glob(os.path.join(self.path, "lib", "*", "site-packages"))
        if not paths:
            logging.error("Failed to find site-packages directory in virtual env:{}".format(self.path))
            sys.exit(1)
        return paths


class RegressionContext:
    def __init__(self, whl_dir, tmp_path, is_latest, pytest_mark_arg):
        self.whl_directory = whl_dir
        self.temp_path = tmp_path
        self.is_latest_depend_test = is_latest
        self.venv = CustomVirtualEnv(self.temp_path)
        self.pytest_mark_arg = pytest_mark_arg
        self.venv.create()

    def init_for_pkg(self, pkg_root):
        # This method is called each time context is switched to test regression for new package
        self.package_root_path = pkg_root
        self.package_name, self.pkg_version, _, _ = parse_setup(self.package_root_path)

    def initialize(self, dep_pkg_root_path):
        self.dep_pkg_root_path = dep_pkg_root_path
        self.venv.clear_venv()

    def deinitialize(self, dep_pkg_root_path):
        # This function can be used to reset code repo to master branch
        # Revert to master branch
        run_check_call(["git", "clean", "-fd"], dep_pkg_root_path)
        run_check_call(["git", "checkout", GIT_MASTER_BRANCH], dep_pkg_root_path)


class RegressionTest:
    def __init__(self, context, package_dependency_dict):
        self.context = context
        self.package_dependency_dict = package_dependency_dict

    def run(self):
        pkg_name = self.context.package_name
        if pkg_name in self.package_dependency_dict:
            logging.info("Running regression test for {}".format(pkg_name))

            self.whl_path = os.path.join(self.context.whl_directory, find_whl(pkg_name, self.context.pkg_version, self.context.whl_directory))
            if find_packages_missing_on_pypi(self.whl_path):
                logging.error("Required packages are not available on PyPI. Skipping regression test")
                exit(0)

            dep_packages = self.package_dependency_dict[pkg_name]
            logging.info("Dependent packages for [{0}]: {1}".format(pkg_name, dep_packages))
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
        self.context.initialize(dep_pkg_path)

        # find GA released tags for package and run test using that code base
        dep_pkg_name, version, _, _ = parse_setup(dep_pkg_path)
        release_tag = get_release_tag(dep_pkg_name, self.context.is_latest_depend_test)
        if not release_tag:
            logging.error("Release tag is not available. Skipping package {} from test".format(dep_pkg_name))
            return

        test_branch_name = "{0}_tests".format(release_tag)
        try:
            git_checkout_branch(test_branch_name, dep_pkg_path)
        except:
            # If git checkout failed for "tests" branch then checkout branch with release tag
            logging.info("Failed to checkout branch {}. Checking out release tagged git repo".format(test_branch_name))
            git_checkout_tag(release_tag, dep_pkg_path)

        try:
            # install packages required to run tests
            run_check_call(
                [
                    self.context.venv.python_executable,
                    "-m",
                    "pip",
                    "install",
                    "-r",
                    test_tools_req_file,
                ],
                dep_pkg_path
            )

            # Install pre-built whl for current package.
            install_package_from_whl(
                self.whl_path,
                self.context.temp_path,
                self.context.venv.python_executable,
            )

            # install dependent package from source
            self._install_packages(dep_pkg_path, self.context.package_name)
            
            # try install of pre-built whl for current package again. if unnecessary, pip does nothing.
            # we do this to ensure that the correct development version is installed. on non-dev builds
            # this step will just skip through.
            install_package_from_whl(
                self.whl_path,
                self.context.temp_path,
                self.context.venv.python_executable,
            )

            self._execute_test(dep_pkg_path)
        finally:
            self.context.deinitialize(dep_pkg_path)

    def _execute_test(self, dep_pkg_path):
        #  Ensure correct version of package is installed
        if not self._is_package_installed(self.context.package_name, self.context.pkg_version):
            logging.error("Incorrect version of package {0} is installed. Expected version {1}".format(self.context.package_name, self.context.pkg_version))
            sys.exit(1)

        logging.info("Running test for {}".format(dep_pkg_path))
        commands = [
            self.context.venv.python_executable,
            "-m",
            "pytest",
            "--verbose",
            "--durations",
            "10",
        ]

        # add any pytest mark arg if present. for e.g. 'not cosmosEmulator'
        if self.context.pytest_mark_arg:
            commands.extend(["-m", self.context.pytest_mark_arg])

        test_dir = self._get_package_test_dir(dep_pkg_path)
        if test_dir:
            commands.append(test_dir)
            run_check_call(commands, self.context.temp_path)
        else:
            logging.info("Test directory is not found in package root. Skipping {} from regression test.".format(self.context.package_name))

    def _get_package_test_dir(self, pkg_root_path):
        # Returns path to test or tests folder within package root directory.
        paths = glob.glob(os.path.join(pkg_root_path, "test")) + glob.glob(os.path.join(pkg_root_path, "tests"))
        if not paths:
            # We will run into this situation only if test and tests are missing in repo.
            # For now, running test for package repo itself to keep it same as regular CI in such cases
            logging.error("'test' folder is not found in {}".format(pkg_root_path))
            return
        return paths[0]

    def _install_packages(self, dependent_pkg_path, pkg_to_exclude):
        python_executable = self.context.venv.python_executable
        working_dir = self.context.package_root_path
        temp_dir = self.context.temp_path

        list_to_exclude = [pkg_to_exclude, 'azure-sdk-tools', 'azure-devtools' ]
        installed_pkgs = [p.split('==')[0] for p in get_installed_packages(self.context.venv.lib_paths) if p.startswith('azure-')]
        logging.info("Installed azure sdk packages:{}".format(installed_pkgs))

        # Do not exclude list of packages in tools directory and so these tools packages will be reinstalled from repo branch we are testing
        root_path = os.path.abspath(os.path.join(dependent_pkg_path, "..", "..", ".."))
        tools_packages = find_tools_packages(root_path)
        installed_pkgs = [req for req in installed_pkgs if req not in tools_packages]

        list_to_exclude.extend(installed_pkgs)
        # install dev requirement but skip already installed package which is being tested or present in dev requirement
        filtered_dev_req_path = filter_dev_requirements(
            dependent_pkg_path, list_to_exclude, dependent_pkg_path
        )

        # early versions of azure-sdk-tools had an unpinned version of azure-mgmt packages. 
        # that unpinned version hits an a code path in azure-sdk-tools that hits this error.
        if filtered_dev_req_path and self.context.is_latest_depend_test == False:
            logging.info(
                "Extending dev requirements with {}".format(OLDEST_EXTENSION_PKGS)
            )
            extend_dev_requirements(
                filtered_dev_req_path, OLDEST_EXTENSION_PKGS
            )
        else:
            logging.info("Not extending dev requirements {} {}".format(filtered_dev_req_path, self.context.is_latest_depend_test))

        if filtered_dev_req_path:
            logging.info("Extending dev requirement to include azure-sdk-tools")
            extend_dev_requirements(
                filtered_dev_req_path, [
                    "../../../tools/azure-sdk-tools",
                    "../../../tools/azure-devtools"
                ]
            )
            logging.info(
                "Installing filtered dev requirements from {}".format(filtered_dev_req_path)
            )
            run_check_call(
                [python_executable, "-m", "pip", "install", "-r", filtered_dev_req_path],
                dependent_pkg_path,
            )
        else:
            logging.info("dev requirements is not found to install")

        # install dependent package which is being verified
        run_check_call(
            [python_executable, "-m", "pip", "install", dependent_pkg_path], temp_dir
        )

    def _is_package_installed(self, package, version):
        # find env root and pacakge locations
        venv_root = self.context.venv.path
        site_packages = self.context.venv.lib_paths
        logging.info("Searching for packages in :{}".format(site_packages))
        installed_pkgs = get_installed_packages(site_packages)
        logging.info("Installed packages: {}".format(installed_pkgs))
        # Verify installed package version
        # Search for exact version or alpha build version of current version.
        pkg_search_string = "{0}=={1}".format(package, version)
        alpha_build_search_string = "{0}=={1}a".format(package, version)
        return any(p == pkg_search_string or p.startswith(alpha_build_search_string) for p in installed_pkgs)


# This method identifies package dependency map for all packages in azure sdk
def find_package_dependency(glob_string, repo_root_dir):
    package_paths = process_glob_string(
        glob_string, repo_root_dir, "", "Regression"
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

    code_repo_root = os.path.join(temp_dir, GIT_REPO_NAME)
    # Make sure root_dir where script is running is not same as code repo which will be reverted to old released branch to run test
    if root_dir == code_repo_root:
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

    targeted_packages = process_glob_string(args.glob_string, target_dir, "", "Regression")
    if len(targeted_packages) == 0:
        exit(0)

    # clone code repo only if it doesn't exist
    if not os.path.exists(code_repo_root):
        clone_repo(temp_dir, AZURE_SDK_FOR_PYTHON_GIT_URL)
    else:
        logging.info(
            "Path {} already exists. Skipping step to clone github repo".format(
                code_repo_root
            )
        )

    # find package dependency map for azure sdk
    pkg_dependency = find_package_dependency(AZURE_GLOB_STRING, code_repo_root)

    # Create regression text context. One context object will be reused for all packages
    context = RegressionContext(
        args.whl_dir, temp_dir, str_to_bool(args.verify_latest), args.mark_arg
    )

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

    parser.add_argument(
        "--mark-arg",
        dest="mark_arg",
        help=(
            'The complete argument for `pytest -m "<input>"`. This can be used to exclude or include specific pytest markers.'
            '--mark_arg="not cosmosEmulator"'
        ),
    )

    args = parser.parse_args()
    run_main(args)
