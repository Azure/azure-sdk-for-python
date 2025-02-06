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
import urllib.parse
from typing import TYPE_CHECKING, Optional, Tuple, TypeVar, Union, Any, Type
from types import TracebackType

from azure.core.pipeline import PipelineRequest, PipelineResponse
from azure.core.pipeline.policies import SansIOHTTPPolicy
from azure.core.pipeline.transport import (
    HttpResponse as LegacyHttpResponse,
    HttpRequest as LegacyHttpRequest,
)
from azure.core.rest import HttpResponse, HttpRequest
from azure.core.settings import settings
from azure.core.tracing import SpanKind
from ...tracing._tracer import default_tracer_provider, TracerProvider
from ...tracing._models import TracingOptions

if TYPE_CHECKING:
    from ...tracing._abstract_span import (
        AbstractSpan,
    )
    from ...tracing.opentelemetry_span import OpenTelemetrySpan

HTTPResponseType = TypeVar("HTTPResponseType", HttpResponse, LegacyHttpResponse)
HTTPRequestType = TypeVar("HTTPRequestType", HttpRequest, LegacyHttpRequest)
ExcInfo = Tuple[Type[BaseException], BaseException, TracebackType]
OptExcInfo = Union[ExcInfo, Tuple[None, None, None]]

_LOGGER = logging.getLogger(__name__)


def _default_network_span_namer(http_request: HTTPRequestType) -> str:
    """Extract the path to be used as network span name.

    :param http_request: The HTTP request
    :type http_request: ~azure.core.pipeline.transport.HttpRequest
    :returns: The string to use as network span name
    :rtype: str
    """
    return http_request.method


class DistributedTracingPolicy(SansIOHTTPPolicy[HTTPRequestType, HTTPResponseType]):
    """The policy to create spans for Azure calls.

    :keyword network_span_namer: A callable to customize the span name
    :type network_span_namer: callable[[~azure.core.pipeline.transport.HttpRequest], str]
    :keyword tracing_attributes: Attributes to set on all created spans
    :type tracing_attributes: dict[str, str]
    """

    TRACING_CONTEXT = "TRACING_CONTEXT"

    # Current HTTP semantic conventions
    _HTTP_RESEND_COUNT = "http.request.resend_count"
    _USER_AGENT_ORIGINAL = "user_agent.original"
    _HTTP_REQUEST_METHOD = "http.request.method"
    _URL_FULL = "url.full"
    _HTTP_RESPONSE_STATUS_CODE = "http.response.status_code"
    _SERVER_ADDRESS = "server.address"
    _SERVER_PORT = "server.port"
    _ERROR_TYPE = "error.type"

    # Legacy HTTP semantic conventions
    _HTTP_USER_AGENT = "http.user_agent"
    _HTTP_METHOD = "http.method"
    _HTTP_URL = "http.url"
    _HTTP_STATUS_CODE = "http.status_code"
    _NET_PEER_NAME = "net.peer.name"
    _NET_PEER_PORT = "net.peer.port"

    # Azure attributes
    _REQUEST_ID = "x-ms-client-request-id"
    _RESPONSE_ID = "x-ms-request-id"
    _REQUEST_ID_ATTR = "az.client_request_id"
    _RESPONSE_ID_ATTR = "az.service_request_id"

    def __init__(self, *, tracer_provider: Optional[TracerProvider] = None, **kwargs: Any):
        self._network_span_namer = kwargs.get("network_span_namer", _default_network_span_namer)
        self._tracing_attributes = kwargs.get("tracing_attributes", {})
        self._tracer_provider = tracer_provider

    def on_request(self, request: PipelineRequest[HTTPRequestType]) -> None:
        ctxt = request.context.options
        try:
            tracing_options: TracingOptions = ctxt.pop("tracing_options", {})
            tracing_enabled = settings.tracing_enabled()

            # User can explicitly disable tracing for this request.
            user_enabled = tracing_options.get("enabled")
            if user_enabled is False:
                return

            # If tracing is disabled globally and user didn't explicitly enable it, don't trace.
            if not tracing_enabled and user_enabled is None:
                return

            span_impl_type = settings.tracing_implementation()
            namer = ctxt.pop("network_span_namer", self._network_span_namer)
            tracing_attributes = ctxt.pop("tracing_attributes", self._tracing_attributes)
            span_name = namer(request.http_request)

            span_attributes = {**tracing_attributes, **tracing_options.get("attributes", {})}

            if span_impl_type:
                # If the plugin is enabled, prioritize it over the core tracing.
                span = span_impl_type(name=span_name, kind=SpanKind.CLIENT)
                for attr, value in span_attributes.items():
                    span.add_attribute(attr, value)  # type: ignore

                headers = span.to_header()
                request.http_request.headers.update(headers)

                request.context[self.TRACING_CONTEXT] = span
            else:
                # Otherwise, use the core tracing.
                tracer = (
                    self._tracer_provider.get_tracer()
                    if self._tracer_provider
                    else default_tracer_provider.get_tracer()
                )
                if not tracer:
                    return

                core_span = tracer.start_span(
                    name=span_name,
                    kind=SpanKind.CLIENT,
                    attributes=span_attributes,
                    record_exception=tracing_options.get("record_exception", True),
                )

                trace_context_headers = tracer.get_trace_context()
                request.http_request.headers.update(trace_context_headers)
                request.context[self.TRACING_CONTEXT] = core_span

        except Exception as err:  # pylint: disable=broad-except
            print(err)
            _LOGGER.warning("Unable to start network span: %s", err)

    def end_span(
        self,
        request: PipelineRequest[HTTPRequestType],
        response: Optional[HTTPResponseType] = None,
        exc_info: Optional[OptExcInfo] = None,
    ) -> None:
        """Ends the span that is tracing the network and updates its status.

        :param request: The PipelineRequest object
        :type request: ~azure.core.pipeline.PipelineRequest
        :param response: The HttpResponse object
        :type response: ~azure.core.rest.HTTPResponse or ~azure.core.pipeline.transport.HttpResponse
        :param exc_info: The exception information
        :type exc_info: tuple
        """
        if self.TRACING_CONTEXT not in request.context:
            return

        span = request.context[self.TRACING_CONTEXT]
        http_request: Union[HttpRequest, LegacyHttpRequest] = request.http_request
        if span is not None:
            self._set_http_attributes(span, request=http_request, response=response)
            set_attribute_func = (
                getattr(span, "add_attribute") if hasattr(span, "add_attribute") else getattr(span, "set_attribute")
            )
            end_func = getattr(span, "finish", None) or getattr(span, "end")

            if request.context.get("retry_count"):
                set_attribute_func(self._HTTP_RESEND_COUNT, request.context["retry_count"])
            request_id = http_request.headers.get(self._REQUEST_ID)
            if request_id is not None:
                set_attribute_func(self._REQUEST_ID_ATTR, request_id)
            if response and self._RESPONSE_ID in response.headers:
                set_attribute_func(self._RESPONSE_ID_ATTR, response.headers[self._RESPONSE_ID])
            if exc_info:
                span.__exit__(*exc_info)
            else:
                end_func()

    def on_response(
        self,
        request: PipelineRequest[HTTPRequestType],
        response: PipelineResponse[HTTPRequestType, HTTPResponseType],
    ) -> None:
        self.end_span(request, response=response.http_response)

    def on_exception(self, request: PipelineRequest[HTTPRequestType]) -> None:
        self.end_span(request, exc_info=sys.exc_info())

    def _set_http_attributes(
        self,
        span: Union["AbstractSpan", "OpenTelemetrySpan"],
        request: Union[HttpRequest, LegacyHttpRequest],
        response: Optional[HTTPResponseType] = None,
    ) -> None:
        """
        Add correct attributes for a http client span.

        :param span: The span to add attributes to.
        :type span: ~azure.core.tracing.AbstractSpan or ~azure.core.tracing.opentelemetry_span.OpenTelemetrySpan
        :param request: The request made
        :type request: azure.core.rest.HttpRequest
        :param response: The response received from the server. Is None if no response received.
        :type response: ~azure.core.pipeline.transport.HttpResponse or ~azure.core.pipeline.transport.AsyncHttpResponse
        """
        set_attribute_func = (
            getattr(span, "add_attribute") if hasattr(span, "add_attribute") else getattr(span, "set_attribute")
        )

        set_attribute_func(self._HTTP_REQUEST_METHOD, request.method)
        set_attribute_func(self._URL_FULL, request.url)

        parsed_url = urllib.parse.urlparse(request.url)
        if parsed_url.hostname:
            set_attribute_func(self._SERVER_ADDRESS, parsed_url.hostname)
        if parsed_url.port and parsed_url.port not in [80, 443]:
            set_attribute_func(self._SERVER_PORT, parsed_url.port)

        user_agent = request.headers.get("User-Agent")
        if user_agent:
            set_attribute_func(self._USER_AGENT_ORIGINAL, user_agent)
        if response and response.status_code:
            set_attribute_func(self._HTTP_RESPONSE_STATUS_CODE, response.status_code)
            if response.status_code >= 400:
                set_attribute_func(self._ERROR_TYPE, str(response.status_code))
        else:
            set_attribute_func(self._HTTP_RESPONSE_STATUS_CODE, 504)
            set_attribute_func(self._ERROR_TYPE, "504")
