import argparse
import os
import sys

from typing import Optional, List
from subprocess import CalledProcessError, run

from .Check import Check
from ci_tools.functions import install_into_venv, find_whl
from ci_tools.scenario.generation import create_package_and_install
from ci_tools.variables import discover_repo_root, set_envvar_defaults, in_ci
from ci_tools.logging import logger
from ci_tools.parsing import ParsedSetup

REPO_ROOT = discover_repo_root()
PYTHON_VERSION_LIMIT = (3, 11)  # apistub doesn't support Python 3.11+


def get_package_wheel_path(pkg_root: str, staging_dir: str = None) -> str:
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
    # Check staging directory first (wheel built by create_package_and_install)
    if staging_dir:
        found_whl = find_whl(staging_dir, pkg_details.name, pkg_details.version)
        if found_whl:
            return os.path.join(staging_dir, found_whl)
    # Otherwise, use wheel in source directory, or fall back on source directory
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
            "--dest-dir",
            dest="dest_dir",
            default=None,
            help="Destination directory for generated API stub token files.",
        )
        p.add_argument(
            "--md",
            dest="generate_md",
            default=False,
            action="store_true",
            help="Generate api.md from the JSON token file using Export-APIViewMarkdown.ps1. Output directory for api.md is the same as the generated token file.",
        )
        p.set_defaults(func=self.run)

    def run(self, args: argparse.Namespace) -> int:
        """Run the apistub check command."""
        logger.info("Running apistub check...")

        if sys.version_info >= PYTHON_VERSION_LIMIT:
            logger.error(
                f"Python version {sys.version_info.major}.{sys.version_info.minor} is not supported. Version must be less than {PYTHON_VERSION_LIMIT[0]}.{PYTHON_VERSION_LIMIT[1]}."
            )
            return 1

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

            if not os.getenv("PREBUILT_WHEEL_DIR"):
                try:
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
                except Exception as e:
                    logger.error(f"{package_name}: failed to build/install wheel: {e}")
                    results.append(1)
                    continue

            self.pip_freeze(executable)

            pkg_path = get_package_wheel_path(package_dir, staging_directory)
            pkg_path = os.path.abspath(pkg_path)

            if in_ci():
                # In CI, pre-install the package and its deps into the venv so that when
                # apistubgen's internal _install_package() runs pip install, all
                # dependencies are already satisfied and the call finishes instantly
                # instead of hitting the 120s timeout under parallel CI load. Locally,
                # apistubgen handles this install itself.
                install_into_venv(executable, [pkg_path], package_dir)

            dest_dir = getattr(args, "dest_dir", None)
            if dest_dir:
                out_token_path = os.path.join(os.path.abspath(dest_dir), package_name)
                os.makedirs(out_token_path, exist_ok=True)
            else:
                out_token_path = os.path.abspath(staging_directory)

            cross_language_mapping_path = get_cross_language_mapping_path(package_dir)

            if cross_language_mapping_path:
                cross_language_mapping_path = os.path.abspath(cross_language_mapping_path)

            cmds = ["-m", "apistub", "--pkg-path", pkg_path]

            if out_token_path:
                cmds.extend(["--out-path", out_token_path])
            if cross_language_mapping_path:
                cmds.extend(["--mapping-path", cross_language_mapping_path])
            if getattr(args, "generate_md", False):
                cmds.append("--skip-pylint")

            logger.info("Running apistub {}.".format(cmds))

            try:
                apistub_result = self.run_venv_command(
                    executable, cmds, cwd=staging_directory, check=False, immediately_dump=False
                )
                if apistub_result.stdout:
                    logger.info(apistub_result.stdout)
                if apistub_result.stderr:
                    logger.warning(apistub_result.stderr)
                if apistub_result.returncode != 0:
                    logger.error(f"{package_name} apistub exited with code {apistub_result.returncode}")
                    results.append(apistub_result.returncode)
                    continue
                if getattr(args, "generate_md", False):
                    token_json_path = os.path.join(out_token_path, f"{package_name}_python.json")
                    md_script = os.path.join(REPO_ROOT, "eng", "common", "scripts", "Export-APIViewMarkdown.ps1")
                    if not os.path.exists(token_json_path):
                        logger.error(f"Token JSON not found at expected path: {token_json_path}")
                        results.append(1)
                        continue
                    logger.info(f"Generating api.md for {package_name}")
                    # When no --dest-dir is given, write api.md directly into the package
                    # directory so it is tracked by git. When --dest-dir is provided, keep
                    # the existing behaviour of writing into <dest_dir>/<package_name>/.
                    md_output_path = package_dir if not dest_dir else out_token_path
                    try:
                        result = run(
                            ["pwsh", md_script, "-TokenJsonPath", token_json_path, "-OutputPath", md_output_path],
                            check=True,
                            capture_output=True,
                            text=True,
                        )
                        # pwsh script logs the api.md location
                        if result.stdout:
                            logger.info(result.stdout)
                    except FileNotFoundError:
                        logger.error("Failed to generate api.md: pwsh (PowerShell) is not installed or not on PATH.")
                        results.append(1)
                    except CalledProcessError as e:
                        logger.error(f"Failed to generate api.md (exit code {e.returncode}):")
                        if e.stderr:
                            logger.error(e.stderr)
                        if e.stdout:
                            logger.error(e.stdout)
                        results.append(1)
            except CalledProcessError as e:
                logger.error(f"{package_name} exited with error {e.returncode}: {e}")
                results.append(e.returncode)

        return max(results) if results else 0
