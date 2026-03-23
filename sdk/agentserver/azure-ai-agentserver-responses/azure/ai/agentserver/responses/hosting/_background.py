# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Background execution helpers for non-stream responses."""

from __future__ import annotations

import asyncio  # pylint: disable=do-not-import-asyncio
from copy import deepcopy
from typing import Any

from .._handlers import RuntimeResponseContext
from ..streaming._helpers import (
    _build_events,
    _coerce_handler_event,
    _apply_stream_event_defaults,
    _extract_response_snapshot_from_events,
)
from ._runtime_state import _ExecutionRecord


async def _run_background_non_stream(
    *,
    create_async: Any,
    parsed: Any,
    context: RuntimeResponseContext,
    cancellation_signal: asyncio.Event,
    record: _ExecutionRecord,
    response_id: str,
    agent_reference: dict[str, Any],
    model: str | None,
) -> None:
    """Execute a non-stream handler in the background and update the execution record.

    Collects handler events, builds the response payload, and transitions the
    record status to ``completed``, ``failed``, or ``cancelled``.

    :keyword create_async: The handler's async generator callable.
    :keyword type create_async: Any
    :keyword parsed: Parsed ``CreateResponse`` model instance.
    :keyword type parsed: Any
    :keyword context: Runtime response context for this request.
    :keyword type context: RuntimeResponseContext
    :keyword cancellation_signal: Event signalling that cancellation was requested.
    :keyword type cancellation_signal: asyncio.Event
    :keyword record: The mutable execution record to update.
    :keyword type record: _ExecutionRecord
    :keyword response_id: The response ID for this execution.
    :keyword type response_id: str
    :keyword agent_reference: Normalized agent reference dictionary.
    :keyword type agent_reference: dict[str, Any]
    :keyword model: Model name, or ``None``.
    :keyword type model: str | None
    :return: None
    :rtype: None
    """
    record.status = "in_progress"
    handler_events: list[dict[str, Any]] = []

    try:
        async for handler_event in create_async(parsed, context, cancellation_signal):
            if cancellation_signal.is_set():
                record.status = "cancelled"
                return

            coerced = _coerce_handler_event(handler_event)
            normalized = _apply_stream_event_defaults(
                coerced,
                response_id=response_id,
                agent_reference=agent_reference,
                model=model,
                sequence_number=None,
            )
            handler_events.append(normalized)
    except Exception:  # pylint: disable=broad-exception-caught
        if record.status != "cancelled":
            record.status = "failed"
            record.response_payload = {
                "id": response_id,
                "response_id": response_id,
                "agent_reference": deepcopy(agent_reference),
                "object": "response",
                "status": "failed",
                "model": model,
                "output": [],
                "created_at": context.created_at,
                "error": {"code": "server_error", "message": "An internal server error occurred."},
            }
        return

    if cancellation_signal.is_set():
        record.status = "cancelled"
        return

    events = handler_events if handler_events else _build_events(
        response_id,
        include_progress=True,
        agent_reference=agent_reference,
        model=model,
    )
    response_payload = _extract_response_snapshot_from_events(
        events,
        response_id=response_id,
        agent_reference=agent_reference,
        model=model,
        remove_sequence_number=True,
    )

    resolved_status = response_payload.get("status")
    record.response_payload = response_payload
    if record.status != "cancelled":
        record.status = resolved_status if isinstance(resolved_status, str) else "completed"


async def _try_execute_background_runner(record: _ExecutionRecord) -> None:
    """Attempt to execute the background runner attached to an execution record.

    This is a one-shot operation: once the runner has been started, subsequent
    calls are no-ops.

    :param record: The execution record whose background runner may be invoked.
    :type record: _ExecutionRecord
    :return: None
    :rtype: None
    """
    if not record.background or record.status in {"completed", "failed", "incomplete", "cancelled"}:
        return

    if record.background_runner is None or record.background_execution_started:
        return

    if record.cancel_signal.is_set():
        record.status = "cancelled"
        return

    runner = record.background_runner
    record.background_execution_started = True
    try:
        await runner()
    finally:
        record.background_runner = None


def _refresh_background_status(record: _ExecutionRecord) -> None:
    """Refresh the status of a background execution record.

    Transitions the record from ``queued`` to ``in_progress`` or ``cancelled``
    based on the current cancellation signal and runner state.

    :param record: The execution record to refresh.
    :type record: _ExecutionRecord
    :return: None
    :rtype: None
    """
    if not record.background or record.status in {"completed", "failed", "incomplete", "cancelled"}:
        return

    if record.background_runner is not None or record.background_execution_started:
        if record.cancel_signal.is_set():
            record.status = "cancelled"
            return

        if record.status == "queued":
            record.status = "in_progress"
        return

    if record.cancel_signal.is_set():
        record.status = "cancelled"
        return

    if record.status == "queued":
        record.status = "in_progress"
