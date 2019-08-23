# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------

import os
import sys
# Ignore async tests for Python < 3.5
collect_ignore_glob = []
if sys.version_info < (3, 5):
    collect_ignore_glob.append("tests/*_async.py")

os.environ['PYTHONHASHSEED'] = '0'
dirname = os.path.dirname(__file__)
seed_filename = os.path.join(dirname, "seed.txt")

with open(seed_filename, "w+") as f:
    if f.readline():
        os.environ['RUN_IDENTIFIER'] = f.readline().strip()
    else:
        if "RUN_IDENTIFIER" not in os.environ:
            print("Please set your RUN_IDENTIFIER environment variable in seed.txt")
            raise NameError
        f.write(os.environ["RUN_IDENTIFIER"])
