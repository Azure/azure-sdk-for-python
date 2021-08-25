# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------

# NOTE: These tests are heavily inspired from the httpx test suite: https://github.com/encode/httpx/tree/master/tests
# Thank you httpx for your wonderful tests!

import pytest
from azure.core.rest import HttpRequest

def _format_query_into_url(url, params):
    request = HttpRequest(method="GET", url=url, params=params)
    return request.url

def test_request_url_with_params():
    url = _format_query_into_url(url="a/b/c?t=y", params={"g": "h"})
    assert url in ["a/b/c?g=h&t=y", "a/b/c?t=y&g=h"]

def test_request_url_with_params_as_list():
    url = _format_query_into_url(url="a/b/c?t=y", params={"g": ["h","i"]})
    assert url in ["a/b/c?g=h&g=i&t=y", "a/b/c?t=y&g=h&g=i"]

def test_request_url_with_params_with_none_in_list():
    with pytest.raises(ValueError):
        _format_query_into_url(url="a/b/c?t=y", params={"g": ["h",None]})

def test_request_url_with_params_with_none():
    with pytest.raises(ValueError):
        _format_query_into_url(url="a/b/c?t=y", params={"g": None})
