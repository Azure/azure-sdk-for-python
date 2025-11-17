# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from typing import Optional, Any, Dict, List, Union, TYPE_CHECKING
from ._models import (
    StringField,
    IntegerField,
    NumberField,
    BooleanField,
    DateField,
    TimeField,
    ArrayField,
    ObjectField,
    JsonField,
    ContentField,
)

# Type stub to help mypy and pyright understand that ContentField has a .value property
if TYPE_CHECKING:

    class ContentFieldTypeStub:
        """Type stub for ContentField to help type checkers understand the .value property."""

        @property
        def value(
            self,
        ) -> Union[
            Optional[str],
            Optional[float],
            Optional[int],
            Optional[bool],
            Optional[Any],
            Optional[List[Any]],
            Optional[dict[str, Any]],
        ]:
            """Get the value of this field regardless of its type."""
            ...  # pylint: disable=unnecessary-ellipsis


__all__ = [
    "RecordMergePatchUpdate",
    "StringField",
    "IntegerField",
    "NumberField",
    "BooleanField",
    "DateField",
    "TimeField",
    "ArrayField",
    "ObjectField",
    "JsonField",
]

# RecordMergePatchUpdate is a TypeSpec artifact that wasn't generated
# It's just an alias for dict[str, str] for model deployments
RecordMergePatchUpdate = Dict[str, str]


def _add_value_property_to_field(field_class: type, value_attr: str) -> None:
    """Add a .value property to a field class that returns the appropriate attribute."""

    @property  # type: ignore[misc]
    def value(self) -> Any:  # type: ignore[misc]
        """Get the value of this field."""
        return getattr(self, value_attr)

    setattr(field_class, "value", value)


def patch_sdk():
    """Patch the SDK to add missing models and convenience properties."""
    from . import _models

    # Add RecordMergePatchUpdate as an alias
    # (AnalyzeInput is now generated in _models.py, so we don\'t need to add it)
    _models.RecordMergePatchUpdate = RecordMergePatchUpdate  # type: ignore[attr-defined]

    # Add .value property to all ContentField subclasses for easier access
    # Note: The attribute names follow the pattern "value_<type>"
    _add_value_property_to_field(StringField, "value_string")
    _add_value_property_to_field(IntegerField, "value_integer")
    _add_value_property_to_field(NumberField, "value_number")
    _add_value_property_to_field(BooleanField, "value_boolean")
    _add_value_property_to_field(DateField, "value_date")
    _add_value_property_to_field(TimeField, "value_time")
    _add_value_property_to_field(ArrayField, "value_array")
    _add_value_property_to_field(ObjectField, "value_object")
    _add_value_property_to_field(JsonField, "value_json")
