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

from ._logger import get_logger

#: Starlette's ``Content`` type — the element type for streaming bodies.
_Content = Union[str, bytes, memoryview]

#: W3C Trace Context header names used for distributed trace propagation.
_W3C_HEADERS = ("traceparent", "tracestate")

#: Baggage key whose value overrides the parent span ID.
_LEAF_CUSTOMER_SPAN_ID = "leaf_customer_span_id"

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


class TracingHelper:
    """Lightweight wrapper around OpenTelemetry.

    Only instantiate when tracing is enabled.  If ``opentelemetry-api`` is
    not installed, a warning is logged and all methods become no-ops.

    When *connection_string* is provided, a :class:`TracerProvider` with an
    Azure Monitor exporter is configured globally and log records from the
    ``azure.ai.agentserver`` logger are forwarded to Application Insights.
    This requires ``opentelemetry-sdk`` and
    ``azure-monitor-opentelemetry-exporter``.
    """

    def __init__(self, connection_string: Optional[str] = None) -> None:
        self._enabled = _HAS_OTEL
        self._tracer: Any = None
        self._propagator: Any = None

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
        try:
            from opentelemetry.sdk.resources import Resource
            from opentelemetry.sdk.trace import TracerProvider as SdkTracerProvider
            from opentelemetry.sdk.trace.export import BatchSpanProcessor

            from azure.monitor.opentelemetry.exporter import (  # type: ignore[import-untyped]
                AzureMonitorTraceExporter,
            )
        except ImportError:
            logger.warning(
                "Application Insights connection string was provided but "
                "required packages are not installed.  Install them with: "
                "pip install azure-ai-agentserver-server[tracing]"
            )
            return

        resource = Resource.create({"service.name": "azure.ai.agentserver"})

        # --- Trace export ---
        provider = SdkTracerProvider(resource=resource)
        exporter = AzureMonitorTraceExporter(
            connection_string=connection_string,
        )
        provider.add_span_processor(BatchSpanProcessor(exporter))
        trace.set_tracer_provider(provider)
        logger.info("Application Insights trace exporter configured.")

        # --- Log export ---
        try:
            from opentelemetry._logs import set_logger_provider
            from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
            from opentelemetry.sdk._logs.export import BatchLogRecordProcessor

            from azure.monitor.opentelemetry.exporter import (  # type: ignore[import-untyped]
                AzureMonitorLogExporter,
            )

            log_provider = LoggerProvider(resource=resource)
            set_logger_provider(log_provider)
            log_exporter = AzureMonitorLogExporter(
                connection_string=connection_string,
            )
            log_provider.add_log_record_processor(
                BatchLogRecordProcessor(log_exporter)
            )
            handler = LoggingHandler(logger_provider=log_provider)
            logging.getLogger("azure.ai.agentserver").addHandler(handler)
            logger.info("Application Insights log exporter configured.")
        except ImportError:
            logger.warning(
                "Log export to Application Insights requires "
                "opentelemetry-sdk.  Logs will not be forwarded."
            )

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


def extract_w3c_carrier(headers: Mapping[str, str]) -> dict[str, str]:
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
    result: dict[str, str] = {}
    for key in _W3C_HEADERS:
        val = headers.get(key)
        if val is not None:
            result[key] = val
    return result


def extract_baggage_header(headers: Mapping[str, str]) -> Optional[str]:
    """Extract the raw ``baggage`` header value from a mapping.

    Returns *None* if the header is not present.

    :param headers: A mapping of header name to value.
    :type headers: Mapping[str, str]
    :return: The raw baggage header value or None.
    :rtype: Optional[str]
    """
    return headers.get("baggage")


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
