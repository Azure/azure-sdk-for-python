#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# Below are common methods for the devops build steps. This is the common location that will be updated with
# package targeting during release.

import glob
from subprocess import check_call, CalledProcessError, Popen
import os
import errno
import shutil
import sys
import logging
import ast
import textwrap
import io
import re
import fnmatch
import platform

# Assumes the presence of setuptools
from pkg_resources import parse_version, parse_requirements, Requirement, WorkingSet, working_set

# this assumes the presence of "packaging"
from packaging.specifiers import SpecifierSet
from packaging.version import Version
from packaging.version import parse

DEV_REQ_FILE = "dev_requirements.txt"
NEW_DEV_REQ_FILE = "new_dev_requirements.txt"
NEW_REQ_PACKAGES = ["azure-core", "azure-mgmt-core"]

logging.getLogger().setLevel(logging.INFO)




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


def str_to_bool(input_string):
    if isinstance(input_string, bool):
        return input_string
    elif input_string.lower() in ("true", "t", "1"):
        return True
    elif input_string.lower() in ("false", "f", "0"):
        return False
    else:
        return False


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


def get_name_from_specifier(version):
    return re.split(r"[><=]", version)[0]

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
                "Command Array: {0}, Target Working Directory: {1}".format(" ".join(command_array), working_directory)
            )
            check_call(" ".join(command_array), cwd=working_directory, shell=True)
        else:
            logging.info("Command Array: {0}, Target Working Directory: {1}".format(command_array, working_directory))
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
        coverage_args.append("--cov-append")
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
                lambda x: any([pkg_id in x for pkg_id in MANAGEMENT_PACKAGE_IDENTIFIERS]),
                [target_pkg],
            )
        )
        or pkg_name in MANAGEMENT_PACKAGE_IDENTIFIERS
    ):
        return True
    else:
        return False


def parse_require(req):
    """
    Parses the incoming version specification and returns a tuple of the requirement name and specifier.

    "azure-core<2.0.0,>=1.11.0" -> [azure-core, <2.0.0,>=1.11.0]
    """
    req_object = Requirement.parse(req.split(";")[0])
    pkg_name = req_object.key
    spec = SpecifierSet(str(req_object).replace(pkg_name, ""))
    return [pkg_name, spec]


def find_whl(package_name, version, whl_directory):
    if not os.path.exists(whl_directory):
        logging.error("Whl directory is incorrect")
        exit(1)

    parsed_version = parse(version)

    logging.info("Searching whl for package {0}-{1}".format(package_name, parsed_version.base_version))
    whl_name_format = "{0}-{1}*.whl".format(package_name.replace("-", "_"), parsed_version.base_version)
    whls = []
    for root, dirnames, filenames in os.walk(whl_directory):
        for filename in fnmatch.filter(filenames, whl_name_format):
            whls.append(os.path.join(root, filename))

    whls = [os.path.relpath(w, whl_directory) for w in whls]

    if not whls:
        logging.error(
            "whl is not found in whl directory {0} for package {1}-{2}".format(
                whl_directory, package_name, parsed_version.base_version
            )
        )
        exit(1)

    return whls[0]

# This method installs package from a pre-built whl
def install_package_from_whl(package_whl_path, working_dir, python_sym_link=sys.executable):
    commands = [
        python_sym_link,
        "-m",
        "pip",
        "install",
        package_whl_path,
        "--extra-index-url",
        "https://pypi.python.org/simple",
    ]
    run_check_call(commands, working_dir)
    logging.info("Installed package from {}".format(package_whl_path))


def filter_dev_requirements(pkg_root_path, packages_to_exclude, dest_dir):
    # This method returns list of requirements from dev_requirements by filtering out packages in given list
    dev_req_path = os.path.join(pkg_root_path, DEV_REQ_FILE)
    if not os.path.exists(dev_req_path):
        logging.info("{0} is not found in package root {1}".format(DEV_REQ_FILE, pkg_root_path))
        return ""

    requirements = []
    with open(dev_req_path, "r") as dev_req_file:
        requirements = dev_req_file.readlines()

    # filter any package given in excluded list
    requirements = [req for req in requirements if os.path.basename(req.replace("\n", "")) not in packages_to_exclude]

    logging.info("Filtered dev requirements: {}".format(requirements))
    # create new dev requirements file with different name for filtered requirements
    new_dev_req_path = os.path.join(dest_dir, NEW_DEV_REQ_FILE)
    with open(new_dev_req_path, "w") as dev_req_file:
        dev_req_file.writelines(requirements)

    return new_dev_req_path


def extend_dev_requirements(dev_req_path, packages_to_include):
    requirements = []
    with open(dev_req_path, "r") as dev_req_file:
        requirements = dev_req_file.readlines()

    # include any package given in included list. omit duplicate
    for requirement in packages_to_include:
        if requirement not in requirements:
            requirements.insert(0, requirement.rstrip() + "\n")

    logging.info("Extending dev requirements. New result:: {}".format(requirements))
    # create new dev requirements file with different name for filtered requirements
    with open(dev_req_path, "w") as dev_req_file:
        dev_req_file.writelines(requirements)


def is_required_version_on_pypi(package_name, spec):
    from pypi_tools.pypi import PyPIClient

    client = PyPIClient()
    versions = []
    try:
        versions = [str(v) for v in client.get_ordered_versions(package_name) if str(v) in spec]
    except:
        logging.error("Package {} is not found on PyPI", package_name)
    return versions


def find_packages_missing_on_pypi(path):
    import pkginfo

    requires = []
    if path.endswith(".whl"):
        requires = list(filter(lambda_filter_azure_pkg, pkginfo.get_metadata(path).requires_dist))
    else:
        _, _, _, requires = parse_setup(path)

    # parse pkg name and spec
    pkg_spec_dict = dict(parse_require(req) for req in requires)
    logging.info("Package requirement: {}".format(pkg_spec_dict))
    # find if version is available on pypi
    missing_packages = [
        "{0}{1}".format(pkg, pkg_spec_dict[pkg])
        for pkg in pkg_spec_dict.keys()
        if not is_required_version_on_pypi(pkg, pkg_spec_dict[pkg])
    ]
    if missing_packages:
        logging.error("Packages not found on PyPI: {}".format(missing_packages))
    return missing_packages


def find_tools_packages(root_path):
    """Find packages in tools directory. For e.g. azure-sdk-tools, azure-devtools"""
    glob_string = os.path.join(root_path, "tools", "*", "setup.py")
    pkgs = [os.path.basename(os.path.dirname(p)) for p in glob.glob(glob_string)]
    logging.info("Packages in tools: {}".format(pkgs))
    return pkgs


def get_installed_packages(paths=None):
    """Find packages in default or given lib paths"""
    # WorkingSet returns installed packages in given path
    # working_set returns installed packages in default path
    # if paths is set then find installed packages from given paths
    ws = WorkingSet(paths) if paths else working_set
    return ["{0}=={1}".format(p.project_name, p.version) for p in ws]


def get_package_properties(setup_py_path):
    """Parse setup.py and return package details like package name, version, whether it's new SDK"""
    pkgName, version, _, requires = parse_setup(setup_py_path)
    is_new_sdk = pkgName in NEW_REQ_PACKAGES or any(map(lambda x: (parse_require(x)[0] in NEW_REQ_PACKAGES), requires))
    return pkgName, version, is_new_sdk, setup_py_path
