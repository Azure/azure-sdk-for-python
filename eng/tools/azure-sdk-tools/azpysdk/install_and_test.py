import argparse
import os
import sys
from subprocess import CalledProcessError
from typing import Dict, List, Optional

from .Check import Check, DEPENDENCY_TOOLS_REQUIREMENTS, PACKAGING_REQUIREMENTS, TEST_TOOLS_REQUIREMENTS

from ci_tools.functions import is_error_code_5_allowed, install_into_venv
from ci_tools.scenario.generation import create_package_and_install
from ci_tools.variables import discover_repo_root, set_envvar_defaults
from ci_tools.logging import logger

REPO_ROOT = discover_repo_root()


class InstallAndTest(Check):
    """Shared implementation for build-and-test style checks."""

    def __init__(
        self,
        *,
        package_type: str,
        proxy_url: Optional[str],
        display_name: str,
        additional_pytest_args: Optional[List[str]] = None,
        coverage_enabled: bool = True,
    ) -> None:
        super().__init__()
        self.package_type = package_type
        self.proxy_url = proxy_url
        self.display_name = display_name
        self.additional_pytest_args = list(additional_pytest_args or [])
        self.coverage_enabled = coverage_enabled

    def register(
        self, subparsers: "argparse._SubParsersAction", parent_parsers: Optional[List[argparse.ArgumentParser]] = None
    ) -> None:
        raise NotImplementedError

    def run(self, args: argparse.Namespace) -> int:
        logger.info(f"Running {self.display_name} check...")

        env_defaults = self.get_env_defaults()
        if env_defaults:
            set_envvar_defaults(env_defaults)

        targeted = self.get_targeted_directories(args)
        if not targeted:
            logger.warning(f"No target packages discovered for {self.display_name} check.")
            return 0

        results: List[int] = []

        for parsed in targeted:
            if os.getcwd() != parsed.folder:
                os.chdir(parsed.folder)
            package_dir = parsed.folder
            package_name = parsed.name

            executable, staging_directory = self.get_executable(args.isolate, args.command, sys.executable, package_dir)
            logger.info(f"Processing {package_name} using interpreter {executable}")

            install_result = self.install_all_requirements(
                executable, staging_directory, package_name, package_dir, args
            )
            if install_result != 0:
                results.append(install_result)
                continue

            pytest_args = self._build_pytest_args(package_dir, args)
            pytest_result = self.run_pytest(executable, staging_directory, package_dir, package_name, pytest_args)
            if pytest_result != 0:
                results.append(pytest_result)
                continue

            if not self.coverage_enabled:
                continue

            coverage_result = self.check_coverage(executable, package_dir, package_name)
            if coverage_result != 0:
                results.append(coverage_result)

        return max(results) if results else 0

    def check_coverage(self, executable: str, package_dir: str, package_name: str) -> int:
        coverage_command = [
            os.path.join(REPO_ROOT, "eng/tox/run_coverage.py"),
            "-t",
            package_dir,
            "-r",
            REPO_ROOT,
        ]
        coverage_result = self.run_venv_command(executable, coverage_command, cwd=package_dir)
        if coverage_result.returncode != 0:
            logger.error(f"Coverage generation failed for {package_name} with exit code {coverage_result.returncode}.")
            if coverage_result.stdout:
                logger.error(coverage_result.stdout)
            if coverage_result.stderr:
                logger.error(coverage_result.stderr)
            return coverage_result.returncode
        return 0

    def run_pytest(
        self, executable: str, staging_directory: str, package_dir: str, package_name: str, pytest_args: List[str]
    ) -> int:
        pytest_command = ["pytest", *pytest_args]

        environment = os.environ.copy()
        environment.update({"PYTHONPYCACHEPREFIX": staging_directory})

        logger.info(f"Running pytest for {package_name} with command: {pytest_command}")
        logger.debug(f"with environment vars: {environment}")

        pytest_result = self.run_venv_command(
            executable,
            pytest_command,
            cwd=package_dir,
            immediately_dump=True,
            additional_environment_settings=environment,
            append_executable=False,
        )
        if pytest_result.returncode != 0:
            if pytest_result.returncode == 5 and is_error_code_5_allowed(package_dir, package_name):
                logger.info(
                    "pytest exited with code 5 for %s, which is allowed for management or opt-out packages.",
                    package_name,
                )
                # Align with tox: skip coverage when tests are skipped entirely
                return 0
            else:
                logger.error(f"pytest failed for {package_name} with exit code {pytest_result.returncode}.")
                return pytest_result.returncode
        return 0

    def install_all_requirements(
        self, executable: str, staging_directory: str, package_name: str, package_dir: str, args: argparse.Namespace
    ) -> int:
        try:
            self._install_common_requirements(executable, package_dir)
            if self.should_install_dev_requirements():
                self.install_dev_reqs(executable, args, package_dir)
        except CalledProcessError as exc:
            logger.error(f"Failed to prepare dependencies for {package_name}: {exc}")
            return exc.returncode or 1

        try:
            create_package_and_install(
                distribution_directory=staging_directory,
                target_setup=package_dir,
                skip_install=False,
                cache_dir=None,
                work_dir=staging_directory,
                force_create=False,
                package_type=self.package_type,
                pre_download_disabled=False,
                python_executable=executable,
            )
        except CalledProcessError as exc:
            logger.error(f"Failed to build/install {self.package_type} for {package_name}: {exc}")
            return 1
        return 0

    def get_env_defaults(self) -> Dict[str, str]:
        defaults: Dict[str, str] = {}

        if os.getenv("PROXY_URL") is not None:
            defaults["PROXY_URL"] = str(os.getenv("PROXY_URL"))
        if self.proxy_url:
            defaults["PROXY_URL"] = self.proxy_url
        return defaults

    def should_install_dev_requirements(self) -> bool:
        return True

    def _install_common_requirements(self, executable: str, package_dir: str) -> None:
        install_into_venv(executable, PACKAGING_REQUIREMENTS, package_dir)

        if os.path.exists(TEST_TOOLS_REQUIREMENTS):
            install_into_venv(executable, ["-r", TEST_TOOLS_REQUIREMENTS], package_dir)
        else:
            logger.warning(f"Test tools requirements file not found at {TEST_TOOLS_REQUIREMENTS}.")

    def _build_pytest_args(self, package_dir: str, args: argparse.Namespace) -> List[str]:
        return self._build_pytest_args_base(
            package_dir,
            args,
            ignore_globs=["**/.venv*", "**/.venv*/**"],
            extra_args=self.additional_pytest_args,
            test_target=package_dir,
        )
