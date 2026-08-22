# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Dict-native OpenAI wire payload helpers."""

from __future__ import annotations

from collections.abc import Mapping
from copy import deepcopy
from datetime import date, datetime
from typing import Any


def enum_value(value: Any) -> Any:
    """Return an enum member's wire value, or the value itself."""
    return getattr(value, "value", value)


def get_field(payload: Any, field: str, default: Any = None) -> Any:
    """Read a field from a wire mapping."""
    if isinstance(payload, Mapping):
        return payload.get(field, default)
    return default


def set_field(payload: Any, field: str, value: Any) -> None:
    """Set a field on a mutable wire mapping."""
    if isinstance(payload, dict):
        payload[field] = value
        return
    raise TypeError("wire payload must be a mutable dictionary")


def is_type(payload: Any, type_value: str) -> bool:
    """Check a wire discriminator without relying on generated model classes."""
    return get_field(payload, "type") == type_value


def to_wire_dict(value: Any) -> dict[str, Any]:
    """Convert a mapping to a JSON-safe wire dict."""
    if not isinstance(value, Mapping):
        raise TypeError("wire payload must be a mapping")
    return _json_safe(value)


def _json_safe(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {key: _json_safe(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_json_safe(item) for item in value]
    if isinstance(value, tuple):
        return [_json_safe(item) for item in value]
    if isinstance(value, datetime):
        return int(value.timestamp())
    if isinstance(value, date):
        return value.isoformat()
    wire_value = getattr(value, "value", None)
    if wire_value is not None:
        return wire_value
    return deepcopy(value)
