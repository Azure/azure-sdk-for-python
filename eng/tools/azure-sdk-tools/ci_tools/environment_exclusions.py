#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from ci_tools.parsing import get_config_setting
from ci_tools.variables import in_public, in_analyze_weekly
import os
from typing import Any

# --------------------------------------------------------------------------------------------------------------------
# DO NOT add packages to the below lists. They are used to omit packages that will never run type checking.
#
# For CI exclusion of type checks, look into adding a pyproject.toml, as indicated in the `The pyproject.toml` section
# of `.doc/eng_sys_checks.md`.

IGNORE_FILTER = ["nspkg", "cognitiveservices"]
FILTER_EXCLUSIONS = []
IGNORE_PACKAGES = [
    "azure-applicationinsights",
    "azure-servicemanagement-legacy",
    "azure",
    "azure-storage",
    "azure-monitor",
    "azure-servicefabric",
    "azure-keyvault",
    "azure-synapse",
    "azure-common",
    "conda-recipe",
    "azure-graphrbac",
    "azure-loganalytics",
    "azure-media-analytics-edge",
    "azure-media-videoanalyzer-edge",
    "azure-template",
]

MUST_RUN_ENVS = ["bandit"]

# all of our checks default to ON, other than the below
CHECK_DEFAULTS = {"black": False}


def is_check_enabled(package_path: str, check: str, default: Any = True) -> bool:
    """
    Single-use function to evaluate whether or not a given check should run against a package.

    In order:
     - Checks for `ci_enabled` flag in pyproject.toml and skips all checks if set to false.
       Public and weekly analyze builds ignore this flag.
     - Honors override variable if one is present: <PACKAGE_NAME>_<CHECK>. (Replace `-` with `_` in the package name.)
     - Falls back to the pyproject.toml at package root (if one exists) for a tools setting enabling/disabling <check>.
     - Rejects a disabled apistub check instead of allowing a package-level opt-out.
    """
    if package_path.endswith("setup.py"):
        package_path = os.path.dirname(package_path)

    if package_path == ".":
        package_path = os.getcwd()

    ci_enabled = get_config_setting(package_path, "ci_enabled", True)
    if not in_public() and not in_analyze_weekly() and ci_enabled is False:
        return False

    # now pull the new pyproject.toml configuration
    check = check.strip().lower()
    config = get_config_setting(package_path, check, default)
    if check == "apistub" and not config:
        raise ValueError(
            f"apistub is required for {package_path} and cannot be disabled. "
            "Remove 'apistub = false' from [tool.azure-sdk-build] in pyproject.toml "
            "and any disabling <PACKAGE_NAME>_APISTUB environment override."
        )

    return config


def is_typing_ignored(package_name: str) -> bool:
    """
    Evaluates a package name and evaluates whether or not this package should be ignored when invoking type checking.
    """
    if package_name in IGNORE_PACKAGES:
        return True
    if package_name not in FILTER_EXCLUSIONS and any([identifier in package_name for identifier in IGNORE_FILTER]):
        return True
    return False
