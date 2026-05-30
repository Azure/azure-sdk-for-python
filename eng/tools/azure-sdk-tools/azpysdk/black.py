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
            if os.getcwd() != parsed.folder:
                os.chdir(parsed.folder)
            package_dir = parsed.folder
            package_name = parsed.name

            executable, staging_directory = self.get_executable(
                args.isolate,
                args.command,
                sys.executable,
                package_dir,
                python_version=getattr(args, "python_version", None),
            )
            logger.info(f"Processing {package_name} for black check")

            self.install_dev_reqs(executable, args, package_dir)

            logger.info(f"Running black against {package_name}")

            check_only = in_ci() != 0

            if check_only:
                if not is_check_enabled(package_dir, "black", default=False):
                    logger.info(f"Package {package_name} opts-out of black check.")
                    continue

            result = self.format_directory(executable, package_dir, check_only=check_only)
            if result is None:
                results.append(1)
                continue

            stderr_text = result.stderr.decode("utf-8") if result.stderr else ""
            stdout_text = result.stdout.decode("utf-8") if result.stdout else ""

            has_issues = result.returncode != 0 if check_only else "reformatted" in stderr_text

            if has_issues:
                if check_only and result.returncode > 1:
                    logger.error(f"Black failed for {package_name} (exit code {result.returncode}).")
                    if stderr_text.strip():
                        logger.error(f"Black stderr:\n{stderr_text}")
                    results.append(result.returncode)
                elif check_only:
                    logger.info(
                        f"The package {package_name} has black formatting issues. "
                        f"Run `azpysdk black .` locally from the package root to reformat."
                    )
                    if stdout_text.strip():
                        logger.info(f"Black diff output:\n{stdout_text}")
                    if stderr_text.strip():
                        logger.info(f"Black summary:\n{stderr_text}")
                    results.append(1)
                else:
                    logger.info(f"The package {package_name} was reformatted.")
                    if stdout_text.strip():
                        logger.info(f"Black diff output:\n{stdout_text}")
                    if stderr_text.strip():
                        logger.info(f"Black summary:\n{stderr_text}")
            else:
                logger.info(f"The package {package_name} is properly formatted, no files changed.")

        return max(results) if results else 0

    @staticmethod
    def format_directory(
        executable: str, target_dir: str, check_only: bool = False
    ) -> Optional[subprocess.CompletedProcess]:
        """Run black on *target_dir* using the repo-wide config.

        Installs the pinned black version into the environment of *executable*,
        then formats all Python files under *target_dir*.

        When *check_only* is True, runs with ``--check --diff`` to report
        issues without modifying files.
        """
        try:
            install_into_venv(executable, [f"black=={BLACK_VERSION}"], target_dir)
        except CalledProcessError as e:
            logger.error(f"Failed to install black, skipping formatting: {e}")
            return None

        config_file_location = os.path.join(REPO_ROOT, "eng/black-pyproject.toml")
        cmd = [executable, "-m", "black", f"--config={config_file_location}"]
        if check_only:
            cmd.append("--check")
            cmd.append("--diff")
        cmd.append(target_dir)

        try:
            return subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=not check_only,
            )
        except subprocess.CalledProcessError as e:
            logger.error(f"Black formatting failed for {target_dir}: {e}")
            if e.stderr:
                logger.error(e.stderr.decode("utf-8"))
            return None
