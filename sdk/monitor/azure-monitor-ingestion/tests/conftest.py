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
from datetime import datetime

import pytest

from devtools_testutils.sanitizers import (
    add_body_key_sanitizer,
    add_general_regex_sanitizer,
    add_header_regex_sanitizer,
    set_custom_default_matcher,
    add_oauth_response_sanitizer
)


# Environment variable keys
ENV_SUBSCRIPTION_ID = "AZURE_SUBSCRIPTION_ID"
ENV_DCE = "AZURE_MONITOR_DCE"
ENV_DCR_ID = "AZURE_MONITOR_DCR_ID"
ENV_STREAM_NAME = "AZURE_MONITOR_STREAM_NAME"
ENV_TENANT_ID = "AZURE_TENANT_ID"
ENV_CLIENT_ID = "AZURE_CLIENT_ID"
ENV_CLIENT_SECRET = "AZURE_CLIENT_SECRET"

# Fake values
TEST_ID = "00000000-0000-0000-0000-000000000000"
TEST_DCE = "https://fake.ingest.monitor.azure.com"
TEST_STREAM_NAME = "test-stream"


@pytest.fixture(scope="session", autouse=True)
def add_sanitizers(test_proxy, environment_variables):
    sanitization_mapping = {
        ENV_SUBSCRIPTION_ID: TEST_ID,
        ENV_TENANT_ID: TEST_ID,
        ENV_CLIENT_ID: TEST_ID,
        ENV_CLIENT_SECRET: TEST_ID,
        ENV_DCE: TEST_DCE,
        ENV_STREAM_NAME: TEST_STREAM_NAME,
        ENV_DCR_ID: TEST_ID
    }
    environment_variables.sanitize_batch(sanitization_mapping)
    set_custom_default_matcher(
        compare_bodies=False, excluded_headers="Authorization,Content-Length,x-ms-client-request-id,x-ms-request-id"
    )
    add_general_regex_sanitizer(
        value="fakeresource",
        regex="(?<=\\/\\/)[a-z-]+(?=\\.westus2-1\\.ingest\\.monitor\\.azure\\.com)"
    )
    add_body_key_sanitizer(json_path="access_token", value="fakekey")
    add_header_regex_sanitizer(key="Set-Cookie", value="[set-cookie;]")
    add_oauth_response_sanitizer()


@pytest.fixture(scope="session")
def monitor_info(environment_variables):
    yield {
        "stream_name": environment_variables.get(ENV_STREAM_NAME),
        "dce": environment_variables.get(ENV_DCE),
        "dcr_id": environment_variables.get(ENV_DCR_ID)
    }


@pytest.fixture(scope="session")
def large_data():
    logs = []
    content = "a" * (1024 * 100) # 100 KiB string

    # Ensure total size is > 2 MiB data
    for i in range(24):
        logs.append({
            "Time": datetime.now().isoformat(),
            "AdditionalContext": content
        })
    return logs
