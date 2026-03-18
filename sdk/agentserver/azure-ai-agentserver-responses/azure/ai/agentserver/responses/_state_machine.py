"""Lifecycle event state machine for Responses streaming."""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping


_TERMINAL_EVENT_TYPES = {"response.completed", "response.failed", "response.incomplete"}
_OUTPUT_ITEM_EVENT_TYPES = {
    "response.output_item.added",
    "response.output_item.delta",
    "response.output_item.done",
}
_EVENT_STAGES = {
    "response.created": 0,
    "response.in_progress": 1,
    "response.completed": 2,
    "response.failed": 2,
    "response.incomplete": 2,
}


class LifecycleStateMachineError(ValueError):
    """Raised when lifecycle events violate ordering constraints."""


def validate_response_event_stream(events: list[Mapping[str, Any]]) -> None:
    """Validate lifecycle and output-item event ordering for a response stream."""
    if not events:
        raise LifecycleStateMachineError("event stream cannot be empty")

    first_type = events[0].get("type")
    if first_type != "response.created":
        raise LifecycleStateMachineError("first lifecycle event must be response.created")

    terminal_count = 0
    last_stage = -1
    terminal_seen = False
    added_indexes: set[int] = set()
    done_indexes: set[int] = set()

    for raw_event in events:
        event_type = raw_event.get("type")
        if not isinstance(event_type, str) or not event_type:
            raise LifecycleStateMachineError("each lifecycle event must include a non-empty type")

        stage = _EVENT_STAGES.get(event_type)
        if stage is not None:
            if stage < last_stage:
                raise LifecycleStateMachineError("lifecycle events are out of order")
            if event_type in _TERMINAL_EVENT_TYPES:
                terminal_count += 1
                if terminal_count > 1:
                    raise LifecycleStateMachineError("multiple terminal lifecycle events are not allowed")
                terminal_seen = True
            last_stage = stage
            continue

        if event_type not in _OUTPUT_ITEM_EVENT_TYPES:
            continue

        if last_stage < 0:
            raise LifecycleStateMachineError("output item events cannot appear before response.created")
        if terminal_seen:
            raise LifecycleStateMachineError("output item events cannot appear after terminal lifecycle event")

        payload = raw_event.get("payload")
        payload_mapping = payload if isinstance(payload, Mapping) else {}
        output_index_raw = payload_mapping.get("output_index", 0)
        output_index = output_index_raw if isinstance(output_index_raw, int) and output_index_raw >= 0 else 0

        if event_type == "response.output_item.added":
            if output_index in done_indexes:
                raise LifecycleStateMachineError("cannot add output item after it has been marked done")
            added_indexes.add(output_index)
            continue

        if output_index not in added_indexes:
            raise LifecycleStateMachineError("output item delta/done requires a preceding output_item.added")

        if event_type == "response.output_item.done":
            done_indexes.add(output_index)
            continue

        if event_type == "response.output_item.delta" and output_index in done_indexes:
            raise LifecycleStateMachineError("output item delta cannot appear after output_item.done")


def normalize_lifecycle_events(
    *, response_id: str, events: list[Mapping[str, Any]], default_model: str | None = None
) -> list[dict[str, Any]]:
    """Normalize lifecycle events with ordering and terminal-state guarantees."""
    normalized: list[dict[str, Any]] = []

    for raw_event in events:
        event_type = raw_event.get("type")
        if not isinstance(event_type, str) or not event_type:
            raise LifecycleStateMachineError("each lifecycle event must include a non-empty type")

        payload_raw = raw_event.get("payload")
        payload = deepcopy(payload_raw) if isinstance(payload_raw, Mapping) else {}

        payload.setdefault("id", response_id)
        payload.setdefault("object", "response")
        if default_model is not None:
            payload.setdefault("model", default_model)

        normalized.append({"type": event_type, "payload": payload})

    if not normalized:
        normalized = [
            {
                "type": "response.created",
                "payload": {
                    "id": response_id,
                    "object": "response",
                    "status": "queued",
                    "model": default_model,
                },
            }
        ]

    validate_response_event_stream(normalized)

    terminal_count = sum(1 for event in normalized if event["type"] in _TERMINAL_EVENT_TYPES)

    if terminal_count == 0:
        normalized.append(
            {
                "type": "response.failed",
                "payload": {
                    "id": response_id,
                    "object": "response",
                    "status": "failed",
                    "model": default_model,
                },
            }
        )

    return normalized
