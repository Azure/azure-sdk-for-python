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

BLACK_VERSION = "24.4.0"
REPO_ROOT = discover_repo_root()


class black(Check):
    def __init__(self) -> None:
        super().__init__()

    def register(
        self, subparsers: "argparse._SubParsersAction", parent_parsers: Optional[List[argparse.ArgumentParser]] = None
    ) -> None:
        """Register the `black` check. The black check installs black and runs black against the target package."""
        parents = parent_parsers or []
        p = subparsers.add_parser("black", parents=parents, help="Run the code formatter black check")
        p.set_defaults(func=self.run)

    def run(self, args: argparse.Namespace) -> int:
        """Run the black check command."""
        logger.info("Running black check...")

        set_envvar_defaults()

        targeted = self.get_targeted_directories(args)

        results: List[int] = []

        for parsed in targeted:
            package_dir = parsed.folder
            package_name = parsed.name

            executable, staging_directory = self.get_executable(args.isolate, args.command, sys.executable, package_dir)
            logger.info(f"Processing {package_name} for black check")

            self.install_dev_reqs(executable, args, package_dir)

            # install black
            try:
                install_into_venv(executable, [f"black=={BLACK_VERSION}"], package_dir)
            except CalledProcessError as e:
                logger.error(f"Failed to install black: {e}")
                return e.returncode

            logger.info(f"Running black against {package_name}")

            config_file_location = os.path.join(REPO_ROOT, "eng/black-pyproject.toml")

            if in_ci():
                if not is_check_enabled(package_dir, "black", default=False):
                    logger.info(f"Package {package_name} opts-out of black check.")
                    continue
            try:
                run_result = subprocess.run(
                    [
                        executable,
                        "-m",
                        "black",
                        f"--config={config_file_location}",
                        package_dir,
                    ],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    check=True,
                )

                if run_result.stderr and "reformatted" in run_result.stderr.decode("utf-8"):
                    if in_ci():
                        logger.info(f"The package {package_name} needs reformat. Run `black` locally to reformat.")
                        results.append(1)
                    else:
                        logger.info(f"The package {package_name} was reformatted.")
                else:
                    logger.info(f"The package {package_name} is properly formatted, no files changed.")

            except subprocess.CalledProcessError as e:
                logger.error(f"Unable to invoke black for {package_name}. Ran into exception {e}.")

        return max(results) if results else 0
