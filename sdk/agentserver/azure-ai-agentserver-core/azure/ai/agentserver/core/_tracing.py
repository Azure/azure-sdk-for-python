# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""OpenTelemetry tracing for AgentHost.

Tracing is automatically enabled when an Application Insights connection
string (``APPLICATIONINSIGHTS_CONNECTION_STRING``) or an OTLP exporter
endpoint (``OTEL_EXPORTER_OTLP_ENDPOINT``) is available.

Requires ``opentelemetry-api`` to be installed::

    pip install azure-ai-agentserver-core[tracing]

If the package is not installed, tracing silently becomes a no-op.

When an Application Insights connection string is available (via constructor
or ``APPLICATIONINSIGHTS_CONNECTION_STRING`` env var), traces **and** logs are
automatically exported to Azure Monitor.  This requires the additional
``opentelemetry-sdk`` and ``azure-monitor-opentelemetry-exporter`` packages
(both included in the ``[tracing]`` extras group).

When the platform sets ``OTEL_EXPORTER_OTLP_ENDPOINT``, an OTLP exporter is
also registered for traces and logs.
"""
import logging
from collections.abc import AsyncIterable, AsyncIterator, Mapping  # pylint: disable=import-error
from contextlib import contextmanager
from typing import TYPE_CHECKING, Any, Iterator, Optional, Union

from . import _config
from ._logger import get_logger

#: Starlette's ``Content`` type — the element type for streaming bodies.
_Content = Union[str, bytes, memoryview]

#: W3C Trace Context header names used for distributed trace propagation.
_W3C_HEADERS = ("traceparent", "tracestate")


# ------------------------------------------------------------------
# GenAI semantic convention attribute keys
# ------------------------------------------------------------------
_ATTR_SERVICE_NAME = "service.name"
_ATTR_GEN_AI_SYSTEM = "gen_ai.system"
_ATTR_GEN_AI_PROVIDER_NAME = "gen_ai.provider.name"
_ATTR_GEN_AI_AGENT_ID = "gen_ai.agent.id"
_ATTR_GEN_AI_AGENT_NAME = "gen_ai.agent.name"
_ATTR_GEN_AI_AGENT_VERSION = "gen_ai.agent.version"
_ATTR_GEN_AI_RESPONSE_ID = "gen_ai.response.id"
_ATTR_GEN_AI_OPERATION_NAME = "gen_ai.operation.name"
_ATTR_GEN_AI_CONVERSATION_ID = "gen_ai.conversation.id"

# Foundry project identity
_ATTR_FOUNDRY_PROJECT_ID = "microsoft.foundry.project.id"

# Constant values
_SERVICE_NAME_VALUE = "azure.ai.agentserver"
_GEN_AI_SYSTEM_VALUE = "azure.ai.agentserver"
_GEN_AI_PROVIDER_NAME_VALUE = "AzureAI Hosted Agents"

logger = get_logger()

_HAS_OTEL = False
_HAS_BAGGAGE = False
try:
    from opentelemetry import context as _otel_context, trace
    from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator

    _HAS_OTEL = True
    try:
        from opentelemetry import baggage as _otel_baggage

        _HAS_BAGGAGE = True
    except ImportError:
        pass
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

    def __init__(
        self,
        connection_string: Optional[str] = None,
    ) -> None:
        self._enabled = _HAS_OTEL
        self._tracer: Any = None
        self._propagator: Any = None

        # Resolve agent identity from environment variables.
        self._agent_name = _config.resolve_agent_name()
        self._agent_version = _config.resolve_agent_version()
        self._project_id = _config.resolve_project_id()

        # gen_ai.agent.id format:
        # "{name}:{version}" when both present, "{name}" when only name, "" otherwise
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

        # Create OTel resource once for all exporters
        resource = _create_resource()

        # Ensure a single TracerProvider exists for all exporters.
        # Create it once up front so that both Azure Monitor and OTLP
        # exporters add processors to the same provider, regardless of
        # which combination is configured or the order they are set up.
        trace_provider = _ensure_trace_provider(resource)

        # Register enrichment processor so Foundry identity attributes
        # appear on ALL spans (including those from underlying frameworks).
        if trace_provider is not None:
            enrichment = _FoundryEnrichmentSpanProcessor(
                agent_name=self._agent_name or None,
                agent_version=self._agent_version or None,
                agent_id=self._agent_id or None,
                project_id=self._project_id or None,
            )
            trace_provider.add_span_processor(enrichment)

        if connection_string:
            self._setup_azure_monitor(
                connection_string, resource, trace_provider)

        # OTLP exporter
        otlp_endpoint = _config.resolve_otlp_endpoint()
        if otlp_endpoint:
            self._setup_otlp_export(otlp_endpoint, resource, trace_provider)

        self._tracer = trace.get_tracer("azure.ai.agentserver")
        self._propagator = TraceContextTextMapPropagator()

    # ------------------------------------------------------------------
    # Azure Monitor auto-configuration
    # ------------------------------------------------------------------

    def _extract_context(
        self,
        carrier: Optional[dict[str, str]],
    ) -> Any:
        """Extract parent trace context from a W3C carrier dict.

        Uses the standard ``traceparent`` / ``tracestate`` headers via
        the OpenTelemetry :class:`TraceContextTextMapPropagator`.

        :param carrier: W3C trace-context headers or None.
        :type carrier: Optional[dict[str, str]]
        :return: The extracted OTel context, or None.
        :rtype: Any
        """
        if not carrier or self._propagator is None:
            return None

        return self._propagator.extract(carrier=carrier)

    @staticmethod
    def _setup_azure_monitor(connection_string: str, resource: Any, trace_provider: Any) -> None:
        """Configure global TracerProvider and LoggerProvider for App Insights.

        Sets up ``AzureMonitorTraceExporter`` so spans are exported to
        Application Insights, and ``AzureMonitorLogExporter`` so log records
        from the ``azure.ai.agentserver`` namespace are forwarded.

        If the required packages are not installed, a warning is logged and
        export is silently skipped — span creation still works via the
        default no-op or user-configured provider.

        :param connection_string: Application Insights connection string.
        :type connection_string: str
        :param resource: Pre-created OTel resource, or None.
        :type resource: Any
        :param trace_provider: The shared TracerProvider, or None.
        :type trace_provider: Any
        """
        if resource is None:
            return
        _setup_trace_export(trace_provider, connection_string)
        _setup_log_export(resource, connection_string)

    @staticmethod
    def _setup_otlp_export(endpoint: str, resource: Any, trace_provider: Any) -> None:
        """Configure OTLP exporter for traces and logs.

        Per container-image-spec, when ``OTEL_EXPORTER_OTLP_ENDPOINT``
        is set, the container must register an OTLP exporter.

        :param endpoint: The OTLP collector endpoint URL.
        :type endpoint: str
        :param resource: Pre-created OTel resource, or None.
        :type resource: Any
        :param trace_provider: The shared TracerProvider, or None.
        :type trace_provider: Any
        """
        if resource is None:
            return
        _setup_otlp_trace_export(trace_provider, endpoint)
        _setup_otlp_log_export(resource, endpoint)

    # ------------------------------------------------------------------
    # Span naming and attribute helpers (shared by all protocols)
    # ------------------------------------------------------------------

    def span_name(self, span_operation: str) -> str:
        """Build a span name using the operation and agent label.

        Per invocation-protocol-spec:
        ``"invoke_agent {Name}:{Version}"`` or ``"invoke_agent {Name}"``
        or ``"invoke_agent"``.

        :param span_operation: The span operation (e.g. ``"invoke_agent"``).
            This becomes the first token of the OTel span name.
        :type span_operation: str
        :return: ``"<span_operation> <name>:<version>"`` or just
            ``"<span_operation>"``.
        :rtype: str
        """
        if self._agent_id:
            return f"{span_operation} {self._agent_id}"
        return span_operation

    def build_span_attrs(
        self,
        invocation_id: str,
        session_id: str,
        operation_name: Optional[str] = None,
    ) -> dict[str, str]:
        """Build GenAI semantic convention span attributes.

        These attributes are common across all protocol heads.
        Per invocation-protocol-spec.

        :param invocation_id: The invocation/request ID for this request.
        :type invocation_id: str
        :param session_id: The session ID (empty string if absent).
        :type session_id: str
        :param operation_name: Optional ``gen_ai.operation.name`` value
            (e.g. ``"invoke_agent"``).  Omitted from the dict when *None*.
        :type operation_name: Optional[str]
        :return: Span attribute dict.
        :rtype: dict[str, str]
        """
        attrs: dict[str, str] = {
            # Identity & GenAI convention tags
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
        return attrs

    @contextmanager
    def span(
        self,
        name: str,
        attributes: Optional[dict[str, str]] = None,
        carrier: Optional[dict[str, str]] = None,
    ) -> Iterator[Any]:
        """Create a traced span if tracing is enabled, otherwise no-op.

        Yields the OpenTelemetry span object when tracing is active, or
        ``None`` when tracing is disabled.  Callers may use the yielded span
        together with :meth:`record_error` to attach error information.

        :param name: Span name, e.g. ``"invoke_agent my_agent:1.0"``.
        :type name: str
        :param attributes: Key-value span attributes.
        :type attributes: Optional[dict[str, str]]
        :param carrier: Incoming HTTP headers for W3C trace-context propagation.
        :type carrier: Optional[dict[str, str]]
        :return: Context manager that yields the OTel span or *None*.
        :rtype: Iterator[Any]
        """
        if not self._enabled or self._tracer is None:
            yield None
            return

        ctx = self._extract_context(carrier)

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
    ) -> Any:
        """Start a span without a context manager.

        Use this for streaming responses where the span must outlive the
        initial ``invoke()`` call.  The caller **must** call :meth:`end_span`
        when the work is finished.

        :param name: Span name, e.g. ``"invoke_agent my_agent:1.0"``.
        :type name: str
        :param attributes: Key-value span attributes.
        :type attributes: Optional[dict[str, str]]
        :param carrier: Incoming HTTP headers for W3C trace-context propagation.
        :type carrier: Optional[dict[str, str]]
        :return: The OTel span, or *None* when tracing is disabled.
        :rtype: Any
        """
        if not self._enabled or self._tracer is None:
            return None

        ctx = self._extract_context(carrier)

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
    ) -> tuple[str, dict[str, str], dict[str, str]]:
        """Extract headers and build span arguments for a request.

        Shared pipeline used by :meth:`start_request_span` and
        :meth:`request_span` to avoid duplicating header extraction,
        attribute building, and span naming.

        :param headers: HTTP request headers (any ``Mapping[str, str]``).
        :type headers: Mapping[str, str]
        :param invocation_id: The invocation/request ID.
        :type invocation_id: str
        :param span_operation: Span operation (e.g. ``"invoke_agent"``).
        :type span_operation: str
        :param operation_name: Optional ``gen_ai.operation.name`` value.
        :type operation_name: Optional[str]
        :param session_id: Session ID from the ``agent_session_id`` query
            parameter.  Defaults to ``""`` (no session).
        :type session_id: str
        :return: ``(name, attributes, carrier)`` ready for
            :meth:`span` or :meth:`start_span`.
        :rtype: tuple[str, dict[str, str], dict[str, str]]
        """
        carrier = _extract_w3c_carrier(headers)
        span_attrs = self.build_span_attrs(
            invocation_id, session_id, operation_name=operation_name
        )
        return self.span_name(span_operation), span_attrs, carrier

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
        :param span_operation: Span operation (e.g. ``"invoke_agent"``).
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
        name, attrs, carrier = self._prepare_request_span_args(
            headers, invocation_id, span_operation, operation_name,
            session_id=session_id,
        )
        return self.start_span(name, attributes=attrs, carrier=carrier)

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
        name, attrs, carrier = self._prepare_request_span_args(
            headers, invocation_id, span_operation, operation_name,
            session_id=session_id,
        )
        with self.span(name, attributes=attrs, carrier=carrier) as otel_span:
            yield otel_span

    # ------------------------------------------------------------------
    # Span lifecycle helpers
    # ------------------------------------------------------------------

    def end_span(self, span: Any, exc: Optional[BaseException] = None) -> None:
        """End a span started with :meth:`start_span`.

        Optionally records an error before ending.  No-op when *span* is
        ``None`` (tracing disabled).

        :param span: The OTel span, or *None*.
        :type span: Any
        :param exc: Optional exception to record before ending.
        :type exc: Optional[BaseException]
        """
        if span is None:
            return
        if exc is not None:
            self.record_error(span, exc)
        span.end()

    @staticmethod
    def record_error(span: Any, exc: BaseException) -> None:
        """Record an exception and ERROR status on a span.

        No-op when *span* is ``None`` (tracing disabled) or when
        ``opentelemetry-api`` is not installed.

        :param span: The OTel span returned by :meth:`span`, or *None*.
        :type span: Any
        :param exc: The exception to record.
        :type exc: BaseException
        """
        if span is not None and _HAS_OTEL:
            span.set_status(trace.StatusCode.ERROR, str(exc))
            span.record_exception(exc)

    @staticmethod
    def set_baggage(keys: dict[str, str]) -> Any:
        """Set W3C Baggage entries on the current context.

        Baggage keys propagate to downstream services via
        the ``baggage`` header.  No-op when the OTel baggage API is not
        available.

        :param keys: Mapping of baggage key → value to set.
        :type keys: dict[str, str]
        :return: A context token that must be passed to :meth:`detach_baggage`
            when the scope ends, or *None* when baggage is unavailable.
        :rtype: Any
        """
        if not _HAS_BAGGAGE:
            return None
        ctx = _otel_context.get_current()
        for key, value in keys.items():
            ctx = _otel_baggage.set_baggage(key, value, context=ctx)
        return _otel_context.attach(ctx)

    @staticmethod
    def detach_baggage(token: Any) -> None:
        """Detach a baggage context previously attached by :meth:`set_baggage`.

        :param token: The token returned by :meth:`set_baggage`.
        :type token: Any
        """
        if token is not None and _HAS_BAGGAGE:
            _otel_context.detach(token)

    @staticmethod
    def set_current_span(span: Any) -> Any:
        """Set a span as the current span in the OTel context.

        This makes *span* the active parent for any child spans created
        by downstream code (e.g. framework handlers).  Without this,
        spans created inside the handler would become siblings rather
        than children of *span*.

        Returns a context token that **must** be passed to
        :meth:`detach_context` when the scope ends.  No-op when *span*
        is ``None`` or tracing is not available.

        :param span: The OTel span to make current, or *None*.
        :type span: Any
        :return: A context token, or *None*.
        :rtype: Any
        """
        if span is None or not _HAS_OTEL:
            return None
        ctx = trace.set_span_in_context(span)
        return _otel_context.attach(ctx)

    @staticmethod
    def detach_context(token: Any) -> None:
        """Detach a context previously attached by :meth:`set_current_span`.

        :param token: The token returned by :meth:`set_current_span`.
        :type token: Any
        """
        if token is not None and _HAS_OTEL:
            _otel_context.detach(token)

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
        error: Optional[BaseException] = None
        try:
            async for chunk in iterator:
                yield chunk
        except BaseException as exc:
            error = exc
            raise
        finally:
            self.end_span(span, exc=error)


class _FoundryEnrichmentSpanProcessor:
    """Span processor that adds Foundry identity attributes to all spans.

    Per the container image spec, ``gen_ai.agent.name``,
    ``gen_ai.agent.version``, ``gen_ai.agent.id``, and
    ``microsoft.foundry.project.id`` must be present on **every** span
    generated by the server — including spans created by underlying
    frameworks (e.g. HTTP client libraries, LLM SDKs).

    Registering this processor on the global :class:`TracerProvider`
    ensures enrichment happens automatically regardless of which
    library creates the span.

    :param agent_name: The Foundry agent name, or *None*.
    :type agent_name: Optional[str]
    :param agent_version: The Foundry agent version, or *None*.
    :type agent_version: Optional[str]
    :param agent_id: The combined agent identifier (``name:version``), or *None*.
    :type agent_id: Optional[str]
    :param project_id: The Foundry project ARM resource ID, or *None*.
    :type project_id: Optional[str]
    """

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
        """Add Foundry identity attributes when a span starts."""
        if self.agent_name:
            span.set_attribute(_ATTR_GEN_AI_AGENT_NAME, self.agent_name)
        if self.agent_version:
            span.set_attribute(_ATTR_GEN_AI_AGENT_VERSION, self.agent_version)
        if self.agent_id:
            span.set_attribute(_ATTR_GEN_AI_AGENT_ID, self.agent_id)
        if self.project_id:
            span.set_attribute(_ATTR_FOUNDRY_PROJECT_ID, self.project_id)

    def _on_ending(self, span: Any) -> None:  # pylint: disable=unused-argument
        """No-op on span ending (called before on_end with mutable span)."""

    def on_end(self, span: Any) -> None:  # pylint: disable=unused-argument
        """No-op on span end."""

    def shutdown(self) -> None:
        """No-op shutdown."""

    def force_flush(self, timeout_millis: int = 30000) -> bool:  # pylint: disable=unused-argument
        """No-op flush — always returns True."""
        return True


def _create_resource() -> Any:
    """Create the OTel resource for exporters.

    :return: A :class:`~opentelemetry.sdk.resources.Resource`, or *None*
        if the required packages are not installed.
    :rtype: Any
    """
    try:
        from opentelemetry.sdk.resources import Resource
    except ImportError:
        logger.warning(
            "Required OTel SDK packages are not installed.  Install them with: "
            "pip install azure-ai-agentserver-core[tracing]"
        )
        return None
    return Resource.create({_ATTR_SERVICE_NAME: _SERVICE_NAME_VALUE})


def _ensure_trace_provider(resource: Any) -> Any:
    """Return or create the global :class:`TracerProvider`.

    If a user-configured ``TracerProvider`` already exists (one that
    supports ``add_span_processor``), it is reused.  Otherwise a new
    ``SdkTracerProvider`` is created with the given *resource* and set
    as the global provider.

    Creating the provider once and passing it to both
    :func:`_setup_trace_export` and :func:`_setup_otlp_trace_export`
    removes the order-dependent initialization that existed previously.

    :param resource: The OTel resource describing this service, or *None*.
    :type resource: Any
    :return: A ``TracerProvider``, or *None* if the SDK is not installed.
    :rtype: Any
    """
    # Called only when _HAS_OTEL is True, so the module-level ``trace``
    # import is guaranteed to be bound.
    if resource is None:
        return None
    try:
        from opentelemetry.sdk.trace import TracerProvider as SdkTracerProvider
    except ImportError:
        return None

    current_provider = trace.get_tracer_provider()
    if hasattr(current_provider, "add_span_processor"):
        return current_provider

    provider = SdkTracerProvider(resource=resource)
    trace.set_tracer_provider(provider)
    return provider


# Sentinel flags to prevent adding duplicate exporters across multiple
# TracingHelper instantiations within the same process.
_az_trace_export_configured = False
_az_log_export_configured = False
_otlp_trace_export_configured = False
_otlp_log_export_configured = False


def _setup_trace_export(provider: Any, connection_string: str) -> None:
    """Add an Azure Monitor span processor to the given *provider*.

    :param provider: The TracerProvider to attach the exporter to, or *None*.
    :type provider: Any
    :param connection_string: Application Insights connection string.
    :type connection_string: str
    """
    global _az_trace_export_configured  # pylint: disable=global-statement
    if _az_trace_export_configured:
        return
    if provider is None:
        return
    try:
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

    exporter = AzureMonitorTraceExporter(connection_string=connection_string)
    provider.add_span_processor(BatchSpanProcessor(exporter))
    _az_trace_export_configured = True
    logger.info("Application Insights trace exporter configured.")


def _setup_log_export(resource: Any, connection_string: str) -> None:
    """Configure a global :class:`LoggerProvider` that exports to App Insights.

    :param resource: The OTel resource describing this service.
    :type resource: Any
    :param connection_string: Application Insights connection string.
    :type connection_string: str
    """
    global _az_log_export_configured  # pylint: disable=global-statement
    if _az_log_export_configured:
        return
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
    log_provider.add_log_record_processor(
        BatchLogRecordProcessor(log_exporter))
    handler = LoggingHandler(logger_provider=log_provider)
    logging.getLogger().addHandler(handler)
    _az_log_export_configured = True
    logger.info("Application Insights log exporter configured.")


def _setup_otlp_trace_export(provider: Any, endpoint: str) -> None:
    """Add an OTLP span processor to the given *provider*.

    :param provider: The TracerProvider to attach the exporter to, or *None*.
    :type provider: Any
    :param endpoint: The OTLP collector endpoint URL.
    :type endpoint: str
    """
    global _otlp_trace_export_configured  # pylint: disable=global-statement
    if _otlp_trace_export_configured:
        return
    if provider is None:
        return
    try:
        from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
        from opentelemetry.sdk.trace.export import BatchSpanProcessor
    except ImportError:
        logger.warning(
            "OTLP trace export requires opentelemetry-sdk and "
            "opentelemetry-exporter-otlp-proto-grpc.  "
            "Traces will not be forwarded via OTLP."
        )
        return

    exporter = OTLPSpanExporter(endpoint=endpoint)
    provider.add_span_processor(BatchSpanProcessor(exporter))
    _otlp_trace_export_configured = True
    logger.info("OTLP trace exporter configured (endpoint=%s).", endpoint)


def _setup_otlp_log_export(resource: Any, endpoint: str) -> None:
    """Configure OTLP log exporter.

    :param resource: The OTel resource describing this service.
    :type resource: Any
    :param endpoint: The OTLP collector endpoint URL.
    :type endpoint: str
    """
    global _otlp_log_export_configured  # pylint: disable=global-statement
    if _otlp_log_export_configured:
        return
    try:
        from opentelemetry._logs import get_logger_provider
        from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter
        from opentelemetry.sdk._logs import LoggerProvider
        from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
    except ImportError:
        logger.warning(
            "OTLP log export requires opentelemetry-sdk and "
            "opentelemetry-exporter-otlp-proto-grpc.  "
            "Logs will not be forwarded via OTLP."
        )
        return

    current_provider = get_logger_provider()
    if hasattr(current_provider, "add_log_record_processor"):
        log_provider = current_provider
    else:
        from opentelemetry._logs import set_logger_provider

        log_provider = LoggerProvider(resource=resource)
        set_logger_provider(log_provider)

    log_exporter = OTLPLogExporter(endpoint=endpoint)
    log_provider.add_log_record_processor(
        BatchLogRecordProcessor(log_exporter))  # type: ignore[union-attr]
    _otlp_log_export_configured = True
    logger.info("OTLP log exporter configured (endpoint=%s).", endpoint)


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
    result: dict[str, str] = {k: v for k in _W3C_HEADERS if (
        v := headers.get(k)) is not None}
    return result
