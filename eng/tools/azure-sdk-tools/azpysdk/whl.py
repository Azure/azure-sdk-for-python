import argparse
import tempfile
import os
from typing import Optional, List, Any
import sys
from subprocess import run

from .Check import Check

from ci_tools.functions import is_error_code_5_allowed, install_into_venv
from ci_tools.variables import set_envvar_defaults
from ci_tools.parsing import ParsedSetup
from ci_tools.scenario.generation import create_package_and_install
from ci_tools.logging import logger


class whl(Check):
    def __init__(self) -> None:
        super().__init__()

    def register(
        self, subparsers: "argparse._SubParsersAction", parent_parsers: Optional[List[argparse.ArgumentParser]] = None
    ) -> None:
        """Register the `whl` check. The `whl` check installs the wheel version of the target package + its dev_requirements.txt,
        then invokes pytest. Failures indicate a test issue.
        """
        parents = parent_parsers or []
        p = subparsers.add_parser("whl", parents=parents, help="Run the whl check")
        p.set_defaults(func=self.run)
        # TODO add mark_args, and other parameters

    def run(self, args: argparse.Namespace) -> int:
        """Run the whl check command."""
        logger.info("Running whl check...")

        set_envvar_defaults()

        targeted = self.get_targeted_directories(args)

        results: List[int] = []

        for parsed in targeted:
            pkg = parsed.folder
            executable, staging_directory = self.get_executable(args.isolate, args.command, sys.executable, pkg)

            logger.info(f"Invoking check with {executable}")

            self.install_dev_reqs(executable, args, pkg)

            create_package_and_install(
                distribution_directory=staging_directory,
                target_setup=pkg,
                skip_install=False,
                cache_dir=None,
                work_dir=staging_directory,
                force_create=False,
                package_type="wheel",
                pre_download_disabled=False,
                python_executable=executable,
            )

            # TODO: split sys.argv[1:] on -- and pass in everything after the -- as additional arguments
            # TODO: handle mark_args
            logger.info(f"Invoke pytest for {pkg}")
            exit_code = run(
                [executable, "-m", "pytest", "."]
                + [
                    "-rsfE",
                    f"--junitxml={pkg}/test-junit-{args.command}.xml",
                    "--verbose",
                    "--cov-branch",
                    "--durations=10",
                    "--ignore=azure",
                    "--ignore-glob=.venv*",
                    "--ignore=build",
                    "--ignore=.eggs",
                    "--ignore=samples",
                ],
                cwd=pkg,
            ).returncode

            if exit_code != 0:
                if exit_code == 5 and is_error_code_5_allowed(parsed.folder, parsed.name):
                    logger.info("Exit code 5 is allowed, continuing execution.")
                else:
                    logger.info(f"pytest failed with exit code {exit_code}.")
                    results.append(exit_code)

        # final result is the worst case of all the results
        return max(results)
