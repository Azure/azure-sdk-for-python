# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""OpenTelemetry tracing for AgentServerHost.

This module provides functions (not classes) for tracing:

- :func:`configure_tracing` — one-time exporter setup (called by ``AgentServerHost.__init__``)
- :func:`request_span` — create a request-scoped span with GenAI attributes
- :func:`end_span` / :func:`record_error` — span lifecycle helpers
- :func:`trace_stream` — wrap streaming responses with span lifecycle

OpenTelemetry is a required dependency — these functions always create
real spans.  Azure Monitor export is optional (lazy-imported).
"""
import logging
import os
from collections.abc import AsyncIterable, AsyncIterator, Mapping  # pylint: disable=import-error
from contextlib import contextmanager
from typing import Any, Iterator, Optional, Union

from opentelemetry import baggage as _otel_baggage, context as _otel_context, trace
from opentelemetry.baggage.propagation import W3CBaggagePropagator
from opentelemetry.propagate import composite
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator

from . import _config

_Content = Union[str, bytes, memoryview]
_W3C_HEADERS = ("traceparent", "tracestate", "baggage")

# GenAI semantic convention attribute keys
_ATTR_SERVICE_NAME = "service.name"
_ATTR_GEN_AI_SYSTEM = "gen_ai.system"
_ATTR_GEN_AI_PROVIDER_NAME = "gen_ai.provider.name"
_ATTR_GEN_AI_AGENT_ID = "gen_ai.agent.id"
_ATTR_GEN_AI_AGENT_NAME = "gen_ai.agent.name"
_ATTR_GEN_AI_AGENT_VERSION = "gen_ai.agent.version"
_ATTR_GEN_AI_RESPONSE_ID = "gen_ai.response.id"
_ATTR_GEN_AI_OPERATION_NAME = "gen_ai.operation.name"
_ATTR_GEN_AI_CONVERSATION_ID = "gen_ai.conversation.id"
_ATTR_FOUNDRY_PROJECT_ID = "microsoft.foundry.project.id"

_SERVICE_NAME_VALUE = "azure.ai.agentserver"
_GEN_AI_SYSTEM_VALUE = "azure.ai.agentserver"
_GEN_AI_PROVIDER_NAME_VALUE = "AzureAI Hosted Agents"

logger = logging.getLogger("azure.ai.agentserver")

# Composite propagator handles both traceparent/tracestate AND baggage
_propagator = composite.CompositePropagator([
    TraceContextTextMapPropagator(),
    W3CBaggagePropagator(),
])


# ======================================================================
# Public API: exporter setup
# ======================================================================


def configure_tracing(connection_string: Optional[str] = None) -> None:
    """Configure OpenTelemetry exporters for Azure Monitor and OTLP.

    Called once at startup by ``AgentServerHost.__init__``.  Users may
    pass a custom function (or ``None``) via the ``configure_tracing``
    constructor parameter to override or disable this default setup.

    :param connection_string: Application Insights connection string.
        When provided, traces and logs are exported to Azure Monitor.
    :type connection_string: str or None
    """
    resource = _create_resource()
    provider = _ensure_trace_provider(resource)

    if provider is not None:
        _register_enrichment_processor(provider)

    if connection_string:
        if resource is not None:
            _setup_trace_export(provider, connection_string)
            _setup_log_export(resource, connection_string)

    otlp_endpoint = _config.resolve_otlp_endpoint()
    if otlp_endpoint and resource is not None:
        _setup_otlp_trace_export(provider, otlp_endpoint)
        _setup_otlp_log_export(resource, otlp_endpoint)


# ======================================================================
# Public API: span operations
# ======================================================================


@contextmanager
def request_span(
    headers: Mapping[str, str],
    request_id: str,
    operation: str,
    *,
    agent_id: str = "",
    agent_name: str = "",
    agent_version: str = "",
    project_id: str = "",
    operation_name: Optional[str] = None,
    session_id: str = "",
    end_on_exit: bool = True,
    instrumentation_scope: str = "Azure.AI.AgentServer",
) -> Iterator[Any]:
    """Create a request-scoped span with GenAI semantic convention attributes.

    Extracts W3C trace context from *headers* and creates a span set as
    current in context (child spans are correctly parented).

    For **non-streaming** requests use ``end_on_exit=True`` (default).
    For **streaming** use ``end_on_exit=False`` and end via :func:`trace_stream`.

    :param headers: HTTP request headers.
    :type headers: Mapping[str, str]
    :param request_id: The request/invocation ID.
    :type request_id: str
    :param operation: Span operation (e.g. ``"invoke_agent"``).
    :type operation: str
    :keyword agent_id: Agent identifier (``"name:version"`` or ``"name"``).
    :paramtype agent_id: str
    :keyword agent_name: Agent name from FOUNDRY_AGENT_NAME.
    :paramtype agent_name: str
    :keyword agent_version: Agent version from FOUNDRY_AGENT_VERSION.
    :paramtype agent_version: str
    :keyword project_id: Foundry project ARM resource ID.
    :paramtype project_id: str
    :keyword operation_name: Optional ``gen_ai.operation.name`` value.
    :paramtype operation_name: str or None
    :keyword session_id: Session ID (empty string if absent).
    :paramtype session_id: str
    :keyword end_on_exit: Whether to end the span when the context exits.
    :paramtype end_on_exit: bool
    :keyword instrumentation_scope: OpenTelemetry instrumentation scope name.
    :paramtype instrumentation_scope: str
    :return: Context manager yielding the OTel span.
    :rtype: Iterator[any]
    """
    tracer = trace.get_tracer(instrumentation_scope)

    # Build span name
    name = f"{operation} {agent_id}" if agent_id else operation

    # Build attributes
    attrs: dict[str, str] = {
        _ATTR_SERVICE_NAME: agent_name or _SERVICE_NAME_VALUE,
        _ATTR_GEN_AI_SYSTEM: _GEN_AI_SYSTEM_VALUE,
        _ATTR_GEN_AI_PROVIDER_NAME: _GEN_AI_PROVIDER_NAME_VALUE,
        _ATTR_GEN_AI_RESPONSE_ID: request_id,
        _ATTR_GEN_AI_AGENT_ID: agent_id,
    }
    if agent_name:
        attrs[_ATTR_GEN_AI_AGENT_NAME] = agent_name
    if agent_version:
        attrs[_ATTR_GEN_AI_AGENT_VERSION] = agent_version
    if operation_name:
        attrs[_ATTR_GEN_AI_OPERATION_NAME] = operation_name
    if session_id:
        attrs[_ATTR_GEN_AI_CONVERSATION_ID] = session_id
    if project_id:
        attrs[_ATTR_FOUNDRY_PROJECT_ID] = project_id

    # Propagate platform request correlation ID as span attribute AND baggage
    x_request_id = headers.get("x-request-id")
    if x_request_id:
        attrs["x_request_id"] = x_request_id

    # Extract W3C trace context (traceparent + tracestate + baggage)
    carrier = _extract_w3c_carrier(headers)
    ctx = _propagator.extract(carrier=carrier) if carrier else None

    # Add x-request-id to baggage for downstream propagation
    if x_request_id:
        ctx = _otel_baggage.set_baggage("x_request_id", x_request_id, context=ctx)

    with tracer.start_as_current_span(
        name=name,
        attributes=attrs,
        kind=trace.SpanKind.SERVER,
        context=ctx,
        end_on_exit=end_on_exit,
    ) as otel_span:
        yield otel_span


def end_span(span: Any, exc: Optional[BaseException] = None) -> None:
    """End a span, optionally recording an error first.

    No-op when *span* is ``None``.

    :param span: The OTel span to end, or ``None``.
    :type span: any
    :param exc: Optional exception to record before ending.
    :type exc: BaseException or None
    """
    if span is None:
        return
    if exc is not None:
        record_error(span, exc)
    span.end()


def flush_spans(timeout_millis: int = 5000) -> None:
    """Flush all pending spans from the TracerProvider.

    The ``BatchSpanProcessor`` buffers spans and exports them on a timer
    (default 5 seconds).  In hosted sandbox environments the platform may
    suspend the process immediately after an HTTP response is sent, before
    the batch timer fires.  Calling this function after ending the request
    span ensures that all child spans — including short-lived ones created
    by third-party tracers (e.g. LangChain/LangGraph per-node spans) — are
    exported before the sandbox is frozen.

    No-op when the OTel SDK is not installed or the provider does not
    support ``force_flush``.

    :param timeout_millis: Maximum time to wait for the flush, in
        milliseconds.  Defaults to 5000 (5 seconds).
    :type timeout_millis: int
    """
    provider = trace.get_tracer_provider()
    flush = getattr(provider, "force_flush", None)
    if flush is not None:
        try:
            flush(timeout_millis)
        except Exception:  # pylint: disable=broad-exception-caught
            logger.debug("TracerProvider.force_flush() failed", exc_info=True)


def record_error(span: Any, exc: BaseException) -> None:
    """Record an exception and ERROR status on a span.

    Sets ``error.type`` and ``otel.status.description`` per OTel
    semantic conventions.

    :param span: The OTel span, or ``None``.
    :type span: any
    :param exc: The exception to record.
    :type exc: BaseException
    """
    if span is not None:
        span.set_status(trace.StatusCode.ERROR, str(exc))
        span.set_attribute("error.type", type(exc).__name__)
        span.record_exception(exc)


async def trace_stream(
    iterator: AsyncIterable[_Content], span: Any
) -> AsyncIterator[_Content]:
    """Wrap a streaming body so the span covers the full transmission.

    Yields chunks unchanged.  Ends the span when the iterator is
    exhausted or raises an exception.

    :param iterator: The async iterable to wrap.
    :type iterator: AsyncIterable[str or bytes or memoryview]
    :param span: The OTel span to end on completion, or ``None``.
    :type span: any
    :return: An async iterator yielding chunks unchanged.
    :rtype: AsyncIterator[str or bytes or memoryview]
    """
    error: Optional[BaseException] = None
    try:
        async for chunk in iterator:
            yield chunk
    except BaseException as exc:
        error = exc
        raise
    finally:
        end_span(span, exc=error)
        flush_spans()


# ======================================================================
# Foundry enrichment span processor
# ======================================================================


class _FoundryEnrichmentSpanProcessor:
    """Adds Foundry identity attributes to ALL spans."""

    def __init__(
        self,
        agent_name: Optional[str] = None,
        agent_version: Optional[str] = None,
        agent_id: Optional[str] = None,
        project_id: Optional[str] = None,
    ) -> None:
        self.agent_name = agent_name
        self.agent_version = agent_version
        self.agent_id = agent_id
        self.project_id = project_id

    def on_start(self, span: Any, parent_context: Any = None) -> None:  # pylint: disable=unused-argument
        if self.project_id:
            span.set_attribute(_ATTR_FOUNDRY_PROJECT_ID, self.project_id)

    def _on_ending(self, span: Any) -> None:
        # Set agent identity attributes at span end so they cannot be
        # overwritten by underlying frameworks (e.g. LangChain, Semantic Kernel).
        #
        # Workaround: opentelemetry-sdk <=1.40.0 sets _end_time before calling
        # _on_ending, which causes set_attribute() to silently no-op despite the
        # spec requiring mutability during OnEnding.  We write to _attributes
        # directly until the SDK is fixed.  The try/except guards against future
        # SDK changes that may rename or remove the internal field.
        # TODO: switch to span.set_attribute() once the SDK honours the spec.
        attrs = getattr(span, "_attributes", None)
        if attrs is None:
            return
        try:
            if self.agent_name:
                attrs[_ATTR_GEN_AI_AGENT_NAME] = self.agent_name
            if self.agent_version:
                attrs[_ATTR_GEN_AI_AGENT_VERSION] = self.agent_version
            if self.agent_id:
                attrs[_ATTR_GEN_AI_AGENT_ID] = self.agent_id
        except Exception:  # pylint: disable=broad-exception-caught
            logger.debug("Failed to enrich span attributes in _on_ending", exc_info=True)

    def on_end(self, span: Any) -> None:  # pylint: disable=unused-argument
        pass

    def shutdown(self) -> None:
        pass

    def force_flush(self, timeout_millis: int = 30000) -> bool:  # pylint: disable=unused-argument
        return True


class _BaggageLogRecordProcessor:
    """OTel log record processor that copies W3C Baggage entries into log attributes.

    Per container-image-spec §6.1, all baggage key-value pairs from the
    current span context should appear as attributes on every log record
    for end-to-end correlation.
    """

    def on_emit(self, log_data: Any) -> None:  # pylint: disable=unused-argument
        """Copy baggage entries into the log record's attributes.

        :param log_data: The log data being emitted.
        :type log_data: any
        """
        try:
            ctx = _otel_context.get_current()
            entries = _otel_baggage.get_all(context=ctx)
            if entries and hasattr(log_data, 'log_record') and log_data.log_record:
                for key, value in entries.items():
                    log_data.log_record.attributes[key] = value  # type: ignore[index]
        except Exception:  # pylint: disable=broad-except
            pass

    def shutdown(self) -> None:
        pass

    def force_flush(self, timeout_millis: int = 30000) -> bool:  # pylint: disable=unused-argument
        return True


# ======================================================================
# Internal: resource, provider, exporters
# ======================================================================


def _create_resource() -> Any:
    try:
        from opentelemetry.sdk.resources import Resource
    except ImportError:
        logger.warning("OTel SDK not installed — tracing resource creation failed.")
        return None
    # service.name maps to cloud_RoleName in App Insights
    agent_name = os.environ.get(_config._ENV_FOUNDRY_AGENT_NAME, "")  # pylint: disable=protected-access
    service_name = agent_name or _SERVICE_NAME_VALUE
    return Resource.create({_ATTR_SERVICE_NAME: service_name})


def _ensure_trace_provider(resource: Any) -> Any:
    if resource is None:
        return None
    try:
        from opentelemetry.sdk.trace import TracerProvider as SdkTracerProvider
    except ImportError:
        return None
    current = trace.get_tracer_provider()
    if hasattr(current, "add_span_processor"):
        return current
    provider = SdkTracerProvider(resource=resource)
    trace.set_tracer_provider(provider)
    return provider


_enrichment_configured = False
_az_trace_configured = False
_az_log_configured = False
_otlp_trace_configured = False
_otlp_log_configured = False


def _register_enrichment_processor(provider: Any) -> None:
    global _enrichment_configured  # pylint: disable=global-statement
    if _enrichment_configured:
        return
    agent_name = _config.resolve_agent_name() or None
    agent_version = _config.resolve_agent_version() or None
    project_id = _config.resolve_project_id() or None

    if agent_name and agent_version:
        agent_id = f"{agent_name}:{agent_version}"
    elif agent_name:
        agent_id = agent_name
    else:
        agent_id = None

    provider.add_span_processor(_FoundryEnrichmentSpanProcessor(
        agent_name=agent_name, agent_version=agent_version,
        agent_id=agent_id, project_id=project_id,
    ))
    _enrichment_configured = True


def _setup_trace_export(provider: Any, connection_string: str) -> None:
    global _az_trace_configured  # pylint: disable=global-statement
    if _az_trace_configured or provider is None:
        return
    try:
        from opentelemetry.sdk.trace.export import BatchSpanProcessor
        from azure.monitor.opentelemetry.exporter import AzureMonitorTraceExporter  # type: ignore[import-untyped]
    except ImportError:
        logger.warning("Trace export requires azure-monitor-opentelemetry-exporter.")
        return
    provider.add_span_processor(BatchSpanProcessor(
        AzureMonitorTraceExporter(connection_string=connection_string)))
    _az_trace_configured = True
    logger.info("Application Insights trace exporter configured.")


def _setup_log_export(resource: Any, connection_string: str) -> None:
    global _az_log_configured  # pylint: disable=global-statement
    if _az_log_configured:
        return
    try:
        from opentelemetry._logs import set_logger_provider
        from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
        from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
        from azure.monitor.opentelemetry.exporter import AzureMonitorLogExporter  # type: ignore[import-untyped]
    except ImportError:
        logger.warning("Log export requires azure-monitor-opentelemetry-exporter.")
        return
    log_provider = LoggerProvider(resource=resource)
    set_logger_provider(log_provider)
    log_provider.add_log_record_processor(BatchLogRecordProcessor(
        AzureMonitorLogExporter(connection_string=connection_string)))
    log_provider.add_log_record_processor(_BaggageLogRecordProcessor())  # type: ignore[arg-type]
    logging.getLogger().addHandler(LoggingHandler(logger_provider=log_provider))
    _az_log_configured = True
    logger.info("Application Insights log exporter configured.")


def _setup_otlp_trace_export(provider: Any, endpoint: str) -> None:
    global _otlp_trace_configured  # pylint: disable=global-statement
    if _otlp_trace_configured or provider is None:
        return
    try:
        from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
        from opentelemetry.sdk.trace.export import BatchSpanProcessor
    except ImportError:
        logger.warning("OTLP trace export requires opentelemetry-exporter-otlp-proto-grpc.")
        return
    provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter(endpoint=endpoint)))
    _otlp_trace_configured = True
    logger.info("OTLP trace exporter configured (endpoint=%s).", endpoint)


def _setup_otlp_log_export(resource: Any, endpoint: str) -> None:
    global _otlp_log_configured  # pylint: disable=global-statement
    if _otlp_log_configured:
        return
    try:
        from opentelemetry._logs import get_logger_provider
        from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter
        from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
        from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
    except ImportError:
        logger.warning("OTLP log export requires opentelemetry-exporter-otlp-proto-grpc.")
        return
    current = get_logger_provider()
    if hasattr(current, "add_log_record_processor"):
        log_provider = current
    else:
        from opentelemetry._logs import set_logger_provider
        log_provider = LoggerProvider(resource=resource)
        set_logger_provider(log_provider)
    log_provider.add_log_record_processor(BatchLogRecordProcessor(
        OTLPLogExporter(endpoint=endpoint)))  # type: ignore[union-attr]
    log_provider.add_log_record_processor(_BaggageLogRecordProcessor())  # type: ignore[arg-type]
    # Note: LoggingHandler is NOT added here to avoid duplicating the
    # handler already installed by _setup_log_export. The OTel LoggerProvider
    # receives log records via the handler added there (or from direct OTel
    # log API usage).  If OTLP is the only exporter, add a handler:
    if not _az_log_configured:
        logging.getLogger().addHandler(LoggingHandler(logger_provider=log_provider))
    _otlp_log_configured = True
    logger.info("OTLP log exporter configured (endpoint=%s).", endpoint)


def _extract_w3c_carrier(headers: Mapping[str, str]) -> dict[str, str]:
    return {k: v for k in _W3C_HEADERS if (v := headers.get(k)) is not None}
