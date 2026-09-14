# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Serialization helpers and value types for the Foundry state-store client.

Request and response bodies are typed models generated from a formal
TypeSpec contract (see ``azure.ai.agentserver.core.storage._generated``)
instead of hand-written dataclasses + ad hoc JSON (de)serialization. The
resource/response model names below are re-exported unchanged from that
generated package; this module only adds the thin ``serialize_*`` /
``deserialize_*`` helpers that translate between those models and the raw
JSON bytes/text the HTTP layer sends and receives, plus a couple of
hand-written convenience types (``JSONObject``, ``Order``, ``StateStoreItemKeyPage``) that
have no wire representation of their own.
"""

# Internal serialize/deserialize helpers below intentionally omit per-param docs.
# pylint: disable=docstring-missing-param,docstring-missing-return,docstring-missing-rtype

from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any, Literal, Union

try:
    from typing import TypeAlias
except ImportError:  # pragma: no cover
    from typing_extensions import TypeAlias  # type: ignore[assignment]  # Python <3.10 fallback

from ._generated import (
    CreateItemRequest,
    CreateStateStoreRequest,
    DeletedStateStore,
    DeletedStateStoreItem,
    ListResponseStateStoreItemKey,
    PutItemRequest,
    StateStore,
    StateStoreItem,
    StateStoreItemRef,
    StateStoreItemKey,
    UpdateStateStoreRequest,
)
from ._json import load_json

JSONValue: TypeAlias = Union[
    str,
    int,
    float,
    bool,
    None,
    list["JSONValue"],
    dict[str, "JSONValue"],
]
JSONObject: TypeAlias = dict[str, JSONValue]
Order: TypeAlias = Literal["asc", "desc"]

__all__ = [
    "JSONObject",
    "JSONValue",
    "Order",
    "StateStore",
    "DeletedStateStore",
    "StateStoreItem",
    "StateStoreItemRef",
    "DeletedStateStoreItem",
    "StateStoreItemKey",
    "StateStoreItemKeyPage",
    "serialize_store_create_request",
    "serialize_store_update_request",
    "serialize_item_create_request",
    "serialize_item_put_request",
    "deserialize_state_store",
    "deserialize_deleted_state_store",
    "deserialize_state_item_ref",
    "deserialize_state_item",
    "deserialize_deleted_state_item",
    "deserialize_list_keys_response",
]


@dataclass
class StateStoreItemKeyPage:
    """A page of keys returned by ``list_keys``.

    A hand-written convenience wrapper (not itself part of the wire contract)
    over the generated ``ListResponseStateStoreItemKey`` envelope, exposing its
    ``data`` array as ``keys`` to match this client's naming.
    """

    keys: list[StateStoreItemKey]
    first_id: str | None = None
    last_id: str | None = None
    has_more: bool = False


_UNSET = object()


def _to_wire_tags(tags: Mapping[str, str] | None) -> dict[str, str] | None:
    return dict(tags) if tags else None


def serialize_store_create_request(
    name: str,
    *,
    user_isolation: bool,
    item_ttl_seconds: int,
    description: str | None,
    tags: Mapping[str, str],
) -> bytes:
    request = CreateStateStoreRequest(
        name=name,
        user_isolation=user_isolation,
        item_ttl_seconds=item_ttl_seconds,
        description=description,
        tags=_to_wire_tags(tags),
    )
    return json.dumps(dict(request)).encode("utf-8")


def serialize_store_update_request(description: str | None | object, tags: Mapping[str, str] | None | object) -> bytes:
    # description/tags use the module-level _UNSET sentinel to distinguish
    # "leave unchanged" (key omitted) from "clear" (key present with a null
    # value). The generated model's *mapping* constructor preserves that
    # distinction (unlike its kwargs constructor, which drops an explicit
    # ``None`` as if the field had been omitted) -- see model_base.Model
    # .__init__: the kwargs branch filters ``v is not None``, the mapping
    # branch does not.
    payload: dict[str, Any] = {}
    if description is not _UNSET:
        payload["description"] = description
    if tags is not _UNSET:
        payload["tags"] = dict(tags) if isinstance(tags, Mapping) else {}
    request = UpdateStateStoreRequest(payload)
    return json.dumps(dict(request)).encode("utf-8")


def serialize_item_create_request(key: str, value: JSONObject, tags: Mapping[str, str] | None) -> bytes:
    request = CreateItemRequest(key=key, value=value, tags=_to_wire_tags(tags))
    return json.dumps(dict(request)).encode("utf-8")


def serialize_item_put_request(value: JSONObject, tags: Mapping[str, str] | None) -> bytes:
    request = PutItemRequest(value=value, tags=_to_wire_tags(tags))
    return json.dumps(dict(request)).encode("utf-8")


def deserialize_state_store(body: str) -> StateStore:
    return StateStore(load_json(body))


def deserialize_deleted_state_store(body: str) -> DeletedStateStore:
    return DeletedStateStore(load_json(body))


def deserialize_state_item_ref(body: str) -> StateStoreItemRef:
    return StateStoreItemRef(load_json(body))


def deserialize_state_item(body: str) -> StateStoreItem:
    return StateStoreItem(load_json(body))


def deserialize_deleted_state_item(body: str) -> DeletedStateStoreItem:
    return DeletedStateStoreItem(load_json(body))


def deserialize_list_keys_response(body: str) -> StateStoreItemKeyPage:
    page = ListResponseStateStoreItemKey(load_json(body))
    return StateStoreItemKeyPage(
        keys=list(page.data or []),
        first_id=page.first_id,
        last_id=page.last_id,
        has_more=bool(page.has_more),
    )
