# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import pytest
from devtools_testutils import test_proxy

# autouse=True will trigger this fixture on each pytest run, even if it's
# not explicitly used by a test method. This is necessary for test recordings.
@pytest.fixture(scope="session", autouse=True)
def start_proxy(test_proxy):
    return
