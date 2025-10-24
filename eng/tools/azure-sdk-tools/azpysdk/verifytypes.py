import argparse
import os
import tempfile
import typing
import sys
import subprocess
import json
import pathlib

from typing import Optional, List
from subprocess import CalledProcessError

from .Check import Check
from ci_tools.functions import install_into_venv
from ci_tools.variables import discover_repo_root, in_ci, set_envvar_defaults, set_envvar_defaults
from ci_tools.environment_exclusions import is_check_enabled, is_typing_ignored
from ci_tools.functions import get_pip_command
from ci_tools.logging import logger

PYRIGHT_VERSION = "1.1.287"
REPO_ROOT = discover_repo_root()


def install_from_main(setup_path: str) -> int:
    path = pathlib.Path(setup_path)
    subdirectory = path.relative_to(REPO_ROOT)
    cwd = os.getcwd()
    with tempfile.TemporaryDirectory() as temp_dir_name:
        os.chdir(temp_dir_name)
        try:
            subprocess.check_call(["git", "init"], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
            subprocess.check_call(
                ["git", "clone", "--no-checkout", "https://github.com/Azure/azure-sdk-for-python.git", "--depth", "1"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.STDOUT,
            )
            os.chdir("azure-sdk-for-python")
            subprocess.check_call(
                ["git", "sparse-checkout", "init", "--cone"], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT
            )
            subprocess.check_call(
                ["git", "sparse-checkout", "set", subdirectory], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT
            )
            subprocess.check_call(["git", "checkout", "main"], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)

            if not os.path.exists(os.path.join(os.getcwd(), subdirectory)):
                # code is not checked into main yet, nothing to compare
                logger.info(f"{subdirectory} is not checked into main, nothing to compare.")
                return 1

            os.chdir(subdirectory)

            command = get_pip_command() + ["install", ".", "--force-reinstall"]

            subprocess.check_call(command, stdout=subprocess.DEVNULL)
        finally:
            os.chdir(cwd)  # allow temp dir to be deleted
        return 0


def get_type_complete_score(commands: typing.List[str], check_pytyped: bool = False) -> float:
    try:
        response = subprocess.run(
            commands,
            check=True,
            capture_output=True,
        )
    except subprocess.CalledProcessError as e:
        if e.returncode != 1:
            logger.error(
                f"Running verifytypes failed: {e.stderr}. See https://aka.ms/python/typing-guide for information."
            )
            return -1.0

        report = json.loads(e.output)
        if check_pytyped:
            pytyped_present = report["typeCompleteness"].get("pyTypedPath", None)
            if not pytyped_present:
                logger.error(f"No py.typed file was found. See https://aka.ms/python/typing-guide for information.")
                return -1.0
        return report["typeCompleteness"]["completenessScore"]

    # library scores 100%
    report = json.loads(response.stdout)
    return report["typeCompleteness"]["completenessScore"]


class verifytypes(Check):
    def __init__(self) -> None:
        super().__init__()

    def register(
        self, subparsers: "argparse._SubParsersAction", parent_parsers: Optional[List[argparse.ArgumentParser]] = None
    ) -> None:
        """Register the verifytypes check. The verifytypes check installs verifytypes and runs verifytypes against the target package."""
        parents = parent_parsers or []
        p = subparsers.add_parser(
            "verifytypes", parents=parents, help="Run the verifytypes check to verify type completeness of a package."
        )
        p.set_defaults(func=self.run)

    def run(self, args: argparse.Namespace) -> int:
        """Run the verifytypes check command."""
        logger.info("Running verifytypes check...")

        set_envvar_defaults()
        targeted = self.get_targeted_directories(args)

        results: List[int] = []

        for parsed in targeted:
            package_dir = parsed.folder
            package_name = parsed.name
            module = parsed.namespace
            executable, staging_directory = self.get_executable(args.isolate, args.command, sys.executable, package_dir)
            logger.info(f"Processing {package_name} for verifytypes check")

            self.install_dev_reqs(executable, args, package_dir)

            # install pyright
            try:
                install_into_venv(executable, [f"pyright=={PYRIGHT_VERSION}"], package_dir)
            except CalledProcessError as e:
                logger.error(f"Failed to install pyright: {e}")
                return e.returncode

            if in_ci():
                if not is_check_enabled(package_dir, "verifytypes") or is_typing_ignored(package_name):
                    logger.info(
                        f"{package_name} opts-out of verifytypes check. See https://aka.ms/python/typing-guide for information."
                    )
                    continue

            commands = [
                executable,
                "-m",
                "pyright",
                "--verifytypes",
                module,
                "--ignoreexternal",
                "--outputjson",
            ]

            # get type completeness score from current code
            score_from_current = get_type_complete_score(commands, check_pytyped=True)
            if score_from_current == -1.0:
                results.append(1)
                continue

            try:
                subprocess.check_call(commands[:-1])
            except subprocess.CalledProcessError:
                logger.warning(
                    "verifytypes reported issues."
                )  # we don't fail on verifytypes, only if type completeness score worsens from main

            if in_ci():
                # get type completeness score from main
                logger.info("Getting the type completeness score from the code in main...")
                if install_from_main(os.path.abspath(package_dir)) > 0:
                    continue

                score_from_main = get_type_complete_score(commands)
                if score_from_main == -1.0:
                    results.append(1)
                    continue

                score_from_main_rounded = round(score_from_main * 100, 1)
                score_from_current_rounded = round(score_from_current * 100, 1)
                logger.info("\n-----Type completeness score comparison-----\n")
                logger.info(f"Score in main: {score_from_main_rounded}%")
                # Give a 5% buffer for type completeness score to decrease
                if score_from_current_rounded < score_from_main_rounded - 5:
                    logger.error(
                        f"\nERROR: The type completeness score of {package_name} has significantly decreased compared to the score in main. "
                        f"See the above output for areas to improve. See https://aka.ms/python/typing-guide for information."
                    )
                    results.append(1)
        return max(results) if results else 0
