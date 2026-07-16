# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Helpers for local dict/TypedDict wire payloads."""

from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime
from typing import Any


def get_field(payload: Any, field: str, default: Any = None) -> Any:
    """Return a field from a mapping-like wire payload."""
    if isinstance(payload, Mapping):
        return payload.get(field, default)
    return default


def is_type(payload: Any, type_value: str) -> bool:
    """Return whether a wire payload has the requested discriminator value."""
    return get_field(payload, "type") == type_value


def to_wire_dict(value: Any) -> Any:
    """Convert JSON-compatible mappings/sequences into plain wire payloads."""
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, datetime):
        return int(value.timestamp())
    if isinstance(value, Mapping):
        return {str(k): to_wire_dict(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [to_wire_dict(item) for item in value]
    raise TypeError(f"Expected JSON-compatible wire payload, got {type(value).__name__}")
