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
from typing import TYPE_CHECKING
from ..exceptions import StreamConsumedError, StreamClosedError
from . import SupportedFormat, PipelineRequest, PipelineResponse

if TYPE_CHECKING:
    from typing import Any, Optional, Callable, Iterator, Union
    from ..rest import (
        HttpRequest as RestHttpRequest,
        HttpResponse as RestHttpResponse
    )
    from .transport import (
        HttpRequest as PipelineTransportHttpRequest,
        HttpResponse as PipelineTransportHttpResponse,
    )
    HTTPRequestType = Union[RestHttpRequest, PipelineTransportHttpRequest, PipelineRequest]
    HTTPResponseType = Union[RestHttpResponse, PipelineTransportHttpResponse, PipelineResponse]


def await_result(func, *args, **kwargs):
    """If func returns an awaitable, raise that this runner can't handle it."""
    result = func(*args, **kwargs)
    if hasattr(result, "__await__"):
        raise TypeError(
            "Policy {} returned awaitable object in non-async pipeline.".format(func)
        )
    return result

def _stream_download_helper(decompress, stream_download_generator, response, chunk_size=None):
    # type: (bool, Callable, HttpResponse, Optional[int]) -> Iterator[bytes]
    if response.is_stream_consumed:
        raise StreamConsumedError()
    if response.is_closed:
        raise StreamClosedError()

    response.is_stream_consumed = True
    stream_download = stream_download_generator(
        pipeline=None,
        response=response,
        chunk_size=chunk_size or response._connection_data_block_size,  # pylint: disable=protected-access
        decompress=decompress,
    )
    for part in stream_download:
        response._num_bytes_downloaded += len(part)
        yield part

def iter_bytes_helper(stream_download_generator, response, chunk_size=None):
    # type: (Callable, HttpResponse, Optional[int]) -> Iterator[bytes]
    if response._has_content():  # pylint: disable=protected-access
        if chunk_size is None:
            chunk_size = len(response.content)
        for i in range(0, len(response.content), chunk_size):
            yield response.content[i: i + chunk_size]
    else:
        for part in _stream_download_helper(
            decompress=True,
            stream_download_generator=stream_download_generator,
            response=response,
            chunk_size=chunk_size
        ):
            yield part
    response.close()

def iter_raw_helper(stream_download_generator, response, chunk_size=None):
    # type: (Callable, HttpResponse, Optional[int]) -> Iterator[bytes]
    for raw_bytes in _stream_download_helper(
        decompress=False,
        stream_download_generator=stream_download_generator,
        response=response,
        chunk_size=chunk_size
    ):
        yield raw_bytes
    response.close()

def get_format(input):
    """Pass in a request or a response to get it's format

    :param input: Request or response
    """
    if hasattr(input, "http_response"):
        inner_input = input.http_response
    elif hasattr(input, "http_request"):
        inner_input = input.http_request
    else:
        inner_input = input
    if hasattr(inner_input, "content"):
        return SupportedFormat.REST
    if hasattr(inner_input, "body"):
        return SupportedFormat.PIPELINE_TRANSPORT
    raise ValueError(
        "The input you passed in has type {} which is not supported. ".format(type(input)) +
        "We recommend you use requests and response from azure.core.rest, but we also accept " +
        "requests and responses from azure.core.pipeline.transport"
    )

def to_rest_response_helper(pipeline_transport_response, response_type):
    response = response_type(
        request=pipeline_transport_response.request._convert(),  # pylint: disable=protected-access
        internal_response=pipeline_transport_response.internal_response,
    )
    response._connection_data_block_size = pipeline_transport_response.block_size  # pylint: disable=protected-access
    return response

def to_pipeline_transport_helper(rest_response, response_type):
    return response_type(
        rest_response.request._convert(),  # pylint: disable=protected-access
        rest_response.internal_response,
        block_size=rest_response._connection_data_block_size  # pylint: disable=protected-access
    )

def prepare_request(sender, request):
    # type: (Any, HTTPRequestType) -> HTTPRequestType
    """Prepare the request for the next sender.

    Converts the request into the type the sender can handle.
    If the sender can handle azure.core.rest requests, we return
    an azure.core.rest request. Otherwise, we return an azure.core.pipeline.transport request

    :param any sender: Either the transport or the next policy in line.
    :param request: The request passed in by the user
    :type request: ~azure.core.rest.HttpRequest or ~azure.core.pipeline.transport.HttpRequest or ~azure.core.pipeline.PipelineRequest
    :return: The request in the format the sender can handle.
    """
    request_format = get_format(request)
    supported_formats = sender.supported_formats if hasattr(sender, "supported_formats") else [SupportedFormat.PIPELINE_TRANSPORT]
    if request_format in supported_formats:
        return request
    if hasattr(request, "http_request"):
        # if I'm a PipelineRequest, need to call a cls method to create a new one
        return PipelineRequest._convert(request)
    return request._convert()

def prepare_response(request, response):
    # type: (HTTPRequestType, HTTPResponseType) -> HTTPResponseType
    """Prepare the response to have the same format as the inputted request.

    Converts the response into the format of the passed in request.

    :param request: The request passed in by the user
    :type request: ~azure.core.rest.HttpRequest or
     ~azure.core.pipeline.transport.HttpRequest or ~azure.core.pipeline.PipelineRequest
    :param response: The current format of the response. May be converted if it has
     a different format than the inputted request
    :type response: ~azure.core.rest.HttpResponse or ~azure.core.pipeline.transport.HttpResponse
     or ~azure.core.pipeline.PipelineResponse
    :return: The response in the same format as the inputted request
    """
    if get_format(request) == get_format(response):
        return response
    if hasattr(response, "http_response"):
        # if I'm a PipelineResponse, need to call a cls method to create a new one
        return PipelineResponse._convert(response)
    return response._convert()
