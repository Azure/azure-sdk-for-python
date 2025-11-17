# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
import re
from typing import Optional, Any, Dict, List, Union, TYPE_CHECKING, Mapping, TypeVar
from azure.core.polling import LROPoller, PollingMethod
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

PollingReturnType_co = TypeVar("PollingReturnType_co", covariant=True)

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
    "AnalyzeLROPoller",
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


def _parse_operation_id(operation_location_header: str) -> str:
    """Parse operation ID from Operation-Location header for analyze operations.

    :param operation_location_header: The Operation-Location header value
    :type operation_location_header: str
    :return: The extracted operation ID
    :rtype: str
    :raises ValueError: If operation ID cannot be extracted
    """
    # Pattern: https://endpoint/.../analyzerResults/{operation_id}?api-version=...
    regex = r".*/analyzerResults/([^?/]+)"

    match = re.search(regex, operation_location_header)
    if not match:
        raise ValueError(f"Could not extract operation ID from: {operation_location_header}")

    return match.group(1)


class AnalyzeLROPoller(LROPoller[PollingReturnType_co]):
    """Custom LROPoller for Content Understanding analyze operations.

    Provides access to the operation ID for tracking and diagnostics.
    """

    @property
    def operation_id(self) -> str:
        """Returns the operation ID for this long-running operation.
        
        The operation ID can be used with get_result_file() to retrieve
        intermediate or final result files from the service.

        :return: The operation ID
        :rtype: str
        :raises ValueError: If the operation ID cannot be extracted
        """
        try:
            operation_location = self.polling_method()._initial_response.http_response.headers["Operation-Location"]  # type: ignore # pylint: disable=protected-access
            return _parse_operation_id(operation_location)
        except (KeyError, ValueError) as e:
            raise ValueError(f"Could not extract operation ID: {str(e)}") from e

    @classmethod
    def from_continuation_token(
        cls, polling_method: PollingMethod[PollingReturnType_co], continuation_token: str, **kwargs: Any
    ) -> "AnalyzeLROPoller":
        """Create a poller from a continuation token.

        :param polling_method: The polling strategy to adopt
        :type polling_method: ~azure.core.polling.PollingMethod
        :param continuation_token: An opaque continuation token
        :type continuation_token: str
        :return: An instance of AnalyzeLROPoller
        :rtype: AnalyzeLROPoller
        :raises ~azure.core.exceptions.HttpResponseError: If the continuation token is invalid.
        """
        (
            client,
            initial_response,
            deserialization_callback,
        ) = polling_method.from_continuation_token(continuation_token, **kwargs)

        return cls(client, initial_response, deserialization_callback, polling_method)


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
