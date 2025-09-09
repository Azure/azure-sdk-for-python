import argparse
import os
import sys

from typing import Optional, List
from subprocess import CalledProcessError, check_call

from .Check import Check
from ci_tools.functions import install_into_venv
from ci_tools.variables import discover_repo_root, in_ci, set_envvar_defaults, in_ci, set_envvar_defaults
from ci_tools.environment_exclusions import is_check_enabled
from ci_tools.logging import logger
from .pylint import pylint

class next_pylint(pylint):
    def __init__(self):
        super().__init__()

    def register(self, subparsers: "argparse._SubParsersAction", parent_parsers: Optional[List[argparse.ArgumentParser]] = None) -> None:
        """Register the next-pylint check. The next-pylint check installs the next version of pylint and runs pylint against the target package.
        """
        parents = parent_parsers or []
        p = subparsers.add_parser("next-pylint", parents=parents, help="Run the pylint check with the next version of pylint")
        p.set_defaults(func=self.run)

    def run(self, args: argparse.Namespace) -> int:
        """Run the pylint check command."""
        args.next = True
        return super().run(args)