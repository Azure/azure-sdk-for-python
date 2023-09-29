from typing import List, Any

import argparse
import os
import sys
import subprocess
import shutil

try:
    import tomllib as toml
except:
    import tomli as toml
import tomli_w as tomlw
import logging

from ci_tools.environment_exclusions import is_check_enabled
from ci_tools.variables import in_ci
from ci_tools.parsing import ParsedSetup
from ci_tools.functions import get_config_setting, discover_prebuilt_package
from ci_tools.build import cleanup_build_artifacts, create_package


def clean_environment():
    pass


def create_requirements_file(package_folder: str, optional_definition: str):
    pass


def install_requirements_file(package_folder: str):
    pass


def run_tests(package_folder: str):
    pass


def create_scenario_file(package_folder: str, optional_config: str) -> str:
    """
    Used to coalesce 3 items:
        - The package being installed
        - The dev_requirements for the package
        - An optional config, which includes possible additions to the install list

    And create a single file installable by `pip install -r <>`

    This file will be dropped into the package root, but gitignored. It is regenerated with every invocation of the `optional` env.
    """

def clean_test_environment(freeze_file: str) -> None:
    """
    Removes all packages within a freeze_file from a pip environment.
    """

    with open(freeze_file, 'r', encoding='utf-8') as f:
        f.readlines()


def replace_dev_reqs(file: str, pkg_root: str) -> None:
    """Takes a target requirements file, replaces all local relative install locations with wheels assembled from whatever that target path was.
    This is an extremely important step that runs on every dev_requirements.txt file before invoking any tox runs.
    
    This is due to the fact that pip isn't multi-process-safe with the activity of installing a local relative requirement. .pyc files are updated
    and removed in place, possibly causing a hang in the install process. When in_ci() is true, this function is run against every single requirement file.
    
    :param str file: the absolute path to the dev_requirements.txt file
    :param str pkg_root: the absolute path to the package's root
    :return: None
    """
    adjusted_req_lines = []

    with open(file, "r") as f:
        for line in f:
            args = [part.strip() for part in line.split() if part and not part.strip() == "-e"]
            amended_line = " ".join(args)

            if amended_line.endswith("]"):
                trim_amount = amended_line[::-1].index("[") + 1
                amended_line = amended_line[0 : (len(amended_line) - trim_amount)]

            adjusted_req_lines.append(amended_line)

    req_file_name = os.path.basename(file)
    logging.info("Old {0}:{1}".format(req_file_name, adjusted_req_lines))

    adjusted_req_lines = list(map(lambda x: build_whl_for_req(x, pkg_root), adjusted_req_lines))
    logging.info("New {0}:{1}".format(req_file_name, adjusted_req_lines))

    with open(file, "w") as f:
        # note that we directly use '\n' here instead of os.linesep due to how f.write() actually handles this stuff internally
        # If a file is opened in text mode (the default), during write python will accidentally double replace due to "\r" being
        # replaced with "\r\n" on Windows. Result: "\r\n\n". Extra line breaks!
        f.write("\n".join(adjusted_req_lines))


def discover_packages(setuppy_path, args):
    packages = []
    if os.getenv("PREBUILT_WHEEL_DIR") is not None and not args.force_create:
        packages = discover_prebuilt_package(os.getenv("PREBUILT_WHEEL_DIR"), setuppy_path, args.package_type)
        pkg = ParsedSetup.from_path(setuppy_path)

        if not packages:
            logging.error(
                "Package is missing in prebuilt directory {0} for package {1} and version {2}".format(
                    os.getenv("PREBUILT_WHEEL_DIR"), pkg.name, pkg.version
                )
            )
            exit(1)
    else:
        packages = build_and_discover_package(
            setuppy_path,
            args.distribution_directory,
            args.target_setup,
            args.package_type,
        )
    return packages


def build_and_install_dev_reqs(file: str, pkg_root: str) -> None:
    """This function builds whls for every requirement found in a package's
    dev_requirements.txt and installs each of them.

    :param str file: the absolute path to the dev_requirements.txt file
    :param str pkg_root: the absolute path to the package's root
    :return: None
    """
    adjusted_req_lines = []

    with open(file, "r") as f:
        for line in f:
            args = [part.strip() for part in line.split() if part and not part.strip() == "-e"]
            amended_line = " ".join(args)

            if amended_line.endswith("]"):
                trim_amount = amended_line[::-1].index("[") + 1
                amended_line = amended_line[0 : (len(amended_line) - trim_amount)]

            adjusted_req_lines.append(amended_line)

    adjusted_req_lines = list(map(lambda x: build_whl_for_req(x, pkg_root), adjusted_req_lines))
    install_deps_commands = [
        sys.executable,
        "-m",
        "pip",
        "install",
    ]
    logging.info(f"Installing dev requirements from freshly built packages: {adjusted_req_lines}")
    install_deps_commands.extend(adjusted_req_lines)
    subprocess.check_call(install_deps_commands)
    shutil.rmtree(os.path.join(pkg_root, ".tmp_whl_dir"))


def build_whl_for_req(req: str, package_path: str) -> str:
    """Builds a whl from the dev_requirements file.

    :param str req: a requirement from the dev_requirements.txt
    :param str package_path: the absolute path to the package's root
    :return: The absolute path to the whl built or the requirement if a third-party package
    """
    from ci_tools.build import create_package

    if ".." in req:
        # Create temp path if it doesn't exist
        temp_dir = os.path.join(package_path, ".tmp_whl_dir")
        if not os.path.exists(temp_dir):
            os.mkdir(temp_dir)

        req_pkg_path = os.path.abspath(os.path.join(package_path, req.replace("\n", "")))
        parsed = ParsedSetup.from_path(req_pkg_path)

        logging.info("Building wheel for package {}".format(parsed.name))
        create_package(req_pkg_path, temp_dir, enable_sdist=False)

        whl_path = os.path.join(temp_dir, find_whl(temp_dir, parsed.name, parsed.version))
        logging.info("Wheel for package {0} is {1}".format(parsed.name, whl_path))
        logging.info("Replacing dev requirement. Old requirement:{0}, New requirement:{1}".format(req, whl_path))
        return whl_path
    else:
        return req


def build_and_discover_package(setuppy_path: str, dist_dir: str, target_setup: str, package_type):
    if package_type == "wheel":
        create_package(setuppy_path, dist_dir, enable_sdist=False)
    else:
        create_package(setuppy_path, dist_dir, enable_wheel=False)

    prebuilt_packages = [
        f for f in os.listdir(dist_dir) if f.endswith(".whl" if package_type == "wheel" else ".tar.gz")
    ]

    if not in_ci():
        logging.info("Cleaning up build directories and files")
        cleanup_build_artifacts(target_setup)
    return prebuilt_packages


def main(mapped_args: argparse.Namespace) -> int:
    parsed_package = ParsedSetup.from_path(mapped_args.target)

    if in_ci():
        if not is_check_enabled(mapped_args.target, "optional", False):
            logging.info(f"Package {parsed_package.package_name} opts-out of optional check.")
            return 0

    optional_configs = get_config_setting(mapped_args.target, "optional")

    if len(optional_configs) == 0:
        logging.info(f"No optional environments detected in pyproject.toml within {mapped_args.target}.")
        return 0

    for config in optional_configs:
        # clean if necessary
        clean_environment(mapped_args.target)

        # install package, dev_reqs, and any additional packages from optional configuration


        # uninstall anything additional
        breakpoint()


def entrypoint():
    parser = argparse.ArgumentParser(
        description="""This entrypoint provides automatic invocation of the 'optional' requirements for a given package. View the pyproject.toml within the targeted package folder to see configuration.""",
    )

    parser.add_argument("-t", "--target", dest="target", help="The target package path", required=True)

    parser.add_argument(
        "-o",
        "--optional",
        dest="optional",
        help="The target environment. If not matched to any of the named optional environments, hard exit. If not provided, all optional environments will be run.",
        required=False,
    )

    parser.add_argument(
        "--temp",
        dest="temp_dir",
        help="The target environment. If not matched to any of the named optional environments, hard exit. If not provided, all optional environments will be run.",
        required=False,
    )

    args, _ = parser.parse_known_args()
    exit(main(mapped_args=args))
