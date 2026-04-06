# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Event coercion, defaults application, and snapshot extraction helpers."""

from __future__ import annotations

from copy import deepcopy
from typing import Any, AsyncIterator

from . import _internals
from ._event_stream import ResponseEventStream
from ._internals import _RESPONSE_SNAPSHOT_EVENT_TYPES
from ._sse import encode_sse_payload
from ..models import _generated as generated_models

EVENT_TYPE = generated_models.ResponseStreamEventType


def _build_events(
    response_id: str,
    *,
    include_progress: bool,
    agent_reference: dict[str, Any],
    model: str | None,
) -> list[dict[str, Any]]:
    """Build a minimal lifecycle event sequence for a response.

    :param response_id: Unique identifier for the response.
    :type response_id: str
    :keyword include_progress: Whether to include an ``in_progress`` event.
    :keyword type include_progress: bool
    :keyword agent_reference: Agent reference metadata dict.
    :keyword type agent_reference: dict[str, Any]
    :keyword model: Optional model identifier.
    :keyword type model: str | None
    :returns: A list of event dicts containing created and completed (and optionally in_progress) events.
    :rtype: list[dict[str, Any]]
    """
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
    """Encode a list of event dicts as SSE-formatted strings.

    :param events: The event dicts to encode.
    :type events: list[dict[str, Any]]
    :returns: An async iterator yielding SSE-formatted strings.
    :rtype: AsyncIterator[str]
    """
    for event in events:
        yield encode_sse_payload(event["type"], event["payload"])


def _coerce_handler_event(handler_event: Any) -> dict[str, Any]:
    """Coerce a handler event to a normalized ``{"type": ..., "payload": ...}`` dict.

    :param handler_event: The event to normalize (dict or model with ``as_dict()``).
    :type handler_event: Any
    :returns: A normalized event dict with ``type`` and ``payload`` keys.
    :rtype: dict[str, Any]
    :raises TypeError: If the event is not a dict or a model with ``as_dict()``.
    :raises ValueError: If the event does not include a non-empty ``type``.
    """
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
    agent_session_id: str | None = None,
) -> dict[str, Any]:
    """Apply response-level defaults to an event payload.

    For lifecycle events whose payload is a ``Response`` snapshot
    (``response.created``, ``response.queued``, ``response.in_progress``,
    ``response.completed``, ``response.failed``, ``response.incomplete``),
    stamps ``id``, ``response_id``, ``object``, ``agent_reference``,
    ``model``, and ``agent_session_id`` using ``setdefault`` so
    handler-supplied values are not overwritten (except
    ``agent_session_id`` which is forcibly stamped per S-048).
    For all other event types the payload is left untouched — those events have
    different schemas per the contract and do not carry these fields.

    ``sequence_number`` is always applied (or removed) regardless of event type,
    because it lives on the ``ResponseStreamEvent`` base class.

    :param event: The event dict to enrich.
    :type event: dict[str, Any]
    :keyword response_id: Response ID to stamp in lifecycle-event payloads.
    :keyword type response_id: str
    :keyword agent_reference: Agent reference metadata dict.
    :keyword type agent_reference: dict[str, Any]
    :keyword model: Optional model identifier.
    :keyword type model: str | None
    :keyword sequence_number: Optional sequence number to set; removed if ``None``.
    :keyword type sequence_number: int | None
    :keyword agent_session_id: Resolved session ID (S-048).
    :keyword type agent_session_id: str | None
    :returns: A deep copy of the event with defaults applied.
    :rtype: dict[str, Any]
    """
    normalized = event  # caller (_coerce_handler_event) already deep-copied
    # Delegate lifecycle-event stamping to the canonical implementation in _internals.
    _internals.apply_common_defaults(
        [normalized],
        response_id=response_id,
        agent_reference=agent_reference if agent_reference else {},
        model=model,
        agent_session_id=agent_session_id,
    )
    payload = normalized.get("payload")
    if not isinstance(payload, dict):
        payload = {}
        normalized["payload"] = payload
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
    agent_session_id: str | None = None,
) -> dict[str, Any]:
    """Extract the latest response snapshot payload from a list of events.

    Scans events in reverse for the most recent response-level lifecycle event
    and returns its payload enriched with defaults. Falls back to building a
    synthetic completed lifecycle if no snapshot event is found.

    :param events: The event stream to search.
    :type events: list[dict[str, Any]]
    :keyword response_id: Response ID for default stamping.
    :keyword type response_id: str
    :keyword agent_reference: Agent reference metadata dict.
    :keyword type agent_reference: dict[str, Any]
    :keyword model: Optional model identifier.
    :keyword type model: str | None
    :keyword remove_sequence_number: Whether to strip ``sequence_number`` from the result.
    :keyword type remove_sequence_number: bool
    :keyword agent_session_id: Resolved session ID (S-048).
    :keyword type agent_session_id: str | None
    :returns: A dict representing the response snapshot payload.
    :rtype: dict[str, Any]
    """
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
            # S-048: forcibly stamp session ID on snapshot
            if agent_session_id is not None:
                snapshot["agent_session_id"] = agent_session_id
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
    # S-048: forcibly stamp session ID on fallback snapshot
    if agent_session_id is not None:
        fallback_payload["agent_session_id"] = agent_session_id
    if remove_sequence_number:
        fallback_payload.pop("sequence_number", None)
    return fallback_payload
