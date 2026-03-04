# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Optional OpenTelemetry tracing for AgentServer.

Tracing is **disabled by default**. Enable it in one of two ways:

1. Set the environment variable ``AGENT_ENABLE_TRACING=true``.
2. Pass ``enable_tracing=True`` to the :class:`AgentServer` constructor
   (constructor argument takes precedence over the env var).

When enabled, the module requires ``opentelemetry-api`` to be installed::

    pip install azure-ai-agentserver[tracing]

If the package is not installed, tracing silently becomes a no-op.
"""
from __future__ import annotations

import logging
import os
from contextlib import contextmanager
from collections.abc import AsyncIterable, AsyncIterator, Mapping  # pylint: disable=import-error
from typing import TYPE_CHECKING, Any, Iterator, Optional, Union

#: Starlette's ``Content`` type — the element type for streaming bodies.
_Content = Union[str, bytes, memoryview]

#: W3C Trace Context header names used for distributed trace propagation.
_W3C_HEADERS = frozenset(("traceparent", "tracestate"))

logger = logging.getLogger("azure.ai.agentserver")

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
    """Lightweight wrapper around OpenTelemetry that can be a complete no-op.

    :param enabled: Explicit enable flag, or *None* to read from
        ``AGENT_ENABLE_TRACING`` env var (default ``false``).
    :type enabled: Optional[bool]
    """

    def __init__(self, enabled: Optional[bool] = None) -> None:
        if enabled is None:
            enabled = os.getenv("AGENT_ENABLE_TRACING", "false").lower() == "true"
        self._enabled = enabled and _HAS_OTEL
        self._tracer: Any = None

        if self._enabled:
            self._tracer = trace.get_tracer("azure.ai.agentserver")
        elif enabled and not _HAS_OTEL:
            logger.warning(
                "Tracing was enabled but opentelemetry-api is not installed. "
                "Install it with: pip install azure-ai-agentserver[tracing]"
            )

    @property
    def enabled(self) -> bool:
        """Whether tracing is active."""
        return self._enabled

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

        :param name: Span name, e.g. ``"AgentServer.invoke"``.
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

        # Extract parent context from W3C traceparent header if present
        ctx = None
        if carrier:
            ctx = TraceContextTextMapPropagator().extract(carrier=carrier)

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

        :param name: Span name, e.g. ``"AgentServer.invoke"``.
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

        ctx = None
        if carrier:
            ctx = TraceContextTextMapPropagator().extract(carrier=carrier)

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
    return {k: v for k, v in headers.items() if k in _W3C_HEADERS}
