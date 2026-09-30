# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Application-owned tracing handle for one target-agent decision."""

from __future__ import annotations

import asyncio  # pylint: disable=do-not-import-asyncio
import re
import threading
import time
import weakref
from enum import Enum
from typing import Any, ContextManager, cast

from opentelemetry import trace as otel_trace
from opentelemetry.trace import Link, SpanContext, TraceState

from azure.ai.agentserver.core import experimental
from azure.core import CaseInsensitiveEnumMeta

from ._codec import _validate_prefixed_identifier_value
from ._tracing import _TRACER, _attach_context, _record_target_duration, _reset_context


_SPAN_CONTEXT_TYPE = cast(type[Any], SpanContext)
_SAFE_RESPONSE_ID = re.compile(r"^r_[0-9a-f]{32}$")


@experimental
class TargetTurnOrigin(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Application-declared origin of a target-agent decision."""

    USER = "user"
    NO_INPUT = "no_input"
    PROACTIVE = "proactive"
    RECOVERY = "recovery"
    OTHER = "other"


@experimental
class TargetTurnOutcome(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Immutable terminal outcome of a target-agent decision."""

    RESPONSE = "response"
    NONE = "none"
    TIMEOUT = "timeout"
    ERROR = "error"
    CANCELLED = "cancelled"
    END_CALL = "end_call"
    TRANSPORT_ERROR = "transport_error"
    ABANDONED = "abandoned"
    OTHER = "other"


def _normalize_enum(enum_type: type[Enum], value: Any, name: str) -> Any:
    if isinstance(value, enum_type):
        return value
    if not isinstance(value, str):
        raise TypeError(f"{name} must be a string or {enum_type.__name__}")
    if not value.strip():
        raise ValueError(f"{name} must not be empty")
    try:
        return enum_type(value)
    except ValueError:
        return enum_type("other")


def _validate_count(value: Any, name: str, *, minimum: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{name} must be an integer")
    if value < minimum or value > 2**63 - 1:
        raise ValueError(f"{name} must be between {minimum} and {2**63 - 1}")
    return value


def _validate_completion(
    outcome: TargetTurnOutcome | str,
    response_id: str | None,
    output_item_count: int | None,
) -> tuple[TargetTurnOutcome, str | None, int | None]:
    normalized_outcome = _normalize_enum(TargetTurnOutcome, outcome, "outcome")
    validated_response_id = None
    if response_id is not None:
        validated_response_id = _validate_prefixed_identifier_value(response_id, "response_id", "r_")
    validated_output_count = None
    if output_item_count is not None:
        validated_output_count = _validate_count(output_item_count, "output_item_count", minimum=0)

    if normalized_outcome is TargetTurnOutcome.RESPONSE:
        if validated_response_id is None or validated_output_count is None or validated_output_count < 1:
            raise ValueError("response outcome requires a response_id and at least one output item")
    elif normalized_outcome is TargetTurnOutcome.NONE:
        if validated_response_id is not None or validated_output_count != 0:
            raise ValueError("none outcome requires no response_id and zero output items")
    elif validated_output_count is not None and validated_output_count > 0 and validated_response_id is None:
        raise ValueError("positive output_item_count requires a response_id")

    return normalized_outcome, validated_response_id, validated_output_count


def _is_safe_telemetry_response_id(value: str) -> bool:
    return _SAFE_RESPONSE_ID.fullmatch(value) is not None


class _TargetTurnActivation:
    __slots__ = ("_owner", "_entered")

    def __init__(self, owner: "TargetTurn") -> None:
        self._owner = owner
        self._entered = False

    def __enter__(self) -> None:
        if self._entered:
            raise RuntimeError("Target turn activation has already been entered")
        self._owner._enter_activation()  # pylint: disable=protected-access
        self._entered = True

    def __exit__(self, _exc_type: Any, _exc_value: Any, _traceback: Any) -> None:
        if self._entered:
            self._owner._exit_activation()  # pylint: disable=protected-access
            self._entered = False


@experimental
class TargetTurn:
    """Application-owned trace lifetime for one target-agent decision."""

    __slots__ = (
        "_activated",
        "_activation_attachment",
        "_activation_task",
        "_active",
        "_affinity",
        "_completed",
        "_connection_context",
        "_origin",
        "_span",
        "_start_ns",
    )
    _activated: bool
    _activation_attachment: (
        tuple[
            tuple[Any, Any] | None,
            tuple[Any, Any] | None,
        ]
        | None
    )
    _activation_task: asyncio.Task[Any] | None
    _active: bool
    _affinity: tuple[
        int,
        weakref.ReferenceType[asyncio.AbstractEventLoop] | None,
    ]
    _completed: bool
    _connection_context: Any
    _origin: str
    _span: Any
    _start_ns: int

    def __init__(self) -> None:
        raise TypeError("TargetTurn instances are created by Session.start_target_turn")

    @classmethod
    def _create(
        cls,
        connection_context: Any,
        *,
        origin: TargetTurnOrigin | str,
        input_count: int,
        trigger_context: SpanContext | None = None,
    ) -> "TargetTurn":
        normalized_origin = _normalize_enum(TargetTurnOrigin, origin, "origin")
        minimum = 0 if normalized_origin in {TargetTurnOrigin.PROACTIVE, TargetTurnOrigin.OTHER} else 1
        validated_input_count = _validate_count(input_count, "input_count", minimum=minimum)
        if normalized_origin is TargetTurnOrigin.PROACTIVE and validated_input_count != 0:
            raise ValueError("input_count must be zero for proactive target turns")
        links: tuple[Link, ...] = ()
        if trigger_context is not None:
            if not isinstance(trigger_context, _SPAN_CONTEXT_TYPE):
                raise TypeError("trigger_context must be a SpanContext or None")
            if not trigger_context.is_valid:
                raise ValueError("trigger_context must contain a valid trace ID and span ID")
            try:
                safe_trigger = SpanContext(
                    trace_id=trigger_context.trace_id,
                    span_id=trigger_context.span_id,
                    is_remote=trigger_context.is_remote,
                    trace_flags=trigger_context.trace_flags,
                    trace_state=TraceState(),
                )
                links = (Link(safe_trigger),)
            except BaseException:  # pylint: disable=broad-exception-caught
                links = ()

        instance = object.__new__(cls)
        instance._activated = False
        instance._activation_attachment = None
        instance._activation_task = None
        instance._active = False
        instance._completed = False
        instance._connection_context = connection_context
        try:
            loop_reference = weakref.ref(asyncio.get_running_loop())
        except RuntimeError:
            loop_reference = None
        instance._affinity = (threading.get_ident(), loop_reference)
        instance._origin = normalized_origin.value
        instance._span = None
        instance._start_ns = time.monotonic_ns()
        if connection_context is not None and _TRACER is not None:
            try:
                instance._span = _TRACER.start_span(
                    "invoke_agent",
                    context=connection_context,
                    kind=otel_trace.SpanKind.INTERNAL,
                    attributes={
                        "gen_ai.operation.name": "invoke_agent",
                        "turn.origin": normalized_origin.value,
                        "bridge.input.count": validated_input_count,
                    },
                    links=links,
                )
            except BaseException:  # pylint: disable=broad-exception-caught
                instance._span = None
        return instance

    @property
    def is_completed(self) -> bool:
        """Whether the first valid completion has committed.

        :return: Whether this target turn is complete.
        :rtype: bool
        """
        return self._completed

    def activate(self) -> ContextManager[None]:
        """Return the single lexical activation scope for this target turn.

        The application must await every task that creates target descendants
        before leaving this scope. The scope must exit in the task that entered it.

        :return: A synchronous context manager that makes this target turn current.
        :rtype: contextlib.AbstractContextManager[None]
        """
        return _TargetTurnActivation(self)

    def complete(
        self,
        *,
        outcome: TargetTurnOutcome | str,
        response_id: str | None = None,
        output_item_count: int | None = None,
    ) -> None:
        """Complete the target turn with application-owned terminal facts.

        Validation depends on ``outcome``:

        * ``TargetTurnOutcome.RESPONSE`` requires ``response_id`` and an
            ``output_item_count`` of at least 1.
        * ``TargetTurnOutcome.NONE`` requires no ``response_id`` and an
            ``output_item_count`` equal to 0.
        * Other outcomes allow both values to be omitted. If
            ``output_item_count`` is positive, ``response_id`` is required.

        :keyword outcome: First immutable terminal outcome.
        :paramtype outcome: TargetTurnOutcome or str
        :keyword response_id: Real response identifier subject to the outcome rules above.
        :paramtype response_id: str or None
        :keyword output_item_count: Completed output item count subject to the outcome rules above.
        :paramtype output_item_count: int or None
        """
        self._check_affinity()
        if self._completed:
            return
        if self._active:
            raise RuntimeError("Target turn cannot complete while its activation is active")

        normalized_outcome, validated_response_id, validated_output_count = _validate_completion(
            outcome, response_id, output_item_count
        )

        self._completed = True
        span = self._span
        error_type = (
            normalized_outcome.value
            if normalized_outcome
            in {
                TargetTurnOutcome.TIMEOUT,
                TargetTurnOutcome.ERROR,
                TargetTurnOutcome.TRANSPORT_ERROR,
                TargetTurnOutcome.ABANDONED,
            }
            else None
        )
        end_monotonic_ns = time.monotonic_ns()
        end_time_ns = time.time_ns()
        try:
            if span is not None:
                attributes: dict[str, Any] = {"bridge.outcome": normalized_outcome.value}
                if validated_output_count is not None:
                    attributes["bridge.output.item_count"] = validated_output_count
                if validated_response_id is not None and _is_safe_telemetry_response_id(validated_response_id):
                    attributes["gen_ai.response.id"] = validated_response_id
                if error_type is not None:
                    attributes["error.type"] = normalized_outcome.value
                for name, value in attributes.items():
                    try:
                        span.set_attribute(name, value)
                    except BaseException:  # pylint: disable=broad-exception-caught
                        pass
                if error_type is not None:
                    try:
                        span.set_status(otel_trace.StatusCode.ERROR)
                    except BaseException:  # pylint: disable=broad-exception-caught
                        pass
                try:
                    span.end(end_time=end_time_ns)
                except BaseException:  # pylint: disable=broad-exception-caught
                    pass
        finally:
            _record_target_duration(
                self._start_ns,
                self._origin,
                normalized_outcome.value,
                error_type,
                end_ns=end_monotonic_ns,
            )
            self._span = None
            self._connection_context = None
            self._activation_task = None
            self._activation_attachment = None

    def _check_affinity(self) -> None:
        thread_id, loop_reference = self._affinity
        if threading.get_ident() != thread_id:
            raise RuntimeError("Target turn must be used on its creation thread")
        if loop_reference is not None:
            try:
                current_loop = asyncio.get_running_loop()
            except RuntimeError as exc:
                raise RuntimeError("Target turn must be used on its creation event loop") from exc
            if current_loop is not loop_reference():
                raise RuntimeError("Target turn must be used on its creation event loop")

    def _enter_activation(self) -> None:
        self._check_affinity()
        if self._completed:
            raise RuntimeError("Target turn has already completed")
        if self._activated:
            raise RuntimeError("Target turn has already been activated")
        self._activated = True
        self._active = True
        self._activation_task = asyncio.current_task() if self._affinity[1] is not None else None
        connection_attachment = _attach_context(self._connection_context)
        target_attachment = None
        if connection_attachment is not None and self._span is not None:
            try:
                target_context = otel_trace.set_span_in_context(self._span, self._connection_context)
            except BaseException:  # pylint: disable=broad-exception-caught
                target_context = None
            if target_context is not None:
                target_attachment = _attach_context(target_context)
        self._activation_attachment = (connection_attachment, target_attachment)

    def _exit_activation(self) -> None:
        if self._affinity[1] is not None and asyncio.current_task() is not self._activation_task:
            raise RuntimeError("Target turn activation must exit in the task that entered it")
        if self._activation_attachment is not None:
            connection_attachment, target_attachment = self._activation_attachment
            _reset_context(target_attachment)
            _reset_context(connection_attachment)
        self._activation_attachment = None
        self._activation_task = None
        self._active = False
