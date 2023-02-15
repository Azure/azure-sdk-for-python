#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from ci_tools.functions import get_config_setting
import os

# --------------------------------------------------------------------------------------------------------------------
# DO NOT add packages to the below lists. They are used to omit packages that will never run type checking.
#
# For CI exclusion of type checks, look into adding a pyproject.toml, as indicated in the `The pyproject.toml` section
# of `.doc/eng_sys_checks.md`.

IGNORE_FILTER = ["nspkg", "mgmt", "cognitiveservices"]
FILTER_EXCLUSIONS = ["azure-mgmt-core"]
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


def is_check_enabled(package_path: str, check: str, default: bool = True) -> bool:
    """
    Single-use function to evaluate whether or not a given check should run against a package.

    In order:
     - Checks <CHECK>_OPT_OUT for package name.
     - Honors override variable if one is present: <PACKAGE-NAME>_<CHECK>.
     - Finally falls back to the pyproject.toml at package root (if one exists) for a tools setting enabling/disabling <check>.
    """
    if package_path.endswith("setup.py"):
        package_path = os.path.dirname(package_path)

    if package_path == ".":
        package_path = os.getcwd()

    enabled = default
    package_name = os.path.basename(package_path)

    # now pull the new pyproject.toml configuration
    config = get_config_setting(package_path, check.strip().lower(), True)

    return config and enabled


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
            if is_check_enabled(package_path, tox_env, True):
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
