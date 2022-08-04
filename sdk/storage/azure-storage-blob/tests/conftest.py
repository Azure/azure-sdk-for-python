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
    add_uri_regex_sanitizer,
    test_proxy,
    add_body_key_sanitizer
)

@pytest.fixture(scope="session", autouse=True)
def add_sanitizers(test_proxy):
    subscription_id = os.environ.get("AZURE_SUBSCRIPTION_ID", "00000000-0000-0000-0000-000000000000")
    tenant_id = os.environ.get("STORAGE_TENANT_ID", "00000000-0000-0000-0000-000000000000")
    add_general_regex_sanitizer(regex=subscription_id, value="00000000-0000-0000-0000-000000000000")
    add_general_regex_sanitizer(regex=tenant_id, value="00000000-0000-0000-0000-000000000000")
    add_header_regex_sanitizer(key="Set-Cookie", value="[set-cookie;]")
    add_header_regex_sanitizer(key="Cookie", value="cookie;")
    add_oauth_response_sanitizer()

    add_header_regex_sanitizer(key="x-ms-copy-source-authorization", value="Sanitized")
    add_header_regex_sanitizer(key="x-ms-encryption-key", value="Sanitized")
    add_header_regex_sanitizer(key="x-ms-encryption-key-sha256", value="Sanitized")

    add_uri_regex_sanitizer(regex=r"\.preprod\.", value=".")

    # sanitizes random UUIDs that are sent in batch request headers and bodies
    add_general_regex_sanitizer(
        value="00000000-0000-0000-0000-000000000000",
        regex="batch[a-z]*_([0-9a-f]{8}\\b-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-\\b[0-9a-f]{12}\\b)",
        group_for_replace="1",
    )
    # sanitizes access tokens in response bodies
    add_body_key_sanitizer(json_path="$..access_token", value="access_token")
