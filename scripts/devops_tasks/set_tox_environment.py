#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import argparse, os
from typing import List

from ci_tools.ci_interactions import set_ci_variable, output_ci_warning
from ci_tools.build import discover_targeted_packages
from ci_tools.environment_exclusions import is_check_enabled

FULL_BUILD_SET = [
    "whl",
    "sdist",
    "depends",
    "latestdependency",
    "mindependency",
    "whl_no_aio",
]
PR_BUILD_SET = ["whl", "sdist", "mindependency"]


def resolve_devops_variable(var_value: str) -> List[str]:
    if var_value:
        if var_value.startswith("$("):
            return []
        else:
            return [tox_env.strip() for tox_env in var_value.split(",") if tox_env.strip()]


def set_devops_value(resolved_set: List[str]) -> None:
    string_value = ",".join(resolved_set)
    set_ci_variable("toxenv", string_value)


def remove_unsupported_values(selected_set: List[str], unsupported_values: List[str]):
    for unsupported_tox_env in unsupported_values:
        if unsupported_tox_env in selected_set:
            selected_set.remove(unsupported_tox_env)


def process_ci_skips(service: str) -> None:
    checks_with_global_skip = ["pylint", "verifywhl", "verifysdist" "bandit", "mypy", "pyright", "verifytypes"]

    root_dir = os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "..", ".."))

    if service:
        target_dir = os.path.join(root_dir, "sdk", service)
    else:
        target_dir = root_dir

    targeted_packages = discover_targeted_packages("azure*", target_dir)

    for check in checks_with_global_skip:
        packages_running_check = []

        for pkg in targeted_packages:
            if is_check_enabled(pkg, check, True):
                packages_running_check.append(pkg)

        if len(packages_running_check) == 0:
            all_packages = set([os.path.basename(pkg) for pkg in targeted_packages])
            set_ci_variable(f"Skip.{check[0].upper()}{check[1:]}", "true")
            output_ci_warning(
                    f"All targeted packages {all_packages} skip the {check} check. Omitting step from build.",
                    "set_tox_environment.py",
            )



if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="This script is used to resolve a set of arguments (that correspond to devops runtime variables) and determine which tox environments should be run for the current job. "
        + "When running against a specific service directory, attempts to find entire analysis steps that can be skipped. EG if pylint is disabled for every package in a given service directory, that "
        + "step should never actually run."
    )

    parser.add_argument("-t", "--team-project", dest="team_project", help="", required=True)

    parser.add_argument(
        "-o",
        "--override",
        dest="override_set",
        help="If you have a set of tox environments that should override the defaults, provide it here. In CI this is runtime variable $(Run.ToxCustomEnvs). EG: \"whl,sdist\".",
    )

    parser.add_argument(
        "-u",
        "--unsupported",
        dest="unsupported",
        help="A list of unsupported environments. EG: \"pylint,sdist\"",
    )

    parser.add_argument(
        "-s",
        "--service",
        dest="service",
        help='If provided, activates secondary capability of this script. If each package in service "A" skips check "pylint", that entire STEP will be skipped.'
        + "If a check is only individually skipped, but still active in other packages of the service, then the step will run and the individual skip logic will apply.",
    )

    args = parser.parse_args()

    team_project = resolve_devops_variable(args.team_project)
    override_set = resolve_devops_variable(args.override_set)
    unsupported = resolve_devops_variable(args.unsupported)

    # by default, we should always start with the default set
    selected_set = PR_BUILD_SET

    # however if we are internal, use the full set
    if "internal" in team_project:
        selected_set = FULL_BUILD_SET

    # if there is an override present, that will win ALWAYS
    if override_set:
        selected_set = override_set

    # however we never run unsupported values
    if unsupported:
        remove_unsupported_values(selected_set, unsupported)

    # and finally set the output variable
    set_devops_value(selected_set)

    if args.service:
        process_ci_skips(args.service)
