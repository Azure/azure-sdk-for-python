import argparse
import os
import sys

from typing import Optional, List
from subprocess import CalledProcessError, run

from .Check import Check
from ci_tools.functions import install_into_venv, find_whl
from ci_tools.scenario.generation import create_package_and_install
from ci_tools.variables import discover_repo_root, set_envvar_defaults
from ci_tools.logging import logger
from ci_tools.parsing import ParsedSetup

REPO_ROOT = discover_repo_root()


def get_package_wheel_path(pkg_root: str) -> str:
    # parse setup.py to get package name and version
    pkg_details = ParsedSetup.from_path(pkg_root)

    # Check if wheel is already built and available for current package
    prebuilt_dir = os.getenv("PREBUILT_WHEEL_DIR")
    if prebuilt_dir:
        logger.info("Using prebuilt wheel directory: {}".format(prebuilt_dir))
        found_whl = find_whl(prebuilt_dir, pkg_details.name, pkg_details.version)
        pkg_path = os.path.join(prebuilt_dir, found_whl) if found_whl else None
        if not pkg_path:
            raise FileNotFoundError(
                "No prebuilt wheel found for package {} version {} in directory {}".format(
                    pkg_details.name, pkg_details.version, prebuilt_dir
                )
            )
        return pkg_path
    # Otherwise, use wheel created in staging directory, or fall back on source directory
    pkg_path = find_whl(pkg_root, pkg_details.name, pkg_details.version) or pkg_root
    return pkg_path


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
        p.add_argument(
            "--token-file",
            dest="token_file",
            default=False,
            action="store_true",
            help="Generate only the raw APIView token file.",
        )
        p.add_argument(
            "--dest-dir",
            dest="dest_dir",
            default=None,
            help="Destination directory for generated API stub files.",
        )
        p.add_argument(
            "--install-deps",
            dest="install_deps",
            default=False,
            action="store_true",
            help="Install target package dev requirements before running.",
        )
        p.set_defaults(func=self.run)

    def ensure_apistub_dependencies(self, executable: str, package_dir: str, staging_directory: str) -> None:
        try:
            self.run_venv_command(executable, ["-c", "import apistub"], cwd=staging_directory, check=True)
            return
        except CalledProcessError:
            logger.info("apistub module is not installed. Installing APIView dependencies.")

        install_into_venv(
            executable,
            [
                "-r",
                os.path.join(REPO_ROOT, "eng", "apiview_reqs.txt"),
                "--index-url=https://pkgs.dev.azure.com/azure-sdk/public/_packaging/azure-sdk-for-python/pypi/simple/",
            ],
            package_dir,
        )

    def run(self, args: argparse.Namespace) -> int:
        """Run the apistub check command."""
        logger.info("Running apistub check...")

        token_file = getattr(args, "token_file", False)
        generate_markdown = not token_file

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
            logger.info(f"Processing {package_name} for apistub check")

            install_deps = getattr(args, "install_deps", False)

            if install_deps:
                # install dependencies
                self.install_dev_reqs(executable, args, package_dir)

            try:
                self.ensure_apistub_dependencies(executable, package_dir, staging_directory)
            except (CalledProcessError, RuntimeError) as e:
                logger.error(f"Failed to install APIView dependencies: {e}")
                return getattr(e, "returncode", 1)

            if not os.getenv("PREBUILT_WHEEL_DIR"):
                create_package_and_install(
                    distribution_directory=staging_directory,
                    target_setup=package_dir,
                    skip_install=True,
                    cache_dir=None,
                    work_dir=staging_directory,
                    force_create=False,
                    package_type="wheel",
                    pre_download_disabled=False,
                    python_executable=executable,
                )

            if install_deps:
                self.pip_freeze(executable)

            pkg_path = get_package_wheel_path(package_dir)
            pkg_path = os.path.abspath(pkg_path)

            out_token_path = os.path.abspath(getattr(args, "dest_dir", None) or package_dir)
            os.makedirs(out_token_path, exist_ok=True)

            cross_language_mapping_path = get_cross_language_mapping_path(package_dir)

            if cross_language_mapping_path:
                cross_language_mapping_path = os.path.abspath(cross_language_mapping_path)

            cmds = ["-m", "apistub", "--pkg-path", pkg_path]

            if out_token_path:
                cmds.extend(["--out-path", out_token_path])
            if cross_language_mapping_path:
                cmds.extend(["--mapping-path", cross_language_mapping_path])
            if generate_markdown:
                cmds.append("--skip-pylint")

            logger.info("Running apistub {}.".format(cmds))

            try:
                self.run_venv_command(executable, cmds, cwd=staging_directory, check=True, immediately_dump=True)
                token_json_path = os.path.join(out_token_path, f"{package_name}_python.json")
                if token_file:
                    if os.path.exists(token_json_path):
                        logger.info(f"Generated APIView token file: {token_json_path}")
                    else:
                        logger.error(f"Expected APIView token file was not generated: {token_json_path}")
                        results.append(1)
                else:
                    md_script = os.path.join(REPO_ROOT, "eng", "common", "scripts", "Export-APIViewMarkdown.ps1")
                    metadata_script = os.path.join(REPO_ROOT, "eng", "scripts", "Extract-APIViewMetadata-Python.ps1")
                    logger.info(f"Generating api.md for {package_name}")
                    try:
                        result = run(
                            ["pwsh", md_script, "-TokenJsonPath", token_json_path, "-OutputPath", out_token_path],
                            check=True,
                            capture_output=True,
                            text=True,
                        )
                        # pwsh script logs the api.md location
                        if result.stdout:
                            logger.info(result.stdout)

                        logger.info(f"Extracting API metadata for {package_name}")
                        metadata_result = run(
                            ["pwsh", metadata_script, "-OutputPath", out_token_path],
                            check=True,
                            capture_output=True,
                            text=True,
                        )
                        if metadata_result.stdout:
                            logger.info(metadata_result.stdout)
                    except FileNotFoundError:
                        logger.error("Failed to generate api.md: pwsh (PowerShell) is not installed or not on PATH.")
                        results.append(1)
                    except CalledProcessError as e:
                        logger.error(f"Failed to generate api.md or extract metadata (exit code {e.returncode}):")
                        if e.stderr:
                            logger.error(e.stderr)
                        if e.stdout:
                            logger.error(e.stdout)
                        results.append(1)
            except CalledProcessError as e:
                logger.error(f"{package_name} exited with error {e.returncode}: {e}")
                results.append(e.returncode)

        return max(results) if results else 0
