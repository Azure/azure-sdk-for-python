import argparse
import os
import sys
from subprocess import CalledProcessError
from typing import List, Optional

from .Check import Check

from ci_tools.functions import is_error_code_5_allowed, install_into_venv
from ci_tools.scenario.generation import create_package_and_install
from ci_tools.variables import discover_repo_root, set_envvar_defaults
from ci_tools.logging import logger

REPO_ROOT = discover_repo_root()

PACKAGING_REQUIREMENTS = [
    "wheel==0.45.1",
    "packaging==24.2",
    "urllib3==2.2.3",
    "tomli==2.2.1",
    "build==1.2.2.post1",
    "pkginfo==1.12.1.2",
]

TEST_TOOLS_REQUIREMENTS = os.path.join(REPO_ROOT, "eng/test_tools.txt")


class whl(Check):
    def __init__(self) -> None:
        super().__init__()

    def register(
        self, subparsers: "argparse._SubParsersAction", parent_parsers: Optional[List[argparse.ArgumentParser]] = None
    ) -> None:
        """Register the `whl` check. The `whl` check installs the wheel version of the target package + its dev_requirements.txt,
        then invokes pytest. Failures indicate a test issue.
        """
        parents = parent_parsers or []
        p = subparsers.add_parser("whl", parents=parents, help="Run the whl check")
        p.set_defaults(func=self.run)
        p.add_argument(
            "--pytest-args",
            nargs=argparse.REMAINDER,
            help="Additional arguments forwarded to pytest.",
        )

    def run(self, args: argparse.Namespace) -> int:
        """Run the whl check command."""
        logger.info("Running whl check...")

        set_envvar_defaults({"PROXY_URL": "http://localhost:5001"})

        targeted = self.get_targeted_directories(args)
        if not targeted:
            logger.warning("No target packages discovered for whl check.")
            return 0

        overall_result = 0

        for parsed in targeted:
            package_dir = parsed.folder
            package_name = parsed.name

            executable, staging_directory = self.get_executable(args.isolate, args.command, sys.executable, package_dir)
            logger.info(f"Processing {package_name} using interpreter {executable}")

            try:
                self._install_common_requirements(executable, package_dir)
                self.install_dev_reqs(executable, args, package_dir)
            except CalledProcessError as exc:
                logger.error(f"Failed to install dependencies for {package_name}: {exc}")
                overall_result = max(overall_result, exc.returncode or 1)
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
                    pre_download_disabled=False,
                    python_executable=executable,
                )
            except CalledProcessError as exc:
                logger.error(f"Failed to build/install wheel for {package_name}: {exc}")
                overall_result = max(overall_result, exc.returncode or 1)
                continue

            pytest_args = self._build_pytest_args(package_dir, args)
            pytest_command = ["-m", "pytest", *pytest_args]
            pytest_result = self.run_venv_command(executable, pytest_command, cwd=package_dir, immediately_dump=True)

            if pytest_result.returncode != 0:
                if pytest_result.returncode == 5 and is_error_code_5_allowed(package_dir, package_name):
                    logger.info(
                        "pytest exited with code 5 for %s, which is allowed for management or opt-out packages.",
                        package_name,
                    )
                    # Align with tox: skip coverage when tests are skipped entirely
                    continue
                logger.error(f"pytest failed for {package_name} with exit code {pytest_result.returncode}.")
                overall_result = max(overall_result, pytest_result.returncode or 1)
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
                overall_result = max(overall_result, coverage_result.returncode)

        return overall_result

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

        additional = args.pytest_args if args.pytest_args else []

        return [*default_args, *additional, package_dir]
