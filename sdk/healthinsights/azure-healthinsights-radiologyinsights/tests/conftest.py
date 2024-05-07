#!/usr/bin/env python
# coding=utf-8

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

from devtools_testutils import test_proxy, add_general_regex_sanitizer


@pytest.fixture(scope="session", autouse=True)
def add_sanitizers(test_proxy):
    healthinsights_endpoint = os.environ.get(
        "AZURE_HEALTH_INSIGHTS_ENDPOINT", "https://fake_ad_resource.cognitiveservices.azure.com/"
    )
    healthinsights_key = os.environ.get("AZURE_HEALTH_INSIGHTS_API_KEY", "00000000000000000000000000000000")
    add_general_regex_sanitizer(
        regex=healthinsights_endpoint, value="https://fake_ad_resource.cognitiveservices.azure.com/"
    )
    add_general_regex_sanitizer(regex=healthinsights_key, value="00000000000000000000000000000000")
