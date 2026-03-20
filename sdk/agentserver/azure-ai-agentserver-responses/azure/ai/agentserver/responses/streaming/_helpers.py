"""Event coercion, defaults application, and snapshot extraction helpers."""

from __future__ import annotations

from copy import deepcopy
from typing import Any, AsyncIterator

from ._event_stream import ResponseEventStream
from ._sse import encode_sse_payload
from ..models import _generated as generated_models

EVENT_TYPE = generated_models.ResponseStreamEventType
_RESPONSE_SNAPSHOT_EVENT_TYPES = {
    EVENT_TYPE.RESPONSE_CREATED.value,
    EVENT_TYPE.RESPONSE_QUEUED.value,
    EVENT_TYPE.RESPONSE_IN_PROGRESS.value,
    EVENT_TYPE.RESPONSE_COMPLETED.value,
    EVENT_TYPE.RESPONSE_FAILED.value,
    EVENT_TYPE.RESPONSE_INCOMPLETE.value,
}


def _build_events(
    response_id: str,
    *,
    include_progress: bool,
    agent_reference: dict[str, Any],
    model: str | None,
) -> list[dict[str, Any]]:
    stream = ResponseEventStream(
        response_id=response_id,
        agent_reference=agent_reference,
        model=model,
    )
    events = [stream.emit_created(status="queued")]
    if include_progress:
        events.append(stream.emit_in_progress())
    events.append(stream.emit_completed())
    return events


async def _encode_sse(events: list[dict[str, Any]]) -> AsyncIterator[str]:
    for event in events:
        yield encode_sse_payload(event["type"], event["payload"])


def _coerce_handler_event(handler_event: Any) -> dict[str, Any]:
    if isinstance(handler_event, dict):
        event_data = deepcopy(handler_event)
    elif hasattr(handler_event, "as_dict"):
        event_data = handler_event.as_dict()
    else:
        raise TypeError("handler events must be dictionaries or generated event models")

    event_type = event_data.get("type")
    if not isinstance(event_type, str) or not event_type:
        raise ValueError("handler event must include a non-empty 'type'")

    payload = event_data.get("payload")
    if isinstance(payload, dict):
        normalized_payload = deepcopy(payload)
    else:
        normalized_payload = {key: deepcopy(value) for key, value in event_data.items() if key != "type"}

    return {"type": event_type, "payload": normalized_payload}


def _apply_stream_event_defaults(
    event: dict[str, Any],
    *,
    response_id: str,
    agent_reference: dict[str, Any],
    model: str | None,
    sequence_number: int | None,
) -> dict[str, Any]:
    normalized = deepcopy(event)
    payload = normalized.get("payload")
    if not isinstance(payload, dict):
        payload = {}
        normalized["payload"] = payload

    payload.setdefault("id", response_id)
    payload.setdefault("response_id", response_id)
    payload.setdefault("object", "response")
    payload.setdefault("agent_reference", deepcopy(agent_reference))
    if model is not None:
        payload.setdefault("model", model)

    if sequence_number is not None:
        payload["sequence_number"] = sequence_number
    else:
        payload.pop("sequence_number", None)
    return normalized


def _extract_response_snapshot_from_events(
    events: list[dict[str, Any]],
    *,
    response_id: str,
    agent_reference: dict[str, Any],
    model: str | None,
    remove_sequence_number: bool = False,
) -> dict[str, Any]:
    for event in reversed(events):
        event_type = event.get("type")
        payload = event.get("payload")
        if event_type in _RESPONSE_SNAPSHOT_EVENT_TYPES and isinstance(payload, dict):
            snapshot = deepcopy(payload)
            snapshot.setdefault("id", response_id)
            snapshot.setdefault("response_id", response_id)
            snapshot.setdefault("agent_reference", deepcopy(agent_reference))
            snapshot.setdefault("object", "response")
            snapshot.setdefault("output", [])
            if model is not None:
                snapshot.setdefault("model", model)
            if remove_sequence_number:
                snapshot.pop("sequence_number", None)
            return snapshot

    fallback_events = _build_events(
        response_id,
        include_progress=True,
        agent_reference=agent_reference,
        model=model,
    )
    fallback_payload = deepcopy(fallback_events[-1]["payload"])
    fallback_payload.setdefault("output", [])
    if remove_sequence_number:
        fallback_payload.pop("sequence_number", None)
    return fallback_payload
