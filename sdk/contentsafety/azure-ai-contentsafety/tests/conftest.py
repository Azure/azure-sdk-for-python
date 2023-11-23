# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import pytest
from devtools_testutils import test_proxy, add_general_string_sanitizer
import os

# autouse=True will trigger this fixture on each pytest run, even if it's not explicitly used by a test method
@pytest.fixture(scope="session", autouse=True)
def start_proxy(test_proxy):
    return


@pytest.fixture(scope="session", autouse=True)
def add_sanitizers(test_proxy):
    content_safety_key = os.environ.get("CONTENT_SAFETY_KEY", "00000000000000000000000000000000")
    content_safety_endpoint = os.environ.get(
        "CONTENT_SAFETY_ENDPOINT", "https://fake_cs_resource.cognitiveservices.azure.com"
    )
    content_safety_client_id = os.environ.get("CONTENT_SAFETY_CLIENT_ID", "00000000000000000000000000000000")
    content_safety_client_secret = os.environ.get("CONTENT_SAFETY_CLIENT_SECRET", "00000000000000000000000000000000")
    content_safety_tenant_id = os.environ.get("CONTENT_SAFETY_TENANT_ID", "00000000000000000000000000000000")
    add_general_string_sanitizer(target=content_safety_key, value="00000000000000000000000000000000")
    add_general_string_sanitizer(
        target=content_safety_endpoint, value="https://fake_cs_resource.cognitiveservices.azure.com"
    )
    add_general_string_sanitizer(target=content_safety_client_id, value="00000000000000000000000000000000")
    add_general_string_sanitizer(target=content_safety_client_secret, value="00000000000000000000000000000000")
    add_general_string_sanitizer(target=content_safety_tenant_id, value="00000000000000000000000000000000")
