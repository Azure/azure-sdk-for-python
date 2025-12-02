import argparse
import os
import sys

from typing import Optional, List
import subprocess
from subprocess import CalledProcessError, check_call

from .Check import Check
from ci_tools.functions import install_into_venv, get_pip_command
from ci_tools.scenario.generation import create_package_and_install
from ci_tools.variables import discover_repo_root, in_ci, set_envvar_defaults
from ci_tools.environment_exclusions import is_check_enabled
from ci_tools.logging import logger, run_logged

REPO_ROOT = discover_repo_root()

class devtest(Check):
    def __init__(self) -> None:
        super().__init__()

    def register(
        self, subparsers: "argparse._SubParsersAction", parent_parsers: Optional[List[argparse.ArgumentParser]] = None
    ) -> None:
        """Register the devtest check. The devtest check tests a package against dependencies installed from a dev index."""
        parents = parent_parsers or []
        p = subparsers.add_parser("devtest", parents=parents, help="Run the devtest check to test a package against dependencies installed from a dev index")
        p.set_defaults(func=self.run)

    def run(self, args: argparse.Namespace) -> int:
        """Run the devtest check command."""
        logger.info("Running devtest check...")

        set_envvar_defaults()
        targeted = self.get_targeted_directories(args)

        results: List[int] = []

        for parsed in targeted:
            package_dir = parsed.folder
            package_name = parsed.name
            executable, staging_directory = self.get_executable(args.isolate, args.command, sys.executable, package_dir)
            logger.info(f"Processing {package_name} for devtest check")

            # install dependencies
            self.install_dev_reqs(executable, args, package_dir)

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

            # install dev build dependency


        return max(results) if results else 0
