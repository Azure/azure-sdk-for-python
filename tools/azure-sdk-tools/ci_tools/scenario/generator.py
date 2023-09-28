from typing import List, Any
import argparse

import os
import sys

try:
    import tomllib as toml
except:
    import tomli as toml
import tomli_w as tomlw
import logging

from ci_tools.environment_exclusions import (
    is_check_enabled
)
from ci_tools.variables import in_ci
from ci_tools.parsing import ParsedSetup
from ci_tools.functions import get_config_setting


def clean_environment():
    pass


def create_requirements_file(package_folder: str, optional_definition: str):
    pass


def install_requirements_file(package_folder: str):
    pass


def run_tests(package_folder: str):
    pass


def create_scenario_file(package_folder: str, optional_config: str) -> str:
    """
    Used to coalesce 3 items:
        - The package being installed
        - The dev_requirements for the package
        - An optional config, which includes possible additions to the install list

    And create a single file installable by `pip install -r <>`

    This file will be dropped into the package root, but gitignored. It is regenerated with every invocation of the `optional` env.
    """
    pass

def entrypoint():
    parser = argparse.ArgumentParser(
        description="""This entrypoint provides automatic invocation of the 'optional' requirements for a given package. View the pyproject.toml within the targeted package folder to see configuration.""",
    )

    parser.add_argument(
        "-t",
        "--target",
        dest="target",
        help="The target package path",
        required=True
    )

    parser.add_argument(
        "-o",
        "--optional",
        dest="optional",
        help="The target environment. If not matched to any of the named optional environments, hard exit. If not provided, all optional environments will be run.",
        required=False
    )

    args, unknown = parser.parse_known_args()
    parsed_package = ParsedSetup.from_path(args.target)

    if in_ci():
        if not is_check_enabled(args.target, "optional"):
            logging.info(
                f"Package {parsed_package.package_name} opts-out of optional check."
            )
            exit(0)

    optional_configs = get_config_setting(args.target, "optional")

    if len(optional_configs) == 0:
        logging.info(f"No optional environments detected in pyproject.toml within {args.target}.")
        exit(0)

    for config in optional_configs:
        # clean if necessary

        # install package, dev_reqs, and any additional packages from optional configuration

        # uninstall anything additional
        breakpoint()
