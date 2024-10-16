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
from devtools_testutils import add_general_regex_sanitizer, test_proxy, set_bodiless_matcher, remove_batch_sanitizers


@pytest.fixture(scope="session", autouse=True)
def add_sanitizers(test_proxy):
    set_bodiless_matcher()

    client_id = os.environ.get("APPCONFIGURATION_CLIENT_ID", "client-id")
    add_general_regex_sanitizer(regex=client_id, value="client-id")
    client_secret = os.environ.get("APPCONFIGURATION_CLIENT_SECRET", "client-secret")
    add_general_regex_sanitizer(regex=client_secret, value="client-secret")
    tenant_id = os.environ.get("APPCONFIGURATION_TENANT_ID", "00000000-0000-0000-0000-000000000000")
    add_general_regex_sanitizer(value="00000000-0000-0000-0000-000000000000", regex=tenant_id)

    # Remove the following sanitizers since certain fields are needed in tests and are non-sensitive:
    #  - AZSDK3447: $.key
    #  - AZSDK3490: $..etag
    #  - AZSDK3493: $..name
    #  - AZSDK4001: host name -> Sanitized
    remove_batch_sanitizers(["AZSDK3447", "AZSDK3490", "AZSDK3493", "AZSDK4001"])
