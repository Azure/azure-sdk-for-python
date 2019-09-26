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
"""
This module is the requests implementation of Pipeline ABC
"""
from azure.core.pipeline import PipelineRequest, PipelineResponse
from .base import SansIOHTTPPolicy

class CustomHookPolicy(SansIOHTTPPolicy):
    """A simple policy that enable the given callback
    with the response.

    **Keyword argument:**

    *raw_response_hook* - Callback function. Will be invoked on response.
    """
    def __init__(self, **kwargs): # pylint: disable=unused-argument,super-init-not-called
        self._callback = None

    def on_request(self, request): # type: ignore # pylint: disable=arguments-differ
        # type: (PipelineRequest) -> None
        """This is executed before sending the request to the next policy.

        :param request: The PipelineRequest object.
        :type request: ~azure.core.pipeline.PipelineRequest
        """
        self._callback = request.context.options.pop('raw_response_hook', None) # type: ignore


    def on_response(self, request, response): # type: ignore # pylint: disable=arguments-differ
        # type: (PipelineRequest, PipelineResponse) -> None
        """This is executed after the request comes back from the policy.

        :param request: The PipelineRequest object.
        :type request: ~azure.core.pipeline.PipelineRequest
        :param response: The PipelineResponse object.
        :type response: ~azure.core.pipeline.PipelineResponse
        """
        if self._callback:
            self._callback(response)
            request.context.options.update({'raw_response_hook': self._callback}) # type: ignore
