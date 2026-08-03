# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Runtime domain models for response sessions and stream events."""

from __future__ import annotations

import asyncio  # pylint: disable=do-not-import-asyncio
from copy import deepcopy
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any, Literal, Mapping, cast

if TYPE_CHECKING:
    from .._response_context import ResponseContext
    from azure.ai.agentserver.core.streaming import EventStream  # pylint: disable=import-error,no-name-in-module
    from ._generated import AgentReference, OutputItem, ResponseObject, ResponseStreamEvent


ResponseStatus = Literal["queued", "in_progress", "completed", "failed", "cancelled", "incomplete"]
TerminalResponseStatus = Literal["completed", "failed", "cancelled", "incomplete"]


# (Spec 024 Phase 5 — Proposal #6/#11) CancellationReason enum DELETED.
# Cancel causes are now surfaced as independent booleans / events on
# :class:`ResponseContext` (``client_cancelled`` bool, ``shutdown``
# asyncio.Event). Steering pressure manifests as ``cancel.is_set()``
# without any cause boolean — handlers that want to distinguish
# steering from explicit cancel inspect ``client_cancelled`` and
# ``shutdown.is_set()`` after observing ``cancel.is_set()``.


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

        :rtype: bool
        """
        return self.event_type in {
            "response.completed",
            "response.failed",
            "response.incomplete",
        }

    @classmethod
    def from_generated(cls, event: ResponseStreamEvent, payload: Mapping[str, Any]) -> "StreamEventRecord":
        """Create a stream event record from a generated response stream event model.

        :param event: The generated response stream event.
        :type event: ResponseStreamEvent
        :param payload: The event payload mapping.
        :type payload: Mapping[str, Any]
        :returns: A new stream event record.
        :rtype: StreamEventRecord
        """
        return cls(sequence_number=event["sequence_number"], event_type=event["type"], payload=payload)


class ResponseExecution:  # pylint: disable=too-many-instance-attributes
    """Lightweight pipeline state for one response execution.

    This type intentionally does not own persisted stream history.
    """

    def __init__(
        self,
        *,
        response_id: str,
        mode_flags: ResponseModeFlags,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
        completed_at: datetime | None = None,
        status: ResponseStatus = "in_progress",
        response: ResponseObject | None = None,
        execution_task: asyncio.Task[Any] | None = None,
        cancel_requested: bool = False,
        client_disconnected: bool = False,
        response_created_seen: bool = False,
        subject: "EventStream | None" = None,
        cancel_signal: asyncio.Event | None = None,
        input_items: list[OutputItem] | None = None,
        previous_response_id: str | None = None,
        response_context: ResponseContext | None = None,
        initial_model: str | None = None,
        initial_agent_reference: AgentReference | dict[str, Any] | None = None,
        agent_session_id: str | None = None,
        conversation_id: str | None = None,
        user_id_key: str | None = None,
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
        self.input_items: list[OutputItem] = input_items if input_items is not None else []
        self.previous_response_id = previous_response_id
        self.response_context = response_context
        self.initial_model = initial_model
        self.initial_agent_reference = initial_agent_reference or {}
        self.agent_session_id = agent_session_id
        self.conversation_id = conversation_id
        self.user_id_key = user_id_key
        self.response_created_signal: asyncio.Event = asyncio.Event()
        self.response_failed_before_events: bool = False
        self.persistence_failed: bool = False
        self.persistence_exception: Exception | None = None

    def transition_to(self, next_status: ResponseStatus) -> None:
        """Transition this execution to a valid lifecycle status.

        Updates ``status``, ``updated_at``, and ``completed_at`` (for terminal states).
        Re-entering the current status is a no-op that only refreshes ``updated_at``.

        :param next_status: The target lifecycle status.
        :type next_status: ResponseStatus
        :raises ValueError: If the requested transition is not allowed.
        """
        allowed: dict[str, set[ResponseStatus]] = {
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

    def set_response_snapshot(self, response: ResponseObject) -> None:
        """Replace the current response snapshot from handler-emitted events.

        :param response: The latest response snapshot to store.
        :type response: ResponseObject
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

        For background non-stream responses, visibility is deferred until
        ``response.created`` is processed (FR-001: response not accessible
        before the handler emits ``response.created``).

        For non-background responses (Row 3, both stream=F and stream=T),
        visibility is deferred until the handler reaches a terminal status
        — per B16, non-bg in-flight responses are not retrievable. (Spec
        024 Phase 2 bookkeeping unification places the record in
        runtime_state at accept-time so cancellation / shutdown / recovery
        can find it; this property gates GET to preserve B16 semantics.)

        :returns: True if this execution can be retrieved via GET.
        :rtype: bool
        """
        if not self.mode_flags.store:
            return False
        # FR-001: bg non-stream responses are not visible until response.created.
        if self.mode_flags.background and not self.mode_flags.stream:
            return self.response_created_signal.is_set()
        # B16: non-bg responses (stream OR non-stream) are visible only after terminal.
        if not self.mode_flags.background:
            return self.status in ("completed", "failed", "cancelled", "incomplete")
        return True

    def apply_event(self, normalized: ResponseStreamEvent, all_events: list[ResponseStreamEvent]) -> None:
        """Apply a normalised stream event — updates self.response and self.status.

        Does nothing if the execution is already ``"cancelled"``.

        :param normalized: The normalised event (``ResponseStreamEvent`` model instance).
        :type normalized: ResponseStreamEvent
        :param all_events: The full ordered list of handler events seen so far
            (used to extract the latest response snapshot).
        :type all_events: list[ResponseStreamEvent]
        """
        # Lazy imports to avoid circular dependency (models.runtime ← streaming._helpers ← models.__init__)
        from ..streaming._helpers import (
            _extract_response_snapshot_from_events,  # pylint: disable=import-outside-toplevel
        )
        from ..streaming._internals import _RESPONSE_SNAPSHOT_EVENT_TYPES  # pylint: disable=import-outside-toplevel

        if self.status == "cancelled":
            return
        event_type = normalized.get("type")
        if event_type in _RESPONSE_SNAPSHOT_EVENT_TYPES:
            agent_reference: Any = (
                self.response.get("agent_reference") if self.response is not None else {}  # type: ignore[union-attr]
            ) or {}
            model = self.response.get("model") if self.response is not None else None  # type: ignore[union-attr]
            snapshot = _extract_response_snapshot_from_events(
                all_events,
                response_id=self.response_id,
                agent_reference=agent_reference,
                model=model,
            )
            self.set_response_snapshot(cast("ResponseObject", snapshot))
            resolved = snapshot.get("status")
            if isinstance(resolved, str):
                self.status = cast(ResponseStatus, resolved)
        elif event_type == "response.output_item.added":
            item = normalized.get("item")
            if item is not None and self.response is not None:
                item_any = cast(Any, item)
                item_dict = item_any.as_dict() if hasattr(item_any, "as_dict") else item
                if isinstance(item_dict, dict):
                    output = self.response.setdefault("output", [])
                    if isinstance(output, list):
                        cast(list[Any], output).append(deepcopy(item_dict))
        elif event_type == "response.output_item.done":
            item = normalized.get("item")
            output_index = normalized.get("output_index")
            if item is not None and isinstance(output_index, int) and self.response is not None:
                item_any = cast(Any, item)
                item_dict = item_any.as_dict() if hasattr(item_any, "as_dict") else item
                if isinstance(item_dict, dict):
                    output = self.response.get("output", [])
                    if isinstance(output, list) and 0 <= output_index < len(output):
                        cast(list[Any], output)[output_index] = deepcopy(item_dict)

    @property
    def agent_reference(self) -> AgentReference | dict[str, Any]:
        """Extract agent_reference from the stored response snapshot.

        :returns: The agent reference model or dict, or empty dict if no response snapshot is set.
        :rtype: AgentReference | dict[str, Any]
        """
        if self.response is not None:
            return self.response.get("agent_reference") or {}  # type: ignore[return-value]
        return {}

    @property
    def model(self) -> str | None:
        """Extract model name from the stored response snapshot.

        :returns: The model name, or ``None`` if no response snapshot is set.
        :rtype: str | None
        """
        if self.response is not None:
            return self.response.get("model")  # type: ignore[return-value]
        return None


class _StreamReplayState:
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
        """Append a stream event and enforce replay sequence integrity."""
        if self.events and event.sequence_number <= self.events[-1].sequence_number:
            raise ValueError("stream event sequence numbers must be strictly increasing")

        if self.events and self.events[-1].terminal:
            raise ValueError("cannot append events after a terminal event")

        self.events.append(event)

    @property
    def terminal_event_seen(self) -> bool:
        """Return whether replay state has already recorded a terminal event."""
        return bool(self.events and self.events[-1].terminal)


def _build_cancelled_response(
    response_id: str,
    agent_reference: AgentReference | dict[str, Any],
    model: str | None,
    created_at: datetime | None = None,
) -> ResponseObject:
    """Build a Response object representing a cancelled terminal state."""
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
        payload["created_at"] = int(created_at.timestamp())
    return cast("ResponseObject", payload)


def _build_failed_response(
    response_id: str,
    agent_reference: AgentReference | dict[str, Any],
    model: str | None,
    created_at: datetime | None = None,
    error_message: str = "An internal server error occurred.",
    error_code: str = "server_error",
) -> ResponseObject:
    """Build a ResponseObject representing a failed terminal state."""
    payload: dict[str, Any] = {
        "id": response_id,
        "response_id": response_id,
        "agent_reference": deepcopy(agent_reference),
        "object": "response",
        "status": "failed",
        "model": model,
        "output": [],
        "error": {"code": error_code, "message": error_message},
    }
    if created_at is not None:
        payload["created_at"] = int(created_at.timestamp())
    return cast("ResponseObject", payload)


_DEFAULT_FAILED_ERROR_MESSAGE = "An internal server error occurred."


def _apply_failed_terminal(base: Mapping[str, Any], *, error: dict[str, Any]) -> dict[str, Any]:
    """Overlay a ``failed`` terminal onto an existing response snapshot."""
    as_dict = getattr(base, "as_dict", None)
    obj = cast("dict[str, Any]", as_dict()) if callable(as_dict) else deepcopy(dict(base))
    obj["status"] = "failed"
    obj["error"] = deepcopy(error)
    obj.pop("completed_at", None)
    return obj


def _apply_cancelled_terminal(base: Mapping[str, Any]) -> dict[str, Any]:
    """Overlay a ``cancelled`` terminal onto an existing response snapshot."""
    as_dict = getattr(base, "as_dict", None)
    obj = cast("dict[str, Any]", as_dict()) if callable(as_dict) else deepcopy(dict(base))
    obj["status"] = "cancelled"
    obj["output"] = []
    obj.pop("error", None)
    obj.pop("completed_at", None)
    return obj


def _resolve_failed_response(
    base: Mapping[str, Any] | None,
    response_id: str,
    agent_reference: AgentReference | dict[str, Any],
    model: str | None,
    *,
    created_at: datetime | None = None,
    error_code: str = "server_error",
    error_message: str = _DEFAULT_FAILED_ERROR_MESSAGE,
) -> ResponseObject:
    """Build a ``failed`` terminal, preserving the handler's response object."""
    if base is not None:
        return cast(
            "ResponseObject",
            _apply_failed_terminal(base, error={"code": error_code, "message": error_message}),
        )
    return _build_failed_response(
        response_id, agent_reference, model, created_at=created_at, error_message=error_message, error_code=error_code
    )


def _resolve_cancelled_response(
    base: Mapping[str, Any] | None,
    response_id: str,
    agent_reference: AgentReference | dict[str, Any],
    model: str | None,
    *,
    created_at: datetime | None = None,
) -> ResponseObject:
    """Build a ``cancelled`` terminal, preserving the handler's response object."""
    if base is not None:
        return cast("ResponseObject", _apply_cancelled_terminal(base))
    return _build_cancelled_response(response_id, agent_reference, model, created_at=created_at)
