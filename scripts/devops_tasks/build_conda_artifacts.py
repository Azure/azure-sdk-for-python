#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# Used to 
# 


import argparse
import sys
import os

from common_tasks import process_glob_string, run_check_call, str_to_bool


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Build Azure Packages, Called from DevOps YAML Pipeline"
    )
    parser.add_argument(
        "-d",
        "--distribution-directory",
        dest="distribution_directory",
        help="The path to the output directory",
        required=True,
    )

    parser.add_argument(
        "glob_string",
        nargs="?",
        help=(
            "A comma separated list of glob strings that will target the top level directories that contain packages. "
            'Examples: All == "azure-*", Single = "azure-keyvault"'
        ),
    )


    parser.add_argument(
        "--meta",
        help=(
            "Location of the meta yml"
        ),
    )

    parser.add_argument(
        "--output_var",
        help=(
            ""
        ),
    )
    

    args = parser.parse_args()
    output_source_location = "a_new_location"

    if args.output_var:
        print("##vso[task.setvariable variable={}]{}".format(args.output_var, output_source))