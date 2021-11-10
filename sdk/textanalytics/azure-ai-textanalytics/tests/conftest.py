
# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import sys
import pytest
from devtools_testutils import add_remove_header_sanitizer


# Ignore async tests for Python < 3.6
collect_ignore_glob = []
if sys.version_info < (3, 6):
    collect_ignore_glob.append("*_async.py")


@pytest.fixture(scope="session", autouse=True)
def add_sanitizers():
    add_remove_header_sanitizer(headers="Ocp-Apim-Subscription-Key")
