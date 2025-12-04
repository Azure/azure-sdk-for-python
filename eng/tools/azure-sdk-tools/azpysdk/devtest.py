import argparse
import sys
import os

from typing import Optional, List
import subprocess
from subprocess import CalledProcessError, check_call

from .Check import Check
from ci_tools.functions import install_into_venv, get_pip_command, discover_targeted_packages
from ci_tools.scenario.generation import create_package_and_install
from ci_tools.variables import discover_repo_root, in_ci, set_envvar_defaults
from ci_tools.environment_exclusions import is_check_enabled
from ci_tools.logging import logger, run_logged

REPO_ROOT = discover_repo_root()
common_task_path = os.path.abspath(os.path.join(REPO_ROOT, "scripts", "devops_tasks"))
sys.path.append(common_task_path)

from common_tasks import get_installed_packages

EXCLUDED_PKGS = [
    "azure-common",
]

# index URL to devops feed
DEV_INDEX_URL = "https://pkgs.dev.azure.com/azure-sdk/public/_packaging/azure-sdk-for-python/pypi/simple"

def get_installed_azure_packages(pkg_name_to_exclude):
    # This method returns a list of installed azure sdk packages
    installed_pkgs = [
        p.split("==")[0] for p in get_installed_packages() if p.startswith("azure-")
    ]

    # Get valid list of Azure SDK packages in repo
    pkgs = discover_targeted_packages("", REPO_ROOT)
    valid_azure_packages = [
        os.path.basename(p) for p in pkgs if "mgmt" not in p and "-nspkg" not in p
    ]

    # Filter current package and any exlcuded package
    pkg_names = [
        p
        for p in installed_pkgs
        if p in valid_azure_packages
        and p != pkg_name_to_exclude
        and p not in EXCLUDED_PKGS
    ]

    logger.info("Installed azure sdk packages: %s", pkg_names)
    return pkg_names

def uninstall_packages(packages):
    # This method uninstall list of given packages so dev build version can be reinstalled
    commands = get_pip_command()
    commands.append("uninstall")

    logger.info("Uninstalling packages: %s", packages)
    commands.extend(packages)
    # Pass Uninstall confirmation
    commands.append("--yes")
    check_call(commands)
    logger.info("Uninstalled packages")

def install_packages(packages):
    # install list of given packages from devops feed

    commands = get_pip_command()
    commands.append("install")

    logger.info("Installing dev build version for packages: %s", packages)
    commands.extend(packages)
    commands.extend(
        [
            "--index-url",
            DEV_INDEX_URL,
        ]
    )
    # install dev build of azure packages
    check_call(commands)

def install_dev_build_packages(pkg_name_to_exclude):
    # Uninstall GA version and reinstall dev build version of dependent packages
    azure_pkgs = get_installed_azure_packages(pkg_name_to_exclude)
    uninstall_packages(azure_pkgs)
    install_packages(azure_pkgs)

class devtest(Check):
    def __init__(self) -> None:
        super().__init__()

    def register(
        self, subparsers: "argparse._SubParsersAction", parent_parsers: Optional[List[argparse.ArgumentParser]] = None
    ) -> None:
        """Register the devtest check. The devtest check tests a package against dependencies installed from a dev index."""
        parents = parent_parsers or []
        p = subparsers.add_parser("devtest", parents=parents, help="Run the devtest check to test a package against dependencies installed from a dev index")
        p.set_defaults(func=self.run)

    def run(self, args: argparse.Namespace) -> int:
        """Run the devtest check command."""
        logger.info("Running devtest check...")

        set_envvar_defaults()
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

            install_dev_build_packages(package_name)

            # invoke pytest


        return max(results) if results else 0
