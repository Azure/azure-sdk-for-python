"""Background execution helpers for non-stream responses."""

from __future__ import annotations

import asyncio
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
    except Exception:
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
