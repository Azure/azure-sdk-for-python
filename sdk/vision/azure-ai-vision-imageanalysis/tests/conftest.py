# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import pytest
from devtools_testutils import test_proxy, remove_batch_sanitizers


# autouse=True will trigger this fixture on each pytest run, even if it's not explicitly used by a test method
@pytest.fixture(scope="session", autouse=True)
def start_proxy(test_proxy):
    return


@pytest.fixture(scope="session", autouse=True)
def add_sanitizers(test_proxy):
    # Remove the following sanitizers since certain fields are needed in tests and are non-sensitive:
    #  - AZSDK3493: $..name
    remove_batch_sanitizers(["AZSDK3493"])
