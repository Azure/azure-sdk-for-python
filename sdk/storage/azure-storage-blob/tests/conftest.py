# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import pytest

from devtools_testutils import add_oauth_response_sanitizer, test_proxy

@pytest.fixture(scope="session", autouse=True)
def add_sanitizers(test_proxy):
    add_oauth_response_sanitizer()
