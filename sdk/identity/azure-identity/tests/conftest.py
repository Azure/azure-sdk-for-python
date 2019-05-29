# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import sys

# Ignore collection of async tests for Python 2
collect_ignore = []
if sys.version_info < (3, 5):
    collect_ignore.append("test_identity_async.py")
