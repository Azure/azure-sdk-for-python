# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from unittest import mock
from devtools_testutils import (
    test_proxy,
    add_body_key_sanitizer,
    add_oauth_response_sanitizer,
    remove_batch_sanitizers,
    add_uri_regex_sanitizer,
    is_live,
)
import pytest

# autouse=True will trigger this fixture on each pytest run, even if it's not explicitly used by a test method
@pytest.fixture(scope="session", autouse=True)
def start_proxy(test_proxy):
    add_body_key_sanitizer(json_path="$..id_token", value="Sanitized")
    add_body_key_sanitizer(json_path="$..client_info", value="Sanitized")
    add_oauth_response_sanitizer()
    add_uri_regex_sanitizer(regex="\\.(?<location>.*)\\.devcenter\\.azure\\.com", group_for_replace="location", value="location")
    # Remove the following sanitizers since certain fields are needed in tests and are non-sensitive:
    #  - AZSDK2003: Location
    #  - AZSDK3493: $..name
    remove_batch_sanitizers(["AZSDK2003", "AZSDK3493"])
    return

@pytest.fixture(scope="session", autouse=True)
def patch_async_sleep():
    async def immediate_return(_):
        return

    if not is_live():
        with mock.patch("asyncio.sleep", immediate_return):
            yield

    else:
        yield


@pytest.fixture(scope="session", autouse=True)
def patch_sleep():
    def immediate_return(_):
        return

    if not is_live():
        with mock.patch("time.sleep", immediate_return):
            yield

    else:
        yield
