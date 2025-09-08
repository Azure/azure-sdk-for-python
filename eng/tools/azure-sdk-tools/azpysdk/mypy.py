import argparse
import os
import sys
import logging
import tempfile

from typing import Optional, List
from subprocess import CalledProcessError, check_call

from .Check import Check
from ci_tools.parsing import ParsedSetup
from ci_tools.functions import discover_targeted_packages
from ci_tools.scenario.generation import create_package_and_install
from ci_tools.variables import in_ci, set_envvar_defaults
from ci_tools.environment_exclusions import (
    is_check_enabled, is_typing_ignored
)

logging.getLogger().setLevel(logging.INFO)

PYTHON_VERSION = "3.9"
MYPY_VERSION = "1.14.1"

class mypy(Check):
    def __init__(self) -> None:
        super().__init__()

    def register(self, subparsers: "argparse._SubParsersAction", parent_parsers: Optional[List[argparse.ArgumentParser]] = None) -> None:
        """Register the `mypy` check. The mypy check installs mypy and runs mypy against the target package.
        """
        parents = parent_parsers or []
        p = subparsers.add_parser("mypy", parents=parents, help="Run the mypy check")
        p.set_defaults(func=self.run)

        p.add_argument(
            "--next", 
            default=False, 
            help="Next version of mypy is being tested",
            required=False
        )

    def run(self, args: argparse.Namespace) -> int:
        """Run the mypy check command."""
        print("Running mypy check in isolated venv...")

        set_envvar_defaults()

        targeted = self.get_targeted_directories(args)

        results: List[int] = []

        for parsed in targeted:
            package_dir = parsed.folder
            package_name = parsed.name
            print(f"Processing {package_name} for mypy check")

            staging_area = tempfile.mkdtemp()
            create_package_and_install(
                distribution_directory=staging_area,
                target_setup=package_dir,
                skip_install=False,
                cache_dir=None,
                work_dir=staging_area,
                force_create=False,
                package_type="wheel",
                pre_download_disabled=False,
            )

            # install mypy
            try:
                if (args.next):
                    # use latest version of mypy
                    check_call([sys.executable, "-m", "pip", "install", "mypy"])
                else:
                    check_call([sys.executable, "-m", "pip", "install", f"mypy=={MYPY_VERSION}"])
            except CalledProcessError as e:
                print("Failed to install mypy:", e)
                return e.returncode

            logging.info(f"Running mypy against {package_name}")

            if not args.next and in_ci():
                if not is_check_enabled(package_dir, "mypy", True) or is_typing_ignored(package_name):
                    logging.info(
                        f"Package {package_name} opts-out of mypy check. See https://aka.ms/python/typing-guide for information."
                    )
                    continue

            top_level_module = parsed.namespace.split(".")[0]

            commands = [
                sys.executable,
                "-m",
                "mypy",
                "--python-version",
                PYTHON_VERSION,
                "--show-error-codes",
                "--ignore-missing-imports",
            ]
            src_code = [*commands, os.path.join(package_dir, top_level_module)]
            src_code_error = None
            sample_code_error = None
            try:
                logging.info(
                    f"Running mypy commands on src code: {src_code}"
                )
                results.append(check_call(src_code))
                logging.info("Verified mypy, no issues found")
            except CalledProcessError as src_error:
                src_code_error = src_error 
                results.append(src_error.returncode)
            
            if not args.next and in_ci() and not is_check_enabled(package_dir, "type_check_samples", True):
                logging.info(
                    f"Package {package_name} opts-out of mypy check on samples."
                )
                continue
            else:
                # check if sample dirs exists, if not, skip sample code check
                samples = os.path.exists(os.path.join(package_dir, "samples"))
                generated_samples = os.path.exists(os.path.join(package_dir, "generated_samples"))
                if not samples and not generated_samples:
                    logging.info(
                        f"Package {package_name} does not have a samples directory."
                    )
                else:
                    sample_code = [
                        *commands,
                        "--check-untyped-defs",
                        "--follow-imports=silent",
                        os.path.join(package_dir, "samples" if samples else "generated_samples"),
                    ]
                    try:
                        logging.info(
                            f"Running mypy commands on sample code: {sample_code}"
                        )
                        results.append(check_call(sample_code))
                    except CalledProcessError as sample_error:
                        sample_code_error = sample_error
                        results.append(sample_error.returncode)

            if args.next and in_ci() and not is_typing_ignored(package_name):
                from gh_tools.vnext_issue_creator import create_vnext_issue, close_vnext_issue
                if src_code_error or sample_code_error:
                    create_vnext_issue(package_dir, "mypy")
                else:
                    close_vnext_issue(package_name, "mypy")
            
        return max(results) if results else 0
        