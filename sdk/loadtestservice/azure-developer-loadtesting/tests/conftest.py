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
import os
import platform
import pytest
import sys

from dotenv import load_dotenv

from devtools_testutils import test_proxy, add_general_regex_sanitizer, add_body_key_sanitizer, add_header_regex_sanitizer

load_dotenv()

@pytest.fixture(scope="session", autouse=True)
def add_sanitizers(test_proxy):
    subscription_id = os.environ.get("LOADTESTING_SUBSCRIPTION_ID", "00000000-0000-0000-0000-000000000000")
    tenant_id = os.environ.get("LOADTESTING_TENANT_ID", "00000000-0000-0000-0000-000000000000")
    client_id = os.environ.get("LOADTESTING_CLIENT_ID", "00000000-0000-0000-0000-000000000000")
    client_secret = os.environ.get("LOADTESTING_CLIENT_SECRET", "00000000-0000-0000-0000-000000000000")
    test_id = os.environ.get("TEST_ID", "000")
    file_id = os.environ.get("FILE_ID", "000")
    test_run_id = os.environ.get("TEST_RUN_ID", "000")
    app_component = os.environ.get("APP_COMPONENT", "000")
    add_general_regex_sanitizer(regex=subscription_id, value="00000000-0000-0000-0000-000000000000")
    add_general_regex_sanitizer(regex=tenant_id, value="00000000-0000-0000-0000-000000000000")
    add_general_regex_sanitizer(regex=client_id, value="00000000-0000-0000-0000-000000000000")
    add_general_regex_sanitizer(regex=client_secret, value="00000000-0000-0000-0000-000000000000")
    add_general_regex_sanitizer(regex=test_id, value="000")
    add_general_regex_sanitizer(regex=file_id, value="000")
    add_general_regex_sanitizer(regex=test_run_id, value="000")
    add_general_regex_sanitizer(regex=app_component, value="000")
    add_header_regex_sanitizer(key="Set-Cookie", value="[set-cookie;]")
    add_header_regex_sanitizer(key="Cookie", value="cookie;")
    add_body_key_sanitizer(json_path="$..access_token", value="access_token")
    add_body_key_sanitizer(json_path="$..url", value="url")
