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
     - Checks <CHECK>_OPT_OUT for package name.
     - Honors override variable if one is present: <PACKAGE_NAME>_<CHECK>. (Note the _ in the package name, `-` is not a valid env variable character.)
     - Checks for `ci_enabled` flag in pyproject.toml and skips all checks if set to false.
     - Finally falls back to the pyproject.toml at package root (if one exists) for a tools setting enabling/disabling <check>.
    """
    if package_path.endswith("setup.py"):
        package_path = os.path.dirname(package_path)

    if package_path == ".":
        package_path = os.getcwd()

    ci_enabled = get_config_setting(package_path, "ci_enabled", True)
    if not in_public() and not in_analyze_weekly() and ci_enabled is False:
        return False

    # now pull the new pyproject.toml configuration
    config = get_config_setting(package_path, check.strip().lower(), default)

    return config


def filter_tox_environment_string(namespace_argument: str, package_path: str) -> str:
    """
    Takes an incoming comma separated list of tox environments and package name. Resolves whether or not
    each given tox environment should run, given comparison to single unified exclusion file in `environment_exclusions`.

    :param namespace_argument: A namespace argument. This takes the form of a comma separated list: "whl,sdist,mindependency". "whl". "lint,pyright,sphinx".
    :param package_path: The path to the package.
    """
    if package_path.endswith("setup.py"):
        package_path = os.path.dirname(package_path)

    if namespace_argument:
        tox_envs = namespace_argument.strip().split(",")
        filtered_set = []

        for tox_env in [env.strip().lower() for env in tox_envs]:
            check_enabled = is_check_enabled(package_path, tox_env, CHECK_DEFAULTS.get(tox_env, True))
            if check_enabled or tox_env in MUST_RUN_ENVS:
                filtered_set.append(tox_env)
        return ",".join(filtered_set)

    return namespace_argument


def is_typing_ignored(package_name: str) -> bool:
    """
    Evaluates a package name and evaluates whether or not this package should be ignored when invoking type checking.
    """
    if package_name in IGNORE_PACKAGES:
        return True
    if package_name not in FILTER_EXCLUSIONS and any([identifier in package_name for identifier in IGNORE_FILTER]):
        return True
    return False
