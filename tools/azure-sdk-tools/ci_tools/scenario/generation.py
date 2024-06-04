import argparse
import os
import sys
import subprocess
import shutil
import logging
from typing import Optional

from ci_tools.environment_exclusions import is_check_enabled
from ci_tools.variables import in_ci
from ci_tools.parsing import ParsedSetup
from ci_tools.functions import (
    get_config_setting,
    discover_prebuilt_package,
    pip_install,
    pip_uninstall,
)
from ci_tools.build import cleanup_build_artifacts, create_package
from ci_tools.parsing import ParsedSetup, parse_require
from ci_tools.functions import get_package_from_repo_or_folder, find_whl, get_pip_list_output, pytest
from .managed_virtual_env import ManagedVirtualEnv


def prepare_environment(package_folder: str, venv_directory: str, env_name: str) -> str:
    """
    Empties the venv_directory directory and creates a virtual environment within. Returns the path to the new python executable.
    """
    venv = ManagedVirtualEnv(venv_directory, env_name)
    venv.create()

    return venv.python_executable


def create_package_and_install(
    distribution_directory: str,
    target_setup: str,
    skip_install: bool,
    cache_dir: str,
    work_dir: str,
    force_create: bool,
    package_type: str,
    pre_download_disabled: bool,
    python_executable: str = None,
) -> None:
    """
    Workhorse for singular package installation given a package and a possible prebuilt wheel directory. Handles installation of both package AND dependencies, handling compatibility
    issues where possible.
    """

    python_exe = python_executable or sys.executable

    commands_options = []
    built_pkg_path = ""
    setup_py_path = os.path.join(target_setup, "setup.py")
    additional_downloaded_reqs = []

    if not os.path.exists(distribution_directory):
        os.mkdir(distribution_directory)

    tmp_dl_folder = os.path.join(distribution_directory, "dl")
    if not os.path.exists(tmp_dl_folder):
        os.mkdir(tmp_dl_folder)

    # preview version is enabled when installing dev build so pip will install dev build version from devpos feed
    if os.getenv("SetDevVersion", "false") == "true":
        commands_options.append("--pre")

    if cache_dir:
        commands_options.extend(["--cache-dir", cache_dir])

    discovered_packages = discover_packages(
        setup_py_path, distribution_directory, target_setup, package_type, force_create
    )

    target_package = ParsedSetup.from_path(setup_py_path)

    # ensure that discovered packages are always copied to the distribution directory regardless of other factors
    for built_package in discovered_packages:
        if os.getenv("PREBUILT_WHEEL_DIR") is not None:
            package_path = os.path.join(os.environ["PREBUILT_WHEEL_DIR"], built_package)
            if os.path.isfile(package_path):
                built_pkg_path = package_path

                # copy this file to the distribution directory just in case we need it later
                shutil.copy(built_pkg_path, distribution_directory)

    if skip_install:
        logging.info("Flag to skip install whl is passed. Skipping package installation")
    else:
        for built_package in discovered_packages:
            if os.getenv("PREBUILT_WHEEL_DIR") is not None and not force_create:
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
                built_pkg_path = os.path.abspath(os.path.join(distribution_directory, built_package))
                logging.info("Installing {w} from fresh built package.".format(w=built_package))

            if not pre_download_disabled:
                requirements = ParsedSetup.from_path(os.path.join(os.path.abspath(target_setup), "setup.py")).requires
                azure_requirements = [req.split(";")[0] for req in requirements if req.startswith("azure-")]

                if azure_requirements:
                    logging.info(
                        "Found {} azure requirement(s): {}".format(len(azure_requirements), azure_requirements)
                    )

                    download_command = [
                        python_exe,
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
                        installed_pkgs = get_pip_list_output(python_exe)
                        logging.info("Installed packages: {}".format(installed_pkgs))

                        # parse the specifier
                        req_name, req_specifier = parse_require(req)

                        # if we have the package already present...
                        if req_name in installed_pkgs:
                            # if there is no specifier for the requirement, we can ignore it
                            if req_specifier is None:
                                addition_necessary = False

                            # ...do we need to install the new version? if the existing specifier matches, we're fine
                            if req_specifier is not None and installed_pkgs[req_name] in req_specifier:
                                addition_necessary = False

                        if addition_necessary:
                            # we only want to add an additional rec for download if it actually exists
                            # in the upstream feed (either dev or pypi)
                            # if it doesn't, we should just install the relative dep if its an azure package
                            installation_additions.append(req)

                    if installation_additions:
                        non_present_reqs = []
                        for addition in installation_additions:
                            try:
                                subprocess.check_call(
                                    download_command + [addition] + commands_options,
                                    env=dict(os.environ, PIP_EXTRA_INDEX_URL=""),
                                )
                            except subprocess.CalledProcessError as e:
                                req_name, req_specifier = parse_require(addition)
                                non_present_reqs.append(req_name)

                        additional_downloaded_reqs = [
                            os.path.abspath(os.path.join(tmp_dl_folder, pth)) for pth in os.listdir(tmp_dl_folder)
                        ] + [
                            get_package_from_repo_or_folder(
                                package_name, os.path.join(target_package.folder, ".tmp_whl_dir")
                            )
                            for package_name in non_present_reqs
                        ]

            commands = [python_exe, "-m", "pip", "install", built_pkg_path]
            commands.extend(additional_downloaded_reqs)
            commands.extend(commands_options)

            if work_dir and os.path.exists(work_dir):
                logging.info("Executing command from {0}:{1}".format(work_dir, commands))
                subprocess.check_call(commands, cwd=work_dir)
            else:
                subprocess.check_call(commands)
            logging.info("Installed {w}".format(w=built_package))


def replace_dev_reqs(file: str, pkg_root: str, wheel_dir: Optional[str]) -> None:
    """Takes a target requirements file, replaces all local relative install locations with wheels assembled from whatever that target path was.
    This is an extremely important step that runs on every dev_requirements.txt file before invoking any tox runs.

    This is due to the fact that pip isn't multi-process-safe with the activity of installing a local relative requirement. .pyc files are updated
    and removed in place, possibly causing a hang in the install process. When in_ci() is true, this function is run against every single requirement file.

    :param str file: the absolute path to the dev_requirements.txt file
    :param str pkg_root: the absolute path to the package's root
    :param Optional[str] wheel_dir: the absolute path to the prebuilt wheel directory
    :return: None
    """
    adjusted_req_lines = []

    with open(file, "r") as f:
        original_req_lines = list(line.strip() for line in f)

    for line in original_req_lines:
        args = [part.strip() for part in line.split() if part and not part.strip() == "-e"]
        amended_line = " ".join(args)
        extras = ""

        if amended_line.endswith("]"):
            amended_line, extras = amended_line.rsplit("[", maxsplit=1)
            if extras:
                extras = f"[{extras}"

        adjusted_req_lines.append(f"{build_whl_for_req(amended_line, pkg_root, wheel_dir)}{extras}")

    req_file_name = os.path.basename(file)
    logging.info("Old {0}:{1}".format(req_file_name, original_req_lines))
    logging.info("New {0}:{1}".format(req_file_name, adjusted_req_lines))

    with open(file, "w") as f:
        # note that we directly use '\n' here instead of os.linesep due to how f.write() actually handles this stuff internally
        # If a file is opened in text mode (the default), during write python will accidentally double replace due to "\r" being
        # replaced with "\r\n" on Windows. Result: "\r\n\n". Extra line breaks!
        f.write("\n".join(adjusted_req_lines))


def discover_packages(
    setup_path: str, distribution_directory: str, target_setup: str, package_type: str, force_create: bool
):
    packages = []
    if os.getenv("PREBUILT_WHEEL_DIR") is not None and not force_create:
        packages = discover_prebuilt_package(os.getenv("PREBUILT_WHEEL_DIR"), setup_path, package_type)
        pkg = ParsedSetup.from_path(setup_path)

        if not packages:
            logging.error(
                "Package is missing in prebuilt directory {0} for package {1} and version {2}".format(
                    os.getenv("PREBUILT_WHEEL_DIR"), pkg.name, pkg.version
                )
            )
            exit(1)
    else:
        packages = build_and_discover_package(
            setup_path,
            distribution_directory,
            target_setup,
            package_type,
        )
    return packages


def build_and_install_dev_reqs(file: str, pkg_root: str) -> None:
    """This function builds whls for every requirement found in a package's
    dev_requirements.txt and installs it.

    :param str file: the absolute path to the dev_requirements.txt file
    :param str pkg_root: the absolute path to the package's root
    :return: None
    """
    adjusted_req_lines = []

    with open(file, "r") as f:
        for line in f:
            # Remove inline comments which are denoted by a "#".
            line = line.split("#")[0].strip()
            if not line:
                continue

            args = [part.strip() for part in line.split() if part and not part.strip() == "-e"]
            amended_line = " ".join(args)

            if amended_line.endswith("]"):
                trim_amount = amended_line[::-1].index("[") + 1
                amended_line = amended_line[0 : (len(amended_line) - trim_amount)]

            adjusted_req_lines.append(amended_line)

    adjusted_req_lines = list(map(lambda x: build_whl_for_req(x, pkg_root, None), adjusted_req_lines))
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


def is_relative_install_path(req: str, package_path: str) -> bool:
    possible_setup_path = os.path.join(package_path, req, "setup.py")

    # blank lines are _allowed_ in a dev requirements. they should not resolve to the package_path erroneously
    if not req:
        return False

    return os.path.exists(possible_setup_path)


def build_whl_for_req(req: str, package_path: str, wheel_dir: Optional[str]) -> str:
    """Builds a whl from the dev_requirements file.

    :param str req: a requirement from the dev_requirements.txt
    :param str package_path: the absolute path to the package's root
    :param Optional[str] wheel_dir: the absolute path to the prebuilt wheel directory
    :return: The absolute path to the whl built or the requirement if a third-party package
    """
    from ci_tools.build import create_package

    if is_relative_install_path(req, package_path):
        req_pkg_path = os.path.abspath(os.path.join(package_path, req.replace("\n", "")))
        parsed = ParsedSetup.from_path(req_pkg_path)

        # First check for prebuilt wheel
        logging.info("Checking for prebuilt wheel for package {}".format(parsed.name))
        prebuilt_whl = None
        if wheel_dir:
            prebuilt_whl = find_whl(wheel_dir, parsed.name, parsed.version)

        if prebuilt_whl:
            whl_path = os.path.join(wheel_dir, prebuilt_whl)
        else:
            # Create temp path if it doesn't exist
            temp_dir = os.path.join(package_path, ".tmp_whl_dir")
            if not os.path.exists(temp_dir):
                os.mkdir(temp_dir)

            logging.info("Building wheel for package {}".format(parsed.name))
            create_package(req_pkg_path, temp_dir, enable_sdist=False)

            whl_path = os.path.join(temp_dir, find_whl(temp_dir, parsed.name, parsed.version))

        logging.info("Wheel for package {0} is {1}".format(parsed.name, whl_path))
        logging.info("Replacing dev requirement. Old requirement: {0}, New requirement: {1}".format(req, whl_path))
        return whl_path
    else:
        return req


def build_and_discover_package(setup_path: str, dist_dir: str, target_setup: str, package_type):
    if package_type == "wheel":
        create_package(setup_path, dist_dir, enable_sdist=False)
    else:
        create_package(setup_path, dist_dir, enable_wheel=False)

    prebuilt_packages = [
        f for f in os.listdir(dist_dir) if f.endswith(".whl" if package_type == "wheel" else ".tar.gz")
    ]

    if not in_ci():
        logging.info("Cleaning up build directories and files")
        cleanup_build_artifacts(target_setup)
    return prebuilt_packages


def prepare_and_test_optional(mapped_args: argparse.Namespace) -> int:
    parsed_package = ParsedSetup.from_path(mapped_args.target)

    if in_ci():
        if not is_check_enabled(mapped_args.target, "optional", False):
            logging.info(f"Package {parsed_package.name} opts-out of optional check.")
            return 0

    optional_configs = get_config_setting(mapped_args.target, "optional")

    if len(optional_configs) == 0:
        logging.info(f"No optional environments detected in pyproject.toml within {mapped_args.target}.")
        return 0

    config_results = []

    for config in optional_configs:
        env_name = config.get("name")

        if mapped_args.optional:
            if env_name != mapped_args.optional:
                logging.info(
                    f"{env_name} does not match targeted environment {mapped_args.optional}, skipping this environment."
                )
                continue

        environment_exe = prepare_environment(mapped_args.target, mapped_args.temp_dir, env_name)

        # install the package (either building manually or pulling from prebuilt directory)
        create_package_and_install(
            distribution_directory=mapped_args.temp_dir,
            target_setup=mapped_args.target,
            skip_install=False,
            cache_dir=None,  # todo, resolve this for CI builds
            work_dir=mapped_args.temp_dir,
            force_create=False,
            package_type="wheel",
            pre_download_disabled=False,
            python_executable=environment_exe,
        )

        dev_reqs = os.path.join(mapped_args.target, "dev_requirements.txt")
        test_tools = os.path.join(mapped_args.target, "..", "..", "..", "eng", "test_tools.txt")

        # install the dev requirements and test_tools requirements files to ensure tests can run
        install_result = pip_install(["-r", dev_reqs, "-r", test_tools], python_executable=environment_exe)
        if not install_result:
            logging.error(
                f"Unable to complete installation of dev_requirements.txt/ci_tools.txt for {parsed_package.name}, check command output above."
            )
            config_results.append(False)
            break

        # install any packages that are added in the optional config
        additional_installs = config.get("install", [])
        install_result = pip_install(additional_installs, python_executable=environment_exe)
        if not install_result:
            logging.error(
                f"Unable to complete installation of additional packages {additional_installs} for {parsed_package.name}, check command output above."
            )
            config_results.append(False)
            break

        # uninstall any configured packages from the optional config
        additional_uninstalls = config.get("uninstall", [])
        uninstall_result = pip_uninstall(additional_uninstalls, python_executable=environment_exe)
        if not uninstall_result:
            logging.error(
                f"Unable to complete removal of packages targeted for uninstall {additional_uninstalls} for {parsed_package.name}, check command output above."
            )
            config_results.append(False)
            break

        # invoke tests
        pytest_args = [
            "-rsfE",
            f"--junitxml={mapped_args.target}/test-junit-optional-{env_name}.xml",
            "--verbose",
            "--durations=10",
            "--ignore=azure",
            "--ignore=.tox",
            "--ignore=build",
            "--ignore=.eggs",
            mapped_args.target,
        ]
        pytest_args.extend(config.get("additional_pytest_args", []))
        logging.info(f"Invoking tests for package {parsed_package.name} and optional environment {env_name}")
        config_results.append(pytest(pytest_args, python_executable=environment_exe))

    if all(config_results):
        logging.info(f"All optional environment(s) for {parsed_package.name} completed successfully.")
        sys.exit(0)
    else:
        for i, config in enumerate(optional_configs):
            if not config_results[i]:
                config_name = config.get("name")
                logging.error(
                    f"Optional environment {config_name} for {parsed_package.name} completed with non-zero exit-code. Check test results above."
                )
        sys.exit(1)
