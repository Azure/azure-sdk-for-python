import argparse
import os
import sys

from typing import Optional, List
from subprocess import CalledProcessError, check_call

from .Check import Check
from ci_tools.functions import install_into_venv, get_pip_command
from ci_tools.scenario.generation import create_package_and_install
from ci_tools.variables import discover_repo_root, in_ci, set_envvar_defaults
from ci_tools.environment_exclusions import is_check_enabled
from ci_tools.logging import logger

JSONDIFF_VERSION = "1.2.0"
REPO_ROOT = discover_repo_root()


class breaking(Check):
    def __init__(self) -> None:
        super().__init__()

    def register(
        self, subparsers: "argparse._SubParsersAction", parent_parsers: Optional[List[argparse.ArgumentParser]] = None
    ) -> None:
        """Register the breaking change check. The breaking change check checks for breaking changes against the target package."""
        parents = parent_parsers or []
        p = subparsers.add_parser("breaking", parents=parents, help="Run the breaking change check")
        p.set_defaults(func=self.run)

    def run(self, args: argparse.Namespace) -> int:
        """Run the breaking change check command."""
        logger.info("Running breaking check...")

        set_envvar_defaults()
        targeted = self.get_targeted_directories(args)

        results: List[int] = []

        BREAKING_CHECKER_PATH = os.path.join(REPO_ROOT, "scripts", "breaking_changes_checker")

        for parsed in targeted:
            package_dir = parsed.folder
            package_name = parsed.name
            executable, staging_directory = self.get_executable(args.isolate, args.command, sys.executable, package_dir)
            logger.info(f"Processing {package_name} for breaking check...")

            # install dependencies
            self.install_dev_reqs(executable, args, package_dir)

            try:
                install_into_venv(
                    executable,
                    [f"jsondiff=={JSONDIFF_VERSION}", "-e", BREAKING_CHECKER_PATH],
                    package_dir,
                )
            except CalledProcessError as e:
                logger.error(f"Failed to install dependencies for {package_name}: {e}")
                results.append(1)
                continue

            create_package_and_install(
                distribution_directory=staging_directory,
                target_setup=package_dir,
                skip_install=False,
                cache_dir=None,
                work_dir=staging_directory,
                force_create=False,
                package_type="sdist",
                pre_download_disabled=False,
                python_executable=executable,
            )

            try:
                cmd = [
                    os.path.join(BREAKING_CHECKER_PATH, "detect_breaking_changes.py"),
                    "--target",
                    package_dir,
                ]
                check_call([executable] + cmd)
                logger.info(f"No breaking changes detected for {package_name}.")
            except CalledProcessError as e:
                logger.error(f"Breaking changes detected for {package_name}: {e}")
                results.append(1)
                continue

        return max(results) if results else 0
