# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Private runtime helpers for response execution and replay state."""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime
from typing import TYPE_CHECKING, Any, Mapping, cast

if TYPE_CHECKING:
    from ._generated import AgentReference, ResponseObject
    from .runtime import StreamEventRecord


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


def apply_failed_terminal(base: Mapping[str, Any], *, error: dict[str, Any]) -> dict[str, Any]:
    """Overlay a ``failed`` terminal onto an existing response snapshot."""
    as_dict = getattr(base, "as_dict", None)
    obj = cast("dict[str, Any]", as_dict()) if callable(as_dict) else deepcopy(dict(base))
    obj["status"] = "failed"
    obj["error"] = deepcopy(error)
    obj.pop("completed_at", None)
    return obj


def apply_cancelled_terminal(base: Mapping[str, Any]) -> dict[str, Any]:
    """Overlay a ``cancelled`` terminal onto an existing response snapshot."""
    as_dict = getattr(base, "as_dict", None)
    obj = cast("dict[str, Any]", as_dict()) if callable(as_dict) else deepcopy(dict(base))
    obj["status"] = "cancelled"
    obj["output"] = []
    obj.pop("error", None)
    obj.pop("completed_at", None)
    return obj


def resolve_failed_response(
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
        return cast("ResponseObject", apply_failed_terminal(base, error={"code": error_code, "message": error_message}))
    return _build_failed_response(
        response_id, agent_reference, model, created_at=created_at, error_message=error_message, error_code=error_code
    )


def resolve_cancelled_response(
    base: Mapping[str, Any] | None,
    response_id: str,
    agent_reference: AgentReference | dict[str, Any],
    model: str | None,
    *,
    created_at: datetime | None = None,
) -> ResponseObject:
    """Build a ``cancelled`` terminal, preserving the handler's response object."""
    if base is not None:
        return cast("ResponseObject", apply_cancelled_terminal(base))
    return _build_cancelled_response(response_id, agent_reference, model, created_at=created_at)
