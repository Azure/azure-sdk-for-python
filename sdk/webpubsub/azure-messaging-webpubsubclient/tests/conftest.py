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
import re
import pytest
from dotenv import load_dotenv
from devtools_testutils import test_proxy, add_general_regex_sanitizer
from testcase import TEST_RESULT
from testcase_async import TEST_RESULT_ASYNC

load_dotenv()


@pytest.fixture(autouse=True)
def clear_test_results():
    TEST_RESULT.clear()
    TEST_RESULT_ASYNC.clear()
    yield
    TEST_RESULT.clear()
    TEST_RESULT_ASYNC.clear()


@pytest.fixture(scope="session", autouse=True)
def add_sanitizers(test_proxy):
    endpoint = os.environ.get("WEBPUBSUBCLIENT_ENDPOINT", "WEBPUBSUBCLIENT_ENDPOINT")
    add_general_regex_sanitizer(
        regex=re.escape(endpoint),
        value="https://myservice.webpubsub.azure.com",
    )
