# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import pytest
from azure.core.rest import HttpRequest

def readonly_checks(response):
    assert isinstance(response.request, HttpRequest)
    with pytest.raises(AttributeError):
        response.request = None

    assert isinstance(response.status_code, int)
    with pytest.raises(AttributeError):
        response.status_code = 200

    assert response.headers
    with pytest.raises(AttributeError):
        response.headers = {"hello": "world"}

    assert response.reason == "OK"
    with pytest.raises(AttributeError):
        response.reason = "Not OK"

    assert response.content_type == 'text/html; charset=utf-8'
    with pytest.raises(AttributeError):
        response.content_type = "bad content type"

    assert response.is_closed
    with pytest.raises(AttributeError):
        response.is_closed = False

    assert response.is_stream_consumed
    with pytest.raises(AttributeError):
        response.is_stream_consumed = False

    # you can set encoding
    assert response.encoding == "utf-8"
    response.encoding = "blah"
    assert response.encoding == "blah"

    assert isinstance(response.url, str)
    with pytest.raises(AttributeError):
        response.url = "http://fakeurl"

    assert response.content is not None
    with pytest.raises(AttributeError):
        response.content = b"bad"