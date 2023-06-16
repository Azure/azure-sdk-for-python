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
import pytest
from devtools_testutils import add_general_string_sanitizer, test_proxy, add_body_key_sanitizer, add_header_regex_sanitizer, add_oauth_response_sanitizer
from devtools_testutils.sanitizers import (
    add_remove_header_sanitizer,
    add_general_regex_sanitizer,
    set_custom_default_matcher,
)

@pytest.fixture(scope="session", autouse=True)
def add_sanitizers(test_proxy):
    # this can be reverted to set_bodiless_matcher() after tests are re-recorded and don't contain these headers
    set_custom_default_matcher(
        compare_bodies=False,
        excluded_headers="Authorization,Content-Length,x-ms-client-request-id,x-ms-request-id",
    )
    add_remove_header_sanitizer(headers="aeg-sas-key, aeg-sas-token")
    add_general_regex_sanitizer(
        value="fakeresource",
        regex="(?<=\\/\\/)[a-z-]+(?=\\.eastus-1\\.eventgrid\\.azure\\.net/api/events)",
    )
    add_header_regex_sanitizer(key="Set-Cookie", value="[set-cookie;]")
    add_header_regex_sanitizer(key="Cookie", value="cookie;")
    add_body_key_sanitizer(json_path="$..access_token", value="access_token")
    add_body_key_sanitizer(json_path="$..id", value="id")
    add_oauth_response_sanitizer()

    tenant_id = os.environ.get("AZURE_TENANT_ID", "00000000-0000-0000-0000-000000000000")
    add_general_regex_sanitizer(regex=tenant_id, value="00000000-0000-0000-0000-000000000000")

