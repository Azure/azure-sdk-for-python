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
from typing import Tuple, Iterable

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

OMITTED_CI_PACKAGES = [
    "azure-mgmt-documentdb",
    "azure-servicemanagement-legacy",
    "azure-mgmt-scheduler",
    "azure",
    "azure-mgmt",
    "azure-storage",
    "azure-monitor",
    "azure-mgmt-regionmove",
]
MANAGEMENT_PACKAGE_IDENTIFIERS = [
    "mgmt",
    "azure-cognitiveservices",
    "azure-servicefabric",
    "nspkg",
    "azure-keyvault",
    "azure-synapse",
    "azure-ai-anomalydetector",
]
META_PACKAGES = ["azure", "azure-mgmt", "azure-keyvault"]
REGRESSION_EXCLUDED_PACKAGES = [
    "azure-common",
]

MANAGEMENT_PACKAGES_FILTER_EXCLUSIONS = [
    "azure-mgmt-core",
]

TEST_COMPATIBILITY_MAP = {"azure-core-tracing-opentelemetry": "<3.10"}

omit_regression = (
    lambda x: "nspkg" not in x
    and "mgmt" not in x
    and os.path.basename(x) not in MANAGEMENT_PACKAGE_IDENTIFIERS
    and os.path.basename(x) not in META_PACKAGES
    and os.path.basename(x) not in REGRESSION_EXCLUDED_PACKAGES
)
omit_docs = lambda x: "nspkg" not in x and os.path.basename(x) not in META_PACKAGES
omit_build = lambda x: x  # Dummy lambda to match omit type
lambda_filter_azure_pkg = lambda x: x.startswith("azure") and "-nspkg" not in x
omit_mgmt = lambda x: "mgmt" not in x or os.path.basename(x) in MANAGEMENT_PACKAGES_FILTER_EXCLUSIONS


# dict of filter type and filter function
omit_funct_dict = {
    "Build": omit_build,
    "Docs": omit_docs,
    "Regression": omit_regression,
    "Omit_management": omit_mgmt,
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


def str_to_bool(input_string):
    if isinstance(input_string, bool):
        return input_string
    elif input_string.lower() in ("true", "t", "1"):
        return True
    elif input_string.lower() in ("false", "f", "0"):
        return False
    else:
        return False


def parse_setup(setup_path: str) -> Tuple[str, str, Iterable[str], str]:
    """
    This function is used for getting metadata about a package from its setup.py.

    Tuple index:
      * 0 = name
      * 1 = version
      * 2 = array of dependencies
      * 3 = python_requires value
    """

    setup_filename = setup_path
    if not setup_path.endswith("setup.py"):
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


def filter_for_compatibility(package_set):
    collected_packages = []
    v = sys.version_info
    running_major_version = Version(".".join([str(v[0]), str(v[1]), str(v[2])]))

    for pkg in package_set:
        spec_set = SpecifierSet(parse_setup_requires(pkg))

        if running_major_version in spec_set:
            collected_packages.append(pkg)

    return collected_packages


def compare_python_version(version_spec):
    current_sys_version = parse(platform.python_version())
    spec_set = SpecifierSet(version_spec)

    return current_sys_version in spec_set


def filter_packages_by_compatibility_override(package_set, resolve_basename=True):
    return [
        p
        for p in package_set
        if compare_python_version(TEST_COMPATIBILITY_MAP.get(os.path.basename(p) if resolve_basename else p, ">=2.7"))
    ]


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
        globbed = glob.glob(os.path.join(target_root_dir, glob_string, "setup.py")) + glob.glob(
            os.path.join(target_root_dir, "sdk/*/", glob_string, "setup.py")
        )
        collected_top_level_directories.extend([os.path.dirname(p) for p in globbed])

    # dedup, in case we have double coverage from the glob strings. Example: "azure-mgmt-keyvault,azure-mgmt-*"
    collected_directories = list(set([p for p in collected_top_level_directories if additional_contains_filter in p]))

    # if we have individually queued this specific package, it's obvious that we want to build it specifically
    # in this case, do not honor the omission list
    if len(collected_directories) == 1:
        pkg_set_ci_filtered = filter_for_compatibility(collected_directories)
    # however, if there are multiple packages being built, we should honor the omission list and NOT build the omitted
    # packages
    else:
        allowed_package_set = remove_omitted_packages(collected_directories)
        pkg_set_ci_filtered = filter_for_compatibility(allowed_package_set)

    # Apply filter based on filter type. for e.g. Docs, Regression, Management
    pkg_set_ci_filtered = list(filter(omit_funct_dict.get(filter_type, omit_build), pkg_set_ci_filtered))
    logging.info("Target packages after filtering by CI: {}".format(pkg_set_ci_filtered))
    logging.info(
        "Package(s) omitted by CI filter: {}".format(list(set(collected_directories) - set(pkg_set_ci_filtered)))
    )
    return sorted(pkg_set_ci_filtered)


def remove_omitted_packages(collected_directories):
    packages = [
        package_dir for package_dir in collected_directories if os.path.basename(package_dir) not in OMITTED_CI_PACKAGES
    ]

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


def parse_require(req) -> Tuple[str, str]:
    """
    Parses the incoming version specification and returns a tuple of the requirement name and specifier.

    "azure-core<2.0.0,>=1.11.0" -> [azure-core, <2.0.0,>=1.11.0]
    """

    req_object = Requirement.parse(req.split(";")[0])
    pkg_name = req_object.key
    spec = SpecifierSet(str(req_object).replace(pkg_name, ""))
    return (pkg_name, spec)


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


def is_required_version_on_pypi(package_name: str, spec: str) -> bool:
    """
    This function evaluates a package name and version specifier combination and returns the versions on pypi
    that satisfy the provided version specifier.

    Import dependency on azure-sdk-tools.
    """

    from pypi_tools.pypi import PyPIClient

    client = PyPIClient()
    versions = []
    try:
        versions = [str(v) for v in client.get_ordered_versions(package_name) if str(v) in spec]
    except:
        logging.error("Package {} is not found on PyPI", package_name)
    return versions


def find_packages_missing_on_pypi(path: str) -> Iterable[str]:
    """
    Given a setup path, evaluate all dependencies and return a list of packages whos specifier can NOT be matched against PyPI releases.

    Import dependency on pkginfo.
    """

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
