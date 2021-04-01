#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# This script is used to execute bandit within a tox environment. Depending on which package is being executed against,
# a failure may be suppressed.


from subprocess import check_call, CalledProcessError
import argparse
import os
import logging
import sys
import pdb

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
        help="an integer for the accumulator",
    )

    args = parser.parse_args()

    print(args.imports)

    importable_packages = []

    for ns in list(args.imports):
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
