# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import os

import pytest
from dotenv import load_dotenv
from devtools_testutils import test_proxy, set_custom_default_matcher

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"), override=False)


# autouse=True will trigger this fixture on each pytest run, even if it's not explicitly used by a test method
@pytest.fixture(scope="session", autouse=True)
def start_proxy(test_proxy):
    return


@pytest.fixture(scope="session", autouse=True)
def add_sanitizers(test_proxy):
    set_custom_default_matcher(ignore_query_ordering=True)
