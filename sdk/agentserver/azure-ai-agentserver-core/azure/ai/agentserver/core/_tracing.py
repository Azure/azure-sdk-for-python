# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""OpenTelemetry tracing for AgentServerHost.

Tracing is automatically enabled when an Application Insights connection
string (``APPLICATIONINSIGHTS_CONNECTION_STRING``) or an OTLP exporter
endpoint (``OTEL_EXPORTER_OTLP_ENDPOINT``) is available.

Requires ``opentelemetry-api`` to be installed::

    pip install azure-ai-agentserver-core[tracing]

If the package is not installed, tracing silently becomes a no-op.
"""
import logging
from collections.abc import AsyncIterable, AsyncIterator, Mapping  # pylint: disable=import-error
from contextlib import contextmanager
from typing import Any, Iterator, Optional, Union

from . import _config
from ._logger import get_logger

_Content = Union[str, bytes, memoryview]
_W3C_HEADERS = ("traceparent", "tracestate")

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

logger = get_logger()

_HAS_OTEL = False
try:
    from opentelemetry import trace
    from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator

    _HAS_OTEL = True
except ImportError:
    pass


class TracingHelper:
    """Lightweight wrapper around OpenTelemetry.

    Automatically configures Azure Monitor and OTLP exporters when the
    corresponding environment variables are set.  All span creation and
    lifecycle is managed by the host framework -- developers never interact
    with this class directly.
    """

    def __init__(self, connection_string: Optional[str] = None) -> None:
        self._enabled = _HAS_OTEL
        self._tracer: Any = None
        self._propagator: Any = None

        self._agent_name = _config.resolve_agent_name()
        self._agent_version = _config.resolve_agent_version()
        self._project_id = _config.resolve_project_id()

        if self._agent_name and self._agent_version:
            self._agent_id = f"{self._agent_name}:{self._agent_version}"
        elif self._agent_name:
            self._agent_id = self._agent_name
        else:
            self._agent_id = ""

        if not self._enabled:
            logger.warning(
                "Tracing was enabled but opentelemetry-api is not installed. "
                "Install it with: pip install azure-ai-agentserver-core[tracing]"
            )
            return

        resource = _create_resource()
        trace_provider = _ensure_trace_provider(resource)

        if trace_provider is not None:
            trace_provider.add_span_processor(_FoundryEnrichmentSpanProcessor(
                agent_name=self._agent_name or None,
                agent_version=self._agent_version or None,
                agent_id=self._agent_id or None,
                project_id=self._project_id or None,
            ))

        if connection_string:
            self._setup_azure_monitor(connection_string, resource, trace_provider)

        otlp_endpoint = _config.resolve_otlp_endpoint()
        if otlp_endpoint:
            self._setup_otlp_export(otlp_endpoint, resource, trace_provider)

        self._tracer = trace.get_tracer("azure.ai.agentserver")
        self._propagator = TraceContextTextMapPropagator()

    # ------------------------------------------------------------------
    # Exporter configuration
    # ------------------------------------------------------------------

    @staticmethod
    def _setup_azure_monitor(connection_string: str, resource: Any, trace_provider: Any) -> None:
        if resource is None:
            return
        _setup_trace_export(trace_provider, connection_string)
        _setup_log_export(resource, connection_string)

    @staticmethod
    def _setup_otlp_export(endpoint: str, resource: Any, trace_provider: Any) -> None:
        if resource is None:
            return
        _setup_otlp_trace_export(trace_provider, endpoint)
        _setup_otlp_log_export(resource, endpoint)

    # ------------------------------------------------------------------
    # Span creation
    # ------------------------------------------------------------------

    @contextmanager
    def request_span(
        self,
        headers: Mapping[str, str],
        invocation_id: str,
        span_operation: str,
        operation_name: Optional[str] = None,
        session_id: str = "",
        end_on_exit: bool = True,
    ) -> Iterator[Any]:
        """Create a request-scoped span from HTTP headers.

        Extracts W3C trace context, builds GenAI attributes, and creates
        a span set as current in context (child spans are correctly parented).

        For **non-streaming** requests use ``end_on_exit=True`` (default).
        For **streaming** requests use ``end_on_exit=False`` and end the
        span via :meth:`trace_stream`.

        :param headers: HTTP request headers.
        :type headers: ~collections.abc.Mapping[str, str]
        :param invocation_id: The request/invocation ID.
        :type invocation_id: str
        :param span_operation: Span operation name (e.g. ``"invoke_agent"``).
        :type span_operation: str
        :param operation_name: Optional ``gen_ai.operation.name`` value.
        :type operation_name: str or None
        :param session_id: Session ID (empty string if absent).
        :type session_id: str
        :param end_on_exit: Whether to end the span when the context exits.
        :type end_on_exit: bool
        :return: Context manager yielding the OTel span or *None*.
        :rtype: ~typing.Iterator
        """
        if not self._enabled or self._tracer is None:
            yield None
            return

        # Build span name
        name = f"{span_operation} {self._agent_id}" if self._agent_id else span_operation

        # Build attributes
        attrs: dict[str, str] = {
            _ATTR_SERVICE_NAME: _SERVICE_NAME_VALUE,
            _ATTR_GEN_AI_SYSTEM: _GEN_AI_SYSTEM_VALUE,
            _ATTR_GEN_AI_PROVIDER_NAME: _GEN_AI_PROVIDER_NAME_VALUE,
            _ATTR_GEN_AI_RESPONSE_ID: invocation_id,
            _ATTR_GEN_AI_AGENT_ID: self._agent_id,
        }
        if self._agent_name:
            attrs[_ATTR_GEN_AI_AGENT_NAME] = self._agent_name
        if self._agent_version:
            attrs[_ATTR_GEN_AI_AGENT_VERSION] = self._agent_version
        if operation_name:
            attrs[_ATTR_GEN_AI_OPERATION_NAME] = operation_name
        if session_id:
            attrs[_ATTR_GEN_AI_CONVERSATION_ID] = session_id
        if self._project_id:
            attrs[_ATTR_FOUNDRY_PROJECT_ID] = self._project_id

        # Extract W3C trace context
        carrier = _extract_w3c_carrier(headers)
        ctx = self._propagator.extract(carrier=carrier) if carrier else None

        with self._tracer.start_as_current_span(
            name=name,
            attributes=attrs,
            kind=trace.SpanKind.SERVER,
            context=ctx,
            end_on_exit=end_on_exit,
        ) as otel_span:
            yield otel_span

    # ------------------------------------------------------------------
    # Span lifecycle
    # ------------------------------------------------------------------

    def end_span(self, span: Any, exc: Optional[BaseException] = None) -> None:
        """End a span, optionally recording an error first.

        :param span: The OTel span to end, or None.
        :type span: any
        :param exc: Optional exception to record on the span.
        :type exc: ~BaseException or None
        """
        if span is None:
            return
        if exc is not None:
            self.record_error(span, exc)
        span.end()

    @staticmethod
    def record_error(span: Any, exc: BaseException) -> None:
        """Record an exception and ERROR status on a span.

        :param span: The OTel span to record the error on.
        :type span: any
        :param exc: The exception to record.
        :type exc: ~BaseException
        """
        if span is not None and _HAS_OTEL:
            span.set_status(trace.StatusCode.ERROR, str(exc))
            span.record_exception(exc)

    async def trace_stream(
        self, iterator: AsyncIterable[_Content], span: Any
    ) -> AsyncIterator[_Content]:
        """Wrap a streaming body so the span covers the full transmission.

        Yields chunks unchanged.  Ends the span when the iterator is
        exhausted or raises an exception.

        :param iterator: The async iterable to wrap.
        :type iterator: ~collections.abc.AsyncIterable
        :param span: The OTel span to end when the stream completes.
        :type span: any
        :return: An async iterator yielding chunks unchanged.
        :rtype: ~collections.abc.AsyncIterator
        """
        error: Optional[BaseException] = None
        try:
            async for chunk in iterator:
                yield chunk
        except BaseException as exc:
            error = exc
            raise
        finally:
            self.end_span(span, exc=error)


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
        if self.agent_name:
            span.set_attribute(_ATTR_GEN_AI_AGENT_NAME, self.agent_name)
        if self.agent_version:
            span.set_attribute(_ATTR_GEN_AI_AGENT_VERSION, self.agent_version)
        if self.agent_id:
            span.set_attribute(_ATTR_GEN_AI_AGENT_ID, self.agent_id)
        if self.project_id:
            span.set_attribute(_ATTR_FOUNDRY_PROJECT_ID, self.project_id)

    def _on_ending(self, span: Any) -> None:  # pylint: disable=unused-argument
        pass

    def on_end(self, span: Any) -> None:  # pylint: disable=unused-argument
        pass

    def shutdown(self) -> None:
        pass

    def force_flush(self, timeout_millis: int = 30000) -> bool:  # pylint: disable=unused-argument
        return True


# ======================================================================
# Infrastructure: resource, provider, exporters
# ======================================================================


def _create_resource() -> Any:
    try:
        from opentelemetry.sdk.resources import Resource
    except ImportError:
        logger.warning("OTel SDK not installed. pip install azure-ai-agentserver-core[tracing]")
        return None
    return Resource.create({_ATTR_SERVICE_NAME: _SERVICE_NAME_VALUE})


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


_az_trace_configured = False
_az_log_configured = False
_otlp_trace_configured = False
_otlp_log_configured = False


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
        from opentelemetry.sdk._logs import LoggerProvider
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
    _otlp_log_configured = True
    logger.info("OTLP log exporter configured (endpoint=%s).", endpoint)


def _extract_w3c_carrier(headers: Mapping[str, str]) -> dict[str, str]:
    return {k: v for k in _W3C_HEADERS if (v := headers.get(k)) is not None}
