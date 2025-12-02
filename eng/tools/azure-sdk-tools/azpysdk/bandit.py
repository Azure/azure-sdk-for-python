import argparse
import os
import sys
from typing import Optional, List
import subprocess
from subprocess import check_call, CalledProcessError

from .Check import Check
from ci_tools.environment_exclusions import is_check_enabled
from ci_tools.variables import in_ci, set_envvar_defaults
from ci_tools.logging import logger
from ci_tools.functions import install_into_venv, get_pip_command


class bandit(Check):
    def __init__(self) -> None:
        super().__init__()

    def register(
        self, subparsers: "argparse._SubParsersAction", parent_parsers: Optional[List[argparse.ArgumentParser]] = None
    ) -> None:
        """Register the bandit check. The bandit check installs bandit and runs bandit against the target package to find common security issues."""
        parents = parent_parsers or []
        p = subparsers.add_parser(
            "bandit", parents=parents, help="Run the bandit check to find common security issues for a package"
        )
        p.set_defaults(func=self.run)

    def run(self, args: argparse.Namespace) -> int:
        """Run the bandit check command."""
        logger.info("Running bandit check...")

        set_envvar_defaults()
        targeted = self.get_targeted_directories(args)

        results: List[int] = []

        for parsed in targeted:
            package_dir = parsed.folder
            package_name = parsed.name
            executable, staging_directory = self.get_executable(args.isolate, args.command, sys.executable, package_dir)
            logger.info(f"Processing {package_name} for bandit check")

            self.install_dev_reqs(executable, args, package_dir)

            try:
                install_into_venv(executable, ["bandit"], package_dir)
            except CalledProcessError as e:
                logger.error(f"Failed to install bandit: {e}")
                return e.returncode

            self.pip_freeze(executable)

            if in_ci():
                if not is_check_enabled(package_dir, "bandit"):
                    logger.warning(f"Bandit is disabled for {package_name}. Skipping...")
                    continue

            try:
                self.run_venv_command(
                    executable, ["-m", "bandit", "-r", os.path.join(package_dir, "azure"), "-ll"], package_dir
                )

            except CalledProcessError as e:
                logger.error(f"{package_name} exited with error {e.returncode}")
                results.append(e.returncode)

        return max(results) if results else 0
