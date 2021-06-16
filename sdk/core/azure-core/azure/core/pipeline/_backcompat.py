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
from enum import Enum
from ..rest import HttpRequest as CoreRestHttpRequest

if TYPE_CHECKING:
    from typing import Union

class SupportedFormat(str, Enum):
    PIPELINE_TRANSPORT = "pipeline_transport"
    REST = "rest"

def _to_pipeline_transport_request(**kwargs):
    from .transport._base import HttpRequest as PipelineTransportHttpRequest
    request=kwargs.pop("request")
    return PipelineTransportHttpRequest(
        method=request.method,
        url=request.url,
        headers=request.headers,
        files=request._files,
        data=request._data,
    )

def get_request_from_format(format, **kwargs):
    request = kwargs.pop("request")
    supported_formats = [SupportedFormat.PIPELINE_TRANSPORT] # old transports don't have this property
    transport = kwargs.pop("transport")
    if hasattr(transport, "supported_formats") and hasattr(transport.supported_formats, "__iter__"):
        supported_formats = transport.supported_formats

    if format not in supported_formats:
        raise ValueError(
            "You passed in a request of type {}, which is not supported by the transport. Supported request types are {}".format(
                format, supported_formats
            )
        )
    if format != SupportedFormat.PIPELINE_TRANSPORT:
        # for backcompat reasons, our pipeline runs azure.core.pipeline.transport.HttpRequests
        request = _to_pipeline_transport_request(request=request)
    return request

def request_to_format(request):
    if hasattr(request, "content"):
        return SupportedFormat.REST
    if hasattr(request, "body"):
        return SupportedFormat.PIPELINE_TRANSPORT
    raise ValueError(
        "The request you passed in has type {} which is not supported. ".format(type(request)) +
        "Recommended format is azure.core.rest.HttpRequest, we also support azure.core.pipeline.transport.HttpRequest"
    )

def get_response_from_format(format, **kwargs):
    request = kwargs.pop("request")
    pipeline_transport_response = kwargs.pop("response")
    transport = kwargs.pop("transport")
    try:
        response_type = transport.format_to_response_type(format)
    except AttributeError:
        raise ValueError(
            "Your response is of format {}, while your transport can only support ".format(type(pipeline_transport_response)) +
            "azure.core.pipeline.transport.HttpResponse"
        )

    # we know response type (for now) is azure.core.rest
    response = response_type(
        request=request,
        internal_response=pipeline_transport_response.internal_response,
    )
    response._connection_data_block_size = pipeline_transport_response.block_size
    return response
