
# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import sys

# fixture needs to be visible from conftest
from testcase import form_recognizer_account

# Ignore async tests for Python < 3.5
collect_ignore_glob = []
if sys.version_info < (3, 5):
    collect_ignore_glob.append("*_async.py")

def pytest_configure(config):
    # register an additional marker
    config.addinivalue_line(
        "usefixtures", "form_recognizer_account"
    )