#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# Below are common methods for the devops build steps. This is the common location that will be updated with
# package targeting during release.

import glob
from subprocess import check_call, CalledProcessError
import os
import errno
import shutil
import sys
import logging
import ast
import textwrap
import io
import re
import pdb

# Assumes the presence of setuptools
from pkg_resources import parse_version, parse_requirements, Requirement

# this assumes the presence of "packaging"
from packaging.specifiers import SpecifierSet
from packaging.version import Version

from pip._internal.operations import freeze

DEV_REQ_FILE = "dev_requirements.txt"
NEW_DEV_REQ_FILE = "new_dev_requirements.txt"

logging.getLogger().setLevel(logging.INFO)

OMITTED_CI_PACKAGES = [
    "azure-mgmt-documentdb",
    "azure-servicemanagement-legacy",
    "azure-mgmt-scheduler",
]
MANAGEMENT_PACKAGE_IDENTIFIERS = [
    "mgmt",
    "azure-cognitiveservices",
    "azure-servicefabric",
    "nspkg",
    "azure-keyvault",
]
NON_MANAGEMENT_CODE_5_ALLOWED = ["azure-keyvault"]
META_PACKAGES = ["azure", "azure-mgmt", "azure-keyvault"]
REGRESSION_EXCLUDED_PACKAGES = [
    "azure-common",
    "azure-servicefabric",
]

omit_regression = (
    lambda x: "nspkg" not in x
    and "mgmt" not in x
    and os.path.basename(x) not in META_PACKAGES
    and os.path.basename(x) not in REGRESSION_EXCLUDED_PACKAGES
)
omit_docs = lambda x: "nspkg" not in x and os.path.basename(x) not in META_PACKAGES
omit_build = lambda x: os.path.basename(x) not in META_PACKAGES
# dict of filter type and filter function
omit_funct_dict = {
    "Build": omit_build,
    "Docs": omit_docs,
    "Regression": omit_regression,
}


def log_file(file_location, is_error=False):
    with open(file_location, "r") as file:
        for line in file:
            sys.stdout.write(line)
        sys.stdout.write("\n")
        sys.stdout.flush()


def read_file(file_location):
    str_buffer = ""
    with open(file_location, "r") as file:
        for line in file:
            str_buffer += line
    return str_buffer


def cleanup_folder(target_folder):
    for file in os.listdir(target_folder):
        file_path = os.path.join(target_folder, file)
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
        except Exception as e:
            logging.error(e)


# helper functions
def clean_coverage(coverage_dir):
    try:
        os.mkdir(coverage_dir)
    except OSError as e:
        if e.errno == errno.EEXIST:
            logging.info("Coverage dir already exists. Cleaning.")
            cleanup_folder(coverage_dir)
        else:
            raise


def parse_setup(setup_path):
    setup_filename = os.path.join(setup_path, "setup.py")
    mock_setup = textwrap.dedent(
        """\
    def setup(*args, **kwargs):
        __setup_calls__.append((args, kwargs))
    """
    )
    parsed_mock_setup = ast.parse(mock_setup, filename=setup_filename)
    with io.open(setup_filename, "r", encoding="utf-8-sig") as setup_file:
        parsed = ast.parse(setup_file.read())
        for index, node in enumerate(parsed.body[:]):
            if (
                not isinstance(node, ast.Expr)
                or not isinstance(node.value, ast.Call)
                or not hasattr(node.value.func, "id")
                or node.value.func.id != "setup"
            ):
                continue
            parsed.body[index:index] = parsed_mock_setup.body
            break

    fixed = ast.fix_missing_locations(parsed)
    codeobj = compile(fixed, setup_filename, "exec")
    local_vars = {}
    global_vars = {"__setup_calls__": []}
    current_dir = os.getcwd()
    working_dir = os.path.dirname(setup_filename)
    os.chdir(working_dir)
    exec(codeobj, global_vars, local_vars)
    os.chdir(current_dir)
    _, kwargs = global_vars["__setup_calls__"][0]

    try:
        python_requires = kwargs["python_requires"]
    # most do not define this, fall back to what we define as universal
    except KeyError as e:
        python_requires = ">=2.7"

    version = kwargs["version"]
    name = kwargs["name"]

    requires = []
    if "install_requires" in kwargs:
        requires = kwargs["install_requires"]

    return name, version, python_requires, requires


def parse_requirements_file(file_location):
    with open(file_location, "r") as f:
        reqs = f.read()

    return dict((req.name, req) for req in parse_requirements(reqs))


def parse_setup_requires(setup_path):
    _, _, python_requires, _ = parse_setup(setup_path)

    return python_requires


def filter_for_compatibility(package_set):
    collected_packages = []
    v = sys.version_info
    running_major_version = Version(".".join([str(v[0]), str(v[1]), str(v[2])]))

    for pkg in package_set:
        spec_set = SpecifierSet(parse_setup_requires(pkg))

        if running_major_version in spec_set:
            collected_packages.append(pkg)

    return collected_packages


# this function is where a glob string gets translated to a list of packages
# It is called by both BUILD (package) and TEST. In the future, this function will be the central location
# for handling targeting of release packages
def process_glob_string(
    glob_string,
    target_root_dir,
    additional_contains_filter="",
    filter_type="Build",
):
    if glob_string:
        individual_globs = glob_string.split(",")
    else:
        individual_globs = "azure-*"
    collected_top_level_directories = []

    for glob_string in individual_globs:
        globbed = glob.glob(
            os.path.join(target_root_dir, glob_string, "setup.py")
        ) + glob.glob(os.path.join(target_root_dir, "sdk/*/", glob_string, "setup.py"))
        collected_top_level_directories.extend([os.path.dirname(p) for p in globbed])

    # dedup, in case we have double coverage from the glob strings. Example: "azure-mgmt-keyvault,azure-mgmt-*"
    collected_directories = list(
        set(
            [
                p
                for p in collected_top_level_directories
                if additional_contains_filter in p
            ]
        )
    )

    # if we have individually queued this specific package, it's obvious that we want to build it specifically
    # in this case, do not honor the omission list
    if len(collected_directories) == 1:
        return filter_for_compatibility(collected_directories)
    # however, if there are multiple packages being built, we should honor the omission list and NOT build the omitted
    # packages
    else:
        allowed_package_set = remove_omitted_packages(collected_directories, filter_type)
        logging.info(
            "Target packages after filtering by omission list: {}".format(
                allowed_package_set
            )
        )

        pkg_set_ci_filtered = filter_for_compatibility(allowed_package_set)
        logging.info(
            "Package(s) omitted by CI filter: {}".format(
                list(set(allowed_package_set) - set(pkg_set_ci_filtered))
            )
        )

        return sorted(pkg_set_ci_filtered)


def remove_omitted_packages(collected_directories, filter_type="Build"):

    packages = [
        package_dir
        for package_dir in collected_directories
        if os.path.basename(package_dir) not in OMITTED_CI_PACKAGES
    ]

    packages = list(filter(omit_funct_dict.get(filter_type, omit_build), packages))
    return packages


def run_check_call(
    command_array,
    working_directory,
    acceptable_return_codes=[],
    run_as_shell=False,
    always_exit=True,
):
    try:
        if run_as_shell:
            logging.info(
                "Command Array: {0}, Target Working Directory: {1}".format(
                    " ".join(command_array), working_directory
                )
            )
            check_call(" ".join(command_array), cwd=working_directory, shell=True)
        else:
            logging.info(
                "Command Array: {0}, Target Working Directory: {1}".format(
                    command_array, working_directory
                )
            )
            check_call(command_array, cwd=working_directory)
    except CalledProcessError as err:
        if err.returncode not in acceptable_return_codes:
            logging.error(err)  # , file = sys.stderr
            if always_exit:
                exit(1)
            else:
                return err


# This function generates code coverage parameters
def create_code_coverage_params(parsed_args, package_name):
    coverage_args = []
    if parsed_args.disablecov:
        logging.info("Code coverage disabled as per the flag(--disablecov)")
        coverage_args.append("--no-cov")
    else:
        current_package_name = package_name.replace("-", ".")
        coverage_args.append("--cov={}".format(current_package_name))
        logging.info(
            "Code coverage is enabled for package {0}, pytest arguements: {1}".format(
                current_package_name, coverage_args
            )
        )
    return coverage_args


# This function returns if error code 5 is allowed for a given package
def is_error_code_5_allowed(target_pkg, pkg_name):
    if (
        all(
            map(
                lambda x: any(
                    [pkg_id in x for pkg_id in MANAGEMENT_PACKAGE_IDENTIFIERS]
                ),
                [target_pkg],
            )
        )
        or pkg_name in NON_MANAGEMENT_CODE_5_ALLOWED
    ):
        return True
    else:
        return False


# This function parses requirement and return package name and specifier
def parse_require(req):
    req_object = Requirement.parse(req)
    pkg_name = req_object.key
    spec = SpecifierSet(str(req_object).replace(pkg_name, ""))
    return [pkg_name, spec]


# This method installs package from a pre-built whl
def install_package_from_whl(
    package_name, version, whl_directory, working_dir, python_sym_link=sys.executable
):
    if not os.path.exists(whl_directory):
        logging.error("Whl directory is incorrect")
        exit(1)

    logging.info("Searching whl for package {}".format(package_name))
    whl_name = "{0}-{1}-*.whl".format(package_name.replace("-", "_"), version)
    paths = glob.glob(os.path.join(whl_directory, whl_name))
    if not paths:
        logging.error(
            "whl is not found in whl directory {0} for package {1}".format(
                whl_directory, package_name
            )
        )
        exit(1)

    package_whl_path = paths[0]
    commands = [python_sym_link, "-m", "pip", "install", package_whl_path]
    run_check_call(commands, working_dir)
    logging.info("Installed package {}".format(package_name))


def filter_dev_requirements(pkg_root_path, packages_to_exclude, dest_dir):
    # This method returns list of requirements from dev_requirements by filtering out packages in given list
    dev_req_path = os.path.join(pkg_root_path, DEV_REQ_FILE)
    requirements = []
    with open(dev_req_path, "r") as dev_req_file:
        requirements = dev_req_file.readlines()

    # filter any package given in excluded list
    requirements = [
        req
        for req in requirements
        if os.path.basename(req.replace("\n", "")) not in packages_to_exclude
    ]

    logging.info("Filtered dev requirements: {}".format(requirements))
    # create new dev requirements file with different name for filtered requirements
    new_dev_req_path = os.path.join(dest_dir, NEW_DEV_REQ_FILE)
    with open(new_dev_req_path, "w") as dev_req_file:
        dev_req_file.writelines(requirements)

    return new_dev_req_path
    