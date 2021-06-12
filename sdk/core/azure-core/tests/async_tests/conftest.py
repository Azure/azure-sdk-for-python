
# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import sys
import pytest
from azure.core.rest import AsyncTestRestClient
from async_generator import yield_, async_generator


# Ignore async tests for Python < 3.5
collect_ignore_glob = []
if sys.version_info < (3, 5):
    collect_ignore_glob.append("async_tests")

@pytest.fixture
def client():
    return AsyncTestRestClient()
