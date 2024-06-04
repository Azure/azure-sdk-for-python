# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import pytest
import types
import io

############################## LISTS USED TO PARAMETERIZE TESTS ##############################
from corehttp.rest import HttpRequest
from corehttp.rest._http_response_impl import HttpResponseImpl as RestHttpResponse
from corehttp.rest._http_response_impl_async import AsyncHttpResponseImpl as RestAsyncHttpResponse


SYNC_TRANSPORTS = []
ASYNC_TRANSPORTS = []

SYNC_TRANSPORT_RESPONSES = []
ASYNC_TRANSPORT_RESPONSES = []

try:
    from corehttp.rest._requests_basic import RestRequestsTransportResponse
    from corehttp.transport.requests import RequestsTransport

    SYNC_TRANSPORTS.append(RequestsTransport)
    SYNC_TRANSPORT_RESPONSES.append(RestRequestsTransportResponse)
except (ImportError, SyntaxError):
    pass

try:
    from corehttp.rest._aiohttp import RestAioHttpTransportResponse
    from corehttp.transport.aiohttp import AioHttpTransport

    ASYNC_TRANSPORTS.append(AioHttpTransport)
    ASYNC_TRANSPORT_RESPONSES.append(RestAioHttpTransportResponse)
except (ImportError, SyntaxError):
    pass

try:
    from corehttp.rest._httpx import HttpXTransportResponse, AsyncHttpXTransportResponse
    from corehttp.transport.httpx import HttpXTransport, AsyncHttpXTransport

    SYNC_TRANSPORTS.append(HttpXTransport)
    SYNC_TRANSPORT_RESPONSES.append(HttpXTransportResponse)
    ASYNC_TRANSPORTS.append(AsyncHttpXTransport)
    ASYNC_TRANSPORT_RESPONSES.append(AsyncHttpXTransportResponse)
except (ImportError, SyntaxError):
    pass

HTTP_RESPONSES = [RestHttpResponse]
ASYNC_HTTP_RESPONSES = [RestAsyncHttpResponse]

############################## HELPER FUNCTIONS ##############################


def create_transport_response(http_response, *args, **kwargs):
    # this creates transport-specific responses,
    # like requests responses / aiohttp responses

    block_size = args[2] if len(args) > 2 else None
    return http_response(request=args[0], internal_response=args[1], block_size=block_size, **kwargs)


def create_http_response(http_response, *args, **kwargs):
    # since the actual http_response object is
    # an ABC for our new responses, it's a little more
    # complicated creating a pure http response.
    # here, we use the HttpResponsImpl, but we still have to pass
    # more things to the init, so making a separate operation
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


def readonly_checks(response):
    # We want these properties to be completely readonly.
    assert isinstance(response.request, HttpRequest)
    assert isinstance(response.status_code, int)
    assert response.headers
    assert response.content_type == "text/html; charset=utf-8"

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

    for attr in dir(response):
        if attr[0] == "_":
            # don't care about private variables
            continue
        if type(getattr(response, attr)) == types.MethodType:
            # methods aren't "readonly"
            continue
        if attr == "encoding":
            # encoding is the only settable new attr
            continue


class NamedIo(io.BytesIO):
    def __init__(self, name: str, *args, **kwargs):
        super(NamedIo, self).__init__(*args, **kwargs)
        self.name = name
