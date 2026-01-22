import argparse
import os
from subprocess import CalledProcessError
import sys

from typing import Optional, List

from .Check import Check
from ci_tools.functions import (
    install_into_venv,
    uninstall_from_venv,
    is_error_code_5_allowed,
)
from ci_tools.scenario.generation import create_package_and_install, prepare_environment
from ci_tools.variables import discover_repo_root, in_ci, set_envvar_defaults
from ci_tools.environment_exclusions import is_check_enabled
from ci_tools.parsing import get_config_setting
from ci_tools.logging import logger

REPO_ROOT = discover_repo_root()


class optional(Check):
    def __init__(self) -> None:
        super().__init__()

    def register(
        self, subparsers: "argparse._SubParsersAction", parent_parsers: Optional[List[argparse.ArgumentParser]] = None
    ) -> None:
        """Register the optional check. The optional check invokes 'optional' requirements for a given package. View the pyproject.toml within the targeted package folder to see configuration."""
        parents = parent_parsers or []
        p = subparsers.add_parser(
            "optional",
            parents=parents,
            help="Run the optional check to invoke 'optional' requirements for a given package.",
        )
        p.set_defaults(func=self.run)

        p.add_argument(
            "-o",
            "--optional",
            dest="optional",
            help="The target environment. If not provided, all optional environments will be run.",
            required=False,
        )

    def run(self, args: argparse.Namespace) -> int:
        """Run the optional check command."""
        logger.info("Running optional check...")

        set_envvar_defaults({"PROXY_URL": "http://localhost:5004"})
        targeted = self.get_targeted_directories(args)

        results: List[int] = []

        for parsed in targeted:
            package_dir = parsed.folder
            package_name = parsed.name
            executable, staging_directory = self.get_executable(args.isolate, args.command, sys.executable, package_dir)
            logger.info(f"Processing {package_name} for optional check")

            if in_ci():
                if not is_check_enabled(package_dir, "optional", False):
                    logger.info(f"Package {package_name} opts-out of optional check.")
                    continue

            try:
                self.install_dev_reqs(executable, args, package_dir)
            except CalledProcessError as exc:
                logger.error(f"Failed to install dependencies for {package_name}: {exc}")
                results.append(exc.returncode)
                continue

            try:
                self.prepare_and_test_optional(package_name, package_dir, staging_directory, args.optional)
            except Exception as e:
                logger.error(f"Optional check for package {package_name} failed with exception: {e}")
                results.append(1)
                continue

        return max(results) if results else 0

    # TODO copying from generation.py, remove old code later
    # TODO remove pytest() function from ci_tools.functions as it was only used in the old version of this logic
    def prepare_and_test_optional(
        self, package_name: str, package_dir: str, temp_dir: str, target_env_name: str
    ) -> None:
        """
        Prepare and test the optional environment for the given package.
        """
        optional_configs = get_config_setting(package_dir, "optional")

        if len(optional_configs) == 0:
            logger.info(f"No optional environments detected in pyproject.toml within {package_dir}.")
            exit(0)

        config_results = []

        for config in optional_configs:
            env_name = config.get("name")

            if target_env_name:
                if env_name != target_env_name:
                    logger.info(
                        f"{env_name} does not match targeted environment {target_env_name}, skipping this environment."
                    )
                    config_results.append(True)
                    continue

            environment_exe = prepare_environment(package_dir, temp_dir, env_name)

            create_package_and_install(
                distribution_directory=temp_dir,
                target_setup=package_dir,
                skip_install=False,
                cache_dir=None,
                work_dir=temp_dir,
                force_create=False,
                package_type="sdist",
                pre_download_disabled=False,
                python_executable=environment_exe,
            )
            dev_reqs = os.path.join(package_dir, "dev_requirements.txt")
            test_tools = os.path.join(REPO_ROOT, "eng", "test_tools.txt")

            # install the dev requirements and test_tools requirements files to ensure tests can run
            try:
                install_into_venv(environment_exe, ["-r", dev_reqs, "-r", test_tools], package_dir)
            except CalledProcessError as exc:
                logger.error(
                    f"Unable to complete installation of dev_requirements.txt and/or test_tools.txt for {package_name}, check command output above."
                )
                config_results.append(False)
                break

            # install any packages that are added in the optional config
            additional_installs = config.get("install", [])
            if additional_installs:
                try:
                    install_into_venv(environment_exe, additional_installs, package_dir)
                except CalledProcessError as exc:
                    logger.error(
                        f"Unable to complete installation of additional packages {additional_installs} for {package_name}, check command output above."
                    )
                    config_results.append(False)
                    break

            # uninstall any configured packages from the optional config
            additional_uninstalls = config.get("uninstall", [])
            if additional_uninstalls:
                try:
                    uninstall_from_venv(environment_exe, additional_uninstalls, package_dir)
                except CalledProcessError as exc:
                    logger.error(
                        f"Unable to complete removal of packages targeted for uninstall {additional_uninstalls} for {package_name}, check command output above."
                    )
                    config_results.append(False)
                    break

            self.pip_freeze(environment_exe)

            # invoke tests
            log_level = os.getenv("PYTEST_LOG_LEVEL", "51")
            junit_path = os.path.join(package_dir, f"test-junit-optional-{env_name}.xml")

            pytest_args = [
                "-rsfE",
                f"--junitxml={junit_path}",
                "--verbose",
                "--cov-branch",
                "--durations=10",
                "--ignore=azure",
                "--ignore=.tox",
                "--ignore-glob=.venv*",
                "--ignore=build",
                "--ignore=.eggs",
                "--ignore=samples",
                f"--log-cli-level={log_level}",
            ]
            pytest_args.extend(config.get("additional_pytest_args", []))

            logger.info(f"Invoking tests for package {package_name} and optional environment {env_name}")

            pytest_command = ["-m", "pytest", *pytest_args]
            pytest_result = self.run_venv_command(
                environment_exe, pytest_command, cwd=package_dir, immediately_dump=True
            )

            if pytest_result.returncode != 0:
                if pytest_result.returncode == 5 and is_error_code_5_allowed(package_dir, package_name):
                    logger.info(
                        "pytest exited with code 5 for %s, which is allowed for management or opt-out packages.",
                        package_name,
                    )
                    # Align with tox: skip coverage when tests are skipped entirely
                    continue
                logger.error(
                    f"pytest failed for {package_name} and optional environment {env_name} with exit code {pytest_result.returncode}."
                )
                config_results.append(False)
            else:
                logger.info(f"pytest succeeded for {package_name} and optional environment {env_name}.")
                config_results.append(True)

        if all(config_results):
            logger.info(f"All optional environment(s) for {package_name} completed successfully.")
            exit(0)
        else:
            for i, config in enumerate(optional_configs):
                if i >= len(config_results):
                    break
                if not config_results[i]:
                    config_name = config.get("name")
                    logger.error(
                        f"Optional environment {config_name} for {package_name} completed with non-zero exit-code. Check test results above."
                    )
            exit(1)
