# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from __future__ import annotations
import logging
import urllib.parse
from typing import Any, Optional, Tuple, Union, Type, Mapping, Dict, TYPE_CHECKING
from types import TracebackType

from ...rest import HttpRequest
from ...rest._rest_py3 import _HttpResponseBase as SansIOHttpResponse
from ._base import SansIOHTTPPolicy
from ...settings import settings
from ...instrumentation.tracing._models import SpanKind, TracingOptions
from ...instrumentation.tracing._tracer import get_tracer

if TYPE_CHECKING:
    from ..pipeline import PipelineRequest, PipelineResponse
    from opentelemetry.trace import Span


ExcInfo = Tuple[Type[BaseException], BaseException, TracebackType]
OptExcInfo = Union[ExcInfo, Tuple[None, None, None]]

_LOGGER = logging.getLogger(__name__)


class DistributedHttpTracingPolicy(SansIOHTTPPolicy[HttpRequest, SansIOHttpResponse]):
    """The policy to create tracing spans for API calls.

    :keyword instrumentation_config: Configuration for the instrumentation providers.
    :type instrumentation_config: dict[str, Any]
    """

    TRACING_CONTEXT = "TRACING_CONTEXT"
    _SUPPRESSION_TOKEN = "SUPPRESSION_TOKEN"

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
        instrumentation_config: Optional[Mapping[str, Any]] = None,
        **kwargs: Any,
    ) -> None:
        self._instrumentation_config = instrumentation_config

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

            config = self._instrumentation_config or {}
            tracer = get_tracer(
                library_name=config.get("library_name"),
                library_version=config.get("library_version"),
                attributes=config.get("attributes"),
            )
            if not tracer:
                _LOGGER.warning(
                    "Tracing is enabled, but not able to get an OpenTelemetry tracer. "
                    "Please ensure that `opentelemetry-api` is installed."
                )
                return

            span_name = request.http_request.method
            span = tracer.start_span(
                name=span_name,
                kind=SpanKind.CLIENT,
                attributes=tracing_options.get("attributes"),
            )

            with tracer.use_span(span, end_on_exit=False):
                trace_context_headers = tracer.get_trace_context()
                request.http_request.headers.update(trace_context_headers)

            request.context[self.TRACING_CONTEXT] = span
            token = tracer._suppress_auto_http_instrumentation()  # pylint: disable=protected-access
            request.context[self._SUPPRESSION_TOKEN] = token
        except Exception as err:  # pylint: disable=broad-except
            _LOGGER.warning("Unable to start HTTP span: %s", err)

    def on_response(
        self,
        request: PipelineRequest[HttpRequest],
        response: PipelineResponse[HttpRequest, SansIOHttpResponse],
    ) -> None:
        if self.TRACING_CONTEXT not in request.context:
            return

        span: Optional["Span"] = request.context[self.TRACING_CONTEXT]
        http_request = request.http_request
        if span:
            self._set_http_client_span_attributes(span, http_request, response=response.http_response)
            if request.context.get("retry_count"):
                span.set_attribute(self._HTTP_RESEND_COUNT, request.context["retry_count"])
            span.end()

        suppression_token = request.context.get(self._SUPPRESSION_TOKEN)
        if suppression_token:
            tracer = get_tracer()
            if tracer:
                tracer._detach_from_context(suppression_token)  # pylint: disable=protected-access

    def _set_http_client_span_attributes(
        self,
        span: "Span",
        request: HttpRequest,
        response: Optional[SansIOHttpResponse] = None,
    ) -> None:
        """Add attributes to an HTTP client span.
        :param span: The span to add attributes to.
        :type span: ~opentelemetry.trace.Span
        :param request: The request made
        :type request: ~corehttp.rest.HttpRequest
        :param response: The response received from the server. Is None if no response received.
        :type response: ~corehttp.rest.HttpResponse
        """
        attributes: Dict[str, Any] = {
            self._HTTP_REQUEST_METHOD: request.method,
            self._URL_FULL: request.url,
        }

        parsed_url = urllib.parse.urlparse(request.url)
        if parsed_url.hostname:
            attributes[self._SERVER_ADDRESS] = parsed_url.hostname
        if parsed_url.port:
            attributes[self._SERVER_PORT] = parsed_url.port

        user_agent = request.headers.get("User-Agent")
        if user_agent:
            attributes[self._USER_AGENT_ORIGINAL] = user_agent
        if response and response.status_code:
            attributes[self._HTTP_RESPONSE_STATUS_CODE] = response.status_code
            if response.status_code >= 400:
                attributes[self._ERROR_TYPE] = str(response.status_code)

        span.set_attributes(attributes)
