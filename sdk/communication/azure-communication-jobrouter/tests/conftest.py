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
import sys

import pytest

from devtools_testutils import (
    test_proxy,
    add_general_regex_sanitizer,
    add_header_regex_sanitizer,
    set_default_session_settings,
    add_uri_regex_sanitizer,
    add_body_key_sanitizer
)
from router_test_constants import (
    SANITIZED,
    FAKE_FUNCTION_URI,
    FAKE_ENDPOINT,
    FAKE_CONNECTION_STRING
)
from azure.communication.jobrouter._shared.utils import parse_connection_str


# fixture needs to be visible from conftest

# autouse=True will trigger this fixture on each pytest run, even if it's not explicitly used by a test method
@pytest.fixture(scope = "session", autouse = True)
def start_proxy(test_proxy):
    set_default_session_settings()

    communication_connection_string = os.getenv("COMMUNICATION_LIVETEST_DYNAMIC_CONNECTION_STRING",
                                                FAKE_CONNECTION_STRING)

    add_general_regex_sanitizer(regex = communication_connection_string,
                                value = FAKE_CONNECTION_STRING)

    endpoint, _ = parse_connection_str(communication_connection_string)
    add_general_regex_sanitizer(regex = endpoint, value = FAKE_ENDPOINT)

    add_header_regex_sanitizer(key = "repeatability-first-sent", value = SANITIZED)
    add_header_regex_sanitizer(key = "repeatability-request-id", value = SANITIZED)
    add_header_regex_sanitizer(key = "x-ms-content-sha256", value = SANITIZED)
    add_header_regex_sanitizer(key = "etag", value = SANITIZED)

    add_body_key_sanitizer(json_path = "$..access_token", value = "access_token")
    add_body_key_sanitizer(json_path = "$..primaryKey", value = "primaryKey")
    add_body_key_sanitizer(json_path = "$..secondaryKey", value = "secondaryKey")
    add_body_key_sanitizer(json_path = "$..etag", value = SANITIZED)
    add_body_key_sanitizer(json_path = "$..functionUri", value = FAKE_FUNCTION_URI)
    add_body_key_sanitizer(json_path = "$..functionKey", value = SANITIZED)
    add_body_key_sanitizer(json_path = "$..appKey", value = SANITIZED)
    add_body_key_sanitizer(json_path = "$..clientId", value = SANITIZED)
    return


@pytest.fixture(scope = "function", autouse = True)
def initialize_test(request):
    if request.node.originalname is None:
        # tox throws error otherwise
        test_name = os.environ.get('PYTEST_CURRENT_TEST').split(':')[-1].split(' ')[0]
        request.cls._testMethodName = test_name
    else:
        request.cls._testMethodName = request.node.originalname


@pytest.fixture(scope = "class", autouse = True)
def initialize_class(request):
    request.cls.queue_ids = {}  # type: Dict[str, List[str]]
    request.cls.distribution_policy_ids = {}  # type: Dict[str, List[str]]
    request.cls.exception_policy_ids = {}  # type: Dict[str, List[str]]
    request.cls.classification_policy_ids = {}  # type: Dict[str, List[str]]
    request.cls.worker_ids = {}  # type: Dict[str, List[str]]
    request.cls.job_ids = {}  # type: Dict[str, List[str]]


# Ignore async tests for Python < 3.5
collect_ignore_glob = []
if sys.version_info < (3, 5):
    collect_ignore_glob.append("*_async.py")
