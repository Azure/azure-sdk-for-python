"""Runtime domain models for response sessions and stream events."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Literal, Mapping

from .._generated import Response, ResponseStreamEvent

ResponseStatus = Literal["queued", "in_progress", "completed", "failed", "cancelled", "incomplete"]
TerminalResponseStatus = Literal["completed", "failed", "cancelled", "incomplete"]


@dataclass(slots=True)
class ResponseModeFlags:
    """Execution mode flags captured from the create request."""

    stream: bool
    store: bool
    background: bool


@dataclass(slots=True)
class StreamEventRecord:
    """A persisted record for one emitted stream event."""

    sequence_number: int
    event_type: str
    payload: Mapping[str, Any]
    emitted_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def terminal(self) -> bool:
        """Return True when this event is one of the terminal response events."""
        return self.event_type in {
            "response.completed",
            "response.failed",
            "response.cancelled",
            "response.incomplete",
        }

    @classmethod
    def from_generated(cls, event: ResponseStreamEvent, payload: Mapping[str, Any]) -> "StreamEventRecord":
        """Create a stream event record from a generated response stream event model."""
        return cls(sequence_number=event.sequence_number, event_type=event.type, payload=payload)


@dataclass(slots=True)
class ResponseExecution:
    """Lightweight pipeline state for one response execution.

    This type intentionally does not own persisted stream history. Stream replay
    concerns are modeled separately in :class:`StreamReplayState`.
    """

    response_id: str
    mode_flags: ResponseModeFlags
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: datetime | None = None
    status: ResponseStatus = "queued"
    response: Response | None = None
    execution_task: asyncio.Task[Any] | None = None
    cancel_requested: bool = False
    client_disconnected: bool = False
    response_created_seen: bool = False

    def transition_to(self, next_status: ResponseStatus) -> None:
        """Transition this execution to a valid lifecycle status.

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
        """Return whether the execution has reached a terminal state."""
        return self.status in {"completed", "failed", "cancelled", "incomplete"}

    def set_response_snapshot(self, response: Response) -> None:
        """Replace the current response snapshot from handler-emitted events."""
        self.response = response
        self.updated_at = datetime.now(timezone.utc)


@dataclass(slots=True)
class StreamReplayState:
    """Persisted stream replay state for one response identifier."""

    response_id: str
    events: list[StreamEventRecord] = field(default_factory=list)

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

