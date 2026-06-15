# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""JSON serialization helpers for Foundry activity state envelopes."""
# pylint: disable=docstring-missing-param,docstring-missing-return,docstring-missing-rtype

from __future__ import annotations

import json
from typing import Any


def serialize_read_request(keys: list[str]) -> bytes:
    """Serialize a batch state-read request to JSON bytes."""
    return json.dumps({"keys": keys}).encode("utf-8")


def serialize_write_request(changes: dict[str, Any]) -> bytes:
    """Serialize a batch state-write request to JSON bytes."""
    payload = {"changes": {key: {"value": value} for key, value in changes.items()}}
    return json.dumps(payload).encode("utf-8")


def serialize_delete_request(keys: list[str]) -> bytes:
    """Serialize a batch state-delete request to JSON bytes."""
    return json.dumps({"keys": keys}).encode("utf-8")


def deserialize_read_response(body: str) -> dict[str, dict[str, Any]]:
    """Deserialize a state-read response, preserving only returned items."""
    data = json.loads(body or "{}")
    raw_items = data.get("items", {})
    if not isinstance(raw_items, dict):
        return {}

    items: dict[str, dict[str, Any]] = {}
    for key, item in raw_items.items():
        if isinstance(item, dict) and "value" in item:
            items[str(key)] = {"value": item.get("value"), "etag": item.get("etag")}
    return items


def deserialize_write_response(body: str) -> dict[str, dict[str, Any]]:
    """Deserialize a state-write response containing per-key etags."""
    data = json.loads(body or "{}")
    raw_items = data.get("items", {})
    if not isinstance(raw_items, dict):
        return {}

    items: dict[str, dict[str, Any]] = {}
    for key, item in raw_items.items():
        if isinstance(item, dict):
            items[str(key)] = {"etag": item.get("etag")}
    return items
