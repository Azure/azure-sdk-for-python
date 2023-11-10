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
from typing import TypeVar, Any

from ..pipeline import PipelineRequest, PipelineResponse
from ...rest import HttpResponse, HttpRequest, AsyncHttpResponse
from ._base import SansIOHTTPPolicy

HttpResponseTypes = TypeVar("HttpResponseTypes", HttpResponse, AsyncHttpResponse)


class CustomHookPolicy(SansIOHTTPPolicy[HttpRequest, HttpResponseTypes]):
    """A simple policy that calls the given callback(s) on the pipeline request and response.

    :keyword callable raw_request_hook: Callback function. Will be invoked on request.
    :keyword callable raw_response_hook: Callback function. Will be invoked on response.
    """

    def __init__(self, **kwargs: Any):
        self._request_callback = kwargs.get("raw_request_hook")
        self._response_callback = kwargs.get("raw_response_hook")

    def on_request(self, request: PipelineRequest[HttpRequest]) -> None:
        """This is executed before sending the request to the next policy.

        :param request: The PipelineRequest object.
        :type request: ~corehttp.runtime.pipeline.PipelineRequest
        """
        request_callback = request.context.options.pop("raw_request_hook", None)
        if request_callback:
            request.context["raw_request_hook"] = request_callback
            request_callback(request)
        elif self._request_callback:
            self._request_callback(request)

        response_callback = request.context.options.pop("raw_response_hook", None)
        if response_callback:
            request.context["raw_response_hook"] = response_callback

    def on_response(
        self, request: PipelineRequest[HttpRequest], response: PipelineResponse[HttpRequest, HttpResponseTypes]
    ) -> None:
        """This is executed after the request comes back from the policy.

        :param request: The PipelineRequest object.
        :type request: ~corehttp.runtime.pipeline.PipelineRequest
        :param response: The PipelineResponse object.
        :type response: ~corehttp.runtime.pipeline.PipelineRequest
        """
        response_callback = response.context.get("raw_response_hook")
        if response_callback:
            response_callback(response)
        elif self._response_callback:
            self._response_callback(response)
