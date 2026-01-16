import argparse
import os
from subprocess import CalledProcessError
import sys

from typing import Optional, List

from .install_and_test import InstallAndTest
from ci_tools.functions import (
    install_into_venv,
    uninstall_from_venv,
)
from ci_tools.scenario.generation import prepare_environment
from ci_tools.variables import discover_repo_root, set_envvar_defaults
from ci_tools.parsing import get_config_setting
from ci_tools.logging import logger

REPO_ROOT = discover_repo_root()


class optional(InstallAndTest):
    def __init__(self) -> None:
        super().__init__(package_type="sdist", proxy_url="http://localhost:5004", display_name="optional")

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

        env_defaults = self.get_env_defaults()
        if env_defaults:
            set_envvar_defaults(env_defaults)

        targeted = self.get_targeted_directories(args)
        if not targeted:
            logger.warning("No target packages discovered for optional check.")
            return 0

        results: List[int] = []

        for parsed in targeted:
            package_dir = parsed.folder
            package_name = parsed.name
            executable, staging_directory = self.get_executable(args.isolate, args.command, sys.executable, package_dir)
            logger.info(f"Processing {package_name} using interpreter {executable}")

            try:
                result = self.prepare_and_test_optional(
                    package_name, package_dir, staging_directory, args.optional, args
                )
                if result != 0:
                    results.append(result)
            except Exception as e:
                logger.error(f"Optional check for package {package_name} failed with exception: {e}")
                results.append(1)
                continue

        return max(results) if results else 0

    # TODO copying from generation.py, remove old code later
    # TODO remove pytest() function from ci_tools.functions as it was only used in the old version of this logic
    def prepare_and_test_optional(
        self, package_name: str, package_dir: str, temp_dir: str, target_env_name: str, args: argparse.Namespace
    ) -> int:
        """
        Prepare and test the optional environment for the given package.
        """
        optional_configs = get_config_setting(package_dir, "optional")

        if not isinstance(optional_configs, list):
            optional_configs = []

        if len(optional_configs) == 0:
            logger.info(f"No optional environments detected in pyproject.toml within {package_dir}.")
            return 0

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

            # install package and testing requirements
            try:
                install_result = self.install_all_requirements(
                    environment_exe, temp_dir, package_name, package_dir, args
                )
                if install_result != 0:
                    logger.error(f"Failed to install base requirements for {package_name} in optional env {env_name}.")
                    config_results.append(False)
                    break
            except CalledProcessError as exc:
                logger.error(
                    f"Failed to install base requirements for {package_name} in optional env {env_name}: {exc}"
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

            try:
                pytest_result = self.run_pytest(
                    environment_exe, temp_dir, package_dir, package_name, pytest_args, cwd=package_dir
                )
                config_results.append(True if pytest_result == 0 else False)
            except CalledProcessError as exc:
                config_results.append(False)

        if all(config_results):
            logger.info(f"All optional environment(s) for {package_name} completed successfully.")
        else:
            for i, config in enumerate(optional_configs):
                if i >= len(config_results):
                    break
                if not config_results[i]:
                    config_name = config.get("name")
                    logger.error(
                        f"Optional environment {config_name} for {package_name} completed with non-zero exit-code. Check test results above."
                    )
            return 1
        return 0
