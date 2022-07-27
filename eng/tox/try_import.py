#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# This script is used to verify that packages are not importable. This is especially useful when
# running checks without the presence of "optional" packages like aiohttp.


import argparse
import logging
import os
import sys

root_dir = os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "..", ".."))
from ci_tools.parsing import ParsedSetup, get_name_from_specifier

logging.getLogger().setLevel(logging.INFO)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Ensures that an environment doesn't have specific packages."
    )

    parser.add_argument(
        "imports",
        metavar="N",
        type=str,
        nargs="+",
        help="The set of packages that we shouldn't be able to import.",
    )

    parser.add_argument(
        "-p",
        "--path-to-setup",
        dest="target_setup",
        help="The path to the setup.py (not including the file) for the package that we are running try_import alongside. The key here is that if a package on our 'check' list actually requires something, we will not fail the check.",
    )

    args = parser.parse_args()

    acceptable_to_import = []
    if args.target_setup:

        reqs = ParsedSetup.from_path(args.target_setup).requires
        acceptable_to_import = [get_name_from_specifier(req).strip() for req in reqs]

    importable_packages = []

    for ns in [ns for ns in list(args.imports) if ns not in acceptable_to_import]:
        try:
            logging.info("Ensuring that namespace {} is not importable.".format(ns))
            exec("import {}".format(ns))
            importable_packages.append(ns)
        except ImportError:
            logging.info("Hit expected import error against {}".format(ns))
            pass

    if importable_packages:
        raise Exception(
            "Was erroneously able to import from {}".format(importable_packages)
        )
