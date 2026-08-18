# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Package-local OpenTelemetry helpers for the typed Voice relay."""

from __future__ import annotations

import time
from typing import Any

from opentelemetry import (
    context as otel_context,
    metrics as otel_metrics,
    trace as otel_trace,
)

from .._version import VERSION


_SCOPE_NAME = "azure.ai.agentserver.invocations.voice"
_SCHEMA_URL = "https://opentelemetry.io/schemas/gen-ai-dev/1.42.0-dev"


def _get_tracer() -> Any:
    try:
        return otel_trace.get_tracer(_SCOPE_NAME, VERSION, schema_url=_SCHEMA_URL)
    except BaseException:  # pylint: disable=broad-exception-caught
        return None


def _get_meter() -> Any:
    try:
        return otel_metrics.get_meter(_SCOPE_NAME, VERSION, schema_url=_SCHEMA_URL)
    except BaseException:  # pylint: disable=broad-exception-caught
        return None


def _create_histogram(meter: Any, name: str, boundaries: tuple[float, ...]) -> Any:
    if meter is None:
        return None
    try:
        return meter.create_histogram(
            name,
            unit="s",
            explicit_bucket_boundaries_advisory=boundaries,
        )
    except BaseException:  # pylint: disable=broad-exception-caught
        return None


def _create_counter(meter: Any, name: str) -> Any:
    if meter is None:
        return None
    try:
        return meter.create_counter(name)
    except BaseException:  # pylint: disable=broad-exception-caught
        return None


_TRACER = _get_tracer()
_METER = _get_meter()
_CONNECTION_DURATION = _create_histogram(
    _METER,
    "azure.ai.agentserver.voice.connection.duration",
    (
        1,
        5,
        10,
        30,
        60,
        120,
        300,
        600,
        1800,
        3600,
        7200,
    ),
)
_TARGET_DURATION = _create_histogram(
    _METER,
    "gen_ai.invoke_agent.duration",
    (
        0.1,
        0.2,
        0.4,
        0.8,
        1.6,
        3.2,
        6.4,
        12.8,
        25.6,
        51.2,
        102.4,
        204.8,
        409.6,
    ),
)
_PROPAGATION_FAILURES = _create_counter(
    _METER,
    "azure.ai.agentserver.trace_context.propagation_failures",
)


def _current_context() -> Any:
    try:
        return otel_context.get_current()
    except BaseException:  # pylint: disable=broad-exception-caught
        return None


def _attach_context(context: Any) -> tuple[Any, Any] | None:
    if context is None:
        return None
    previous = _current_context()
    if previous is None:
        return None
    try:
        return otel_context.attach(context), previous
    except BaseException:  # pylint: disable=broad-exception-caught
        return None


def _reset_context(attachment: tuple[Any, Any] | None) -> None:
    if attachment is None:
        return
    token, previous = attachment
    try:
        token.var.reset(token)
        return
    except BaseException:  # pylint: disable=broad-exception-caught
        pass
    try:
        token.var.set(previous)
    except BaseException:  # pylint: disable=broad-exception-caught
        pass


class _SpanScope:
    """One returned span and its lexical context attachment."""

    __slots__ = (
        "_attachment",
        "_completed",
        "_context",
        "_end_time_ns",
        "_span",
        "_start_ns",
    )

    def __init__(
        self,
        span: Any = None,
        attachment: tuple[Any, Any] | None = None,
        *,
        context: Any = None,
        start_ns: int | None = None,
    ) -> None:
        self._span = span
        self._attachment = attachment
        self._completed = False
        self._context = context
        self._end_time_ns: int | None = None
        self._start_ns = time.monotonic_ns() if start_ns is None else start_ns

    @classmethod
    def start(
        cls,
        name: str,
        *,
        kind: otel_trace.SpanKind,
        parent_context: Any,
        attributes: dict[str, Any] | None = None,
    ) -> "_SpanScope":
        if parent_context is None or _TRACER is None:
            return cls(start_ns=time.monotonic_ns())
        start_ns = time.monotonic_ns()
        try:
            span = _TRACER.start_span(
                name,
                context=parent_context,
                kind=kind,
                attributes=attributes,
            )
        except BaseException:  # pylint: disable=broad-exception-caught
            return cls(start_ns=start_ns)
        span_context = None
        try:
            span_context = otel_trace.set_span_in_context(span, parent_context)
            attachment = _attach_context(span_context)
        except BaseException:  # pylint: disable=broad-exception-caught
            attachment = None
        if span_context is None or attachment is None:
            try:
                span.end()
            except BaseException:  # pylint: disable=broad-exception-caught
                pass
            return cls(start_ns=start_ns)
        return cls(span, attachment, context=span_context, start_ns=start_ns)

    @property
    def context(self) -> Any:
        """Return the explicit child context only after lexical attachment succeeded."""
        return self._context

    @property
    def is_active(self) -> bool:
        """Whether span creation and lexical attachment both succeeded.

        :return: Whether this scope can parent semantic descendants.
        :rtype: bool
        """
        return self._span is not None and self._attachment is not None and self._context is not None

    @property
    def is_completed(self) -> bool:
        """Whether a terminal connection outcome already committed.

        :return: Whether the connection outcome is immutable.
        :rtype: bool
        """
        return self._completed

    def complete_connection(self, outcome: str, close_code: int) -> None:
        if self._completed:
            return
        self._completed = True
        self._set_attributes(
            {
                "azure.ai.agentserver.invocations_ws.close_code": close_code,
                "bridge.outcome": outcome,
            }
        )
        if outcome not in {"completed", "cancelled"}:
            self._set_error(outcome)
        end_ns = time.monotonic_ns()
        self._end_time_ns = time.time_ns()
        metric_attributes = {"bridge.outcome": outcome}
        if outcome not in {"completed", "cancelled"}:
            metric_attributes["error.type"] = outcome
        _record_metric(
            _CONNECTION_DURATION,
            max(0.0, (end_ns - self._start_ns) / 1_000_000_000),
            metric_attributes,
        )

    def record_callback_error(self, error_type: str) -> None:
        self._set_error(error_type)

    def set_attributes(self, attributes: dict[str, Any]) -> None:
        """Best-effort enrichment before the span terminal boundary.

        :param attributes: Content-free span attributes to add.
        :type attributes: dict[str, Any]
        """
        self._set_attributes(attributes)

    def _set_attributes(self, attributes: dict[str, Any]) -> None:
        if self._span is None:
            return
        for name, value in attributes.items():
            try:
                self._span.set_attribute(name, value)
            except BaseException:  # pylint: disable=broad-exception-caught
                pass

    def _set_error(self, error_type: str) -> None:
        if self._span is None:
            return
        try:
            self._span.set_attribute("error.type", error_type)
        except BaseException:  # pylint: disable=broad-exception-caught
            pass
        try:
            self._span.set_status(otel_trace.StatusCode.ERROR)
        except BaseException:  # pylint: disable=broad-exception-caught
            pass

    def close(self) -> None:
        attachment = self._attachment
        self._attachment = None
        _reset_context(attachment)
        span = self._span
        self._span = None
        self._context = None
        if span is None:
            return
        try:
            span.end(end_time=self._end_time_ns)
        except BaseException:  # pylint: disable=broad-exception-caught
            pass


def _connection_outcome(close_code: int, error_code: str | None) -> str:
    error_outcomes = {
        "cancelled": "cancelled",
        "accept_failed": "accept_error",
        "internal_error": "callback_error",
    }
    if error_code is not None:
        return error_outcomes.get(error_code, "internal_error")
    if close_code in {1000, 1001}:
        outcome = "completed"
    elif close_code in {1002, 1003, 1007, 1008, 1009, 1010}:
        outcome = "protocol_error"
    else:
        outcome = "transport_error"
    return outcome


def _record_target_duration(
    start_ns: int,
    origin: str,
    outcome: str,
    error_type: str | None,
    *,
    end_ns: int,
) -> None:
    attributes = {"turn.origin": origin, "bridge.outcome": outcome}
    if error_type is not None:
        attributes["error.type"] = error_type
    _record_metric(
        _TARGET_DURATION,
        max(0.0, (end_ns - start_ns) / 1_000_000_000),
        attributes,
    )


def _record_propagation_failure(error_type: str) -> None:
    try:
        _PROPAGATION_FAILURES.add(
            1,
            {
                "azure.ai.agentserver.trace_context.propagation.hop": "hosted_agents_to_agentserver",
                "error.type": error_type,
            },
        )
    except BaseException:  # pylint: disable=broad-exception-caught
        pass


def _record_metric(instrument: Any, value: float, attributes: dict[str, str]) -> None:
    try:
        instrument.record(value, attributes)
    except BaseException:  # pylint: disable=broad-exception-caught
        pass
