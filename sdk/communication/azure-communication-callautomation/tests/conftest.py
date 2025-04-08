# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import pytest
import os
from devtools_testutils import (
    add_general_regex_sanitizer,
    add_header_regex_sanitizer,
    set_default_session_settings,
    add_body_key_sanitizer,
    add_general_string_sanitizer,
    remove_batch_sanitizers,
)


# autouse=True will trigger this fixture on each pytest run, even if it's not explicitly used by a test method
@pytest.fixture(scope="session", autouse=True)
def start_proxy(test_proxy):

    set_default_session_settings()

    fake_connection_str = "endpoint=https://sanitized.communication.azure.com/;accesskey=fake=="
    connection_str = os.getenv("COMMUNICATION_LIVETEST_STATIC_CONNECTION_STRING", fake_connection_str)
    add_general_string_sanitizer(target=connection_str, value=fake_connection_str)

    add_general_regex_sanitizer(regex="https://[^/]+", value="https://sanitized")
    add_general_regex_sanitizer(regex="wss://[^/]+", value="wss://sanitized")
    add_body_key_sanitizer(json_path="callbackUri", value="https://sanitized/")
    add_body_key_sanitizer(json_path="transportUrl", value="https://sanitized/")
    add_body_key_sanitizer(json_path="$..file.uri", value="https://REDACTED/prompt.wav")
    add_body_key_sanitizer(json_path="$..incomingCallContext", value="REDACTED")
    add_header_regex_sanitizer(key="Set-Cookie", value="sanitized")
    add_header_regex_sanitizer(key="Date", value="sanitized")
    add_header_regex_sanitizer(key="Cookie", value="sanitized")
    add_header_regex_sanitizer(key="client-request-id", value="sanitized")
    add_header_regex_sanitizer(key="MS-CV", value="sanitized")
    add_header_regex_sanitizer(key="X-Azure-Ref", value="sanitized")
    add_header_regex_sanitizer(key="x-ms-content-sha256", value="sanitized")
    add_header_regex_sanitizer(key="x-ms-client-request-id", value="sanitized")
    add_header_regex_sanitizer(key="x-ms-date", value="sanitized")
    add_header_regex_sanitizer(key="x-ms-request-id", value="sanitized")
    add_header_regex_sanitizer(key="Content-Security-Policy-Report-Only", value="sanitized")
    add_header_regex_sanitizer(key="Repeatability-First-Sent", value="sanitized")
    add_header_regex_sanitizer(key="Repeatability-Request-ID", value="sanitized")
    add_header_regex_sanitizer(key="x-ms-host", value="sanitized")

    # Remove the following sanitizers since certain fields are needed in tests and are non-sensitive:
    #  - AZSDK3430: $..id
    remove_batch_sanitizers(["AZSDK3430"])

    return
