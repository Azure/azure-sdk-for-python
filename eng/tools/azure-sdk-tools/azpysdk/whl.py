import argparse
import logging
import tempfile
import os
from typing import Optional, List, Any
from pytest import pytest_main
import sys

from .Check import Check

from ci_tools.functions import discover_targeted_packages, is_error_code_5_allowed, pip_install
from ci_tools.variables import set_envvar_defaults
from ci_tools.scenario.generation import create_package_and_install


class whl(Check):
    def __init__(self) -> None:
        super().__init__()

    def register(self, subparsers: "argparse._SubParsersAction", parent_parsers: Optional[List[argparse.ArgumentParser]] = None) -> None:
        """Register the `whl` check.

        `subparsers` is the object returned by ArgumentParser.add_subparsers().
        `parent_parsers` is an optional list of parent ArgumentParser objects
        that contain common arguments. Avoid mutating default arguments.
        """
        parents = parent_parsers or []
        p = subparsers.add_parser("whl", parents=parents, help="Run the whl check")
        p.set_defaults(func=self.run)
        # Add any additional arguments specific to WhlCheck here (do not re-add common args)

    # todo: figure out venv abstraction mechanism
    def run(self, args: argparse.Namespace) -> int:
        """Run the whl check command."""
        print("Running whl check...")

        set_envvar_defaults()

        target_dir = os.getcwd()
        targeted = discover_targeted_packages(args.target, target_dir)
        results = []

        for pkg in targeted:
            dev_requirements = os.path.join(pkg, "dev_requirements.txt")

            if os.path.exists(dev_requirements):
                pip_install([f"-r {dev_requirements}"], sys.executable)

            staging_area = tempfile.mkdtemp()

            create_package_and_install(
                distribution_directory=staging_area,
                target_setup=pkg,
                skip_install=False,
                cache_dir=None,
                work_dir=staging_area,
                force_create=False,
                package_type="wheel",
                pre_download_disabled=False,
            )

            # todo, come up with a good pattern for passing all the additional args after -- to pytest
            logging.info(f"Invoke pytest for {pkg}")

            exit_code = pytest_main(
                [pkg]
            )

            if exit_code != 0:
                if exit_code == 5 and is_error_code_5_allowed():
                    logging.info("Exit code 5 is allowed, continuing execution.")
                else:
                    logging.info(f"pytest failed with exit code {exit_code}.")
                    results.append(exit_code)

        # final result is the worst case of all the results
        return max(results)
