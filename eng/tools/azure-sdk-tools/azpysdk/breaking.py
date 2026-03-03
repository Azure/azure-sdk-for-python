import argparse
import os
import sys

from typing import Optional, List
from subprocess import CalledProcessError, check_call

from .Check import Check
from ci_tools.functions import install_into_venv
from ci_tools.scenario.generation import create_package_and_install
from ci_tools.variables import discover_repo_root, set_envvar_defaults
from ci_tools.logging import logger

JSONDIFF_VERSION = "1.2.0"
REPO_ROOT = discover_repo_root()
BREAKING_CHECKER_PATH = os.path.join(REPO_ROOT, "scripts", "breaking_changes_checker")


class breaking(Check):
    def __init__(self) -> None:
        super().__init__()

    def register(
        self, subparsers: "argparse._SubParsersAction", parent_parsers: Optional[List[argparse.ArgumentParser]] = None
    ) -> None:
        """Register the breaking change check. The breaking change check checks for breaking changes against the target package."""
        parents = parent_parsers or []
        p = subparsers.add_parser("breaking", parents=parents, help="Run the breaking change check")
        p.set_defaults(func=self.run)

        p.add_argument(
            "-m",
            "--module",
            dest="target_module",
            help="The target module. The target module passed will be the top most module in the package.",
            default=None,
        )
        p.add_argument(
            "--in-venv",
            dest="in_venv",
            help="Check if we are in the newly created venv.",
            default=False,
        )
        p.add_argument(
            "-s",
            "--stable-version",
            dest="stable_version",
            help="The stable version of the target package, if it exists on PyPi.",
            default=None,
        )
        p.add_argument(
            "-c",
            "--changelog",
            dest="changelog",
            help="Output changes listed in changelog format.",
            action="store_true",
            default=False,
        )
        p.add_argument(
            "--code-report",
            dest="code_report",
            help="Output a code report for a package.",
            action="store_true",
            default=False,
        )
        p.add_argument(
            "--source-report",
            dest="source_report",
            help="Path to the code report for the previous package version.",
            default=None,
        )
        p.add_argument(
            "--target-report",
            dest="target_report",
            help="Path to the code report for the new package version.",
            default=None,
        )
        p.add_argument(
            "--latest-pypi-version",
            dest="latest_pypi_version",
            help="Use the latest package version on PyPi (can be preview or stable).",
            action="store_true",
            default=False,
        )

    def run(self, args: argparse.Namespace) -> int:
        """Run the breaking change check command."""
        logger.info("Running breaking check...")

        set_envvar_defaults()
        targeted = self.get_targeted_directories(args)

        results: List[int] = []

        for parsed in targeted:
            if os.getcwd() != parsed.folder:
                os.chdir(parsed.folder)
            package_dir = parsed.folder
            package_name = parsed.name
            executable, staging_directory = self.get_executable(args.isolate, args.command, sys.executable, package_dir)
            logger.info(f"Processing {package_name} for breaking check...")

            # install dependencies
            self.install_dev_reqs(executable, args, package_dir)

            try:
                install_into_venv(
                    executable,
                    [f"jsondiff=={JSONDIFF_VERSION}", "-e", BREAKING_CHECKER_PATH],
                    package_dir,
                )
            except CalledProcessError as e:
                logger.error(
                    f"Failed to install jsondiff or breaking change checker while processing {package_name}: {e}"
                )
                results.append(1)
                continue

            create_package_and_install(
                distribution_directory=staging_directory,
                target_setup=package_dir,
                skip_install=False,
                cache_dir=None,
                work_dir=staging_directory,
                force_create=False,
                package_type="sdist",
                pre_download_disabled=False,
                python_executable=executable,
            )

            try:
                cmd = [
                    executable,
                    os.path.join(BREAKING_CHECKER_PATH, "detect_breaking_changes.py"),
                    "--target",
                    package_dir,
                ]
                if getattr(args, "target_module", None):
                    cmd.extend(["--module", args.target_module])
                if getattr(args, "in_venv", False):
                    cmd.extend(["--in-venv", str(args.in_venv).lower()])
                if getattr(args, "stable_version", None):
                    cmd.extend(["--stable_version", args.stable_version])
                if getattr(args, "changelog", False):
                    cmd.append("--changelog")
                if getattr(args, "code_report", False):
                    cmd.append("--code-report")
                if getattr(args, "source_report", None):
                    cmd.extend(["--source-report", args.source_report])
                if getattr(args, "target_report", None):
                    cmd.extend(["--target-report", args.target_report])
                if getattr(args, "latest_pypi_version", False):
                    cmd.append("--latest-pypi-version")
                check_call(cmd)
            except CalledProcessError as e:
                logger.error(f"Breaking check failed for {package_name}: {e}")
                results.append(1)
                continue

        return max(results) if results else 0
