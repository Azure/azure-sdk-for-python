# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Serialization helpers and value types for the Foundry state-store client."""

# Internal serialize/deserialize helpers below intentionally omit per-param docs.
# pylint: disable=docstring-missing-param,docstring-missing-return,docstring-missing-rtype

from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any, Literal, Union

try:
    from typing import TypeAlias
except ImportError:  # pragma: no cover
    from typing_extensions import TypeAlias  # type: ignore[assignment]  # Python <3.10 fallback

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


@dataclass
class StateStoreInfo:
    """Descriptor for a state store resource."""

    id: str | None
    name: str
    user_isolation: bool
    item_ttl_seconds: int | None
    description: str | None = None
    tags: dict[str, str] = field(default_factory=dict)
    created_at: int | None = None
    updated_at: int | None = None


@dataclass
class DeletedStateStore:
    """Deleted-store marker returned by store delete operations."""

    id: str | None
    name: str
    deleted: bool


@dataclass
class StateItemMetadata:
    """Metadata returned by create/update item operations."""

    id: str | None
    key: str
    etag: str | None = None
    created_at: int | None = None
    updated_at: int | None = None


@dataclass
class StateItem:
    """A single stored item returned by ``get``."""

    id: str | None
    key: str
    value: JSONObject
    tags: dict[str, str] = field(default_factory=dict)
    etag: str | None = None
    created_at: int | None = None
    updated_at: int | None = None


@dataclass
class DeletedStateItem:
    """Deleted-item marker returned by item delete operations."""

    id: str | None
    key: str
    deleted: bool


@dataclass
class StateKey:
    """A key entry returned by ``list_keys``."""

    id: str | None
    key: str
    tags: dict[str, str] = field(default_factory=dict)
    etag: str | None = None
    created_at: int | None = None
    updated_at: int | None = None


@dataclass
class KeyPage:
    """A page of keys returned by ``list_keys``."""

    keys: list[StateKey]
    first_id: str | None = None
    last_id: str | None = None
    has_more: bool = False


def serialize_store_create_request(
    name: str,
    *,
    user_isolation: bool,
    item_ttl_seconds: int,
    description: str | None,
    tags: Mapping[str, str],
) -> bytes:
    payload: dict[str, Any] = {
        "name": name,
        "user_isolation": user_isolation,
        "item_ttl_seconds": item_ttl_seconds,
    }
    if description is not None:
        payload["description"] = description
    if tags:
        payload["tags"] = dict(tags)
    return json.dumps(payload).encode("utf-8")


def serialize_store_update_request(description: str | None | object, tags: Mapping[str, str] | None | object) -> bytes:
    payload: dict[str, Any] = {}
    if description is not _UNSET:
        payload["description"] = description
    if tags is not _UNSET:
        payload["tags"] = {} if tags is None else dict(tags)
    return json.dumps(payload).encode("utf-8")


def serialize_item_create_request(key: str, value: JSONObject, tags: Mapping[str, str] | None) -> bytes:
    payload: dict[str, Any] = {"key": key, "value": value}
    if tags:
        payload["tags"] = dict(tags)
    return json.dumps(payload).encode("utf-8")


def serialize_item_put_request(value: JSONObject, tags: Mapping[str, str] | None) -> bytes:
    payload: dict[str, Any] = {"value": value}
    if tags:
        payload["tags"] = dict(tags)
    return json.dumps(payload).encode("utf-8")


def _as_epoch(value: Any) -> int | None:
    return value if isinstance(value, int) and not isinstance(value, bool) else None


def _as_string_dict(value: Any) -> dict[str, str]:
    if not isinstance(value, dict):
        return {}
    return {str(key): str(item) for key, item in value.items()}


def deserialize_state_store(body: str) -> StateStoreInfo:
    data = load_json(body)
    return StateStoreInfo(
        id=_as_optional_str(data.get("id")),
        name=str(data.get("name", "")),
        user_isolation=bool(data.get("user_isolation", False)),
        item_ttl_seconds=_as_epoch(data.get("item_ttl_seconds")),
        description=_as_optional_str(data.get("description")),
        tags=_as_string_dict(data.get("tags")),
        created_at=_as_epoch(data.get("created_at")),
        updated_at=_as_epoch(data.get("updated_at")),
    )


def deserialize_deleted_state_store(body: str) -> DeletedStateStore:
    data = load_json(body)
    return DeletedStateStore(
        id=_as_optional_str(data.get("id")),
        name=str(data.get("name", "")),
        deleted=bool(data.get("deleted", False)),
    )


def deserialize_state_item_metadata(body: str) -> StateItemMetadata:
    data = load_json(body)
    return StateItemMetadata(
        id=_as_optional_str(data.get("id")),
        key=str(data.get("key", "")),
        etag=_as_optional_str(data.get("etag")),
        created_at=_as_epoch(data.get("created_at")),
        updated_at=_as_epoch(data.get("updated_at")),
    )


def deserialize_state_item(body: str) -> StateItem:
    data = load_json(body)
    raw_value = data.get("value")
    value = raw_value if isinstance(raw_value, dict) else {}
    return StateItem(
        id=_as_optional_str(data.get("id")),
        key=str(data.get("key", "")),
        value=value,
        tags=_as_string_dict(data.get("tags")),
        etag=_as_optional_str(data.get("etag")),
        created_at=_as_epoch(data.get("created_at")),
        updated_at=_as_epoch(data.get("updated_at")),
    )


def deserialize_deleted_state_item(body: str) -> DeletedStateItem:
    data = load_json(body)
    return DeletedStateItem(
        id=_as_optional_str(data.get("id")),
        key=str(data.get("key", "")),
        deleted=bool(data.get("deleted", False)),
    )


def deserialize_list_keys_response(body: str) -> KeyPage:
    data = load_json(body)
    raw_items = data.get("data", [])
    keys: list[StateKey] = []
    if isinstance(raw_items, list):
        for entry in raw_items:
            if isinstance(entry, dict) and entry.get("key") is not None:
                keys.append(
                    StateKey(
                        id=_as_optional_str(entry.get("id")),
                        key=str(entry["key"]),
                        tags=_as_string_dict(entry.get("tags")),
                        etag=_as_optional_str(entry.get("etag")),
                        created_at=_as_epoch(entry.get("created_at")),
                        updated_at=_as_epoch(entry.get("updated_at")),
                    )
                )
    return KeyPage(
        keys=keys,
        first_id=_as_optional_str(data.get("first_id")),
        last_id=_as_optional_str(data.get("last_id")),
        has_more=bool(data.get("has_more", False)),
    )


def _as_optional_str(value: Any) -> str | None:
    return str(value) if value is not None else None


_UNSET = object()
