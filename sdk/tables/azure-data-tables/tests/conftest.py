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
from devtools_testutils import add_general_regex_sanitizer, add_body_key_sanitizer, test_proxy

# fixture needs to be visible from conftest

@pytest.fixture(scope="session", autouse=True)
def add_sanitizers(test_proxy):
    # sanitizes table/cosmos account names in URLs
    add_general_regex_sanitizer(
        value="fakeendpoint",
        regex="(?<=\\/\\/)[a-z]+(?=(?:|-secondary)\\.(?:table|blob|queue)\\.(?:cosmos|core)\\."
              "(?:azure|windows)\\.(?:com|net))",
    )
    # sanitizes random UUIDs that are sent in batch request headers and bodies
    add_general_regex_sanitizer(
        value="00000000-0000-0000-0000-000000000000",
        regex="batch[a-z]*_([0-9a-f]{8}\\b-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-\\b[0-9a-f]{12}\\b)",
        group_for_replace="1",
    )
    # sanitizes tenant ID
    tenant_id = os.environ.get("TABLES_TENANT_ID", "00000000-0000-0000-0000-000000000000")
    add_general_regex_sanitizer(value="00000000-0000-0000-0000-000000000000", regex=tenant_id)
    # sanitizes tenant ID used in test_challenge_auth(_async).py tests
    challenge_tenant_id = os.environ.get("CHALLENGE_TABLES_TENANT_ID", "00000000-0000-0000-0000-000000000000")
    add_general_regex_sanitizer(value="00000000-0000-0000-0000-000000000000", regex=challenge_tenant_id)
    # sanitizes access tokens in response bodies
    add_body_key_sanitizer(json_path="$..access_token", value="access_token")
