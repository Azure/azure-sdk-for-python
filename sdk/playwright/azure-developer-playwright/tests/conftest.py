# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
import os
import pytest
from dotenv import load_dotenv

load_dotenv()

from devtools_testutils import (
    test_proxy,
    add_general_regex_sanitizer,
    add_general_string_sanitizer,
    add_body_key_sanitizer,
    add_header_regex_sanitizer,
)


@pytest.fixture(scope="session", autouse=True)
def start_proxy(test_proxy, patch_sleep, patch_async_sleep):
    return


@pytest.fixture(scope="session", autouse=True)
def add_sanitizers(test_proxy):
    # Sanitize subscription ID
    playwright_subscription_id = os.environ.get(
        "PLAYWRIGHT_SUBSCRIPTION_ID", "00000000-0000-0000-0000-000000000000"
    )
    add_general_regex_sanitizer(
        regex=playwright_subscription_id, value="00000000-0000-0000-0000-000000000000"
    )

    # Sanitize endpoint
    playwright_endpoint = os.environ.get("PLAYWRIGHT_ENDPOINT", "")
    if playwright_endpoint:
        add_general_string_sanitizer(
            target=playwright_endpoint, value="https://fake_playwright_endpoint.com"
        )
        # Also sanitize the reporting subdomain variant
        reporting_endpoint = playwright_endpoint.replace(
            ".api.playwright.", ".reporting.api.playwright."
        )
        add_general_string_sanitizer(
            target=reporting_endpoint,
            value="https://fake_playwright_endpoint.com",
        )

    # Sanitize workspace ID
    playwright_workspace_id = os.environ.get(
        "PLAYWRIGHT_WORKSPACE_ID", "00000000-0000-0000-0000-000000000000"
    )
    add_general_regex_sanitizer(
        regex=playwright_workspace_id, value="00000000-0000-0000-0000-000000000000"
    )

    # Sanitize cookies and tokens
    add_header_regex_sanitizer(key="Set-Cookie", value="[set-cookie;]")
    add_header_regex_sanitizer(key="Cookie", value="cookie;")
    add_body_key_sanitizer(json_path="$..access_token", value="access_token")
