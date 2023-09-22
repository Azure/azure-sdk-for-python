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


def clean_environment():
    pass


def create_requirements_file(package_folder: str, optional_definition: str):
    pass


def install_requirements_file(package_folder: str):
    pass


def run_tests(package_folder: str):
    pass


def entrypoint():
    parser = argparse.ArgumentParser(
        description="""This entrypoint provides automatic invocation of the 'optional' requirements for a given package. View the pyproject.toml within the targeted package folder to see configuration.""",
    )

    parser.add_argument(
        "-t",
        "--target",
        dest="target",
        help="The target package path"
    )
    args = parser.parse_args()

    parsed_package = ParsedSetup.from_path(args.target)

    if in_ci():
        if not is_check_enabled(args.target, "optional"):
            logging.info(
                f"Package {parsed_package.package_name} opts-out of optional check."
            )
            exit(0)

    