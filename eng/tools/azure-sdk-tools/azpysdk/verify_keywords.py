import argparse
import os
import sys
import subprocess

from typing import Optional, List
from subprocess import CalledProcessError

from ci_tools.functions import install_into_venv
from ci_tools.variables import in_ci, discover_repo_root, set_envvar_defaults
from ci_tools.environment_exclusions import is_check_enabled
from ci_tools.logging import logger

from .Check import Check

class verify_keywords(Check):
    def __init__(self) -> None:
        super().__init__()

    def register(
        self, subparsers: "argparse._SubParsersAction", parent_parsers: Optional[List[argparse.ArgumentParser]] = None
    ) -> None:
        """Register the `verify_keywords` check. The verify_keywords check checks the keywords of a targeted python package. If the keyword 'azure sdk' is not present, error."""
        parents = parent_parsers or []
        p = subparsers.add_parser("verify_keywords", parents=parents, help="Run the keyword verification check")
        p.set_defaults(func=self.run)

    def run(self, args: argparse.Namespace) -> int:
        """Run the verify_keywords check command."""
        logger.info("Running verify_keywords check...")

        set_envvar_defaults()

        targeted = self.get_targeted_directories(args)

        results: List[int] = []

        for parsed in targeted:
            package_dir = parsed.folder
            package_name = parsed.name

            executable, staging_directory = self.get_executable(args.isolate, args.command, sys.executable, package_dir)
            logger.info(f"Processing {package_name} for verify_keywords check")

            subprocess.check_call(["sdk_verify_keywords", "-t", package_dir])

        return max(results) if results else 0
