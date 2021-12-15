# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import pytest
import types
############################## LISTS USED TO PARAMETERIZE TESTS ##############################
from azure.core.rest import HttpRequest as RestHttpRequest
from azure.core.pipeline.transport import HttpRequest as PipelineTransportHttpRequest
from azure.core.pipeline._tools import is_rest
HTTP_REQUESTS = [PipelineTransportHttpRequest, RestHttpRequest]
REQUESTS_TRANSPORT_RESPONSES = []

from azure.core.pipeline.transport import HttpResponse as PipelineTransportHttpResponse
from azure.core.rest._http_response_impl import HttpResponseImpl as RestHttpResponse
HTTP_RESPONSES = [PipelineTransportHttpResponse, RestHttpResponse]

ASYNC_HTTP_RESPONSES = []

try:
    from azure.core.pipeline.transport import AsyncHttpResponse as PipelineTransportAsyncHttpResponse
    from azure.core.rest._http_response_impl_async import AsyncHttpResponseImpl as RestAsyncHttpResponse
    ASYNC_HTTP_RESPONSES = [PipelineTransportAsyncHttpResponse, RestAsyncHttpResponse]
except (ImportError, SyntaxError):
    pass

try:
    from azure.core.pipeline.transport import RequestsTransportResponse as PipelineTransportRequestsTransportResponse
    from azure.core.rest._requests_basic import RestRequestsTransportResponse
    REQUESTS_TRANSPORT_RESPONSES = [PipelineTransportRequestsTransportResponse, RestRequestsTransportResponse]
except ImportError:
    pass

from azure.core.pipeline.transport._base import HttpClientTransportResponse as PipelineTransportHttpClientTransportResponse
from azure.core.rest._http_response_impl import RestHttpClientTransportResponse
HTTP_CLIENT_TRANSPORT_RESPONSES = [PipelineTransportHttpClientTransportResponse, RestHttpClientTransportResponse]

ASYNCIO_REQUESTS_TRANSPORT_RESPONSES = []

try:
    from azure.core.pipeline.transport import AsyncioRequestsTransportResponse as PipelineTransportAsyncioRequestsTransportResponse
    from azure.core.rest._requests_asyncio import RestAsyncioRequestsTransportResponse
    ASYNCIO_REQUESTS_TRANSPORT_RESPONSES = [PipelineTransportAsyncioRequestsTransportResponse, RestAsyncioRequestsTransportResponse]
except (ImportError, SyntaxError):
    pass

AIOHTTP_TRANSPORT_RESPONSES = []

try:
    from azure.core.pipeline.transport import AioHttpTransportResponse as PipelineTransportAioHttpTransportResponse
    from azure.core.rest._aiohttp import RestAioHttpTransportResponse
    AIOHTTP_TRANSPORT_RESPONSES = [PipelineTransportAioHttpTransportResponse, RestAioHttpTransportResponse]
except (ImportError, SyntaxError):
    pass

############################## HELPER FUNCTIONS ##############################

def request_and_responses_product(*args):
    pipeline_transport = tuple([PipelineTransportHttpRequest]) + tuple(arg[0] for arg in args)
    rest = tuple([RestHttpRequest]) + tuple(arg[1] for arg in args)
    return [pipeline_transport, rest]

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

def create_transport_response(http_response, *args, **kwargs):
    # this creates transport-specific responses,
    # like requests responses / aiohttp responses
    if is_rest(http_response):
        block_size = args[2] if len(args) > 2 else None
        return http_response(
            request=args[0],
            internal_response=args[1],
            block_size=block_size,
            **kwargs
        )
    return http_response(*args, **kwargs)

def create_http_response(http_response, *args, **kwargs):
    # since the actual http_response object is
    # an ABC for our new responses, it's a little more
    # complicated creating a pure http response.
    # here, we use the HttpResponsImpl, but we still have to pass
    # more things to the init, so making a separate operation
    if is_rest(http_response):
        block_size = args[2] if len(args) > 2 else None
        return http_response(
            request=args[0],
            internal_response=args[1],
            block_size=block_size,
            status_code=kwargs.pop("status_code", 200),
            reason=kwargs.pop("reason", "OK"),
            content_type=kwargs.pop("content_type", "application/json"),
            headers=kwargs.pop("headers", {}),
            stream_download_generator=kwargs.pop("stream_download_generator", None),
            **kwargs
        )
    return http_response(*args, **kwargs)

def readonly_checks(response, old_response_class):
    # though we want these properties to be completely readonly, it doesn't work
    # for the backcompat properties
    assert isinstance(response.request, RestHttpRequest)
    assert isinstance(response.status_code, int)
    assert response.headers
    assert response.content_type == 'text/html; charset=utf-8'

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

    old_response = old_response_class(response.request, response.internal_response, response.block_size)
    for attr in dir(response):
        if attr[0] == '_':
            # don't care about private variables
            continue
        if type(getattr(response, attr)) == types.MethodType:
            # methods aren't "readonly"
            continue
        if attr == "encoding":
            # encoding is the only settable new attr
            continue
        if not attr in vars(old_response):
            with pytest.raises(AttributeError):
                setattr(response, attr, "new_value")
