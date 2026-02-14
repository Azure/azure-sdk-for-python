"""Update code snippets in README.md files from sample code.

This command runs black formatting on sample files as a prerequisite step,
then extracts code snippets from Python sample files and updates README.md files.
"""

import argparse
import os
import sys
import subprocess
from pathlib import Path
from typing import Optional, List
from subprocess import CalledProcessError

from ci_tools.functions import install_into_venv
from ci_tools.variables import in_ci, discover_repo_root, set_envvar_defaults
from ci_tools.logging import logger

from .Check import Check

BLACK_VERSION = "24.4.0"
REPO_ROOT = discover_repo_root()


class update_snippets(Check):
    def __init__(self) -> None:
        super().__init__()

    def register(
        self, subparsers: "argparse._SubParsersAction", parent_parsers: Optional[List[argparse.ArgumentParser]] = None
    ) -> None:
        """Register the `update-snippets` check."""
        parents = parent_parsers or []
        p = subparsers.add_parser(
            "update-snippets",
            parents=parents,
            help="Update code snippets in README.md from sample files (runs black first)",
        )
        p.add_argument(
            "--no-black",
            action="store_true",
            help="Skip black formatting step (use only if you are confident snippets are already formatted)",
        )
        p.set_defaults(func=self.run)

    def run(self, args: argparse.Namespace) -> int:
        """Run the update-snippets command."""
        logger.info("Running update-snippets check...")

        set_envvar_defaults()

        targeted = self.get_targeted_directories(args)

        results: List[int] = []

        for parsed in targeted:
            package_dir = parsed.folder
            package_name = parsed.name

            executable, staging_directory = self.get_executable(args.isolate, args.command, sys.executable, package_dir)
            logger.info(f"Processing {package_name} for snippet update")

            self.install_dev_reqs(executable, args, package_dir)

            # Install black as a prerequisite
            if not args.no_black:
                try:
                    logger.info("Installing black as a prerequisite...")
                    install_into_venv(executable, [f"black=={BLACK_VERSION}"], package_dir)
                except CalledProcessError as e:
                    logger.error(f"Failed to install black: {e}")
                    return e.returncode
            else:
                logger.info("Skipping black installation (--no-black flag provided)")

            # Run the snippet updater with black integration
            logger.info(f"Running snippet updater for {package_name}")

            snippet_updater_path = os.path.join(
                REPO_ROOT, "eng/tools/azure-sdk-tools/ci_tools/snippet_update/python_snippet_updater.py"
            )

            cmd = [executable, snippet_updater_path, str(package_dir)]
            if args.no_black:
                cmd.append("--no-black")

            try:
                run_result = subprocess.run(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    check=True,
                )

                logger.info(f"Snippets updated successfully for {package_name}")
                if run_result.stdout:
                    logger.info(run_result.stdout.decode("utf-8"))

            except subprocess.CalledProcessError as e:
                logger.error(f"Failed to update snippets for {package_name}: {e.stderr.decode('utf-8')}")
                results.append(1)

        return max(results) if results else 0
