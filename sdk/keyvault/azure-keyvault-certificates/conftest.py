# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import sys
import os

# Ignore async tests for Python < 3.5
collect_ignore_glob = []
if sys.version_info < (3, 5):
    collect_ignore_glob.append("tests/*_async.py")

identifier = os.environ.get("RUN_IDENTIFIER")
if not identifier:
    # get the run identifier for unique test runs
    dirname = os.path.dirname(__file__)
    seed_filename = os.path.abspath(os.path.join(dirname, "tests", "seed.txt"))

    # definitely not running in pipeline
    with open(seed_filename, "r") as f:
        os.environ["RUN_IDENTIFIER"] = f.read()
