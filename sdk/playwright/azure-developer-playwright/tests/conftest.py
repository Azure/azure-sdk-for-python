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
    remove_batch_sanitizers,
    set_custom_default_matcher,
)


@pytest.fixture(scope="session", autouse=True)
def start_proxy(test_proxy, patch_sleep, patch_async_sleep):
    set_custom_default_matcher(excluded_headers="Cookie")
    return


@pytest.fixture(scope="session", autouse=True)
def add_sanitizers(test_proxy):
    # Sanitize subscription ID
    playwright_subscription_id = os.environ.get("PLAYWRIGHT_SUBSCRIPTION_ID", "00000000-0000-0000-0000-000000000000")
    add_general_regex_sanitizer(regex=playwright_subscription_id, value="00000000-0000-0000-0000-000000000000")

    # Sanitize endpoint (both https:// and http:// variants for @odata.context)
    playwright_endpoint = os.environ.get("PLAYWRIGHT_ENDPOINT", "")
    if playwright_endpoint:
        # Extract hostname for protocol-agnostic sanitization
        hostname = playwright_endpoint.replace("https://", "").replace("http://", "")
        reporting_hostname = hostname.replace(".api.playwright.", ".reporting.api.playwright.")

        # Sanitize reporting subdomain first (longer match) to avoid partial matches
        add_general_string_sanitizer(
            target=reporting_hostname,
            value="fake.reporting.api.playwright.microsoft.com",
        )
        add_general_string_sanitizer(target=hostname, value="fake.api.playwright.microsoft.com")

    # Sanitize workspace ID
    playwright_workspace_id = os.environ.get("PLAYWRIGHT_WORKSPACE_ID", "00000000-0000-0000-0000-000000000000")
    add_general_regex_sanitizer(regex=playwright_workspace_id, value="00000000-0000-0000-0000-000000000000")

    # Sanitize browser session test endpoint (separate workspace)
    session_endpoint = os.environ.get("PLAYWRIGHT_SESSION_ENDPOINT", "")
    if session_endpoint:
        session_hostname = session_endpoint.replace("https://", "").replace("http://", "")
        session_reporting_hostname = session_hostname.replace(".api.playwright.", ".reporting.api.playwright.")
        add_general_string_sanitizer(
            target=session_reporting_hostname,
            value="fake.reporting.api.playwright.microsoft.com",
        )
        add_general_string_sanitizer(target=session_hostname, value="fake.api.playwright.microsoft.com")

    session_workspace_id = os.environ.get("PLAYWRIGHT_SESSION_WORKSPACE_ID", "00000000-0000-0000-0000-000000000000")
    add_general_regex_sanitizer(regex=session_workspace_id, value="00000000-0000-0000-0000-000000000000")

    session_id = os.environ.get("PLAYWRIGHT_SESSION_ID", "00000000-0000-0000-0000-000000000000")
    add_general_regex_sanitizer(regex=session_id, value="00000000-0000-0000-0000-000000000000")

    # Sanitize cookies and tokens
    add_header_regex_sanitizer(key="Set-Cookie", value="[set-cookie;]")
    add_header_regex_sanitizer(key="Cookie", value="cookie;")
    add_body_key_sanitizer(json_path="$..access_token", value="access_token")
    add_body_key_sanitizer(json_path="$..jwtToken", value="sanitized")
    add_body_key_sanitizer(json_path="$..creatorId", value="00000000-0000-0000-0000-000000000000")
    add_body_key_sanitizer(json_path="$..creatorName", value="Sanitized")

    # Remove overly aggressive default sanitizers for $..id and $..name
    remove_batch_sanitizers(["AZSDK3430", "AZSDK3493"])
