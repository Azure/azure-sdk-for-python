#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# This script is used to execute pylint within a tox environment. Depending on which package is being executed against,
# a failure may be suppressed.

from subprocess import check_call, CalledProcessError
import argparse
import os
import logging
import sys
from typing import Optional

from ci_tools.environment_exclusions import is_check_enabled
from ci_tools.parsing import ParsedSetup
from ci_tools.variables import in_ci

logging.getLogger().setLevel(logging.INFO)

root_dir = os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "..", ".."))
# Add custom pylint plugin to path
lint_plugin_path = os.path.join(root_dir, "scripts", "pylint_custom_plugin")


def get_top_level_module_path(package_dir: Optional[str]) -> Optional[str]:
    """Tries to return the path to the top level module for the package.

    :param Optional[str] package_dir: Path to package, or None

    :return: None if package_dir is None or package opted out from pylint
             str path to top level module otherwise
    """
    if not package_dir:
        return None

    pkg_details = ParsedSetup.from_path(os.path.abspath(package_dir))
    top_level_module = pkg_details.namespace.split(".")[0]

    if in_ci() and not is_check_enabled(package_dir, "pylint"):
        logging.info(f"Package {pkg_details.name} opts-out of pylint check.")
        return None

    return os.path.join(package_dir, top_level_module)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run pylint against target folder. "
        "Extra parameters that are not listed below are forwarded to pylint."
    )

    parser.add_argument("--pylint-help", action="store_true", help="Show pylint's help and exit.", required=False)

    parser.add_argument(
        "-t",
        "--target",
        dest="target_package",
        help="The target package directory on disk. The target module passed to pylint will be <target_package>/azure.",
        required=False,
    )

    parser.add_argument(
        "--next",
        action="store_true",
        help="Next version of pylint is being tested.",
        required=False,
    )

    args, pylint_args = parser.parse_known_args()
    rcFileLocation = os.path.join(root_dir, "eng" if args.next else "", "pylintrc")
    targetPackagePath = get_top_level_module_path(args.target_package)

    if targetPackagePath:
        pylint_args.insert(0, targetPackagePath)
    if args.pylint_help:
        pylint_args.insert(0, "--help")

    try:
        check_call(
            [
                sys.executable,
                "-m",
                "pylint",
                "--rcfile={}".format(rcFileLocation),
                "--output-format=parseable",
                *pylint_args,
            ]
        )
    except CalledProcessError as e:
        logging.error("pylint exited with linting error {}".format(e.returncode))
        exit(1)
