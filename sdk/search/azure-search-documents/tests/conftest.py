# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------

import sys
import pytest
from devtools_testutils import test_proxy
from devtools_testutils.sanitizers import add_remove_header_sanitizer, add_general_regex_sanitizer

# Ignore async tests for Python < 3.5
collect_ignore = []
if sys.version_info < (3, 5):
    collect_ignore.append("async_tests")

@pytest.fixture(scope="session", autouse=True)
def add_sanitizers(test_proxy):
    add_remove_header_sanitizer(headers="api-key")

    # Ensure all search service endpoint names are mocked to "test-service"
    add_general_regex_sanitizer(
        value="://fakesearchendpoint.search.windows.net",
        regex=r"://(.+).search.windows.net"
    )
    # Remove storage connection strings from recordings
    add_general_regex_sanitizer(
        value="AccountKey=FAKE;",
        regex=r"AccountKey=([^;]+);"
    )
    # Remove storage account names from recordings
    add_general_regex_sanitizer(
        value="AccountName=fakestoragecs;",
        regex=r"AccountName=([^;]+);"
    )
