# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Internal helper functions extracted from ResponseEventStream.

These are pure or near-pure functions that operate on event dicts and wire
payloads. They carry no mutable state of their own.
"""

from __future__ import annotations

from collections.abc import MutableMapping
from copy import deepcopy
from datetime import datetime
from types import GeneratorType
from typing import Any, cast

from azure.ai.agentserver.responses import models as response_models
from azure.ai.agentserver.responses.models import AgentReference

# Event types whose ``response`` field is a full Response snapshot.
# Only these events should carry id/response_id/object/agent_reference/model.
_RESPONSE_SNAPSHOT_EVENT_TYPES: frozenset[str] = frozenset(
    {
        "response.queued",
        "response.created",
        "response.in_progress",
        "response.completed",
        "response.failed",
        "response.incomplete",
    }
)

_DEFAULT_AGENT_REFERENCE: dict[str, str] = {
    "type": "agent_reference",
    "name": "server-default-agent",
}


# ---------------------------------------------------------------------------
# Pure / near-pure helpers
# ---------------------------------------------------------------------------


def construct_event_model(wire_dict: dict[str, Any]) -> response_models.ResponseStreamEvent:
    """Return a copied ``ResponseStreamEvent`` wire payload.

    :param wire_dict: A wire-format event dict.
    :type wire_dict: dict[str, Any]
    :returns: A copied event wire payload.
    :rtype: ~azure.ai.agentserver.responses.models.ResponseStreamEvent
    """
    return cast(response_models.ResponseStreamEvent, deepcopy(wire_dict))


def enum_value(value: Any) -> Any:
    """Return the ``.value`` of an enum member, or the value itself.

    :param value: An enum member or a plain value.
    :type value: Any
    :returns: The ``.value`` attribute if present, otherwise *value* unchanged.
    :rtype: Any
    """
    return getattr(value, "value", value)


def coerce_model_mapping(value: Any) -> dict[str, Any] | None:
    """Normalise a wire mapping or ``None`` to a plain dict copy.

    :param value: A wire mapping, or ``None``.
    :type value: Any
    :returns: A deep-copied plain dict, or ``None`` if *value* is ``None`` or not coercible.
    :rtype: dict[str, Any] | None
    """
    if value is None:
        return None
    if isinstance(value, dict):
        return deepcopy(value)
    return None


def response_agent_reference(agent_reference: AgentReference | dict[str, Any] | None) -> dict[str, Any]:
    """Return a valid response-level agent reference wire payload.

    An empty dict is still used elsewhere as the sentinel for "do not stamp
    output items", but response snapshots must carry a valid agent_reference
    object.

    :param agent_reference: The candidate agent reference payload.
    :type agent_reference: AgentReference | dict[str, Any] | None
    :returns: A response-level agent reference payload.
    :rtype: dict[str, Any]
    """
    if isinstance(agent_reference, MutableMapping) and agent_reference:
        return dict(deepcopy(agent_reference))
    return deepcopy(_DEFAULT_AGENT_REFERENCE)


def is_default_agent_reference(value: Any) -> bool:
    return (
        isinstance(value, MutableMapping)
        and value.get("type") == _DEFAULT_AGENT_REFERENCE["type"]
        and value.get("name") == _DEFAULT_AGENT_REFERENCE["name"]
        and not value.get("version")
    )


def materialize_wire_payload(value: Any) -> Any:
    """Recursively resolve generators/tuples to plain lists/dicts.

    :param value: A nested structure that may contain generators or tuples.
    :type value: Any
    :returns: A fully materialized structure using only dicts and lists.
    :rtype: Any
    """
    if isinstance(value, dict):
        return {key: materialize_wire_payload(item) for key, item in value.items()}
    if isinstance(value, list):
        return [materialize_wire_payload(item) for item in value]
    if isinstance(value, tuple):
        return [materialize_wire_payload(item) for item in value]
    if isinstance(value, GeneratorType):
        return [materialize_wire_payload(item) for item in value]
    if isinstance(value, datetime):
        return int(value.timestamp())
    return value


def apply_common_defaults(
    events: list[response_models.ResponseStreamEvent],
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
    ``"response"`` key.

    **S-038**: ``agent_session_id`` is forcibly stamped (not ``setdefault``)
    on every ``response.*`` event so the resolved session ID is always
    present regardless of what the handler emits.

    **S-040**: ``conversation`` is forcibly stamped on every ``response.*``
    event so the resolved conversation round-trips on all lifecycle events.

    :param events: The list of event payloads to mutate.
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
        snapshot_dict = cast(dict[str, Any], snapshot)
        snapshot_dict.setdefault("id", response_id)
        snapshot_dict.setdefault("response_id", response_id)
        snapshot_dict.setdefault("object", "response")
        existing_agent_reference = snapshot_dict.get("agent_reference")
        if (
            not isinstance(existing_agent_reference, MutableMapping)
            or not existing_agent_reference
            or (is_default_agent_reference(existing_agent_reference) and bool(agent_reference))
        ):
            snapshot_dict["agent_reference"] = response_agent_reference(agent_reference)
        if model is not None:
            snapshot_dict.setdefault("model", model)
        # S-038: forcibly stamp session ID on every response.* event
        if agent_session_id is not None:
            snapshot_dict["agent_session_id"] = agent_session_id
        # S-040: forcibly stamp conversation on every response.* event
        if conversation_id is not None:
            snapshot_dict["conversation"] = {"id": conversation_id}


def track_completed_output_item(
    response: response_models.ResponseObject,
    event: response_models.ResponseStreamEvent,
) -> None:
    """When an output-item-done event arrives, persist the item on the response.

    Checks if the event is of type ``response.output_item.done`` and, if so,
    stores the item at the appropriate index in ``response.output``.

    :param response: The response envelope to which the completed item is attached.
    :type response: ~azure.ai.agentserver.responses.models.ResponseObject
    :param event: The event to inspect.
    :type event: ResponseStreamEvent
    :rtype: None
    """
    if event.get("type") != "response.output_item.done":
        return

    output_index = event.get("output_index")
    item_raw = event.get("item")

    if not isinstance(output_index, int) or output_index < 0 or item_raw is None:
        return

    if isinstance(item_raw, dict):
        item_dict = deepcopy(item_raw)
    else:
        return

    output_items: list[Any] = response.get("output") if isinstance(response.get("output"), list) else []
    if not isinstance(response.get("output"), list):
        response["output"] = output_items

    while len(output_items) <= output_index:
        output_items.append(None)

    output_items[output_index] = deepcopy(item_dict)


def coerce_usage(
    usage: response_models.ResponseUsage | dict[str, Any] | None,
) -> dict[str, Any] | None:
    """Normalise a usage value to a plain wire dict.

    :param usage: A usage dict or ``None``.
    :type usage: ~azure.ai.agentserver.responses.models.ResponseUsage | dict[str, Any] | None
    :returns: A usage dict, or ``None`` if *usage* is ``None``.
    :rtype: dict[str, Any] | None
    :raises TypeError: If *usage* is not a dict.
    """
    if usage is None:
        return None
    if isinstance(usage, dict):
        return dict(deepcopy(usage))
    raise TypeError("usage must be a dict")


def extract_response_fields(
    response: response_models.ResponseObject,
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
        dict(deepcopy(agent_reference)) if isinstance(agent_reference, MutableMapping) else None
    )
    model = payload.get("model")
    model_str = model if isinstance(model, str) and model else None
    return agent_ref, model_str
