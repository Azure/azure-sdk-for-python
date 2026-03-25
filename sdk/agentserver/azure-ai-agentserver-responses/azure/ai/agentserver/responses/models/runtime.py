# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Runtime domain models for response sessions and stream events."""

from __future__ import annotations

import asyncio  # pylint: disable=do-not-import-asyncio
from copy import deepcopy
from datetime import datetime, timezone
from typing import Any, Literal, Mapping

from ._generated import Response, ResponseStreamEvent, ResponseStreamEventType

EVENT_TYPE = ResponseStreamEventType

ResponseStatus = Literal["queued", "in_progress", "completed", "failed", "cancelled", "incomplete"]
TerminalResponseStatus = Literal["completed", "failed", "cancelled", "incomplete"]


class ResponseModeFlags:
    """Execution mode flags captured from the create request."""

    def __init__(self, *, stream: bool, store: bool, background: bool) -> None:
        self.stream = stream
        self.store = store
        self.background = background


class StreamEventRecord:
    """A persisted record for one emitted stream event."""

    def __init__(
        self,
        *,
        sequence_number: int,
        event_type: str,
        payload: Mapping[str, Any],
        emitted_at: datetime | None = None,
    ) -> None:
        self.sequence_number = sequence_number
        self.event_type = event_type
        self.payload = payload
        self.emitted_at = emitted_at if emitted_at is not None else datetime.now(timezone.utc)

    @property
    def terminal(self) -> bool:
        """Return True when this event is one of the terminal response events.

        Terminal events are ``response.completed``, ``response.failed``,
        and ``response.incomplete``.

        :returns: True if the event type is terminal, False otherwise.
        :rtype: bool
        """
        return self.event_type in {
            EVENT_TYPE.RESPONSE_COMPLETED.value,
            EVENT_TYPE.RESPONSE_FAILED.value,
            EVENT_TYPE.RESPONSE_INCOMPLETE.value,
        }

    @classmethod
    def from_generated(cls, event: ResponseStreamEvent, payload: Mapping[str, Any]) -> "StreamEventRecord":
        """Create a stream event record from a generated response stream event model.

        :param event: The generated response stream event to convert.
        :type event: ResponseStreamEvent
        :param payload: The serialized payload mapping for the event.
        :type payload: Mapping[str, Any]
        :returns: A new ``StreamEventRecord`` populated from the generated event.
        :rtype: StreamEventRecord
        """
        return cls(sequence_number=event.sequence_number, event_type=event.type, payload=payload)


class ResponseExecution:  # pylint: disable=too-many-instance-attributes
    """Lightweight pipeline state for one response execution.

    This type intentionally does not own persisted stream history. Stream replay
    concerns are modeled separately in :class:`StreamReplayState`.
    """

    def __init__(
        self,
        *,
        response_id: str,
        mode_flags: ResponseModeFlags,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
        completed_at: datetime | None = None,
        status: ResponseStatus = "queued",
        response: Response | None = None,
        execution_task: asyncio.Task[Any] | None = None,
        cancel_requested: bool = False,
        client_disconnected: bool = False,
        response_created_seen: bool = False,
        subject: Any | None = None,
        cancel_signal: asyncio.Event | None = None,
        input_items: list[dict[str, Any]] | None = None,
        previous_response_id: str | None = None,
        response_context: Any | None = None,
    ) -> None:
        self.response_id = response_id
        self.mode_flags = mode_flags
        self.created_at = created_at if created_at is not None else datetime.now(timezone.utc)
        self.updated_at = updated_at if updated_at is not None else datetime.now(timezone.utc)
        self.completed_at = completed_at
        self.status = status
        self.response = response
        self.execution_task = execution_task
        self.cancel_requested = cancel_requested
        self.client_disconnected = client_disconnected
        self.response_created_seen = response_created_seen
        self.subject = subject
        self.cancel_signal = cancel_signal if cancel_signal is not None else asyncio.Event()
        self.input_items: list[dict[str, Any]] = input_items if input_items is not None else []
        self.previous_response_id = previous_response_id
        self.response_context = response_context

    def transition_to(self, next_status: ResponseStatus) -> None:
        """Transition this execution to a valid lifecycle status.

        Updates ``status``, ``updated_at``, and ``completed_at`` (for terminal states).
        Re-entering the current status is a no-op that only refreshes ``updated_at``.

        :param next_status: The target lifecycle status.
        :type next_status: ResponseStatus
        :raises ValueError: If the requested transition is not allowed.
        """
        allowed: dict[ResponseStatus, set[ResponseStatus]] = {
            "queued": {"in_progress", "failed"},
            "in_progress": {"completed", "failed", "cancelled", "incomplete"},
            "completed": set(),
            "failed": set(),
            "cancelled": set(),
            "incomplete": set(),
        }

        if next_status == self.status:
            self.updated_at = datetime.now(timezone.utc)
            return

        if next_status not in allowed[self.status]:
            raise ValueError(f"invalid status transition: {self.status} -> {next_status}")

        self.status = next_status
        now = datetime.now(timezone.utc)
        self.updated_at = now
        if self.is_terminal:
            self.completed_at = now

    @property
    def is_terminal(self) -> bool:
        """Return whether the execution has reached a terminal state.

        :returns: True if the status is one of completed, failed, cancelled, or incomplete.
        :rtype: bool
        """
        return self.status in {"completed", "failed", "cancelled", "incomplete"}

    def set_response_snapshot(self, response: Response) -> None:
        """Replace the current response snapshot from handler-emitted events.

        :param response: The latest response snapshot to store.
        :type response: Response
        """
        self.response = response
        self.updated_at = datetime.now(timezone.utc)

    @property
    def replay_enabled(self) -> bool:
        """SSE replay is only available for background+stream+store responses.

        :returns: True if this execution supports SSE replay.
        :rtype: bool
        """
        return self.mode_flags.stream and self.mode_flags.store and self.mode_flags.background

    @property
    def visible_via_get(self) -> bool:
        """Non-streaming stored responses are retrievable via GET after completion.

        :returns: True if this execution can be retrieved via GET.
        :rtype: bool
        """
        return self.mode_flags.store

    def apply_event(self, normalized: dict[str, Any], all_events: list[dict[str, Any]]) -> None:
        """Apply a normalised stream event — updates self.response and self.status.

        Does nothing if the execution is already ``"cancelled"``.

        :param normalized: The normalised event dictionary (``{"type": ..., "payload": {...}}``).
        :type normalized: dict[str, Any]
        :param all_events: The full ordered list of handler events seen so far
            (used to extract the latest response snapshot).
        :type all_events: list[dict[str, Any]]
        """
        # Lazy imports to avoid circular dependency (models.runtime ← streaming._helpers ← models.__init__)
        from ..streaming._internals import _RESPONSE_SNAPSHOT_EVENT_TYPES  # pylint: disable=import-outside-toplevel
        from ..streaming._helpers import _extract_response_snapshot_from_events  # pylint: disable=import-outside-toplevel

        if self.status == "cancelled":
            return
        event_type = normalized.get("type")
        payload = normalized.get("payload", {})
        if event_type in _RESPONSE_SNAPSHOT_EVENT_TYPES:
            agent_reference = (
                self.response.get("agent_reference") if self.response is not None else {}  # type: ignore[union-attr]
            ) or {}
            model = self.response.get("model") if self.response is not None else None  # type: ignore[union-attr]
            snapshot = _extract_response_snapshot_from_events(
                all_events,
                response_id=self.response_id,
                agent_reference=agent_reference,
                model=model,
            )
            self.set_response_snapshot(Response(snapshot))
            resolved = snapshot.get("status")
            if isinstance(resolved, str):
                self.status = resolved
        elif event_type == EVENT_TYPE.RESPONSE_OUTPUT_ITEM_ADDED.value:
            item = payload.get("item")
            if isinstance(item, dict) and self.response is not None:
                output = self.response.setdefault("output", [])
                if isinstance(output, list):
                    output.append(deepcopy(item))
        elif event_type == EVENT_TYPE.RESPONSE_OUTPUT_ITEM_DONE.value:
            item = payload.get("item")
            output_index = payload.get("output_index")
            if isinstance(item, dict) and isinstance(output_index, int) and self.response is not None:
                output = self.response.get("output", [])
                if isinstance(output, list) and 0 <= output_index < len(output):
                    output[output_index] = deepcopy(item)

    # ------------------------------------------------------------------
    # Compat shims — bridge to _ExecutionRecord attribute names during the
    # Phase 2 → Phase 7 transition.  Remove after Task 7.2.
    # ------------------------------------------------------------------

    # Non-stream background records store their runner in background_runner;
    # ResponseExecution records are always inline-or-task-based.
    background_runner: Any = None
    background_execution_started: bool = False

    @property
    def background(self) -> bool:
        """Compat: return mode_flags.background."""
        return self.mode_flags.background

    @property
    def store(self) -> bool:
        """Compat: return mode_flags.store."""
        return self.mode_flags.store

    @property
    def stream(self) -> bool:
        """Compat: return mode_flags.stream."""
        return self.mode_flags.stream

    @property
    def agent_reference(self) -> dict[str, Any]:
        """Compat: extract agent_reference from the stored response snapshot."""
        if self.response is not None:
            return self.response.get("agent_reference") or {}  # type: ignore[return-value]
        return {}

    @property
    def model(self) -> str | None:
        """Compat: extract model name from the stored response snapshot."""
        if self.response is not None:
            return self.response.get("model")  # type: ignore[return-value]
        return None

    @property
    def response_payload(self) -> dict[str, Any] | None:
        """Compat: return the response snapshot as a plain dict (read-only copy)."""
        if self.response is not None:
            return self.response.as_dict()
        return None

    @response_payload.setter
    def response_payload(self, value: dict[str, Any] | None) -> None:
        """Compat: accept a plain dict and store it as the response snapshot."""
        if isinstance(value, dict):
            self.set_response_snapshot(Response(value))

    def to_snapshot(self) -> dict[str, Any]:
        """Compat: build a normalized response snapshot dict (mirrors _RuntimeState.to_snapshot)."""
        if self.response is not None:
            result: dict[str, Any] = self.response.as_dict()
            result.setdefault("id", self.response_id)
            result.setdefault("response_id", self.response_id)
            result.setdefault("object", "response")
            result["status"] = self.status
            return result
        return {
            "id": self.response_id,
            "response_id": self.response_id,
            "object": "response",
            "status": self.status,
        }


class StreamReplayState:
    """Persisted stream replay state for one response identifier."""

    def __init__(
        self,
        *,
        response_id: str,
        events: list[StreamEventRecord] | None = None,
    ) -> None:
        self.response_id = response_id
        self.events = events if events is not None else []

    def append(self, event: StreamEventRecord) -> None:
        """Append a stream event and enforce replay sequence integrity.

        :param event: The stream event record to append.
        :type event: StreamEventRecord
        :raises ValueError: If the sequence number is not strictly increasing or
            a terminal event has already been recorded.
        """
        if self.events and event.sequence_number <= self.events[-1].sequence_number:
            raise ValueError("stream event sequence numbers must be strictly increasing")

        if self.events and self.events[-1].terminal:
            raise ValueError("cannot append events after a terminal event")

        self.events.append(event)

    @property
    def terminal_event_seen(self) -> bool:
        """Return whether replay state has already recorded a terminal event.

        :returns: True if the last recorded event is terminal, False otherwise.
        :rtype: bool
        """
        return bool(self.events and self.events[-1].terminal)


def build_cancelled_response(
    response_id: str,
    agent_reference: dict[str, Any],
    model: str | None,
    created_at: datetime | None = None,
) -> Response:
    """Build a Response object representing a cancelled terminal state.

    :param response_id: The response identifier.
    :type response_id: str
    :param agent_reference: The agent reference metadata dict.
    :type agent_reference: dict[str, Any]
    :param model: Optional model identifier.
    :type model: str | None
    :param created_at: Optional creation timestamp; defaults to now if omitted.
    :type created_at: datetime | None
    :returns: A Response object with status ``"cancelled"`` and empty output.
    :rtype: Response
    """
    payload: dict[str, Any] = {
        "id": response_id,
        "response_id": response_id,
        "agent_reference": deepcopy(agent_reference),
        "object": "response",
        "status": "cancelled",
        "model": model,
        "output": [],
    }
    if created_at is not None:
        payload["created_at"] = created_at.isoformat()
    return Response(payload)
