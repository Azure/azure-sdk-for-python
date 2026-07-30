# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Object-style compatibility models for response payloads."""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping


class ResponseModel(dict[str, Any]):
    """Dictionary-backed response model with attribute access.

    The Responses server stores and streams JSON-compatible dictionaries
    internally. This wrapper preserves that wire-native representation while
    restoring the object-style access pattern used by client SDK response
    models.
    """

    def __init__(self, mapping: Mapping[str, Any] | None = None, **kwargs: Any) -> None:
        values: dict[str, Any] = {}
        if mapping is not None:
            values.update(mapping)
        values.update(kwargs)
        super().__init__((key, _wrap_value(value)) for key, value in values.items())

    def __getattr__(self, name: str) -> Any:
        try:
            return self[name]
        except KeyError as exc:
            raise AttributeError(name) from exc

    def __setattr__(self, name: str, value: Any) -> None:
        self[name] = _wrap_value(value)

    def __delattr__(self, name: str) -> None:
        try:
            del self[name]
        except KeyError as exc:
            raise AttributeError(name) from exc

    def copy(self) -> "ResponseModel":  # type: ignore[override]
        """Return a shallow object-model copy."""
        return type(self)(self)

    def as_dict(self) -> dict[str, Any]:
        """Return a plain dictionary representation of the model."""
        return _unwrap_value(self)

    def to_dict(self) -> dict[str, Any]:
        """Return a plain dictionary representation of the model."""
        return self.as_dict()


def _wrap_value(value: Any) -> Any:
    if isinstance(value, ResponseModel):
        return value
    if isinstance(value, Mapping):
        return ResponseModel(value)
    if isinstance(value, list):
        return [_wrap_value(item) for item in value]
    if isinstance(value, tuple):
        return tuple(_wrap_value(item) for item in value)
    return value


def _unwrap_value(value: Any) -> Any:
    if isinstance(value, ResponseModel):
        return {key: _unwrap_value(item) for key, item in value.items()}
    if isinstance(value, Mapping):
        return {str(key): _unwrap_value(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_unwrap_value(item) for item in value]
    if isinstance(value, tuple):
        return [_unwrap_value(item) for item in value]
    return deepcopy(value)


def create_response_model_type(name: str, module_name: str) -> type[ResponseModel]:
    """Create a named response model class backed by :class:`ResponseModel`."""

    return type(name, (ResponseModel,), {"__module__": module_name})


__all__ = ["ResponseModel", "create_response_model_type"]
