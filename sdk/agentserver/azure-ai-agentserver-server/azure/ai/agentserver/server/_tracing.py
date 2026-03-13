# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Optional OpenTelemetry tracing for AgentServer.

Tracing is **disabled by default**. Enable it in one of two ways:

1. Set the environment variable ``AGENT_ENABLE_TRACING=true``.
2. Pass ``enable_tracing=True`` to the :class:`AgentServer` constructor
   (constructor argument takes precedence over the env var).

When enabled, the module requires ``opentelemetry-api`` to be installed::

    pip install azure-ai-agentserver-server[tracing]

If the package is not installed, tracing silently becomes a no-op.

When an Application Insights connection string is available (via constructor
or ``APPLICATIONINSIGHTS_CONNECTION_STRING`` env var), traces **and** logs are
automatically exported to Azure Monitor.  This requires the additional
``opentelemetry-sdk`` and ``azure-monitor-opentelemetry-exporter`` packages
(both included in the ``[tracing]`` extras group).
"""
from __future__ import annotations

import logging
from contextlib import contextmanager
from collections.abc import AsyncIterable, AsyncIterator, Mapping  # pylint: disable=import-error
from typing import TYPE_CHECKING, Any, Iterator, Optional, Union

from . import _config
from ._logger import get_logger

#: Starlette's ``Content`` type — the element type for streaming bodies.
_Content = Union[str, bytes, memoryview]

#: W3C Trace Context header names used for distributed trace propagation.
_W3C_HEADERS = ("traceparent", "tracestate")

#: Baggage key whose value overrides the parent span ID.
_LEAF_CUSTOMER_SPAN_ID = "leaf_customer_span_id"

# ------------------------------------------------------------------
# GenAI semantic convention attribute keys
# ------------------------------------------------------------------
_ATTR_INVOCATION_ID = "invocation.id"
_ATTR_RESPONSE_ID = "gen_ai.response.id"
_ATTR_PROVIDER_NAME = "gen_ai.provider.name"
_ATTR_AGENT_ID = "gen_ai.agent.id"
_ATTR_PROJECT_ID = "microsoft.foundry.project.id"
_ATTR_OPERATION_NAME = "gen_ai.operation.name"
_ATTR_CONVERSATION_ID = "gen_ai.conversation.id"

_PROVIDER_NAME_VALUE = "microsoft.foundry"

logger = get_logger()

_HAS_OTEL = False
try:
    from opentelemetry import trace
    from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator

    _HAS_OTEL = True
except ImportError:
    if TYPE_CHECKING:
        from opentelemetry import trace
        from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator


class _TracingHelper:
    """Lightweight wrapper around OpenTelemetry.

    Only instantiate when tracing is enabled.  If ``opentelemetry-api`` is
    not installed, a warning is logged and all methods become no-ops.

    When *connection_string* is provided, a :class:`TracerProvider` with an
    Azure Monitor exporter is configured globally and log records from the
    ``azure.ai.agentserver`` logger are forwarded to Application Insights.
    This requires ``opentelemetry-sdk`` and
    ``azure-monitor-opentelemetry-exporter``.
    """

    def __init__(
        self,
        connection_string: Optional[str] = None,
    ) -> None:
        self._enabled = _HAS_OTEL
        self._tracer: Any = None
        self._propagator: Any = None

        # Resolve agent identity from environment variables.
        agent_name = _config.resolve_agent_name()
        agent_version = _config.resolve_agent_version()
        self._agent_label = (
            f"{agent_name}:{agent_version}" if agent_name and agent_version else agent_name
        )
        self._project_id = _config.resolve_project_id()

        if not self._enabled:
            logger.warning(
                "Tracing was enabled but opentelemetry-api is not installed. "
                "Install it with: pip install azure-ai-agentserver-server[tracing]"
            )
            return

        if connection_string:
            self._setup_azure_monitor(connection_string)

        self._tracer = trace.get_tracer("azure.ai.agentserver")
        self._propagator = TraceContextTextMapPropagator()

    # ------------------------------------------------------------------
    # Azure Monitor auto-configuration
    # ------------------------------------------------------------------

    def _extract_context(
        self,
        carrier: Optional[dict[str, str]],
        baggage_header: Optional[str] = None,
    ) -> Any:
        """Extract parent trace context from a W3C carrier dict.

        When a ``baggage`` header is provided and contains a
        ``leaf_customer_span_id`` key, the parent span ID is overridden
        so that the server's root span is parented under the leaf customer
        span rather than the span referenced in the ``traceparent`` header.

        :param carrier: W3C trace-context headers or None.
        :type carrier: Optional[dict[str, str]]
        :param baggage_header: Raw ``baggage`` header value or None.
        :type baggage_header: Optional[str]
        :return: The extracted OTel context, or None.
        :rtype: Any
        """
        if not carrier or self._propagator is None:
            return None

        ctx = self._propagator.extract(carrier=carrier)

        if not baggage_header:
            return ctx

        leaf_span_id = _parse_baggage_key(baggage_header, _LEAF_CUSTOMER_SPAN_ID)
        if not leaf_span_id:
            return ctx

        return _override_parent_span_id(ctx, leaf_span_id)

    @staticmethod
    def _setup_azure_monitor(connection_string: str) -> None:
        """Configure global TracerProvider and LoggerProvider for App Insights.

        Sets up ``AzureMonitorTraceExporter`` so spans are exported to
        Application Insights, and ``AzureMonitorLogExporter`` so log records
        from the ``azure.ai.agentserver`` namespace are forwarded.

        If the required packages are not installed, a warning is logged and
        export is silently skipped — span creation still works via the
        default no-op or user-configured provider.

        :param connection_string: Application Insights connection string.
        :type connection_string: str
        """
        resource = _create_resource()
        if resource is None:
            return
        _setup_trace_export(resource, connection_string)
        _setup_log_export(resource, connection_string)

    # ------------------------------------------------------------------
    # Span naming and attribute helpers (shared by all protocols)
    # ------------------------------------------------------------------

    def span_name(self, span_operation: str) -> str:
        """Build a span name using the operation and agent label.

        :param span_operation: The span operation (e.g. ``"execute_agent"``).
            This becomes the first token of the OTel span name.
        :type span_operation: str
        :return: ``"<span_operation> <name>:<version>"`` or just
            ``"<span_operation>"``.
        :rtype: str
        """
        if self._agent_label:
            return f"{span_operation} {self._agent_label}"
        return span_operation

    def build_span_attrs(
        self,
        invocation_id: str,
        session_id: str,
        operation_name: Optional[str] = None,
    ) -> dict[str, str]:
        """Build GenAI semantic convention span attributes.

        These attributes are common across all protocol heads (invocation,
        chat, etc.).

        :param invocation_id: The invocation/request ID for this request.
        :type invocation_id: str
        :param session_id: The session ID header value (empty string if absent).
        :type session_id: str
        :param operation_name: Optional ``gen_ai.operation.name`` value
            (e.g. ``"invoke_agent"``).  Omitted from the dict when *None*.
        :type operation_name: Optional[str]
        :return: Span attribute dict.
        :rtype: dict[str, str]
        """
        attrs: dict[str, str] = {
            _ATTR_INVOCATION_ID: invocation_id,
            _ATTR_RESPONSE_ID: invocation_id,
            _ATTR_PROVIDER_NAME: _PROVIDER_NAME_VALUE,
        }
        if self._agent_label:
            attrs[_ATTR_AGENT_ID] = self._agent_label
        if self._project_id:
            attrs[_ATTR_PROJECT_ID] = self._project_id
        if operation_name:
            attrs[_ATTR_OPERATION_NAME] = operation_name
        if session_id:
            attrs[_ATTR_CONVERSATION_ID] = session_id
        return attrs

    @contextmanager
    def span(
        self,
        name: str,
        attributes: Optional[dict[str, str]] = None,
        carrier: Optional[dict[str, str]] = None,
        baggage_header: Optional[str] = None,
    ) -> Iterator[Any]:
        """Create a traced span if tracing is enabled, otherwise no-op.

        Yields the OpenTelemetry span object when tracing is active, or
        ``None`` when tracing is disabled.  Callers may use the yielded span
        together with :meth:`record_error` to attach error information.

        :param name: Span name, e.g. ``"execute_agent my_agent:1.0"``.
        :type name: str
        :param attributes: Key-value span attributes.
        :type attributes: Optional[dict[str, str]]
        :param carrier: Incoming HTTP headers for W3C trace-context propagation.
        :type carrier: Optional[dict[str, str]]
        :param baggage_header: Raw ``baggage`` header value for
            ``leaf_customer_span_id`` extraction.
        :type baggage_header: Optional[str]
        :return: Context manager that yields the OTel span or *None*.
        :rtype: Iterator[Any]
        """
        if not self._enabled or self._tracer is None:
            yield None
            return

        ctx = self._extract_context(carrier, baggage_header)

        with self._tracer.start_as_current_span(
            name=name,
            attributes=attributes or {},
            kind=trace.SpanKind.SERVER,
            context=ctx,
        ) as otel_span:
            yield otel_span

    def start_span(
        self,
        name: str,
        attributes: Optional[dict[str, str]] = None,
        carrier: Optional[dict[str, str]] = None,
        baggage_header: Optional[str] = None,
    ) -> Any:
        """Start a span without a context manager.

        Use this for streaming responses where the span must outlive the
        initial ``invoke()`` call.  The caller **must** call :meth:`end_span`
        when the work is finished.

        :param name: Span name, e.g. ``"execute_agent my_agent:1.0"``.
        :type name: str
        :param attributes: Key-value span attributes.
        :type attributes: Optional[dict[str, str]]
        :param carrier: Incoming HTTP headers for W3C trace-context propagation.
        :type carrier: Optional[dict[str, str]]
        :param baggage_header: Raw ``baggage`` header value for
            ``leaf_customer_span_id`` extraction.
        :type baggage_header: Optional[str]
        :return: The OTel span, or *None* when tracing is disabled.
        :rtype: Any
        """
        if not self._enabled or self._tracer is None:
            return None

        ctx = self._extract_context(carrier, baggage_header)

        return self._tracer.start_span(
            name=name,
            attributes=attributes or {},
            kind=trace.SpanKind.SERVER,
            context=ctx,
        )

    # ------------------------------------------------------------------
    # Request-level convenience wrappers
    # ------------------------------------------------------------------

    def _prepare_request_span_args(
        self,
        headers: Mapping[str, str],
        invocation_id: str,
        span_operation: str,
        operation_name: Optional[str] = None,
        session_id: str = "",
    ) -> tuple[str, dict[str, str], dict[str, str], Optional[str]]:
        """Extract headers and build span arguments for a request.

        Shared pipeline used by :meth:`start_request_span` and
        :meth:`request_span` to avoid duplicating header extraction,
        attribute building, and span naming.

        :param headers: HTTP request headers (any ``Mapping[str, str]``).
        :type headers: Mapping[str, str]
        :param invocation_id: The invocation/request ID.
        :type invocation_id: str
        :param span_operation: Span operation (e.g. ``"execute_agent"``).
        :type span_operation: str
        :param operation_name: Optional ``gen_ai.operation.name`` value.
        :type operation_name: Optional[str]
        :param session_id: Session ID from the ``agent_session_id`` query
            parameter.  Defaults to ``""`` (no session).
        :type session_id: str
        :return: ``(name, attributes, carrier, baggage)`` ready for
            :meth:`span` or :meth:`start_span`.
        :rtype: tuple[str, dict[str, str], dict[str, str], Optional[str]]
        """
        carrier = _extract_w3c_carrier(headers)
        baggage = headers.get("baggage")
        span_attrs = self.build_span_attrs(
            invocation_id, session_id, operation_name=operation_name
        )
        return self.span_name(span_operation), span_attrs, carrier, baggage

    def start_request_span(
        self,
        headers: Mapping[str, str],
        invocation_id: str,
        span_operation: str,
        operation_name: Optional[str] = None,
        session_id: str = "",
    ) -> Any:
        """Start a request-scoped span, extracting context from HTTP headers.

        Convenience method that combines header extraction, attribute
        building, span naming, and span creation into a single call.
        Use for streaming responses where the span must outlive the
        initial handler call.  The caller **must** call :meth:`end_span`
        when work is finished.

        :param headers: HTTP request headers (any ``Mapping[str, str]``).
        :type headers: Mapping[str, str]
        :param invocation_id: The invocation/request ID.
        :type invocation_id: str
        :param span_operation: Span operation (e.g. ``"execute_agent"``).
            Becomes the first token of the OTel span name via
            :meth:`span_name`.
        :type span_operation: str
        :param operation_name: Optional ``gen_ai.operation.name`` attribute
            value (e.g. ``"invoke_agent"``).  Omitted when *None*.
        :type operation_name: Optional[str]
        :param session_id: Session ID from the ``agent_session_id`` query
            parameter.  Defaults to ``""`` (no session).
        :type session_id: str
        :return: The OTel span, or *None* when tracing is disabled.
        :rtype: Any
        """
        name, attrs, carrier, baggage = self._prepare_request_span_args(
            headers, invocation_id, span_operation, operation_name,
            session_id=session_id,
        )
        return self.start_span(name, attributes=attrs, carrier=carrier, baggage_header=baggage)

    @contextmanager
    def request_span(
        self,
        headers: Mapping[str, str],
        invocation_id: str,
        span_operation: str,
        operation_name: Optional[str] = None,
        session_id: str = "",
    ) -> Iterator[Any]:
        """Create a request-scoped span as a context manager.

        Convenience method that combines header extraction, attribute
        building, span naming, and span creation into a single call.
        Use for non-streaming request handlers where the span should
        cover the entire handler execution.

        :param headers: HTTP request headers (any ``Mapping[str, str]``).
        :type headers: Mapping[str, str]
        :param invocation_id: The invocation/request ID.
        :type invocation_id: str
        :param span_operation: Span operation (e.g. ``"get_invocation"``).
            Becomes the first token of the OTel span name via
            :meth:`span_name`.
        :type span_operation: str
        :param operation_name: Optional ``gen_ai.operation.name`` attribute
            value.  Omitted when *None*.
        :type operation_name: Optional[str]
        :param session_id: Session ID from the ``agent_session_id`` query
            parameter.  Defaults to ``""`` (no session).
        :type session_id: str
        :return: Context manager that yields the OTel span or *None*.
        :rtype: Iterator[Any]
        """
        name, attrs, carrier, baggage = self._prepare_request_span_args(
            headers, invocation_id, span_operation, operation_name,
            session_id=session_id,
        )
        otel_span = self.start_span(name, attributes=attrs, carrier=carrier, baggage_header=baggage)
        try:
            yield otel_span
        except Exception as exc:  # pylint: disable=broad-exception-caught
            self.end_span(otel_span, exc=exc)
            raise
        self.end_span(otel_span)

    # ------------------------------------------------------------------
    # Span lifecycle helpers
    # ------------------------------------------------------------------

    def end_span(self, span: Any, exc: Optional[Exception] = None) -> None:
        """End a span started with :meth:`start_span`.

        Optionally records an error before ending.  No-op when *span* is
        ``None`` (tracing disabled).

        :param span: The OTel span, or *None*.
        :type span: Any
        :param exc: Optional exception to record before ending.
        :type exc: Optional[Exception]
        """
        if span is None:
            return
        if exc is not None:
            self.record_error(span, exc)
        span.end()

    @staticmethod
    def record_error(span: Any, exc: Exception) -> None:
        """Record an exception and ERROR status on a span.

        No-op when *span* is ``None`` (tracing disabled) or when
        ``opentelemetry-api`` is not installed.

        :param span: The OTel span returned by :meth:`span`, or *None*.
        :type span: Any
        :param exc: The exception to record.
        :type exc: Exception
        """
        if span is not None and _HAS_OTEL:
            span.set_status(trace.StatusCode.ERROR, str(exc))
            span.record_exception(exc)

    async def trace_stream(
        self, iterator: AsyncIterable[_Content], span: Any
    ) -> AsyncIterator[_Content]:
        """Wrap a streaming body iterator so the tracing span covers the full
        duration of data transmission.

        Yields chunks from *iterator* unchanged.  When the iterator is
        exhausted or raises an exception the span is ended (with error status
        if applicable).  Safe to call when tracing is disabled (*span* is
        ``None``).

        :param iterator: The original async body iterator from
            :class:`~starlette.responses.StreamingResponse`.
        :type iterator: AsyncIterable[Union[str, bytes, memoryview]]
        :param span: The OTel span (or *None* when tracing is disabled).
        :type span: Any
        :return: An async iterator that yields chunks unchanged.
        :rtype: AsyncIterator[Union[str, bytes, memoryview]]
        """
        error: Optional[Exception] = None
        try:
            async for chunk in iterator:
                yield chunk
        except Exception as exc:
            error = exc
            raise
        finally:
            self.end_span(span, exc=error)


def _create_resource() -> Any:
    """Create the OTel resource for Azure Monitor exporters.

    :return: A :class:`~opentelemetry.sdk.resources.Resource`, or *None*
        if the required packages are not installed.
    :rtype: Any
    """
    try:
        from opentelemetry.sdk.resources import Resource
    except ImportError:
        logger.warning(
            "Application Insights connection string was provided but "
            "required packages are not installed.  Install them with: "
            "pip install azure-ai-agentserver-server[tracing]"
        )
        return None
    return Resource.create({"service.name": "azure.ai.agentserver"})


def _setup_trace_export(resource: Any, connection_string: str) -> None:
    """Configure a global :class:`TracerProvider` that exports to App Insights.

    :param resource: The OTel resource describing this service.
    :type resource: Any
    :param connection_string: Application Insights connection string.
    :type connection_string: str
    """
    try:
        from opentelemetry.sdk.trace import TracerProvider as SdkTracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor

        from azure.monitor.opentelemetry.exporter import (  # type: ignore[import-untyped]
            AzureMonitorTraceExporter,
        )
    except ImportError:
        logger.warning(
            "Trace export to Application Insights requires "
            "opentelemetry-sdk and azure-monitor-opentelemetry-exporter.  "
            "Traces will not be forwarded."
        )
        return

    provider = SdkTracerProvider(resource=resource)
    exporter = AzureMonitorTraceExporter(connection_string=connection_string)
    provider.add_span_processor(BatchSpanProcessor(exporter))
    trace.set_tracer_provider(provider)
    logger.info("Application Insights trace exporter configured.")


def _setup_log_export(resource: Any, connection_string: str) -> None:
    """Configure a global :class:`LoggerProvider` that exports to App Insights.

    :param resource: The OTel resource describing this service.
    :type resource: Any
    :param connection_string: Application Insights connection string.
    :type connection_string: str
    """
    try:
        from opentelemetry._logs import set_logger_provider
        from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
        from opentelemetry.sdk._logs.export import BatchLogRecordProcessor

        from azure.monitor.opentelemetry.exporter import (  # type: ignore[import-untyped]
            AzureMonitorLogExporter,
        )
    except ImportError:
        logger.warning(
            "Log export to Application Insights requires "
            "opentelemetry-sdk.  Logs will not be forwarded."
        )
        return

    log_provider = LoggerProvider(resource=resource)
    set_logger_provider(log_provider)
    log_exporter = AzureMonitorLogExporter(connection_string=connection_string)
    log_provider.add_log_record_processor(BatchLogRecordProcessor(log_exporter))
    handler = LoggingHandler(logger_provider=log_provider)
    logging.getLogger("azure.ai.agentserver").addHandler(handler)
    logger.info("Application Insights log exporter configured.")


def _extract_w3c_carrier(headers: Mapping[str, str]) -> dict[str, str]:
    """Extract W3C trace-context headers from a mapping.

    Filters the input to only ``traceparent`` and ``tracestate`` — the two
    headers defined by the `W3C Trace Context`_ standard.  This avoids
    passing unrelated headers (e.g. ``authorization``, ``cookie``) into the
    OpenTelemetry propagator.

    .. _W3C Trace Context: https://www.w3.org/TR/trace-context/

    :param headers: A mapping of header name to value (e.g.
        ``request.headers``).
    :type headers: Mapping[str, str]
    :return: A dict containing only the W3C propagation headers present
        in *headers*.
    :rtype: dict[str, str]
    """
    result: dict[str, str] = {k: v for k in _W3C_HEADERS if (v := headers.get(k)) is not None}
    return result


def _parse_baggage_key(baggage: str, key: str) -> Optional[str]:
    """Parse a single key from a W3C Baggage header value.

    The `W3C Baggage`_ format is a comma-separated list of
    ``key=value`` pairs with optional properties after a ``;``.

    Example::

        leaf_customer_span_id=abc123,other=val

    .. _W3C Baggage: https://www.w3.org/TR/baggage/

    :param baggage: The raw header value.
    :type baggage: str
    :param key: The baggage key to look up.
    :type key: str
    :return: The value for *key*, or *None* if not found.
    :rtype: Optional[str]
    """
    for member in baggage.split(","):
        member = member.strip()
        if not member:
            continue
        # Split on first '=' only; value may contain '='
        kv_part = member.split(";", 1)[0]  # strip optional properties
        eq_idx = kv_part.find("=")
        if eq_idx < 0:
            continue
        k = kv_part[:eq_idx].strip()
        v = kv_part[eq_idx + 1:].strip()
        if k == key:
            return v
    return None


def _override_parent_span_id(ctx: Any, hex_span_id: str) -> Any:
    """Create a new context with the same trace ID but a different parent span ID.

    Constructs a :class:`~opentelemetry.trace.SpanContext` with the trace ID
    taken from the existing context and the span ID replaced by
    *hex_span_id*.  The resulting context can be used as the ``context``
    argument to ``start_span`` / ``start_as_current_span``.

    Returns the original *ctx* unchanged if *hex_span_id* is invalid or
    ``opentelemetry-api`` is not installed.

    :param ctx: An OTel context produced by ``TraceContextTextMapPropagator.extract()``.
    :type ctx: Any
    :param hex_span_id: 16-character lower-case hex string representing the
        desired parent span ID.
    :type hex_span_id: str
    :return: A context with the overridden parent span ID, or the original.
    :rtype: Any
    """
    if not _HAS_OTEL:
        return ctx

    try:
        new_span_id = int(hex_span_id, 16)
    except (ValueError, TypeError):
        logger.warning("Invalid leaf_customer_span_id in baggage: %r", hex_span_id)
        return ctx

    if new_span_id == 0:
        return ctx

    # Grab the trace ID from the current parent span in ctx.
    current_span = trace.get_current_span(ctx)
    current_ctx = current_span.get_span_context()
    if current_ctx is None or not current_ctx.is_valid:
        return ctx

    custom_span_ctx = trace.SpanContext(
        trace_id=current_ctx.trace_id,
        span_id=new_span_id,
        is_remote=True,
        trace_flags=current_ctx.trace_flags,
        trace_state=current_ctx.trace_state,
    )
    custom_parent = trace.NonRecordingSpan(custom_span_ctx)
    return trace.set_span_in_context(custom_parent, ctx)
