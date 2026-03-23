# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Lifecycle event state machine for Responses streaming."""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping, MutableMapping, Sequence, cast

from ..models import _generated as generated_models

EVENT_TYPE = generated_models.ResponseStreamEventType
OUTPUT_ITEM_DELTA_EVENT_TYPE = "response.output_item.delta"

_TERMINAL_EVENT_TYPES = {
    EVENT_TYPE.RESPONSE_COMPLETED.value,
    EVENT_TYPE.RESPONSE_FAILED.value,
    EVENT_TYPE.RESPONSE_INCOMPLETE.value,
}
_OUTPUT_ITEM_EVENT_TYPES = {
    EVENT_TYPE.RESPONSE_OUTPUT_ITEM_ADDED.value,
    OUTPUT_ITEM_DELTA_EVENT_TYPE,
    EVENT_TYPE.RESPONSE_OUTPUT_ITEM_DONE.value,
}
_EVENT_STAGES = {
    EVENT_TYPE.RESPONSE_CREATED.value: 0,
    EVENT_TYPE.RESPONSE_IN_PROGRESS.value: 1,
    EVENT_TYPE.RESPONSE_COMPLETED.value: 2,
    EVENT_TYPE.RESPONSE_FAILED.value: 2,
    EVENT_TYPE.RESPONSE_INCOMPLETE.value: 2,
}


class LifecycleStateMachineError(ValueError):
    """Raised when lifecycle events violate ordering constraints."""


def validate_response_event_stream(events: Sequence[Mapping[str, Any]]) -> None:
    """Validate lifecycle and output-item event ordering for a response stream.

    Checks that the first event is ``response.created``, lifecycle events
    are in monotonically non-decreasing order, at most one terminal event
    exists, and output-item events obey added/delta/done constraints.

    :param events: The sequence of event mappings to validate.
    :type events: Sequence[Mapping[str, Any]]
    :rtype: None
    :raises LifecycleStateMachineError: If any ordering or structural constraint is violated.
    """
    if not events:
        raise LifecycleStateMachineError("event stream cannot be empty")

    first_type = events[0].get("type")
    if first_type != EVENT_TYPE.RESPONSE_CREATED.value:
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

        if event_type == EVENT_TYPE.RESPONSE_OUTPUT_ITEM_ADDED.value:
            if output_index in done_indexes:
                raise LifecycleStateMachineError("cannot add output item after it has been marked done")
            added_indexes.add(output_index)
            continue

        if output_index not in added_indexes:
            raise LifecycleStateMachineError("output item delta/done requires a preceding output_item.added")

        if event_type == EVENT_TYPE.RESPONSE_OUTPUT_ITEM_DONE.value:
            done_indexes.add(output_index)
            continue

        if event_type == OUTPUT_ITEM_DELTA_EVENT_TYPE and output_index in done_indexes:
            raise LifecycleStateMachineError("output item delta cannot appear after output_item.done")


def normalize_lifecycle_events(
    *, response_id: str, events: Sequence[Mapping[str, Any]], default_model: str | None = None
) -> list[dict[str, Any]]:
    """Normalize lifecycle events with ordering and terminal-state guarantees.

    Applies ``id`` and ``model`` defaults to each payload, validates ordering,
    and appends a synthetic ``response.failed`` terminal event when none is present.

    :keyword response_id: Response ID to stamp in each event payload.
    :keyword type response_id: str
    :keyword events: The sequence of raw lifecycle event mappings.
    :keyword type events: Sequence[Mapping[str, Any]]
    :keyword default_model: Optional default model identifier to set.
    :keyword type default_model: str | None
    :returns: A list of normalized event dicts with guaranteed terminal event.
    :rtype: list[dict[str, Any]]
    :raises LifecycleStateMachineError: If a lifecycle event has no type or ordering is invalid.
    """
    normalized: list[dict[str, Any]] = []

    for raw_event in events:
        event_type = raw_event.get("type")
        if not isinstance(event_type, str) or not event_type:
            raise LifecycleStateMachineError("each lifecycle event must include a non-empty type")

        payload_raw = raw_event.get("payload")
        payload_raw_dict = deepcopy(payload_raw) if isinstance(payload_raw, Mapping) else {}
        payload = cast(MutableMapping[str, Any], payload_raw_dict)

        payload.setdefault("id", response_id)
        payload.setdefault("object", "response")
        if default_model is not None:
            payload.setdefault("model", default_model)

        normalized.append({"type": event_type, "payload": payload})

    if not normalized:
        normalized = [
            {
                "type": EVENT_TYPE.RESPONSE_CREATED.value,
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
                "type": EVENT_TYPE.RESPONSE_FAILED.value,
                "payload": {
                    "id": response_id,
                    "object": "response",
                    "status": "failed",
                    "model": default_model,
                },
            }
        )

    return normalized
