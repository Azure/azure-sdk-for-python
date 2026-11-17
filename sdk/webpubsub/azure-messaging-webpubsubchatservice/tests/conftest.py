# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
import pytest
from dotenv import load_dotenv
from devtools_testutils import (
    remove_batch_sanitizers,
    set_custom_default_matcher,
    test_proxy,
)

load_dotenv(override=False)


@pytest.fixture(scope="session", autouse=True)
def start_proxy(test_proxy):
    return


@pytest.fixture(scope="session", autouse=True)
def add_sanitizers(test_proxy):
    set_custom_default_matcher(ignore_query_ordering=True)
    remove_batch_sanitizers(["AZSDK3430", "AZSDK3433", "AZSDK3442", "AZSDK3490", "AZSDK3493", "AZSDK4001"])
