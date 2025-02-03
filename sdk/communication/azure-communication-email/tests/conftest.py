# --------------------------------------------------------------------------
#
# Copyright (c) Microsoft Corporation. All rights reserved.
#
# The MIT License (MIT)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the ""Software""), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED *AS IS*, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.
#
# --------------------------------------------------------------------------
import pytest
import os
from devtools_testutils import (
    add_general_regex_sanitizer,
    add_header_regex_sanitizer,
    add_body_key_sanitizer,
    set_default_session_settings,
    add_uri_regex_sanitizer,
)
from azure.communication.email._shared.utils import parse_connection_str
from azure.communication.email._api_versions import DEFAULT_VERSION


@pytest.fixture(scope="session", autouse=True)
def add_sanitizers(test_proxy):
    set_default_session_settings()

    communication_connection_string = os.getenv(
        "COMMUNICATION_CONNECTION_STRING_EMAIL", "endpoint=https://someEndpoint/;accesskey=someAccessKeyw=="
    )
    sender_address = os.getenv("SENDER_ADDRESS", "someSender@contoso.com")
    recipient_address = os.getenv("RECIPIENT_ADDRESS", "someRecipient@domain.com")

    add_general_regex_sanitizer(
        regex=communication_connection_string, value="endpoint=https://someEndpoint/;accesskey=someAccessKeyw=="
    )
    add_general_regex_sanitizer(regex=sender_address, value="someSender@contoso.com")
    add_general_regex_sanitizer(regex=recipient_address, value="someRecipient@domain.com")

    add_body_key_sanitizer(json_path="$.id", value="someId")

    endpoint, _ = parse_connection_str(communication_connection_string)
    add_general_regex_sanitizer(regex=endpoint, value="someEndpoint")

    add_header_regex_sanitizer(key="x-ms-content-sha256", value="sanitized")
    add_header_regex_sanitizer(
        key="Operation-Location", value="https://someEndpoint/emails/operations/someId?api-version=" + DEFAULT_VERSION
    )

    add_uri_regex_sanitizer(
        regex="https://[^/]+/emails/operations/.*?api", value="https://someEndpoint/emails/operations/someId?api"
    )
    add_uri_regex_sanitizer(regex="https://[^/]+/emails:send\\?api", value="https://someEndpoint/emails:send?api")
