# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Lifecycle event state machine for Responses streaming."""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping, MutableMapping, Sequence, cast

from ..models import _generated as generated_models

OUTPUT_ITEM_DELTA_EVENT_TYPE = "response.output_item.delta"

_TERMINAL_EVENT_TYPES = {
    generated_models.ResponseStreamEventType.RESPONSE_COMPLETED.value,
    generated_models.ResponseStreamEventType.RESPONSE_FAILED.value,
    generated_models.ResponseStreamEventType.RESPONSE_INCOMPLETE.value,
}
_TERMINAL_TYPE_STATUS: dict[str, set[str]] = {
    "response.completed": {"completed"},
    "response.failed": {"failed", "cancelled"},
    "response.incomplete": {"incomplete"},
}
_OUTPUT_ITEM_EVENT_TYPES = {
    generated_models.ResponseStreamEventType.RESPONSE_OUTPUT_ITEM_ADDED.value,
    OUTPUT_ITEM_DELTA_EVENT_TYPE,
    generated_models.ResponseStreamEventType.RESPONSE_OUTPUT_ITEM_DONE.value,
}
_EVENT_STAGES = {
    generated_models.ResponseStreamEventType.RESPONSE_CREATED.value: 0,
    generated_models.ResponseStreamEventType.RESPONSE_IN_PROGRESS.value: 1,
    generated_models.ResponseStreamEventType.RESPONSE_COMPLETED.value: 2,
    generated_models.ResponseStreamEventType.RESPONSE_FAILED.value: 2,
    generated_models.ResponseStreamEventType.RESPONSE_INCOMPLETE.value: 2,
}


class EventStreamValidator:
    """Incremental validator that maintains state across calls.

    Unlike :func:`_validate_response_event_stream` which re-scans the full
    event list each time, this class validates one event at a time in O(1).
    """

    def __init__(self) -> None:
        self._last_stage: int = -1
        self._terminal_count: int = 0
        self._terminal_seen: bool = False
        self._added_indexes: set[int] = set()
        self._done_indexes: set[int] = set()
        self._event_count: int = 0

    def validate_next(self, event: Mapping[str, Any]) -> None:
        """Validate one new event against accumulated state.

        :param event: The event mapping to validate.
        :type event: Mapping[str, Any]
        :rtype: None
        :raises ValueError: If any ordering or structural constraint is violated.
        """
        event_type = event.get("type")
        if not isinstance(event_type, str) or not event_type:
            raise ValueError("each lifecycle event must include a non-empty type")

        if self._event_count == 0 and event_type != generated_models.ResponseStreamEventType.RESPONSE_CREATED.value:
            raise ValueError("first lifecycle event must be response.created")

        self._event_count += 1

        stage = _EVENT_STAGES.get(event_type)
        if stage is not None:
            if stage < self._last_stage:
                raise ValueError("lifecycle events are out of order")
            if event_type in _TERMINAL_EVENT_TYPES:
                self._terminal_count += 1
                if self._terminal_count > 1:
                    raise ValueError("multiple terminal lifecycle events are not allowed")
                allowed_statuses = _TERMINAL_TYPE_STATUS.get(event_type)
                if allowed_statuses is not None:
                    response = event.get("response")
                    actual_status = response.get("status") if isinstance(response, Mapping) else None
                    if actual_status and actual_status not in allowed_statuses:
                        expected = " or ".join(sorted(allowed_statuses))
                        raise ValueError(
                            f"terminal event '{event_type}' has status '{actual_status}', expected {expected}"
                        )
                self._terminal_seen = True
            self._last_stage = stage
            return

        if event_type not in _OUTPUT_ITEM_EVENT_TYPES:
            return

        if self._last_stage < 0:
            raise ValueError("output item events cannot appear before response.created")
        if self._terminal_seen:
            raise ValueError("output item events cannot appear after terminal lifecycle event")

        output_index_raw = event.get("output_index", 0)
        output_index = output_index_raw if isinstance(output_index_raw, int) and output_index_raw >= 0 else 0

        if event_type == generated_models.ResponseStreamEventType.RESPONSE_OUTPUT_ITEM_ADDED.value:
            if output_index in self._done_indexes:
                raise ValueError("cannot add output item after it has been marked done")
            self._added_indexes.add(output_index)
            return

        if output_index not in self._added_indexes:
            raise ValueError("output item delta/done requires a preceding output_item.added")

        if event_type == generated_models.ResponseStreamEventType.RESPONSE_OUTPUT_ITEM_DONE.value:
            self._done_indexes.add(output_index)
            return

        if event_type == OUTPUT_ITEM_DELTA_EVENT_TYPE and output_index in self._done_indexes:
            raise ValueError("output item delta cannot appear after output_item.done")


def _validate_response_event_stream(events: Sequence[Mapping[str, Any]]) -> None:
    """Validate lifecycle and output-item event ordering for a response stream.

    Checks that the first event is ``response.created``, lifecycle events
    are in monotonically non-decreasing order, at most one terminal event
    exists, and output-item events obey added/delta/done constraints.

    :param events: The sequence of event mappings to validate.
    :type events: Sequence[Mapping[str, Any]]
    :rtype: None
    :raises ValueError: If any ordering or structural constraint is violated.
    """
    if not events:
        raise ValueError("event stream cannot be empty")

    validator = EventStreamValidator()
    for event in events:
        validator.validate_next(event)


def _normalize_lifecycle_events(
    *, response_id: str, events: Sequence[Mapping[str, Any]], default_model: str | None = None
) -> list[dict[str, Any]]:
    """Normalize lifecycle events with ordering and terminal-state guarantees.

    Applies ``id`` and ``model`` defaults to each event, validates ordering,
    and appends a synthetic ``response.failed`` terminal event when none is present.

    :keyword response_id: Response ID to stamp in each event.
    :keyword type response_id: str
    :keyword events: The sequence of raw lifecycle event mappings.
    :keyword type events: Sequence[Mapping[str, Any]]
    :keyword default_model: Optional default model identifier to set.
    :keyword type default_model: str | None
    :returns: A list of normalized event dicts with guaranteed terminal event.
    :rtype: list[dict[str, Any]]
    :raises ValueError: If a lifecycle event has no type or ordering is invalid.
    """
    normalized: list[dict[str, Any]] = []

    for raw_event in events:
        event_type = raw_event.get("type")
        if not isinstance(event_type, str) or not event_type:
            raise ValueError("each lifecycle event must include a non-empty type")

        payload_raw = raw_event.get("response")
        payload_raw_dict = deepcopy(payload_raw) if isinstance(payload_raw, Mapping) else {}
        payload = cast(MutableMapping[str, Any], payload_raw_dict)

        payload.setdefault("id", response_id)
        payload.setdefault("object", "response")
        if default_model is not None:
            payload.setdefault("model", default_model)

        normalized.append({"type": event_type, "response": payload, "sequence_number": 0})

    if not normalized:
        normalized = [
            {
                "type": generated_models.ResponseStreamEventType.RESPONSE_CREATED.value,
                "response": {
                    "id": response_id,
                    "object": "response",
                    "status": "in_progress",
                    "model": default_model,
                },
                "sequence_number": 0,
            }
        ]

    _validate_response_event_stream(normalized)

    terminal_count = sum(1 for event in normalized if event["type"] in _TERMINAL_EVENT_TYPES)

    if terminal_count == 0:
        normalized.append(
            {
                "type": generated_models.ResponseStreamEventType.RESPONSE_FAILED.value,
                "response": {
                    "id": response_id,
                    "object": "response",
                    "status": "failed",
                    "model": default_model,
                },
                "sequence_number": 0,
            }
        )

    return normalized
