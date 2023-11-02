# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import pytest
import types

############################## LISTS USED TO PARAMETERIZE TESTS ##############################
from corehttp.rest import HttpRequest as RestHttpRequest

HTTP_REQUESTS = [RestHttpRequest]
REQUESTS_TRANSPORT_RESPONSES = []

from corehttp.rest._http_response_impl import HttpResponseImpl as RestHttpResponse

HTTP_RESPONSES = [RestHttpResponse]

ASYNC_HTTP_RESPONSES = []

try:
    from corehttp.rest._http_response_impl_async import AsyncHttpResponseImpl as RestAsyncHttpResponse

    ASYNC_HTTP_RESPONSES = [RestAsyncHttpResponse]
except (ImportError, SyntaxError):
    pass

try:
    from corehttp.rest._requests_basic import RestRequestsTransportResponse

    REQUESTS_TRANSPORT_RESPONSES = [RestRequestsTransportResponse]
except ImportError:
    pass

from corehttp.rest._http_response_impl import RestHttpClientTransportResponse

HTTP_CLIENT_TRANSPORT_RESPONSES = [RestHttpClientTransportResponse]

AIOHTTP_TRANSPORT_RESPONSES = []

try:
    from corehttp.rest._aiohttp import RestAioHttpTransportResponse

    AIOHTTP_TRANSPORT_RESPONSES = [RestAioHttpTransportResponse]
except (ImportError, SyntaxError):
    pass

############################## HELPER FUNCTIONS ##############################


def request_and_responses_product(*args):
    rest = tuple([RestHttpRequest]) + tuple(arg[0] for arg in args)
    return [rest]


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
        return http_request(method=method, url=url, headers=headers, files=files, data=data, **kwargs)
    return http_request(*args, **kwargs)


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
    assert isinstance(response.request, RestHttpRequest)
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
