# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------

import os
import sys
os.environ['PYTHONHASHSEED'] = '0'

# Ignore async tests for Python < 3.5
collect_ignore_glob = []
if sys.version_info < (3, 5):
    collect_ignore_glob.append("tests/*_async.py")

dirname = os.path.dirname(os.path.abspath(__file__))
seed_filename = os.path.abspath(os.path.join(dirname, "seed.txt"))

run_identifier_set = False

try:
    with open(seed_filename, "r") as f:
        if os.path.getsize(seed_filename):
            os.environ['RUN_IDENTIFIER'] = f.readline().strip()
            run_identifier_set = True
except FileNotFoundError:
    # if file has not yet been created
    if "RUN_IDENTIFIER" not in os.environ:
        print("Please set your RUN_IDENTIFIER environment variable in seed.txt")
        raise NameError
    with open(seed_filename, "w") as f:
        f.write(os.environ["RUN_IDENTIFIER"])

# if file is created but empty
if not run_identifier_set:
    if "RUN_IDENTIFIER" not in os.environ:
        print("Please set your RUN_IDENTIFIER environment variable in seed.txt")
        raise NameError
    with open(seed_filename, "w") as f:
        f.write(os.environ["RUN_IDENTIFIER"])