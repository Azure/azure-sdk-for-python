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
            package_dir = parsed.folder
            package_name = parsed.name

            executable, staging_directory = self.get_executable(args.isolate, args.command, sys.executable, package_dir)
            logger.info(f"Processing {package_name} using interpreter {executable}")

            try:
                self._install_common_requirements(executable, package_dir)
                if self.should_install_dev_requirements():
                    self.install_dev_reqs(executable, args, package_dir)
                self.after_dependencies_installed(executable, package_dir, staging_directory, args)
            except CalledProcessError as exc:
                logger.error(f"Failed to prepare dependencies for {package_name}: {exc}")
                results.append(exc.returncode)
                continue

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
                results.append(1)
                continue

            try:
                self.before_pytest(executable, package_dir, staging_directory, args)
            except CalledProcessError as exc:
                logger.error(f"Pre-pytest hook failed for {package_name}: {exc}")
                results.append(exc.returncode or 1)
                continue

            pytest_args = self._build_pytest_args(package_dir, args)
            pytest_command = ["-m", "pytest", *pytest_args]
            pytest_result = self.run_venv_command(
                executable, pytest_command, cwd=staging_directory, immediately_dump=True
            )

            if pytest_result.returncode != 0:
                if pytest_result.returncode == 5 and is_error_code_5_allowed(package_dir, package_name):
                    logger.info(
                        "pytest exited with code 5 for %s, which is allowed for management or opt-out packages.",
                        package_name,
                    )
                    # Align with tox: skip coverage when tests are skipped entirely
                    continue
                else:
                    results.append(pytest_result.returncode)
                    logger.error(
                        f"pytest failed for {package_name} with exit code {pytest_result.returncode}."
                    )
                    continue

            if not self.coverage_enabled:
                continue

            coverage_command = [
                os.path.join(REPO_ROOT, "eng/tox/run_coverage.py"),
                "-t",
                package_dir,
                "-r",
                REPO_ROOT,
            ]
            coverage_result = self.run_venv_command(executable, coverage_command, cwd=package_dir)
            if coverage_result.returncode != 0:
                logger.error(
                    f"Coverage generation failed for {package_name} with exit code {coverage_result.returncode}."
                )
                if coverage_result.stdout:
                    logger.error(coverage_result.stdout)
                if coverage_result.stderr:
                    logger.error(coverage_result.stderr)
                results.append(coverage_result.returncode)

        return max(results) if results else 0

    def get_env_defaults(self) -> Dict[str, str]:
        defaults: Dict[str, str] = {}
        if self.proxy_url:
            defaults["PROXY_URL"] = self.proxy_url
        return defaults

    def should_install_dev_requirements(self) -> bool:
        return True

    def after_dependencies_installed(
        self, executable: str, package_dir: str, staging_directory: str, args: argparse.Namespace
    ) -> None:
        del executable, package_dir, staging_directory, args
        return None

    def before_pytest(
        self, executable: str, package_dir: str, staging_directory: str, args: argparse.Namespace
    ) -> None:
        del executable, package_dir, staging_directory, args
        return None

    def _install_common_requirements(self, executable: str, package_dir: str) -> None:
        install_into_venv(executable, PACKAGING_REQUIREMENTS, package_dir)

        if os.path.exists(TEST_TOOLS_REQUIREMENTS):
            install_into_venv(executable, ["-r", TEST_TOOLS_REQUIREMENTS], package_dir)
        else:
            logger.warning(f"Test tools requirements file not found at {TEST_TOOLS_REQUIREMENTS}.")

    def _build_pytest_args(self, package_dir: str, args: argparse.Namespace) -> List[str]:
        log_level = os.getenv("PYTEST_LOG_LEVEL", "51")
        junit_path = os.path.join(package_dir, f"test-junit-{args.command}.xml")

        default_args = [
            f"{package_dir}",
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

        pytest_args = [*default_args, *self.additional_pytest_args]

        if getattr(args, "pytest_args", None):
            pytest_args.extend(args.pytest_args)

        pytest_args.append(package_dir)

        return pytest_args
