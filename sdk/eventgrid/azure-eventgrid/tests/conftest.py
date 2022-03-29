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
import platform
import sys
import pytest
from devtools_testutils import test_proxy
from devtools_testutils.sanitizers import add_remove_header_sanitizer, add_general_regex_sanitizer, set_custom_default_matcher

# Ignore async tests for Python < 3.5
collect_ignore_glob = []
if sys.version_info < (3, 5):
    collect_ignore_glob.append("*_async.py")
    collect_ignore_glob.append("test_cncf*")

@pytest.fixture(scope="session", autouse=True)
def add_aeg_sanitizer(test_proxy):
    # this can be reverted to set_bodiless_matcher() after tests are re-recorded and don't contain these headers
    set_custom_default_matcher(
        compare_bodies=False, excluded_headers="Authorization,Content-Length,x-ms-client-request-id,x-ms-request-id"
    )
    add_remove_header_sanitizer(headers="aeg-sas-key, aeg-sas-token")
    add_general_regex_sanitizer(
        value="fakeresource",
        regex="(?<=\\/\\/)[a-z-]+(?=\\.westus2-1\\.eventgrid\\.azure\\.net/api/events)"
    )
