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
    from typing import TYPE_CHECKING
except ImportError:
    TYPE_CHECKING = False

if TYPE_CHECKING:
    from typing import Any, TypeVar, Optional

    HTTPResponseType = TypeVar("HTTPResponseType")
    HTTPRequestType = TypeVar("HTTPRequestType")


class DistributedTracingPolicy(SansIOHTTPPolicy):
    """The policy to create spans for Azure Calls"""

    def __init__(self, name_of_spans="span - http call"):
        # type: (str, str, str) -> None
        self.name_of_child_span = name_of_spans
        self.parent_span_dict = {}
        self._http_user_agent = "http.user_agent"
        self._http_method = "http.method"
        self._http_url = "http.url"
        self._http_status_code = "http.status_code"
        self._request_id = "x-ms-request-id"

    def set_header(self, request, span):
        # type: (PipelineRequest[HTTPRequestType], Any) -> None
        """
        Sets the header information on the span.
        """
        headers = span.to_header()
        request.http_request.headers.update(headers)
        span.add_attribute(self._http_method, request.http_request.method)
        span.add_attribute(self._http_url, request.http_request.url)
        span.add_attribute(self._http_user_agent, request.http_request.headers.get("User-Agent", ""))

    def on_request(self, request, **kwargs):
        # type: (PipelineRequest[HTTPRequestType], Any) -> None
        parent_span = tracing_context.current_span.get()  # type: AbstractSpan

        if parent_span is None:
            return

        only_propagate = settings.tracing_should_only_propagate()
        if only_propagate:
            self.set_header(request, parent_span)
            return

        child = parent_span.span(name=self.name_of_child_span)
        child.start()

        set_span_contexts(child)
        self.parent_span_dict[child] = parent_span
        self.set_header(request, child)

    def end_span(self, response=None):
        # type: (Optional[PipelineResponse[HTTPRequestType, HTTPResponseType]]) -> None
        """Ends the span that is tracing the network and updates its status."""
        span = tracing_context.current_span.get()  # type: AbstractSpan
        only_propagate = settings.tracing_should_only_propagate()
        if span and not only_propagate:
            # span.add_attribute("http.url", request.http_request)
            if response:
                span.add_attribute(self._http_status_code, response.http_response.status_code)
                span.add_attribute(self._request_id, response.http_response.headers.get(self._request_id, ""))
            else:
                span.add_attribute(self._http_status_code, 504)
            span.finish()
            set_span_contexts(self.parent_span_dict[span])

    def on_response(self, request, response, **kwargs):
        # type: (PipelineRequest[HTTPRequestType], PipelineResponse[HTTPRequestType, HTTPResponseType], Any) -> None
        self.end_span(response=response)

    def on_exception(self, _request, **kwargs):  # pylint: disable=unused-argument
        # type: (PipelineRequest[HTTPRequestType], Any) -> bool
        self.end_span()
