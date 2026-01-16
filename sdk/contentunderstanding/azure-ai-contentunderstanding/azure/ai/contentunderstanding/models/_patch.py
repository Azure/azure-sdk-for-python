# pylint: disable=line-too-long,useless-suppression
# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
import re
from typing import Any, Dict, List, Optional, TypeVar
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

# Note: The .value property is added to ContentField classes at runtime in patch_sdk()
# Type annotations are set on the classes' __annotations__ for type checker support

PollingReturnType_co = TypeVar("PollingReturnType_co", covariant=True)

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
    def from_poller(cls, poller: LROPoller[PollingReturnType_co]) -> "AnalyzeLROPoller[PollingReturnType_co]":
        """Wrap an existing LROPoller without re-initializing the polling method.

        This avoids duplicate HTTP requests that would occur if we created a new
        LROPoller instance (which calls polling_method.initialize() again).

        :param poller: The existing LROPoller to wrap
        :type poller: ~azure.core.polling.LROPoller
        :return: An AnalyzeLROPoller wrapping the same polling state
        :rtype: AnalyzeLROPoller
        """
        # Create instance without calling __init__ to avoid re-initialization
        instance: AnalyzeLROPoller[PollingReturnType_co] = object.__new__(cls)
        # Copy all attributes from the original poller
        instance.__dict__.update(poller.__dict__)
        return instance

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


def _add_value_property_to_field(field_class: type, value_attr: str, return_type: Any = Any) -> None:
    """Add a .value property implementation at runtime.

    This function adds the actual property implementation so IntelliSense works.
    The type declarations in TYPE_CHECKING tell type checkers about the types.

    :param field_class: The field class to add the property to.
    :type field_class: type
    :param value_attr: The attribute name to read from (e.g., "value_string").
    :type value_attr: str
    :param return_type: The expected return type for better type checking.
    :type return_type: Any
    :return: None
    :rtype: None
    """

    def value_getter(self: Any) -> Any:
        """Get the value of this field.

        :return: The value of the field.
        :rtype: Any
        """
        return getattr(self, value_attr, None)

    # Set return type annotation for better type checking
    value_getter.__annotations__["return"] = return_type

    # Create property with type annotation
    value_property = property(value_getter)

    # Add property to class at runtime (for IntelliSense)
    setattr(field_class, "value", value_property)

    # Also add to __annotations__ for better IDE support
    if not hasattr(field_class, "__annotations__"):
        field_class.__annotations__ = {}
    field_class.__annotations__["value"] = return_type


def patch_sdk():
    """Patch the SDK to add missing models and convenience properties."""
    from . import _models

    # Add RecordMergePatchUpdate as an alias
    _models.RecordMergePatchUpdate = RecordMergePatchUpdate  # type: ignore[attr-defined]

    # Runtime implementation: Add .value property to all ContentField subclasses
    # The TYPE_CHECKING block above declares the types for static analysis
    # These runtime implementations make IntelliSense work
    _add_value_property_to_field(StringField, "value_string", Optional[str])
    _add_value_property_to_field(IntegerField, "value_integer", Optional[int])
    _add_value_property_to_field(NumberField, "value_number", Optional[float])
    _add_value_property_to_field(BooleanField, "value_boolean", Optional[bool])
    _add_value_property_to_field(DateField, "value_date", Optional[str])
    _add_value_property_to_field(TimeField, "value_time", Optional[str])
    _add_value_property_to_field(ArrayField, "value_array", Optional[List[Any]])
    _add_value_property_to_field(ObjectField, "value_object", Optional[Dict[str, Any]])
    _add_value_property_to_field(JsonField, "value_json", Optional[Any])

    # Add dynamic .value to ContentField base class
    # This checks which value_* attribute exists and returns it
    def _content_field_value_getter(self: ContentField) -> Any:
        """Get the value of this field regardless of its specific type.

        :param self: The ContentField instance.
        :type self: ContentField
        :return: The value of the field.
        :rtype: Any
        """
        for attr in [
            "value_string",
            "value_integer",
            "value_number",
            "value_boolean",
            "value_date",
            "value_time",
            "value_array",
            "value_object",
            "value_json",
        ]:
            if hasattr(self, attr):
                return getattr(self, attr)
        return None

    # Set return type annotation
    _content_field_value_getter.__annotations__["return"] = Any

    # Add property to ContentField base class
    content_field_value = property(_content_field_value_getter)
    setattr(ContentField, "value", content_field_value)

    # Also add to __annotations__ for IDE support
    if not hasattr(ContentField, "__annotations__"):
        ContentField.__annotations__ = {}
    ContentField.__annotations__["value"] = Any

    # SDK-FIX: Patch AudioVisualContent.__init__ to handle KeyFrameTimesMs casing inconsistency
    # The service returns "KeyFrameTimesMs" (capital K) but TypeSpec defines "keyFrameTimesMs" (lowercase k)
    # This fix is forward compatible: if the service fixes the issue and returns "keyFrameTimesMs" correctly,
    # the patch will be a no-op and the correct value will pass through unchanged.
    _original_audio_visual_content_init = _models.AudioVisualContent.__init__  # type: ignore[attr-defined] # pylint: disable=I1101

    def _patched_audio_visual_content_init(self, *args: Any, **kwargs: Any) -> None:
        """Patched __init__ that normalizes casing for KeyFrameTimesMs before calling parent.

        This patch is forward compatible: it only normalizes when the service returns incorrect casing.
        If the service returns the correct "keyFrameTimesMs" casing, the patch does nothing.

        :param args: Positional arguments passed to __init__.
        :type args: Any
        """
        # If first arg is a dict (mapping), normalize the casing
        if args and isinstance(args[0], dict):
            mapping = dict(args[0])  # Make a copy
            # SDK-FIX: Handle both "keyFrameTimesMs" (TypeSpec) and "KeyFrameTimesMs" (service response)
            # Forward compatible: only normalizes if incorrect casing exists and correct casing doesn't
            if "KeyFrameTimesMs" in mapping and "keyFrameTimesMs" not in mapping:
                mapping["keyFrameTimesMs"] = mapping["KeyFrameTimesMs"]
            # Call original with normalized mapping
            args = (mapping,) + args[1:]
        _original_audio_visual_content_init(self, *args, **kwargs)

    _models.AudioVisualContent.__init__ = _patched_audio_visual_content_init  # type: ignore[assignment] # pylint: disable=I1101
