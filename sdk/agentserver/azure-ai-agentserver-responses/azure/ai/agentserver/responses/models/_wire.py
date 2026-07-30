# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Helpers for local dict/TypedDict wire payloads."""

from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime
from typing import Any


def get_field(payload: Any, field: str, default: Any = None) -> Any:
    """Return a field from a mapping-like wire payload.

    :param payload: The wire payload to read.
    :type payload: Any
    :param field: The field name to read.
    :type field: str
    :param default: The value to return when the field is absent.
    :type default: Any
    :returns: The field value, or *default* when unavailable.
    :rtype: Any
    """
    if isinstance(payload, Mapping):
        return payload.get(field, default)
    if hasattr(payload, field):
        return getattr(payload, field)
    return default


def is_type(payload: Any, type_value: str) -> bool:
    """Return whether a wire payload has the requested discriminator value.

    :param payload: The wire payload to inspect.
    :type payload: Any
    :param type_value: The expected discriminator value.
    :type type_value: str
    :returns: ``True`` if the payload has the requested type.
    :rtype: bool
    """
    return get_field(payload, "type") == type_value


def to_wire_dict(value: Any) -> Any:
    """Convert JSON-compatible mappings/sequences into plain wire payloads.

    :param value: The value to normalize.
    :type value: Any
    :returns: A JSON-compatible wire payload.
    :rtype: Any
    :raises TypeError: If *value* is not JSON-compatible.
    """
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, datetime):
        return int(value.timestamp())
    if hasattr(value, "as_dict") and callable(value.as_dict):
        return to_wire_dict(value.as_dict())
    if hasattr(value, "to_dict") and callable(value.to_dict):
        return to_wire_dict(value.to_dict())
    if isinstance(value, Mapping):
        return {str(k): to_wire_dict(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [to_wire_dict(item) for item in value]
    raise TypeError(f"Expected JSON-compatible wire payload, got {type(value).__name__}")
