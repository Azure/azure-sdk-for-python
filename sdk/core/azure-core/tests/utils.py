# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import pytest
############################## LISTS USED TO PARAMETERIZE TESTS ##############################
from azure.core.pipeline.transport import(
    HttpRequest as PipelineTransportHttpRequest,
    HttpResponse as PipelineTransportHttpResponse,
)

from azure.core.rest import (
    HttpRequest as RestHttpRequest,
    HttpResponse as RestHttpResponse,
)

HTTP_REQUESTS = [PipelineTransportHttpRequest, RestHttpRequest]
HTTP_RESPONSES = [PipelineTransportHttpResponse, RestHttpResponse]

try:
    from azure.core.pipeline.transport import AsyncHttpResponse as PipelineTransportAsyncHttpResponse
    from azure.core.rest import AsyncHttpResponse as RestAsyncHttpResponse
    ASYNC_HTTP_RESPONSES = [PipelineTransportAsyncHttpResponse, RestAsyncHttpResponse]
except (SyntaxError, ImportError):
    ASYNC_HTTP_RESPONSES = None

try:
    from azure.core.pipeline.transport._requests_basic import (
        RequestsTransportResponse as PipelineTransportRequestsTransportResponse,
        RestRequestsTransportResponse,
    )
    REQUESTS_TRANSPORT_RESPONSES = [PipelineTransportRequestsTransportResponse, RestRequestsTransportResponse]
except (SyntaxError, ImportError):
    REQUESTS_TRANSPORT_RESPONSES = None

try:
    from azure.core.pipeline.transport._aiohttp import (
        AioHttpTransportResponse as PipelineTransportAioHttpTransportResponse,
        RestAioHttpTransportResponse
    )
    AIOHTTP_TRANSPORT_RESPONSES = [PipelineTransportAioHttpTransportResponse, RestAioHttpTransportResponse]
except (SyntaxError, ImportError):
    AIOHTTP_TRANSPORT_RESPONSES = None


try:
    from azure.core.pipeline.transport._requests_asyncio import (
        AsyncioRequestsTransportResponse as PipelineTransportAsyncioRequestsTransportResponse,
        RestAsyncioRequestsTransportResponse,
    )
    ASYNCIO_REQUESTS_TRANSPORT_RESPONSES = [PipelineTransportAsyncioRequestsTransportResponse, RestAsyncioRequestsTransportResponse]
except (SyntaxError, ImportError):
    ASYNCIO_REQUESTS_TRANSPORT_RESPONSES = None

def pipeline_transport_and_rest_product(*args):
    # add pipeline transport requests / responses
    my_response = [
        tuple(arg[0] for arg in args)
    ]
    # add rest requests / responses
    my_response.extend([
        tuple(arg[1] for arg in args)
    ])
    return my_response

############################## HELPER FUNCTIONS ##############################

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

def create_http_response(http_response, *args, **kwargs):
    if hasattr(http_response, "content"):
        response = http_response(request=args[0], internal_response=args[1], **kwargs)
        if len(args) > 2:
            response._connection_data_block_size = args[2]
        return response
    return http_response(*args, **kwargs)

def is_rest_http_request(http_request):
    return hasattr(http_request, "content")

def is_rest_http_response(http_response):
    return hasattr(http_response, "content")

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
