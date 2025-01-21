# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import os

import pytest

from devtools_testutils import (
    add_general_regex_sanitizer,
    add_header_regex_sanitizer,
    add_oauth_response_sanitizer,
    test_proxy,
    remove_batch_sanitizers,
)


@pytest.fixture(scope="session", autouse=True)
def add_sanitizers(test_proxy):
    subscription_key = os.environ.get("SUBSCRIPTION_KEY", "subscription-key")
    tenant_id = os.environ.get("MAPS_TENANT_ID", "tenant-id")
    client_secret = os.environ.get("MAPS_CLIENT_SECRET", "MyClientSecret")
    add_general_regex_sanitizer(regex=subscription_key, value="AzureMapsSubscriptionKey")
    add_general_regex_sanitizer(regex=tenant_id, value="MyTenantId")
    add_general_regex_sanitizer(regex=client_secret, value="MyClientSecret")
    # add_oauth_response_sanitizer()

    # Remove the following sanitizers since certain fields are needed in tests and are non-sensitive:
    #  - AZSDK3430: $..id
    #  - AZSDK3493: $..name
    remove_batch_sanitizers(["AZSDK3430", "AZSDK3493"])
