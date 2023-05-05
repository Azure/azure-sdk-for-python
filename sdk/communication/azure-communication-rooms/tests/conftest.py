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
from devtools_testutils import add_general_string_sanitizer, add_header_regex_sanitizer, add_body_key_sanitizer, set_default_session_settings
from azure.communication.rooms._shared.utils import parse_connection_str

@pytest.fixture(scope="session", autouse=True)
def add_sanitizers(test_proxy):
    set_default_session_settings()

    communication_connection_string = os.getenv("COMMUNICATION_CONNECTION_STRING_ROOMS", "endpoint=https://sanitized.communication.azure.com/;accesskey=fake===")

    add_general_string_sanitizer(target=communication_connection_string, value="endpoint=https://sanitized.communication.azure.com/;accesskey=fake===")
    endpoint, _ = parse_connection_str(communication_connection_string)
    add_general_string_sanitizer(target=endpoint, value="sanitized.communication.azure.com")
    add_header_regex_sanitizer(key="x-ms-content-sha256", value="sanitized")
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
    add_header_regex_sanitizer(
        key="Content-Security-Policy-Report-Only", value="sanitized")
    add_header_regex_sanitizer(key="Repeatability-First-Sent", value="sanitized")
    add_header_regex_sanitizer(key="Repeatability-Request-ID", value="sanitized")
