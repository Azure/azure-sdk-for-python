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
from azure.core.pipeline import PipelineRequest
from azure.core.pipeline.transport import (
    HttpResponse as LegacyHttpResponse,
    HttpRequest as LegacyHttpRequest,
)
from azure.core.rest import HttpResponse, HttpRequest
from azure.core.policies import SansIOHTTPPolicy

HTTPResponseType = TypeVar("HTTPResponseType", HttpResponse, LegacyHttpResponse)
HTTPRequestType = TypeVar("HTTPRequestType", HttpRequest, LegacyHttpRequest)


class InvokePolicy(SansIOHTTPPolicy[HTTPRequestType, HTTPResponseType]):
    """A simple policy that enable the given callback
    with the response.

    :keyword callback acquire_policy_token_hook: Callback function. Will be invoked on request.
    """

    def __init__(self, **kwargs: Any):
        self._callback = kwargs.get("acquire_policy_token_hook")

    def on_request(self, request: PipelineRequest[HTTPRequestType]) -> None:
        """This is executed before sending the request to the next policy.

        :param request: The PipelineRequest object.
        :type request: ~azure.core.pipeline.PipelineRequest
        """
        request_callback = request.context.options.pop("acquire_policy_token_hook", None)
        if request_callback:
            request.context["acquire_policy_token_hook"] = request_callback
            request_callback(request)
        elif self._request_callback:
            self._request_callback(request)
