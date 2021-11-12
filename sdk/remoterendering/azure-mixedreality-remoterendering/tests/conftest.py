# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import sys

# Ignore collection of async tests for Python 2
collect_ignore_glob = []
if sys.version_info < (3, 5):
    collect_ignore_glob.append("*_async.py")
