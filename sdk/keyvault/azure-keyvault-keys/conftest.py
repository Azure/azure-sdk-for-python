# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------

import sys
os.environ['PYTHONHASHSEED'] = '0'

# Ignore async tests for Python < 3.5
collect_ignore_glob = []
if sys.version_info < (3, 5):
    collect_ignore_glob.append("tests/*_async.py")

identifier = os.environ.get("RUN_IDENTIFIER")
if not identifier:
    # get the run identifier for unique test runs
    dirname = os.path.dirname(os.path.abspath(__file__))
    seed_filename = os.path.abspath(os.path.join(dirname, "tests", "seed.txt"))

    # definitely not running in pipeline
    # could be running locally under direction of ignorant or negligent dev
    with open(seed_filename, 'r') as f:
        os.environ['RUN_IDENTIFIER'] = f.read()
