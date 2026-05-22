# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Event coercion, defaults application, and snapshot extraction helpers."""

from __future__ import annotations

from collections.abc import MutableMapping
from copy import deepcopy
from typing import Any, AsyncIterator

from ..models import _generated as generated_models
from ..models._generated import AgentReference
from . import _internals
from ._event_stream import ResponseEventStream
from ._internals import _RESPONSE_SNAPSHOT_EVENT_TYPES
from ._sse import encode_sse_event


def strip_nulls(d: dict) -> dict:
    """Recursively remove keys whose values are ``None`` from a dict.

    Only dict values are recursed into; lists and other containers are
    left untouched so that ``0``, ``False``, ``""``, and ``[]`` are
    preserved.

    :param d: The dictionary to strip.
    :type d: dict
    :returns: A new dictionary with ``None``-valued keys removed.
    :rtype: dict
    """
    return {k: strip_nulls(v) if isinstance(v, dict) else v for k, v in d.items() if v is not None}


def _build_events(
    response_id: str,
    *,
    include_progress: bool,
    agent_reference: AgentReference | dict[str, Any] | None,
    model: str | None,
) -> list[generated_models.ResponseStreamEvent]:
    """Build a minimal lifecycle event sequence for a response.

    Returns ``ResponseStreamEvent`` model instances representing the standard
    lifecycle: ``response.created`` → (optionally) ``response.in_progress`` →
    ``response.completed``.

    :param response_id: Unique identifier for the response.
    :type response_id: str
    :keyword include_progress: Whether to include an ``in_progress`` event.
    :keyword type include_progress: bool
    :keyword agent_reference: Agent reference model or metadata dict.
    :keyword type agent_reference: AgentReference | dict[str, Any]
    :keyword model: Optional model identifier.
    :keyword type model: str | None
    :returns: A list of typed ``ResponseStreamEvent`` model instances.
    :rtype: list[~azure.ai.agentserver.responses.models._generated.ResponseStreamEvent]
    """
    if agent_reference is None:
        ref = None
    elif isinstance(agent_reference, AgentReference):
        ref = agent_reference
    else:
        ref = AgentReference(agent_reference)
    stream = ResponseEventStream(
        response_id=response_id,
        agent_reference=ref,
        model=model,
    )
    stream.emit_created(status="in_progress")
    if include_progress:
        stream.emit_in_progress()
    stream.emit_completed()
    return list(stream._events)  # pylint: disable=protected-access


async def _encode_sse(events: list[generated_models.ResponseStreamEvent]) -> AsyncIterator[str]:
    """Encode a list of ``ResponseStreamEvent`` model instances as SSE-formatted strings.

    :param events: The events to encode.
    :type events: list[ResponseStreamEvent]
    :returns: An async iterator yielding SSE-formatted strings.
    :rtype: AsyncIterator[str]
    """
    for event in events:
        yield encode_sse_event(event)


def _coerce_handler_event(
    handler_event: generated_models.ResponseStreamEvent | dict[str, Any],
) -> generated_models.ResponseStreamEvent:
    """Coerce a handler event to a ``ResponseStreamEvent`` model instance.

    Handlers may yield events in any of these shapes:

    - **Generated event models** (already typed)::

          ResponseCreatedEvent(response={...}, sequence_number=0)

    - **Wire / SSE format** for lifecycle events::

          {"type": "response.created", "response": {"id": "...", "status": "in_progress", ...}, "sequence_number": 0}

    - **Wire / SSE format** for content events::

          {"type": "response.output_text.delta", "output_index": 0, "delta": "Hello", "sequence_number": 3}

    All shapes are normalised to a ``ResponseStreamEvent`` model instance
    for typed internal pipeline processing.

    :param handler_event: The event to normalize (dict or model instance).
    :type handler_event: ResponseStreamEvent | dict[str, Any]
    :returns: A typed ``ResponseStreamEvent`` model instance.
    :rtype: ~azure.ai.agentserver.responses.models._generated.ResponseStreamEvent
    :raises TypeError: If the event is not a dict or a model with ``as_dict()``.
    :raises ValueError: If the event does not include a non-empty ``type``.
    """
    from ._internals import construct_event_model  # pylint: disable=import-outside-toplevel

    # Already a typed model — return a copy via as_dict() round-trip.
    if isinstance(handler_event, generated_models.ResponseStreamEvent):
        return construct_event_model(handler_event.as_dict())

    if isinstance(handler_event, dict):
        event_data = deepcopy(handler_event)
    elif hasattr(handler_event, "as_dict"):
        event_data = handler_event.as_dict()
    else:
        raise TypeError("handler events must be dictionaries or generated event models")

    event_type = event_data.get("type")
    if not isinstance(event_type, str) or not event_type:
        raise ValueError("handler event must include a non-empty 'type'")

    return construct_event_model(event_data)


def _apply_stream_event_defaults(
    event: generated_models.ResponseStreamEvent,
    *,
    response_id: str,
    agent_reference: AgentReference | dict[str, Any],
    model: str | None,
    sequence_number: int | None,
    agent_session_id: str | None = None,
    conversation_id: str | None = None,
) -> generated_models.ResponseStreamEvent:
    """Apply response-level defaults to a ``ResponseStreamEvent`` model instance.

    For lifecycle events whose ``response`` attribute carries a ``Response``
    snapshot, stamps ``id``, ``response_id``, ``object``, ``agent_reference``,
    ``model``, and ``agent_session_id`` using ``setdefault`` so handler-supplied
    values are not overwritten (except ``agent_session_id`` which is forcibly
    stamped per S-038).

    ``sequence_number`` is always applied at the top level of the event,
    because it lives on the ``ResponseStreamEvent`` base class.

    :param event: The event model instance to enrich.
    :type event: ResponseStreamEvent
    :keyword response_id: Response ID to stamp in lifecycle-event payloads.
    :keyword type response_id: str
    :keyword agent_reference: Agent reference model or metadata dict.
    :keyword type agent_reference: AgentReference | dict[str, Any]
    :keyword model: Optional model identifier.
    :keyword type model: str | None
    :keyword sequence_number: Optional sequence number to set; ``None`` leaves it unchanged.
    :keyword type sequence_number: int | None
    :keyword agent_session_id: Resolved session ID (S-038).
    :keyword type agent_session_id: str | None
    :keyword conversation_id: Optional conversation ID to associate with the event.
    :paramtype conversation_id: str | None
    :returns: The event with defaults applied (same object, mutated in-place).
    :rtype: ResponseStreamEvent
    """
    normalized = event  # caller (_coerce_handler_event) already deep-copied
    # Delegate lifecycle-event stamping to the canonical implementation in _internals.
    _internals.apply_common_defaults(
        [normalized],
        response_id=response_id,
        agent_reference=agent_reference if agent_reference else {},
        model=model,
        agent_session_id=agent_session_id,
        conversation_id=conversation_id,
    )
    # Stamp response_id and agent_reference on output items (B20/B21)
    event_type = normalized.get("type", "")
    if event_type in ("response.output_item.added", "response.output_item.done"):
        item = normalized.get("item")
        if isinstance(item, (dict, MutableMapping)):
            item.setdefault("response_id", response_id)
            if agent_reference:
                # Use explicit None check instead of setdefault so that
                # builder items with agent_reference=None are overridden.
                if item.get("agent_reference") is None:
                    item["agent_reference"] = agent_reference

    if sequence_number is not None:
        normalized["sequence_number"] = sequence_number
    return normalized


def _extract_response_snapshot_from_events(
    events: list[generated_models.ResponseStreamEvent],
    *,
    response_id: str,
    agent_reference: AgentReference | dict[str, Any],
    model: str | None,
    remove_sequence_number: bool = False,
    agent_session_id: str | None = None,
    conversation_id: str | None = None,
) -> dict[str, Any]:
    """Extract the latest response snapshot payload from a list of events.

    Scans events in reverse for the most recent response-level lifecycle event
    and returns its payload enriched with defaults. Falls back to building a
    synthetic completed lifecycle if no snapshot event is found.

    :param events: The event stream to search.
    :type events: list[dict[str, Any]]
    :keyword response_id: Response ID for default stamping.
    :keyword type response_id: str
    :keyword agent_reference: Agent reference model or metadata dict.
    :keyword type agent_reference: AgentReference | dict[str, Any]
    :keyword model: Optional model identifier.
    :keyword type model: str | None
    :keyword remove_sequence_number: Whether to strip ``sequence_number`` from the result.
    :keyword type remove_sequence_number: bool
    :keyword agent_session_id: Resolved session ID (S-038).
    :keyword type agent_session_id: str | None
    :keyword conversation_id: Optional conversation ID to associate with the snapshot.
    :paramtype conversation_id: str | None
    :returns: A dict representing the response snapshot payload.
    :rtype: dict[str, Any]
    """
    for event in reversed(events):
        event_type = event.get("type")
        snapshot_source = event.get("response")
        if event_type in _RESPONSE_SNAPSHOT_EVENT_TYPES and isinstance(snapshot_source, MutableMapping):
            if hasattr(snapshot_source, "as_dict"):
                snapshot = snapshot_source.as_dict()  # type: ignore[union-attr]
            else:
                snapshot = deepcopy(dict(snapshot_source))
            snapshot.setdefault("id", response_id)
            snapshot.setdefault("response_id", response_id)
            snapshot.setdefault("agent_reference", deepcopy(agent_reference))
            snapshot.setdefault("object", "response")
            snapshot.setdefault("output", [])
            if model is not None:
                snapshot.setdefault("model", model)
            # S-038: forcibly stamp session ID on snapshot
            if agent_session_id is not None:
                snapshot["agent_session_id"] = agent_session_id
            # S-040: forcibly stamp conversation on snapshot
            if conversation_id is not None:
                snapshot["conversation"] = {"id": conversation_id}
            if remove_sequence_number:
                snapshot.pop("sequence_number", None)
            return strip_nulls(snapshot)

    fallback_events = _build_events(
        response_id,
        include_progress=True,
        agent_reference=agent_reference,
        model=model,
    )
    # _build_events returns model instances — extract snapshot from the last lifecycle event.
    last_event = fallback_events[-1]
    last_wire = last_event.as_dict()
    fallback_snapshot = dict(last_wire.get("response", {}))
    fallback_snapshot.setdefault("output", [])
    # S-038: forcibly stamp session ID on fallback snapshot
    if agent_session_id is not None:
        fallback_snapshot["agent_session_id"] = agent_session_id
    # S-040: forcibly stamp conversation on fallback snapshot
    if conversation_id is not None:
        fallback_snapshot["conversation"] = {"id": conversation_id}
    if remove_sequence_number:
        fallback_snapshot.pop("sequence_number", None)
    return strip_nulls(fallback_snapshot)
