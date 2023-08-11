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

from devtools_testutils import add_body_key_sanitizer, add_general_string_sanitizer, add_remove_header_sanitizer

@pytest.fixture(scope="session", autouse=True)
def add_sanitizers(test_proxy):
    add_body_key_sanitizer(json_path="$..credential", value="sanitized")
    # Two `id` sanitizers are used since this key can be nested at different levels in bodies
    add_body_key_sanitizer(json_path="$.id", value="sanitized")
    add_body_key_sanitizer(json_path="$..id", value="sanitized")
    add_body_key_sanitizer(json_path="$..username", value="sanitized")

    sanitized_endpoint = "https://sanitized.communication.azure.com"
    endpoint = os.environ.get("COMMUNICATION_SERVICE_ENDPOINT", sanitized_endpoint)
    add_general_string_sanitizer(target=endpoint, value=sanitized_endpoint)
    add_remove_header_sanitizer(headers="x-ms-content-sha256")
