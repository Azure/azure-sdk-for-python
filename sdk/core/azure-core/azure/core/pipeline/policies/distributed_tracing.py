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

from azure.core.pipeline import PipelineRequest, PipelineResponse
from azure.core.tracing.context import tracing_context
from azure.core.tracing.abstract_span import AbstractSpan
from azure.core.tracing.common import set_span_contexts
from azure.core.pipeline.policies import SansIOHTTPPolicy
from azure.core.settings import settings

try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse

try:
    from typing import TYPE_CHECKING
except ImportError:
    TYPE_CHECKING = False

if TYPE_CHECKING:
    from typing import Any, Optional
    from azure.core.pipeline.transport import HttpRequest, HttpResponse


class DistributedTracingPolicy(SansIOHTTPPolicy):
    """The policy to create spans for Azure Calls"""

    def __init__(self):
        # type: (str, str, str) -> None
        self.parent_span_dict = {}
        self._request_id = "x-ms-client-request-id"
        self._response_id = "x-ms-request-id"

    def set_header(self, request, span):
        # type: (PipelineRequest[HttpRequest], Any) -> None
        """
        Sets the header information on the span.
        """
        headers = span.to_header()
        request.http_request.headers.update(headers)

    def on_request(self, request):
        # type: (PipelineRequest[HttpRequest], Any) -> None
        parent_span = tracing_context.current_span.get()
        wrapper_class = settings.tracing_implementation()
        original_context = [parent_span, None]
        if parent_span is None and wrapper_class is not None:
            current_span_instance = wrapper_class.get_current_span()
            original_context[1] = current_span_instance
            parent_span = wrapper_class(current_span_instance)

        if parent_span is None:
            return

        only_propagate = settings.tracing_should_only_propagate()
        if only_propagate:
            self.set_header(request, parent_span)
            return

        path = urlparse(request.http_request.url).path
        if not path:
            path = "/"
        child = parent_span.span(name=path)
        child.start()

        set_span_contexts(child)
        self.parent_span_dict[child] = original_context
        self.set_header(request, child)

    def end_span(self, request, response=None):
        # type: (HttpRequest, Optional[HttpResponse]) -> None
        """Ends the span that is tracing the network and updates its status."""
        span = tracing_context.current_span.get()  # type: AbstractSpan
        only_propagate = settings.tracing_should_only_propagate()
        if span and not only_propagate:
            span.set_http_attributes(request, response=response)
            request_id = request.headers.get(self._request_id)
            if request_id is not None:
                span.add_attribute(self._request_id, request_id)
            if response and self._response_id in response.headers:
                span.add_attribute(self._response_id, response.headers[self._response_id])
            span.finish()
            set_span_contexts(*self.parent_span_dict.pop(span, None))

    def on_response(self, request, response):
        # type: (PipelineRequest[HttpRequest], PipelineResponse[HttpRequest, HttpResponse], Any) -> None
        self.end_span(request.http_request, response=response.http_response)

    def on_exception(self, _request):  # pylint: disable=unused-argument
        # type: (PipelineRequest[HttpRequest], Any) -> bool
        self.end_span(_request.http_request)
