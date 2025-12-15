import argparse
import sys

from typing import Optional, List

from .Check import Check
from ci_tools.functions import install_into_venv, get_pip_command
from ci_tools.scenario.generation import create_package_and_install, prepare_and_test_optional

from ci_tools.variables import set_envvar_defaults
from ci_tools.logging import logger


class optional(Check):
    def __init__(self) -> None:
        super().__init__()

    def register(
        self, subparsers: "argparse._SubParsersAction", parent_parsers: Optional[List[argparse.ArgumentParser]] = None
    ) -> None:
        """Register the optional check. The optional check invokes 'optional' requirements for a given package. View the pyproject.toml within the targeted package folder to see configuration."""
        parents = parent_parsers or []
        p = subparsers.add_parser(
            "optional",
            parents=parents,
            help="Run the optional check to invoke 'optional' requirements for a given package.",
        )
        p.set_defaults(func=self.run)

        p.add_argument(
            "-o",
            "--optional",
            dest="optional",
            help="The target environment. If not provided, all optional environments will be run.",
            required=False,
        )

    def run(self, args: argparse.Namespace) -> int:
        """Run the optional check command."""
        logger.info("Running optional check...")

        set_envvar_defaults()
        targeted = self.get_targeted_directories(args)

        results: List[int] = []

        for parsed in targeted:
            package_dir = parsed.folder
            package_name = parsed.name
            executable, staging_directory = self.get_executable(args.isolate, args.command, sys.executable, package_dir)
            logger.info(f"Processing {package_name} for optional check")

            # install dependencies
            self.install_dev_reqs(executable, args, package_dir)

            prepare_and_test_optional(args)

        return max(results) if results else 0
