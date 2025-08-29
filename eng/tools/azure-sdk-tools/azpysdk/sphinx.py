import argparse
import os
import sys
import tempfile

from typing import Optional, List
from subprocess import CalledProcessError, check_call

from .Check import Check
from ci_tools.parsing import ParsedSetup
from ci_tools.functions import pip_install
from ci_tools.scenario.generation import create_package_and_install
from ci_tools.variables import in_ci, set_envvar_defaults
from ci_tools.environment_exclusions import (
    is_check_enabled, is_typing_ignored
)
from ci_tools.logging import logger

class sphinx(Check):
    def __init__(self) -> None:
        super().__init__()

    def register(self, subparsers: "argparse._SubParsersAction", parent_parsers: Optional[List[argparse.ArgumentParser]] = None) -> None:
        """Register the `sphinx` check. The sphinx check installs sphinx and runs sphinx against the target package.
        """
        parents = parent_parsers or []
        p = subparsers.add_parser("sphinx", parents=parents, help="Run the sphinx check")
        p.set_defaults(func=self.run)

    def run(self, args: argparse.Namespace) -> int:
        """Run the sphinx check command."""
        logger.info("Running sphinx check in isolated venv...")

        set_envvar_defaults()

        targeted = self.get_targeted_directories(args)

        results: List[int] = []

        return max(results) if results else 0