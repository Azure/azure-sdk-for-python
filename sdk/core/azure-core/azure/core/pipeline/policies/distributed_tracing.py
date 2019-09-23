# --------------------------------------------------------------------------
#
# Copyright (c) Microsoft Corporation. All rights reserved.
#
# The MIT License (MIT)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the ""Software""), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED *AS IS*, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
# --------------------------------------------------------------------------
"""Traces network calls using the implementation library from the settings."""
import logging
import sys
from six.moves import urllib

from azure.core.pipeline.policies import SansIOHTTPPolicy
from azure.core.settings import settings

try:
    from typing import TYPE_CHECKING
except ImportError:
    TYPE_CHECKING = False

if TYPE_CHECKING:
    # the HttpRequest and HttpResponse related type ignores stem from this issue: #5796
    from azure.core.pipeline.transport import HttpRequest, HttpResponse  # pylint: disable=ungrouped-imports
    from azure.core.tracing.abstract_span import AbstractSpan  # pylint: disable=ungrouped-imports
    from azure.core.pipeline import PipelineRequest, PipelineResponse  # pylint: disable=ungrouped-imports
    from typing import Any, Optional, Dict, List, Union, Tuple


_LOGGER = logging.getLogger(__name__)


class DistributedTracingPolicy(SansIOHTTPPolicy):
    """The policy to create spans for Azure Calls"""
    TRACING_CONTEXT = "TRACING_CONTEXT"

    def __init__(self):
        # type: () -> None
        self.parent_span_dict = {}  # type: Dict[AbstractSpan, List[Union[AbstractSpan, Any]]]
        self._request_id = "x-ms-client-request-id"
        self._response_id = "x-ms-request-id"

    def set_header(self, request, span):  # pylint: disable=no-self-use
        # type: (PipelineRequest, Any) -> None
        """
        Sets the header information on the span.
        """
        headers = span.to_header()
        request.http_request.headers.update(headers)

    def on_request(self, request):
        # type: (PipelineRequest) -> None
        try:
            span_impl_type = settings.tracing_implementation()
            if span_impl_type is None:
                return

            path = urllib.parse.urlparse(request.http_request.url).path
            if not path:
                path = "/"

            span = span_impl_type(name=path)
            span.start()

            self.set_header(request, span)

            request.context[self.TRACING_CONTEXT] = span
        except Exception as err:  # pylint: disable=broad-except
            _LOGGER.warning("Unable to start network span: %s", err)

    def end_span(self, request, response=None, exc_info=None):
        # type: (PipelineRequest, Optional[HttpResponse], Optional[Tuple]) -> None
        """Ends the span that is tracing the network and updates its status."""
        if self.TRACING_CONTEXT not in request.context:
            return

        span = request.context[self.TRACING_CONTEXT]  # type: AbstractSpan
        http_request = request.http_request  # type: HttpRequest
        if span is not None:
            span.set_http_attributes(http_request, response=response)
            request_id = http_request.headers.get(self._request_id)
            if request_id is not None:
                span.add_attribute(self._request_id, request_id)
            if response and self._response_id in response.headers:
                span.add_attribute(self._response_id, response.headers[self._response_id])
            if exc_info:
                span.__exit__(*exc_info)
            else:
                span.finish()

    def on_response(self, request, response):
        # type: (PipelineRequest, PipelineResponse) -> None
        self.end_span(request, response=response.http_response)

    def on_exception(self, request):  # pylint: disable=unused-argument
        # type: (PipelineRequest) -> bool
        self.end_span(request, exc_info=sys.exc_info())
        return False
