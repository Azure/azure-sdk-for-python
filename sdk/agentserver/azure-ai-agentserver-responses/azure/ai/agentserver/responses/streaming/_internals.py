# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Internal helper functions extracted from ResponseEventStream.

These are pure or near-pure functions that operate on event dicts
and generated model objects. They carry no mutable state of their own.
"""

from __future__ import annotations

from collections.abc import Callable, MutableMapping
from copy import deepcopy
from types import GeneratorType
from typing import Any, cast

from ..models import _generated as generated_models
from ..models._generated import AgentReference

# Event types whose ``response`` field is a full Response snapshot.
# Only these events should carry id/response_id/object/agent_reference/model.
_RESPONSE_SNAPSHOT_EVENT_TYPES: frozenset[str] = frozenset(
    {
        generated_models.ResponseStreamEventType.RESPONSE_QUEUED.value,
        generated_models.ResponseStreamEventType.RESPONSE_CREATED.value,
        generated_models.ResponseStreamEventType.RESPONSE_IN_PROGRESS.value,
        generated_models.ResponseStreamEventType.RESPONSE_COMPLETED.value,
        generated_models.ResponseStreamEventType.RESPONSE_FAILED.value,
        generated_models.ResponseStreamEventType.RESPONSE_INCOMPLETE.value,
    }
)


# ---------------------------------------------------------------------------
# Pure / near-pure helpers
# ---------------------------------------------------------------------------


def construct_event_model(wire_dict: dict[str, Any]) -> generated_models.ResponseStreamEvent:
    """Construct a typed ``ResponseStreamEvent`` subclass from a wire-format dict.

    Uses the discriminator-based ``__mapping__`` on the base class for
    polymorphic dispatch.  For example, a dict with ``"type": "response.created"``
    produces a ``ResponseCreatedEvent`` instance.

    :param wire_dict: A wire-format event dict.
    :type wire_dict: dict[str, Any]
    :returns: A typed event model instance.
    :rtype: ~azure.ai.agentserver.responses.models._generated.ResponseStreamEvent
    """
    event_type = wire_dict.get("type", "")
    if isinstance(event_type, str):
        event_class = generated_models.ResponseStreamEvent.__mapping__.get(event_type)
        if event_class is not None:
            # __mapping__ values are classes; the generated type annotation is imprecise.
            constructor = cast(Callable[[dict[str, Any]], generated_models.ResponseStreamEvent], event_class)
            return constructor(wire_dict)
    return generated_models.ResponseStreamEvent(wire_dict)


def enum_value(value: Any) -> Any:
    """Return the ``.value`` of an enum member, or the value itself.

    :param value: An enum member or a plain value.
    :type value: Any
    :returns: The ``.value`` attribute if present, otherwise *value* unchanged.
    :rtype: Any
    """
    return getattr(value, "value", value)


def coerce_model_mapping(value: Any) -> dict[str, Any] | None:
    """Normalise a generated model, dict, or ``None`` to a plain dict copy.

    :param value: A generated model, a dict, or ``None``.
    :type value: Any
    :returns: A deep-copied plain dict, or ``None`` if *value* is ``None`` or not coercible.
    :rtype: dict[str, Any] | None
    """
    if value is None:
        return None
    if isinstance(value, dict):
        return deepcopy(value)
    if hasattr(value, "as_dict"):
        result = value.as_dict()
        if isinstance(result, dict):
            return result
    return None


def materialize_generated_payload(value: Any) -> Any:
    """Recursively resolve generators/tuples to plain lists/dicts.

    :param value: A nested structure that may contain generators or tuples.
    :type value: Any
    :returns: A fully materialized structure using only dicts and lists.
    :rtype: Any
    """
    if isinstance(value, dict):
        return {key: materialize_generated_payload(item) for key, item in value.items()}
    if isinstance(value, list):
        return [materialize_generated_payload(item) for item in value]
    if isinstance(value, tuple):
        return [materialize_generated_payload(item) for item in value]
    if isinstance(value, GeneratorType):
        return [materialize_generated_payload(item) for item in value]
    return value


def apply_common_defaults(
    events: list[generated_models.ResponseStreamEvent],
    *,
    response_id: str,
    agent_reference: AgentReference | dict[str, Any] | None,
    model: str | None,
    agent_session_id: str | None = None,
    conversation_id: str | None = None,
) -> None:
    """Stamp lifecycle event snapshots with response-level defaults.

    Only events whose type is a ``Response`` snapshot
    (``response.queued``, ``response.created``, ``response.in_progress``,
    ``response.completed``, ``response.failed``, ``response.incomplete``)
    receive ``id``, ``response_id``, ``object``, ``agent_reference``,
    ``model``, ``agent_session_id``, and ``conversation`` defaults.  Other
    event types carry different schemas per the contract and are left untouched.

    Events must use wire format where the snapshot is nested under the
    ``"response"`` key (``ResponseStreamEvent`` models or equivalent dicts).

    **S-038**: ``agent_session_id`` is forcibly stamped (not ``setdefault``)
    on every ``response.*`` event so the resolved session ID is always
    present regardless of what the handler emits.

    **S-040**: ``conversation`` is forcibly stamped on every ``response.*``
    event so the resolved conversation round-trips on all lifecycle events.

    :param events: The list of events to mutate (``ResponseStreamEvent`` models).
    :type events: list[ResponseStreamEvent]
    :keyword response_id: Response ID to set as default.
    :keyword type response_id: str
    :keyword agent_reference: Optional agent reference model or metadata dict.
    :keyword type agent_reference: AgentReference | dict[str, Any] | None
    :keyword model: Optional model identifier.
    :keyword type model: str | None
    :keyword agent_session_id: Resolved session ID (S-038).
    :keyword type agent_session_id: str | None
    :keyword conversation_id: Resolved conversation ID (S-040).
    :keyword type conversation_id: str | None
    :rtype: None
    """
    for event in events:
        event_type = event.get("type")
        if event_type not in _RESPONSE_SNAPSHOT_EVENT_TYPES:
            continue
        snapshot = event.get("response")
        if not isinstance(snapshot, MutableMapping):
            continue
        snapshot.setdefault("id", response_id)
        snapshot.setdefault("response_id", response_id)
        snapshot.setdefault("object", "response")
        if agent_reference is not None:
            snapshot.setdefault("agent_reference", deepcopy(agent_reference))
        if model is not None:
            snapshot.setdefault("model", model)
        # S-038: forcibly stamp session ID on every response.* event
        if agent_session_id is not None:
            snapshot["agent_session_id"] = agent_session_id
        # S-040: forcibly stamp conversation on every response.* event
        if conversation_id is not None:
            snapshot["conversation"] = {"id": conversation_id}


def track_completed_output_item(
    response: generated_models.ResponseObject,
    event: generated_models.ResponseStreamEvent,
) -> None:
    """When an output-item-done event arrives, persist the item on the response.

    Checks if the event is of type ``response.output_item.done`` and, if so,
    stores the item at the appropriate index in ``response.output``.

    :param response: The response envelope to which the completed item is attached.
    :type response: ~azure.ai.agentserver.responses.models._generated.Response
    :param event: The event to inspect (``ResponseStreamEvent`` model instance).
    :type event: ResponseStreamEvent
    :rtype: None
    """
    if event.get("type") != generated_models.ResponseStreamEventType.RESPONSE_OUTPUT_ITEM_DONE.value:
        return

    output_index = event.get("output_index")
    item_raw = event.get("item")

    if not isinstance(output_index, int) or output_index < 0 or item_raw is None:
        return

    # Coerce item to a plain dict for the OutputItem constructor
    if hasattr(item_raw, "as_dict"):
        item_dict = item_raw.as_dict()
    elif isinstance(item_raw, dict):
        item_dict = deepcopy(item_raw)
    else:
        return

    output_items: list[Any] = response.output if isinstance(response.output, list) else []
    if not isinstance(response.output, list):
        response.output = output_items

    try:
        typed_item: Any = generated_models.OutputItem._deserialize(item_dict, [])  # pylint: disable=protected-access
    except Exception:  # pylint: disable=broad-exception-caught
        typed_item = deepcopy(item_dict)

    while len(output_items) <= output_index:
        output_items.append(None)

    output_items[output_index] = typed_item


def coerce_usage(
    usage: generated_models.ResponseUsage | dict[str, Any] | None,
) -> generated_models.ResponseUsage | None:
    """Normalise a usage value to a generated ``ResponseUsage`` instance.

    :param usage: A usage dict, a ``ResponseUsage`` model, or ``None``.
    :type usage: ~azure.ai.agentserver.responses.models._generated.ResponseUsage | dict[str, Any] | None
    :returns: A ``ResponseUsage`` instance, or ``None`` if *usage* is ``None``.
    :rtype: ~azure.ai.agentserver.responses.models._generated.ResponseUsage | None
    :raises TypeError: If *usage* is not a dict or a generated ``ResponseUsage`` model.
    """
    if usage is None:
        return None
    if isinstance(usage, dict):
        return generated_models.ResponseUsage(deepcopy(usage))
    if hasattr(usage, "as_dict"):
        return generated_models.ResponseUsage(usage.as_dict())
    raise TypeError("usage must be a dict or a generated ResponseUsage model")


def extract_response_fields(
    response: generated_models.ResponseObject,
) -> tuple[AgentReference | dict[str, Any] | None, str | None]:
    """Pull ``agent_reference`` and ``model`` from a response in one pass.

    :param response: The response envelope to inspect.
    :type response: ~azure.ai.agentserver.responses.models.ResponseObject
    :returns: Tuple of (agent_reference or None, model string or None).
    :rtype: tuple[~azure.ai.agentserver.responses.models.AgentReference | dict[str, Any] | None, str | None]
    """
    payload = coerce_model_mapping(response)
    if not isinstance(payload, dict):
        return None, None
    agent_reference = payload.get("agent_reference")
    agent_ref: AgentReference | dict[str, Any] | None = (
        dict(agent_reference) if isinstance(agent_reference, MutableMapping) else None
    )
    model = payload.get("model")
    model_str = model if isinstance(model, str) and model else None
    return agent_ref, model_str
