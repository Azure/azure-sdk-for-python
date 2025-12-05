import argparse
import sys
import os
import glob

from typing import Optional, List

from .Check import Check
from ci_tools.functions import (
    install_into_venv,
    uninstall_from_venv,
    is_error_code_5_allowed,
    get_pip_command,
    discover_targeted_packages,
)
from ci_tools.scenario.generation import create_package_and_install
from ci_tools.variables import discover_repo_root, set_envvar_defaults
from ci_tools.logging import logger

REPO_ROOT = discover_repo_root()
common_task_path = os.path.abspath(os.path.join(REPO_ROOT, "scripts", "devops_tasks"))
sys.path.append(common_task_path)

from common_tasks import get_installed_packages

EXCLUDED_PKGS = [
    "azure-common",
]

# index URL to devops feed
DEV_INDEX_URL = "https://pkgs.dev.azure.com/azure-sdk/public/_packaging/azure-sdk-for-python/pypi/simple"

TEST_TOOLS_REQUIREMENTS = os.path.join(REPO_ROOT, "eng/test_tools.txt")


def get_installed_azure_packages(executable: str, pkg_name_to_exclude: str) -> List[str]:
    """
    Returns a list of installed Azure SDK packages in the venv, excluding specified packages.

    :param executable: Path to the Python executable in the venv.
    :param pkg_name_to_exclude: Package name to exclude from the result.
    :return: List of installed Azure SDK package names.
    """
    venv_root = os.path.dirname(os.path.dirname(executable))
    # Find site-packages directory within the venv
    site_packages_pattern = os.path.join(venv_root, "lib", "python*", "site-packages")
    site_packages_dirs = glob.glob(site_packages_pattern)
    installed_pkgs = [p.split("==")[0] for p in get_installed_packages(site_packages_dirs) if p.startswith("azure-")]

    # Get valid list of Azure SDK packages in repo
    pkgs = discover_targeted_packages("", REPO_ROOT)
    valid_azure_packages = [os.path.basename(p) for p in pkgs if "mgmt" not in p and "-nspkg" not in p]

    # Filter current package and any excluded package
    pkg_names = [
        p for p in installed_pkgs if p in valid_azure_packages and p != pkg_name_to_exclude and p not in EXCLUDED_PKGS
    ]

    logger.info("Installed azure sdk packages: %s", pkg_names)
    return pkg_names


def uninstall_packages(executable: str, packages: List[str], working_directory: str):
    """
    Uninstalls a list of packages from the virtual environment so dev build versions can be reinstalled.

    :param executable: Path to the Python executable in the virtual environment.
    :param packages: List of package names to uninstall.
    :param working_directory: Directory from which to run the uninstall command.
    :raises Exception: If uninstallation fails.
    :return: None
    """
    if len(packages) == 0:
        logger.warning("No packages to uninstall.")
        return

    logger.info("Uninstalling packages: %s", packages)

    try:
        uninstall_from_venv(executable, packages, working_directory)
    except Exception as e:
        logger.error(f"Failed to uninstall packages: {e}")
        raise e
    logger.info("Uninstalled packages")


def install_packages(executable: str, packages: List[str], working_directory: str):
    # install list of given packages from devops feed
    if len(packages) == 0:
        logger.warning("No packages to install.")
        return

    logger.info("Installing dev build version for packages: %s", packages)

    commands = packages
    commands.extend(
        [
            "--index-url",
            DEV_INDEX_URL,
        ]
    )

    # install dev build of azure packages
    try:
        install_into_venv(executable, commands, working_directory)
    except Exception as e:
        logger.error(f"Failed to install packages: {e}")
        raise e
    logger.info("Installed dev build version for packages")


def install_dev_build_packages(executable: str, pkg_name_to_exclude: str, working_directory: str):
    # Uninstall GA version and reinstall dev build version of dependent packages
    azure_pkgs = get_installed_azure_packages(executable, pkg_name_to_exclude)
    uninstall_packages(executable, azure_pkgs, working_directory)
    install_packages(executable, azure_pkgs, working_directory)


class devtest(Check):
    def __init__(self) -> None:
        super().__init__()

    def register(
        self, subparsers: "argparse._SubParsersAction", parent_parsers: Optional[List[argparse.ArgumentParser]] = None
    ) -> None:
        """Register the devtest check. The devtest check tests a package against dependencies installed from a dev index."""
        parents = parent_parsers or []
        p = subparsers.add_parser(
            "devtest",
            parents=parents,
            help="Run the devtest check to test a package against dependencies installed from a dev index",
        )
        p.set_defaults(func=self.run)
        p.add_argument(
            "--pytest-args",
            nargs=argparse.REMAINDER,
            help="Additional arguments forwarded to pytest.",
        )

    def run(self, args: argparse.Namespace) -> int:
        """Run the devtest check command."""
        logger.info("Running devtest check...")

        set_envvar_defaults({"PROXY_URL": "http://localhost:5002"})
        targeted = self.get_targeted_directories(args)

        results: List[int] = []

        for parsed in targeted:
            package_dir = parsed.folder
            package_name = parsed.name
            executable, staging_directory = self.get_executable(args.isolate, args.command, sys.executable, package_dir)
            logger.info(f"Processing {package_name} for devtest check")

            # install dependencies
            self.install_dev_reqs(executable, args, package_dir)

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

            if os.path.exists(TEST_TOOLS_REQUIREMENTS):
                try:
                    install_into_venv(executable, ["-r", TEST_TOOLS_REQUIREMENTS], package_dir)
                except Exception as e:
                    logger.error(f"Failed to install test tools requirements: {e}")
                    results.append(1)
                    continue
            else:
                logger.warning(f"Test tools requirements file not found at {TEST_TOOLS_REQUIREMENTS}.")

            try:
                install_dev_build_packages(executable, package_name, package_dir)
            except Exception as e:
                logger.error(f"Failed to install dev build packages: {e}")
                results.append(1)
                continue

            pytest_args = self._build_pytest_args(package_dir, args)

            pytest_result = self.run_venv_command(
                executable, ["-m", "pytest", *pytest_args], cwd=package_dir, immediately_dump=True
            )

            if pytest_result.returncode != 0:
                if pytest_result.returncode == 5 and is_error_code_5_allowed(package_dir, package_name):
                    logger.info(
                        "pytest exited with code 5 for %s, which is allowed for management or opt-out packages.",
                        package_name,
                    )
                    # Align with tox: skip coverage when tests are skipped entirely
                    continue

                logger.error(f"pytest failed for {package_name} with exit code {pytest_result.returncode}.")
                results.append(pytest_result.returncode)

        return max(results) if results else 0
