import argparse
import os
import sys
from subprocess import CalledProcessError
from typing import Dict, List, Optional

from .Check import Check, DEPENDENCY_TOOLS_REQUIREMENTS, PACKAGING_REQUIREMENTS, TEST_TOOLS_REQUIREMENTS

from ci_tools.functions import install_into_venv, is_error_code_5_allowed
from ci_tools.scenario.generation import create_package_and_install
from ci_tools.scenario.dependency_resolution import install_dependent_packages
from ci_tools.variables import discover_repo_root, set_envvar_defaults
from ci_tools.logging import logger

REPO_ROOT = discover_repo_root()


class DependencyCheck(Check):
    """Shared implementation for dependency bound test environments."""

    def __init__(
        self,
        *,
        dependency_type: str,
        proxy_url: Optional[str],
        display_name: str,
        additional_packages: Optional[List[str]] = None,
    ) -> None:
        super().__init__()
        self.dependency_type = dependency_type
        self.proxy_url = proxy_url
        self.display_name = display_name
        self.additional_packages = list(additional_packages or [])

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
                self._install_dependency_requirements(executable, package_dir)
            except CalledProcessError as exc:
                logger.error(f"Failed to install base dependencies for {package_name}: {exc}")
                results.append(exc.returncode)
                continue

            try:
                install_dependent_packages(
                    setup_py_file_path=package_dir,
                    dependency_type=self.dependency_type,
                    temp_dir=staging_directory,
                    python_executable=executable,
                )
            except Exception as exc:  # pragma: no cover - defensive logging
                logger.error(f"Dependency resolution failed for {package_name}: {exc}")
                results.append(1)
                continue

            try:
                create_package_and_install(
                    distribution_directory=staging_directory,
                    target_setup=package_dir,
                    skip_install=False,
                    cache_dir=None,
                    work_dir=staging_directory,
                    force_create=False,
                    package_type="wheel",
                    pre_download_disabled=True,
                    python_executable=executable,
                )
            except CalledProcessError as exc:
                logger.error(f"Failed to build/install wheel for {package_name}: {exc}")
                results.append(1)
                continue

            self.pip_freeze(executable)

            if not self._verify_installed_packages(executable, package_dir, staging_directory):
                results.append(1)
                continue

            pytest_args = self._build_pytest_args(package_dir, args)
            pytest_command = ["-m", "pytest", *pytest_args]
            pytest_result = self.run_venv_command(
                executable,
                pytest_command,
                cwd=staging_directory,
                immediately_dump=True,
            )

            if pytest_result.returncode != 0:
                if pytest_result.returncode == 5 and is_error_code_5_allowed(package_dir, package_name):
                    logger.info(
                        "pytest exited with code 5 for %s, which is allowed for management or opt-out packages.",
                        package_name,
                    )
                    continue
                logger.error(
                    f"pytest failed for {package_name} with exit code {pytest_result.returncode}."
                )
                results.append(pytest_result.returncode)

        return max(results) if results else 0

    def get_env_defaults(self) -> Dict[str, str]:
        defaults: Dict[str, str] = {"DEPENDENCY_TYPE": self.dependency_type}
        if self.proxy_url:
            defaults["PROXY_URL"] = self.proxy_url
        return defaults

    def _install_dependency_requirements(self, executable: str, package_dir: str) -> None:
        install_into_venv(executable, PACKAGING_REQUIREMENTS, package_dir)

        if os.path.exists(DEPENDENCY_TOOLS_REQUIREMENTS):
            install_into_venv(executable, ["-r", DEPENDENCY_TOOLS_REQUIREMENTS], package_dir)
        else:
            logger.warning(f"Dependency tools requirements file not found at {DEPENDENCY_TOOLS_REQUIREMENTS}.")

        if os.path.exists(TEST_TOOLS_REQUIREMENTS):
            install_into_venv(executable, ["-r", TEST_TOOLS_REQUIREMENTS], package_dir)
        else:
            logger.warning(f"Test tools requirements file not found at {TEST_TOOLS_REQUIREMENTS}.")

        if self.additional_packages:
            install_into_venv(executable, self.additional_packages, package_dir)

    def _verify_installed_packages(self, executable: str, package_dir: str, staging_directory: str) -> bool:
        packages_file = os.path.join(staging_directory, "packages.txt")
        if not os.path.exists(packages_file):
            logger.error(f"Expected packages.txt not found at {packages_file} for {package_dir}.")
            return False

        verify_script = os.path.join(REPO_ROOT, "eng/tox/verify_installed_packages.py")
        verify_command = [verify_script, "--packages-file", packages_file]
        verify_result = self.run_venv_command(executable, verify_command, cwd=package_dir)

        if verify_result.returncode != 0:
            logger.error(f"verify_installed_packages failed for {package_dir} (exit code {verify_result.returncode}).")
            if verify_result.stdout:
                logger.error(verify_result.stdout)
            if verify_result.stderr:
                logger.error(verify_result.stderr)
            return False

        return True

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
            "--no-cov",
        ]

        pytest_args = list(default_args)

        if getattr(args, "pytest_args", None):
            pytest_args.extend(args.pytest_args)

        pytest_args.append(package_dir)

        return pytest_args
