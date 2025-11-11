import argparse
import os
import sys

from typing import Optional, List
import subprocess
from subprocess import CalledProcessError, check_call

from .Check import Check
from ci_tools.functions import install_into_venv, get_pip_command, find_whl
from ci_tools.scenario.generation import create_package_and_install, get_pip_command
from ci_tools.variables import discover_repo_root, in_ci, set_envvar_defaults
from ci_tools.environment_exclusions import is_check_enabled
from ci_tools.logging import logger, run_logged
from ci_tools.parsing import ParsedSetup

REPO_ROOT = discover_repo_root()


def get_package_wheel_path(pkg_root: str, out_path: str) -> tuple[str, Optional[str]]:
    # parse setup.py to get package name and version
    pkg_details = ParsedSetup.from_path(pkg_root)

    # Check if wheel is already built and available for current package
    prebuilt_dir = os.getenv("PREBUILT_WHEEL_DIR")
    out_token_path = None
    if prebuilt_dir:
        found_whl = find_whl(prebuilt_dir, pkg_details.name, pkg_details.version)
        pkg_path = os.path.join(prebuilt_dir, found_whl) if found_whl else None
        if not pkg_path:
            raise FileNotFoundError(
                "No prebuilt wheel found for package {} version {} in directory {}".format(
                    pkg_details.name, pkg_details.version, prebuilt_dir
                )
            )
        # If the package is a wheel and out_path is given, the token file output path should be the parent directory of the wheel
        if out_path:
            out_token_path = os.path.join(out_path, os.path.basename(os.path.dirname(pkg_path)))
        return pkg_path, out_token_path
    pkg_path = pkg_root
    # If the package is not a wheel and out_path is given, the token file output path should be the same as the target package path
    if out_path:            
        out_token_path = os.path.join(out_path, os.path.basename(pkg_path))
        if not os.path.exists(out_token_path):
            os.makedirs(out_token_path, exist_ok=True)
    return pkg_path, out_token_path


def get_cross_language_mapping_path(pkg_root):
    mapping_path = os.path.join(pkg_root, "apiview-properties.json")
    if os.path.exists(mapping_path):
        return mapping_path
    return None


class apistub(Check):
    def __init__(self) -> None:
        super().__init__()

    def register(
        self, subparsers: "argparse._SubParsersAction", parent_parsers: Optional[List[argparse.ArgumentParser]] = None
    ) -> None:
        """Register the apistub check. The apistub check generates an API stub of the target package."""
        parents = parent_parsers or []
        p = subparsers.add_parser(
            "apistub", parents=parents, help="Run the apistub check to generate an API stub for a package"
        )
        p.set_defaults(func=self.run)

    def run(self, args: argparse.Namespace) -> int:
        """Run the apistub check command."""
        logger.info("Running apistub check...")

        set_envvar_defaults()
        targeted = self.get_targeted_directories(args)

        results: List[int] = []

        for parsed in targeted:
            package_dir = parsed.folder
            package_name = parsed.name
            executable, staging_directory = self.get_executable(args.isolate, args.command, sys.executable, package_dir)
            logger.info(f"Processing {package_name} for apistub check")

            # install dependencies
            self.install_dev_reqs(executable, args, package_dir)

            try:
                install_into_venv(
                    executable,
                    [
                        "-r",
                        os.path.join(REPO_ROOT, "eng", "apiview_reqs.txt"),
                        "--index-url=https://pkgs.dev.azure.com/azure-sdk/public/_packaging/azure-sdk-for-python/pypi/simple/",
                    ],
                    package_dir,
                )
            except CalledProcessError as e:
                logger.error(f"Failed to install dependencies: {e}")
                return e.returncode

            self.pip_freeze(executable)

            # Check if a wheel is already built for current package and install from wheel when available
            # If wheel is not available then install package from source
            pkg_path, out_token_path = get_package_wheel_path(package_dir, staging_directory)
            cross_language_mapping_path = get_cross_language_mapping_path(package_dir)

            cmds = [executable, "-m", "apistub", "--pkg-path", pkg_path]

            if out_token_path:
                cmds.extend(["--out-path", out_token_path])
            if cross_language_mapping_path:
                cmds.extend(["--mapping-path", cross_language_mapping_path])

            logger.info("Running apistubgen {}.".format(cmds))

            try:
                check_call(cmds, cwd=package_dir)
            except CalledProcessError as e:
                logger.error(f"{package_name} exited with error {e.returncode}")
                results.append(e.returncode)

        return max(results) if results else 0
