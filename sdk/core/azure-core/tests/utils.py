# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import pytest
############################## LISTS USED TO PARAMETERIZE TESTS ##############################
from azure.core.rest import HttpRequest as RestHttpRequest
from azure.core.pipeline.transport import HttpRequest as PipelineTransportHttpRequest

HTTP_REQUESTS = [PipelineTransportHttpRequest, RestHttpRequest]


############################## HELPER FUNCTIONS ##############################

def is_rest(http_request):
    return hasattr(http_request, "content")

def create_http_request(http_request, *args, **kwargs):
    if hasattr(http_request, "content"):
        method = args[0]
        url = args[1]
        try:
            headers = args[2]
        except IndexError:
            headers = None
        try:
            files = args[3]
        except IndexError:
            files = None
        try:
            data = args[4]
        except IndexError:
            data = None
        return http_request(
            method=method,
            url=url,
            headers=headers,
            files=files,
            data=data,
            **kwargs
        )
    return http_request(*args, **kwargs)

def readonly_checks(response):
    assert isinstance(response.request, RestHttpRequest)
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
