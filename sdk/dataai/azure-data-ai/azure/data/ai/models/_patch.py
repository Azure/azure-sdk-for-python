# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Serialization customizations for error details projected by Azure Core."""

from collections.abc import Mapping
from copy import deepcopy
from typing import Any, Optional

from azure.core.exceptions import ODataV4Format

from .._utils.model_base import rest_field
from ._models import ProblemDetails as _GeneratedProblemDetails

__all__ = ["ProblemDetails"]


def _error_fields(error: ODataV4Format) -> dict[str, Any]:
    return {
        "code": error.code,
        "message": error.message,
        "target": error.target,
        "details": _json_value(error.details),
        "innererror": _json_value(error.innererror),
    }


def _json_value(value: Any) -> Any:
    if isinstance(value, _SerializableError):
        return value.as_dict()
    if isinstance(value, ODataV4Format):
        return {name: field for name, field in _error_fields(value).items() if field is not None}
    if isinstance(value, Mapping):
        return {name: _json_value(field) for name, field in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_value(field) for field in value]
    return value


class _SerializableError(ODataV4Format):
    def __init__(self, json_object: Mapping[str, Any]) -> None:
        self._original = deepcopy(dict(json_object))
        projected = deepcopy(self._original)
        # A detail's additional "error" property is not the outer error envelope.
        projected.pop("error", None)
        super().__init__(projected)
        self._initial_fields = _error_fields(self)

    def as_dict(self, *, exclude_readonly: bool = False) -> dict[str, Any]:  # pylint: disable=unused-argument
        # Core normalizes absent/null fields and drops extensions. Preserve the
        # original JSON unless a caller actually changes a projected value.
        result = deepcopy(self._original)
        for name, value in _error_fields(self).items():
            if value != self._initial_fields[name]:
                result[name] = value
        return result


def _deserialize_details(values: list[Any]) -> list[Any]:
    return [
        (
            _SerializableError(value)
            if isinstance(value, Mapping) and (value.get("code") or value.get("message"))
            else value
        )
        for value in values
    ]


class ProblemDetails(_GeneratedProblemDetails):
    """Details about an HTTP API error."""

    details: Optional[list[ODataV4Format]] = rest_field(
        visibility=["read", "create", "update", "delete", "query"],
        deserializer=_deserialize_details,
    )
    """An array of details about specific errors that led to this reported error."""

    def as_dict(self, *, exclude_readonly: bool = False) -> dict[str, Any]:
        """Return a JSON-compatible dictionary, including projected error details.

        :keyword bool exclude_readonly: Whether to remove readonly properties.
        :return: A JSON-compatible dictionary.
        :rtype: dict
        """
        return _json_value(super().as_dict(exclude_readonly=exclude_readonly))


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
