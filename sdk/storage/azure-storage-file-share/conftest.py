# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import sys
import pytest
import platform


# Ignore async tests for Python < 3.5
collect_ignore_glob = []
if sys.version_info < (3, 5) or platform.python_implementation() == 'PyPy':
    collect_ignore_glob.append("tests/*_async.py")
