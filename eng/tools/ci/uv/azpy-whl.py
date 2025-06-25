#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.9"
# dependencies = [
#   "wheel==0.45.1",
#   "packaging==24.2",
#   "urllib3==2.2.3",
#   "tomli",
#   "build==1.2.2.post1",
#   "pytest==8.3.5",
#   "pytest-cov==5.0.0",
#   "azure-sdk-tools",
#   "setuptools",
#   "pytest-asyncio==0.24.0",
#   "pytest-custom-exit-code==0.3.0",
#   "pytest-xdist==3.2.1",
#   "coverage==7.6.1",
#   "bandit==1.6.2",
#   "pyproject-api==1.8.0",
#   "jinja2==3.1.6",
#   "json-delta==2.0.2",
#   "readme-renderer==43.0",
#   "python-dotenv==1.0.1",
#   "pyyaml==6.0.2",
#   "six==1.17.0",
#   "uv",
# ]
#
# [tool.uv.sources]
# azure-sdk-tools = { path = "../../../../tools/azure-sdk-tools", editable = true }
# ///

import os
import argparse

from ci_tools.functions import discover_targeted_packages

from ci_tools.uv import install_uv_devrequirements, set_environment_variable_defaults, DEFAULT_ENVIRONMENT_VARIABLES, uv_pytest
from ci_tools.variables import discover_repo_root
from ci_tools.scenario.generation import create_package_and_install
import tempfile
import shutil
import os

def main():
    parser = argparse.ArgumentParser(
        description="Run dev tooling against a given package directory"
    )
    parser.add_argument(
        "target",
        nargs="?",
        default="azure-core",
        help="Path to the target package folder (default: current directory)",
    )
    args = parser.parse_args()

    set_environment_variable_defaults(DEFAULT_ENVIRONMENT_VARIABLES)

    # todo, we should use os.cwd as the target if no target is provided
    # with some validation to ensure we're in a package directory (eg setup.py or pyproject.toml exists) and not repo root.
    target_root_dir=discover_repo_root()
    targeted = discover_targeted_packages(args.target, target_root_dir)

    failed = False

    for pkg in targeted:
        install_uv_devrequirements(
            pkg_path=pkg,
            allow_nonpresence=True,
        )

        staging_area = tempfile.mkdtemp()

        create_package_and_install(
            distribution_directory=staging_area,
            target_setup=pkg,
            skip_install=False,
            cache_dir=None,
            work_dir=staging_area,
            force_create=False,
            package_type="wheel",
            pre_download_disabled=False,
        )

        uv_pytest(target_path=pkg, additional_args=["--cov", "--cov-report=xml", "--cov-report=html"])

if __name__ == "__main__":
    main()
