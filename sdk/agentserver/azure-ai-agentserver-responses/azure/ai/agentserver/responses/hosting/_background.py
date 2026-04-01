# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Background execution helpers for non-stream responses."""

from __future__ import annotations

import asyncio  # pylint: disable=do-not-import-asyncio
from copy import deepcopy
from typing import Any

from .._response_context import ResponseContext
from ..models import _generated as generated_models
from ..models.runtime import ResponseExecution, build_failed_response
from ..streaming._helpers import (
    _build_events,
    _coerce_handler_event,
    _apply_stream_event_defaults,
    _extract_response_snapshot_from_events,
)


async def _run_background_non_stream(
    *,
    create_async: Any,
    parsed: Any,
    context: ResponseContext,
    cancellation_signal: asyncio.Event,
    record: ResponseExecution,
    response_id: str,
    agent_reference: dict[str, Any],
    model: str | None,
    provider: Any = None,
    store: bool = True,
    agent_session_id: str | None = None,
) -> None:
    """Execute a non-stream handler in the background and update the execution record.

    Collects handler events, builds the response payload, and transitions the
    record status to ``completed``, ``failed``, or ``cancelled``.

    :keyword create_async: The handler's async generator callable.
    :keyword type create_async: Any
    :keyword parsed: Parsed ``CreateResponse`` model instance.
    :keyword type parsed: Any
    :keyword context: Runtime response context for this request.
    :keyword type context: ResponseContext
    :keyword cancellation_signal: Event signalling that cancellation was requested.
    :keyword type cancellation_signal: asyncio.Event
    :keyword record: The mutable execution record to update.
    :keyword type record: ResponseExecution
    :keyword response_id: The response ID for this execution.
    :keyword type response_id: str
    :keyword agent_reference: Normalized agent reference dictionary.
    :keyword type agent_reference: dict[str, Any]
    :keyword model: Model name, or ``None``.
    :keyword type model: str | None
    :keyword provider: Optional persistence provider; when set and ``store`` is ``True``,
        ``update_response_async`` is called after terminal state is reached.
    :keyword type provider: Any
    :keyword store: Whether the response should be persisted via the provider.
    :keyword type store: bool
    :keyword agent_session_id: Resolved session ID (S-048).
    :keyword type agent_session_id: str | None
    :return: None
    :rtype: None
    """
    record.transition_to("in_progress")
    handler_events: list[dict[str, Any]] = []

    try:
        try:
            first_event_processed = False
            async for handler_event in create_async(parsed, context, cancellation_signal):
                if cancellation_signal.is_set():
                    record.transition_to("cancelled")
                    return

                coerced = _coerce_handler_event(handler_event)
                normalized = _apply_stream_event_defaults(
                    coerced,
                    response_id=response_id,
                    agent_reference=agent_reference,
                    model=model,
                    sequence_number=None,
                    agent_session_id=agent_session_id,
                )
                handler_events.append(normalized)
                if not first_event_processed:
                    first_event_processed = True
                    # Set initial response snapshot for POST response body without
                    # changing record.status (transition_to manages status lifecycle)
                    _initial_snapshot = _extract_response_snapshot_from_events(
                        handler_events,
                        response_id=response_id,
                        agent_reference=agent_reference,
                        model=model,
                        agent_session_id=agent_session_id,
                    )
                    record.set_response_snapshot(generated_models.ResponseObject(_initial_snapshot))
                    record.response_created_signal.set()
        except Exception:  # pylint: disable=broad-exception-caught
            if record.status != "cancelled":
                record.set_response_snapshot(
                    build_failed_response(
                        response_id,
                        agent_reference,
                        model,
                        created_at=context.created_at,
                    )
                )
                record.transition_to("failed")
            if not first_event_processed:
                # Mark failure before any events so run_background can return HTTP 500
                record.response_failed_before_events = True
            record.response_created_signal.set()  # unblock run_background on failure
            return

        if cancellation_signal.is_set():
            record.transition_to("cancelled")
            record.response_created_signal.set()  # unblock run_background on cancellation
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
            agent_session_id=agent_session_id,
        )

        resolved_status = response_payload.get("status")
        if record.status != "cancelled":
            record.set_response_snapshot(generated_models.ResponseObject(response_payload))
            record.transition_to(resolved_status if isinstance(resolved_status, str) else "completed")
    finally:
        # Always unblock run_background (idempotent if already set)
        record.response_created_signal.set()
        # Persist terminal state update via provider (bg non-stream: update after runner completes)
        if (
            store
            and provider is not None
            and record.status not in {"cancelled"}
            and record.response is not None
        ):
            try:
                await provider.update_response_async(record.response)
            except Exception:  # pylint: disable=broad-exception-caught
                pass  # best effort


def _refresh_background_status(record: ResponseExecution) -> None:
    """Refresh the status of a background execution record.

    Checks the execution task state and cancellation signal to update the
    record status. Called by GET/DELETE/cancel endpoints to reflect the
    current runner state without triggering execution.

    :param record: The execution record to refresh.
    :type record: ResponseExecution
    :return: None
    :rtype: None
    """
    if not record.mode_flags.background or record.is_terminal:
        return

    if record.cancel_signal.is_set() and not record.is_terminal:
        record.status = "cancelled"
        return

    # execution_task is started immediately in run_background (Task 3.1)
    if record.execution_task is not None and record.execution_task.done():
        if not record.is_terminal:
            if record.execution_task.cancelled():
                record.status = "cancelled"
            else:
                exc = record.execution_task.exception()
                if exc is not None:
                    record.status = "failed"
