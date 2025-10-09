import argparse
import os
import sys
import subprocess
from typing import Optional, List

from .Check import Check
from ci_tools.functions import install_into_venv
from ci_tools.variables import set_envvar_defaults
from ci_tools.logging import logger


class ruff(Check):
    def __init__(self) -> None:
        super().__init__()

    def register(
        self, subparsers: "argparse._SubParsersAction", parent_parsers: Optional[List[argparse.ArgumentParser]] = None
    ) -> None:
        """Register the ruff check. The ruff check installs ruff and runs ruff against the target package."""
        parents = parent_parsers or []
        p = subparsers.add_parser("ruff", parents=parents, help="Run the ruff check")
        p.set_defaults(func=self.run)

    def run(self, args: argparse.Namespace) -> int:
        """Run the ruff check command."""
        logger.info("Running ruff check...")

        set_envvar_defaults()
        targeted = self.get_targeted_directories(args)

        results: List[int] = []

        for parsed in targeted:
            package_dir = parsed.folder
            package_name = parsed.name
            executable, staging_directory = self.get_executable(args.isolate, args.command, sys.executable, package_dir)
            logger.info(f"Processing {package_name} for ruff check")

            self.install_dev_reqs(executable, args, package_dir)

            try:
                install_into_venv(executable, ["ruff"], package_dir)
            except subprocess.CalledProcessError as e:
                logger.error(f"Failed to install ruff: {e}")
                return e.returncode

            top_level_module = parsed.namespace.split(".")[0]

            try:
                subprocess.check_call(
                    [
                        executable,
                        "-m",
                        "ruff",
                        "check",
                        os.path.join(package_dir, top_level_module),
                    ]
                )
            except subprocess.CalledProcessError as e:
                logger.error(f"ruff check failed for {package_name}: {e}")
                results.append(e.returncode)

        return max(results) if results else 0
