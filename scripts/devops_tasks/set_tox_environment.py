#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import argparse

FULL_BUILD_SET = [
    "whl",
    "sdist",
    "depends",
    "latestdependency",
    "mindependency",
    "whl_no_aio",
]
PR_BUILD_SET = ["whl", "sdist", "mindependency"]


def resolve_devops_variable(var_value):
    if var_value.startswith("$("):
        return []
    else:
        return [tox_env.strip() for tox_env in var_value.split(",") if tox_env.strip()]


def set_devops_value(resolved_set):
    string_value = ",".join(resolved_set)

    print('Setting environment variable toxenv with value "{}"'.format(string_value))
    print("##vso[task.setvariable variable=toxenv]{}".format(string_value))


def remove_unsupported_values(selected_set, unsupported_values):
    for unsupported_tox_env in unsupported_values:
        if unsupported_tox_env in selected_set:
            selected_set.remove(unsupported_tox_env)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="This script is used to resolve a set of arguments (that correspond to devops runtime variables) and determine which tox environments should be run for the current job."
    )

    parser.add_argument(
        "-t", "--team-project", dest="team_project", help="", required=True
    )

    parser.add_argument(
        "-o",
        "--override",
        dest="override_set",
        help="",
    )

    parser.add_argument(
        "-u",
        "--unsupported",
        dest="unsupported",
        help="",
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
    remove_unsupported_values(selected_set, unsupported)

    # and finally output
    set_devops_value(selected_set)
