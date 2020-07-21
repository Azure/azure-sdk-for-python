#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.

from subprocess import check_call, CalledProcessError
import argparse
import os
import logging
import sys


logging.getLogger().setLevel(logging.INFO)

root_dir = os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "..", ".."))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run apistubgen against target folder. ")

    parser.add_argument(
        "-t",
        "--target",
        dest="target_package",
        help="The target package directory on disk.",
        required=True,
    )

    parser.add_argument(
        "-w",
        "--work_dir",
        dest="work_dir",
        help="Working directory to run apistubgen",
        required=True,
    )


    args = parser.parse_args()
    check_call(
        [
                "apistubgen",
                "--pkg-path",
                args.target_package,
            ],

            cwd=args.work_dir
    )

        
