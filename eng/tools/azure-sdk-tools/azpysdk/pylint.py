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

REPO_ROOT = discover_repo_root()
PYLINT_VERSION = "3.2.7"

class pylint(Check):
    def __init__(self) -> None:
        super().__init__()

    def register(self, subparsers: "argparse._SubParsersAction", parent_parsers: Optional[List[argparse.ArgumentParser]] = None) -> None:
        """Register the pylint check. The pylint check installs pylint and runs pylint against the target package.
        """
        parents = parent_parsers or []
        p = subparsers.add_parser("pylint", parents=parents, help="Run the pylint check")
        p.set_defaults(func=self.run)

        p.add_argument(
            "--next",
            default=False,
            help="Next version of pylint is being tested.",
            required=False,
        )

    def run(self, args: argparse.Namespace) -> int:
        """Run the pylint check command."""
        logger.info("Running pylint check...")

        set_envvar_defaults()
        targeted = self.get_targeted_directories(args)

        results: List[int] = []

        for parsed in targeted:
            package_dir = parsed.folder
            package_name = parsed.name
            executable, staging_directory = self.get_executable(args.isolate, args.command, sys.executable, package_dir)
            logger.info(f"Processing {package_name} for pylint check")

            # install dependencies
            try:
                install_into_venv(executable, ["azure-pylint-guidelines-checker==0.5.6", "--index-url=https://pkgs.dev.azure.com/azure-sdk/public/_packaging/azure-sdk-for-python/pypi/simple/"], package_dir)
            except CalledProcessError as e:
                logger.error("Failed to install dependencies:", e)
                return e.returncode

            # install pylint
            try:
                if args.next:
                    # use latest version of pylint
                    install_into_venv(executable, ["pylint"], package_dir)
                else:
                    install_into_venv(executable, [f"pylint=={PYLINT_VERSION}"], package_dir)
            except CalledProcessError as e:
                logger.error("Failed to install pylint:", e)
                return e.returncode

            top_level_module = parsed.namespace.split(".")[0]

            if in_ci():
                if not is_check_enabled(package_dir, "pylint"):
                    logger.info(
                        f"Package {package_name} opts-out of pylint check."
                    )
                    continue

            rcFileLocation = os.path.join(REPO_ROOT, "eng/pylintrc") if args.next else os.path.join(REPO_ROOT, "pylintrc")

            try:
                results.append(check_call(
                    [
                        executable,
                        "-m",
                        "pylint",
                        "--rcfile={}".format(rcFileLocation),
                        "--output-format=parseable",
                        os.path.join(package_dir, top_level_module),
                    ]
                ))
            except CalledProcessError as e:
                logger.error(
                    "{} exited with linting error {}. Please see this link for more information https://aka.ms/azsdk/python/pylint-guide".format(package_name, e.returncode)
                )
                if args.next and in_ci():
                    from gh_tools.vnext_issue_creator import create_vnext_issue
                    create_vnext_issue(package_dir, "pylint")

                results.append(e.returncode)

            if args.next and in_ci():
                from gh_tools.vnext_issue_creator import close_vnext_issue
                close_vnext_issue(package_name, "pylint")

        return max(results) if results else 0
