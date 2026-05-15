# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Observability setup (logging + tracing) for AgentServerHost.

This module is the single source of truth for all logging handlers,
tracing exporters, and span operations:

**Logging & tracing setup:**

- :func:`configure_observability` — default one-time setup called by
  ``AgentServerHost.__init__``.  Configures:

  - Console ``StreamHandler`` on the **root** logger (so both SDK and
    user ``logging.info()`` calls are visible).
  - Suppression of noisy Azure Core HTTP logging policy output.
  - Trace and log export via ``microsoft-opentelemetry`` distro (auto-detects
    Azure Monitor from ``APPLICATIONINSIGHTS_CONNECTION_STRING`` and OTLP
    from ``OTEL_EXPORTER_OTLP_ENDPOINT``).

  Users may pass a custom callable (or ``None``) via the
  ``configure_observability`` constructor parameter to override or
  disable this default setup.

**Span operations:**

- :func:`request_span` — create a request-scoped span with GenAI attributes
- :func:`end_span` / :func:`record_error` — span lifecycle helpers
- :func:`trace_stream` — wrap streaming responses with span lifecycle
- :func:`set_current_span` / :func:`detach_context` — explicit context management

OpenTelemetry is a required dependency — these functions always create
real spans.  Azure Monitor export is optional (auto-configured by the distro).
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
_ATTR_SESSION_ID = "microsoft.session.id"

# Baggage keys consumed by tracing.
# Currently, the invocations package sets the session-id baggage key.
# The conversation-id baggage key is defined for propagation/mapping, but
# is not currently set elsewhere in this repo.  Incoming requests from
# the calling service may carry either key as W3C baggage.
_BAGGAGE_SESSION_ID = "azure.ai.agentserver.session_id"
_BAGGAGE_CONVERSATION_ID = "azure.ai.agentserver.conversation_id"

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
# Public API: observability setup
# ======================================================================

# Sentinel attribute name set on the console handler to prevent adding
# duplicates across multiple AgentServerHost instantiations.
_CONSOLE_HANDLER_ATTR = "_agentserver_console"


def configure_observability(
    *,
    connection_string: Optional[str] = None,
    log_level: Optional[str] = None,
) -> None:
    """Default observability setup: console logging + tracing/OTel export.

    Attaches a formatted ``StreamHandler`` to the **root** logger so that
    both SDK and user ``logging.info()`` calls are visible on the console.
    Then configures OpenTelemetry tracing and log export (Azure Monitor
    and/or OTLP) when a connection string or OTLP endpoint is available.

    Pass this function (or a custom replacement) as the
    ``configure_observability`` parameter of :class:`AgentServerHost`.
    Pass ``None`` to disable all SDK-managed observability setup.

    :keyword connection_string: Application Insights connection string.
    :paramtype connection_string: str or None
    :keyword log_level: Log level name (e.g. ``"INFO"``, ``"DEBUG"``).
    :paramtype log_level: str or None
    """
    # Console logging on the root logger so user logs are also visible.
    resolved_level = _config.resolve_log_level(log_level)
    root = logging.getLogger()
    root.setLevel(resolved_level)
    # Only add a console handler if root doesn't already have one.
    # Check for our sentinel-marked handler AND any existing StreamHandler
    # (e.g. from user's logging.basicConfig() or framework setup) to
    # prevent duplicate output on stderr.
    _has_console = any(
        getattr(h, _CONSOLE_HANDLER_ATTR, False)
        or (isinstance(h, logging.StreamHandler) and not isinstance(h, logging.FileHandler))
        for h in root.handlers
    )
    if not _has_console:
        _console = logging.StreamHandler()
        _console.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s"))
        setattr(_console, _CONSOLE_HANDLER_ATTR, True)
        root.addHandler(_console)

    # Suppress the noisy Azure Core HTTP logging policy logger.
    logging.getLogger("azure.core.pipeline.policies.http_logging_policy").setLevel(logging.WARNING)

    # Tracing and OTel export
    _configure_tracing(connection_string=connection_string)


def _configure_tracing(connection_string: Optional[str] = None) -> None:
    """Configure OpenTelemetry exporters via the microsoft-opentelemetry distro.

    Internal helper called by :func:`configure_observability`.

    :param connection_string: Application Insights connection string.
        When provided, traces and logs are exported to Azure Monitor.
    :type connection_string: str or None
    """
    resource = _create_resource()
    if resource is None:
        logger.warning("Failed to create OTel resource — tracing will not be configured.")
        return

    # Build custom processors
    agent_name = _config.resolve_agent_name() or None
    agent_version = _config.resolve_agent_version() or None
    project_id = _config.resolve_project_id() or None

    if agent_name and agent_version:
        agent_id = f"{agent_name}:{agent_version}"
    elif agent_name:
        agent_id = agent_name
    else:
        agent_id = None

    span_processors = [
        _FoundryEnrichmentSpanProcessor(
            agent_name=agent_name, agent_version=agent_version,
            agent_id=agent_id, project_id=project_id,
        ),
    ]
    log_record_processors = [_BaggageLogRecordProcessor()]  # type: ignore[list-item]

    try:
        _setup_distro_export(
            resource=resource,
            span_processors=span_processors,
            log_record_processors=log_record_processors,
            connection_string=connection_string,
        )
        logger.info("Tracing configured successfully via microsoft-opentelemetry distro.")
    except ImportError:
        logger.warning("microsoft-opentelemetry is not installed — tracing export disabled.")
        # Still set up TracerProvider with enrichment processor so spans are created
        _ensure_trace_provider(resource, span_processors)


def _setup_distro_export(
    *,
    resource: Any,
    span_processors: list[Any],
    log_record_processors: list[Any],
    connection_string: Optional[str] = None,
) -> None:
    """Delegate to microsoft-opentelemetry distro for exporter configuration.

    Separated into its own function so tests can easily mock it without
    intercepting lazy imports.

    :keyword resource: OTel resource describing this service.
    :keyword span_processors: Span processors to register.
    :keyword log_record_processors: Log record processors to register.
    :keyword connection_string: Application Insights connection string.
    """
    from microsoft.opentelemetry import use_microsoft_opentelemetry

    kwargs: dict[str, Any] = {
        "resource": resource,
        "span_processors": span_processors,
        "log_record_processors": log_record_processors,
    }

    # Azure Monitor export is off by default in the distro — enable it
    # when a connection string is available.
    if connection_string:
        kwargs["enable_azure_monitor"] = True
        kwargs["azure_monitor_connection_string"] = connection_string

    use_microsoft_opentelemetry(**kwargs)


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
        attrs[_ATTR_SESSION_ID] = session_id
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

    with tracer.start_as_current_span(  # type: ignore[reportGeneralTypeIssues]
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


def set_current_span(span: Any) -> Any:
    """Set a span as the current span in the OTel context.

    This makes *span* the active parent for any child spans created
    by downstream code (e.g. framework handlers).  Without this,
    spans created inside the handler would become siblings rather
    than children of *span*.

    Returns a context token that **must** be passed to
    :func:`detach_context` when the scope ends.  No-op when *span*
    is ``None``.

    :param span: The OTel span to make current, or *None*.
    :type span: Any
    :return: A context token, or *None*.
    :rtype: Any
    """
    if span is None:
        return None
    ctx = trace.set_span_in_context(span)
    return _otel_context.attach(ctx)


def detach_context(token: Any) -> None:
    """Detach a context previously attached by :func:`set_current_span`.

    Best-effort no-op when *token* is ``None`` or when the token is no
    longer the current OpenTelemetry context.

    :param token: The token returned by :func:`set_current_span`.
    :type token: Any
    """
    if token is not None:
        try:
            _otel_context.detach(token)
        except ValueError:
            logging.getLogger(__name__).debug(
                "Ignoring OpenTelemetry context detach for a non-current token.",
                exc_info=True,
            )


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

    def on_start(self, span: Any, parent_context: Any = None) -> None:
        if self.project_id:
            span.set_attribute(_ATTR_FOUNDRY_PROJECT_ID, self.project_id)

        # Stamp session and conversation IDs from baggage so child spans
        # created by frameworks (LangChain, Semantic Kernel, etc.) inherit them.
        ctx = parent_context or _otel_context.get_current()
        session_id = _otel_baggage.get_baggage(_BAGGAGE_SESSION_ID, context=ctx)
        if session_id:
            span.set_attribute(_ATTR_SESSION_ID, session_id)
        conversation_id = _otel_baggage.get_baggage(_BAGGAGE_CONVERSATION_ID, context=ctx)
        if conversation_id:
            span.set_attribute(_ATTR_GEN_AI_CONVERSATION_ID, conversation_id)

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


def _ensure_trace_provider(resource: Any, span_processors: Optional[list[Any]] = None) -> Any:
    """Get or create a TracerProvider, optionally adding span processors.

    Used as a fallback when the microsoft-opentelemetry distro is not installed.

    :param resource: OTel resource describing this service.
    :type resource: ~typing.Any
    :param span_processors: Optional span processors to register.
    :type span_processors: list[~typing.Any] or None
    """
    if resource is None:
        return None
    try:
        from opentelemetry.sdk.trace import TracerProvider as SdkTracerProvider
    except ImportError:
        return None
    current = trace.get_tracer_provider()
    if hasattr(current, "add_span_processor"):
        provider = current
    else:
        provider = SdkTracerProvider(resource=resource)
        trace.set_tracer_provider(provider)
    if span_processors and not getattr(provider, "_agentserver_processors_added", False):
        for proc in span_processors:
            provider.add_span_processor(proc)
        provider._agentserver_processors_added = True  # type: ignore[attr-defined]  # pylint: disable=protected-access
    return provider


def _extract_w3c_carrier(headers: Mapping[str, str]) -> dict[str, str]:
    return {k: v for k in _W3C_HEADERS if (v := headers.get(k)) is not None}
