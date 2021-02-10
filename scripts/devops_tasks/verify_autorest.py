#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import argparse
from git import Repo
import os
import logging
import sys

from common_tasks import run_check_call

logging.getLogger().setLevel(logging.INFO)

root_dir = os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "..", ".."))
sdk_dir = os.path.join(root_dir, "sdk")


def run_autorest(service_dir):
    
    pass


def check_diff():
    repo = Repo(root_dir)
    t = repo.head.commit.tree
    d = repo.git.diff(t)
    if d:
        raise ValueError(
            "Found difference between re-generated code and current commit. \
                Please re-generate with the latest autorest."
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run autorest to verify generated code.')
    parser.add_argument(
        'service_directory',
        help="Directory of the package being tested"
    )

    args = parser.parse_args()
    run_autorest(args.service_directory)

    check_diff()
