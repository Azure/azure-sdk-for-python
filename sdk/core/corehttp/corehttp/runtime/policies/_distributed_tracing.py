# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from __future__ import annotations
import logging
import urllib.parse
from typing import Any, Optional, Tuple, Union, Type, TYPE_CHECKING
from types import TracebackType

from ...rest import HttpRequest
from ...rest._rest_py3 import _HttpResponseBase as SansIOHttpResponse
from ._base import SansIOHTTPPolicy
from ...settings import settings
from ...instrumentation.tracing._models import SpanKind, TracingOptions
from ...instrumentation.tracing._tracer import TracerProvider, default_tracer_provider

if TYPE_CHECKING:
    from ..pipeline import PipelineRequest, PipelineResponse
    from ...instrumentation.tracing.opentelemetry_span import OpenTelemetrySpan


ExcInfo = Tuple[Type[BaseException], BaseException, TracebackType]
OptExcInfo = Union[ExcInfo, Tuple[None, None, None]]

_LOGGER = logging.getLogger(__name__)


def _get_span_name(http_request: HttpRequest) -> str:
    path = urllib.parse.urlparse(http_request.url).path
    if not path:
        path = "/"
    return f"{http_request.method} {path}"


class DistributedTracingPolicy(SansIOHTTPPolicy[HttpRequest, SansIOHttpResponse]):
    """The policy to create tracing spans for API calls.

    :keyword tracer_provider: The tracer provider to use. If not provided, a default tracer provider will be used.
    :paramtype tracer_provider: ~corehttp.instrumentation.tracing.TracerProvider
    """

    TRACING_CONTEXT = "TRACING_CONTEXT"

    # Attribute names
    _HTTP_RESEND_COUNT = "http.request.resend_count"

    _USER_AGENT_ORIGINAL = "user_agent.original"
    _HTTP_REQUEST_METHOD = "http.request.method"
    _URL_FULL = "url.full"
    _HTTP_RESPONSE_STATUS_CODE = "http.response.status_code"
    _SERVER_ADDRESS = "server.address"
    _SERVER_PORT = "server.port"
    _ERROR_TYPE = "error.type"

    def __init__(  # pylint: disable=unused-argument
        self,
        *,
        tracer_provider: Optional[TracerProvider] = None,
        **kwargs: Any,
    ) -> None:
        self._tracer_provider = tracer_provider

    def on_request(self, request: PipelineRequest[HttpRequest]) -> None:
        ctxt = request.context.options
        try:
            tracing_options: TracingOptions = ctxt.pop("tracing_options", {})

            # User can explicitly disable tracing for this request.
            user_enabled = tracing_options.get("enabled")
            if user_enabled is False:
                return

            # If tracing is disabled globally and user didn't explicitly enable it, don't trace.
            if not settings.tracing_enabled and user_enabled is None:
                return

            tracer = (
                self._tracer_provider.get_tracer() if self._tracer_provider else default_tracer_provider.get_tracer()
            )
            if not tracer:
                return

            span_name = _get_span_name(request.http_request)
            span = tracer.start_span(
                name=span_name,
                kind=SpanKind.CLIENT,
                attributes=tracing_options.get("attributes"),
                record_exception=tracing_options.get("record_exception", True),
            )

            trace_context_headers = tracer.get_trace_context()
            request.http_request.headers.update(trace_context_headers)
            request.context[self.TRACING_CONTEXT] = span
        except Exception as err:  # pylint: disable=broad-except
            _LOGGER.warning("Unable to start HTTP span: %s", err)

    def on_response(
        self,
        request: PipelineRequest[HttpRequest],
        response: PipelineResponse[HttpRequest, SansIOHttpResponse],
    ) -> None:
        if self.TRACING_CONTEXT not in request.context:
            return

        span: "OpenTelemetrySpan" = request.context[self.TRACING_CONTEXT]
        http_request = request.http_request
        if span:
            self._add_http_attributes(span, http_request, response=response.http_response)
            if request.context.get("retry_count"):
                span.set_attribute(self._HTTP_RESEND_COUNT, request.context["retry_count"])
            span.end()

    def _add_http_attributes(
        self,
        span: "OpenTelemetrySpan",
        http_request: HttpRequest,
        response: Optional[SansIOHttpResponse],
    ) -> None:

        span.set_attribute(self._HTTP_REQUEST_METHOD, http_request.method)
        span.set_attribute(self._URL_FULL, http_request.url)

        parsed_url = urllib.parse.urlparse(http_request.url)
        if parsed_url.hostname:
            span.set_attribute(self._SERVER_ADDRESS, parsed_url.hostname)
        if parsed_url.port and parsed_url.port not in [80, 443]:
            span.set_attribute(self._SERVER_PORT, parsed_url.port)

        user_agent = http_request.headers.get("User-Agent")
        if user_agent:
            span.set_attribute(self._USER_AGENT_ORIGINAL, user_agent)
        if response and response.status_code:
            span.set_attribute(self._HTTP_RESPONSE_STATUS_CODE, response.status_code)
            if response.status_code >= 400:
                span.set_attribute(self._ERROR_TYPE, str(response.status_code))
        else:
            span.set_attribute(self._HTTP_RESPONSE_STATUS_CODE, 504)
            span.set_attribute(self._ERROR_TYPE, "504")
