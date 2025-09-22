# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from typing import List, Optional, Any, Union, overload, TYPE_CHECKING
from ._models import (
    StringField, IntegerField, NumberField, BooleanField,
    DateField, TimeField, ArrayField, ObjectField, ContentField,
    AnalyzeInput as AnalyzeInputGenerated
)

# Type stub to help mypy and pyright understand that ContentField has a .value property
# This is needed because we monkey-patch the .value property at runtime
if TYPE_CHECKING:
    # This block is only for type checking, never executed
    class ContentField:
        """Type stub for ContentField to help type checkers understand the .value property."""
        
        @property
        def value(self) -> Union[Optional[str], Optional[float], Optional[int], Optional[bool], Optional[Any], Optional[List[Any]], Optional[dict[str, Any]]]:
            """Get the value of this field regardless of its type."""
            ...

# Additional type annotation to help both mypy and pyright understand the .value property
# This creates a runtime type annotation that type checkers can understand
from typing import get_type_hints

# Add a type annotation to ContentField to help type checkers understand the .value property
# This is a runtime annotation that doesn't affect execution but helps static analysis
ContentField.value: property  # type: ignore[attr-defined]

__all__: List[str] = [
    "StringField", "IntegerField", "NumberField", "BooleanField",
    "DateField", "TimeField", "ArrayField", "ObjectField", "AnalyzeInput"
]


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize

    :return: None
    :rtype: None
    """




# Monkey-patch the StringField class to add the value property
def _string_field_value(self) -> Optional[str]:
    """Get the string value of this field."""
    return self.value_string

setattr(StringField, 'value', property(_string_field_value))


# Monkey-patch the IntegerField class to add the value property
def _integer_field_value(self) -> Optional[int]:
    """Get the integer value of this field."""
    return self.value_integer

setattr(IntegerField, 'value', property(_integer_field_value))


# Monkey-patch the NumberField class to add the value property
def _number_field_value(self) -> Optional[float]:
    """Get the number value of this field.
    
    :return: The number value of this field
    :rtype: Optional[float]
    """
    return self.value_number

setattr(NumberField, 'value', property(_number_field_value))


# Monkey-patch the BooleanField class to add the value property
def _boolean_field_value(self) -> Optional[bool]:
    """Get the boolean value of this field.
    
    :return: The boolean value of this field
    :rtype: Optional[bool]
    """
    return self.value_boolean

setattr(BooleanField, 'value', property(_boolean_field_value))


# Monkey-patch the DateField class to add the value property
def _date_field_value(self) -> Optional[Any]:
    """Get the date value of this field.
    
    :return: The date value of this field
    :rtype: Optional[Any]
    """
    return self.value_date

setattr(DateField, 'value', property(_date_field_value))


# Monkey-patch the TimeField class to add the value property
def _time_field_value(self) -> Optional[Any]:
    """Get the time value of this field.
    
    :return: The time value of this field
    :rtype: Optional[Any]
    """
    return self.value_time

setattr(TimeField, 'value', property(_time_field_value))


# Monkey-patch the ArrayField class to add the value property
def _array_field_value(self) -> Optional[List[Any]]:
    """Get the array value of this field.
    
    :return: The array value of this field
    :rtype: Optional[List[Any]]
    """
    return self.value_array

setattr(ArrayField, 'value', property(_array_field_value))


# Monkey-patch the ObjectField class to add the value property
def _object_field_value(self) -> Optional[dict[str, Any]]:
    """Get the object value of this field.
    
    :return: The object value of this field
    :rtype: Optional[dict[str, Any]]
    """
    return self.value_object

setattr(ObjectField, 'value', property(_object_field_value))


# Monkey-patch ContentField to add a generic value property for IntelliSense
def _content_field_value(self) -> Union[Optional[str], Optional[float], Optional[int], Optional[bool], Optional[Any], Optional[List[Any]], Optional[dict[str, Any]]]:
    """Get the value of this field regardless of its type.
    
    This property automatically returns the appropriate value based on the field type.
    IntelliSense will show this property as available on all ContentField instances.
    
    :return: The field value, type depends on the specific field type
    :rtype: Union[Optional[str], Optional[float], Optional[int], Optional[bool], Optional[Any], Optional[List[Any]], Optional[dict[str, Any]]]
    """
    # This will work because we've monkey-patched all the individual field types
    # with their own .value properties above
    return getattr(self, 'value', None)

setattr(ContentField, 'value', property(_content_field_value))


# Example usage:
# Instead of:
#   if field.type == "string":
#       value = field.value_string
#   elif field.type == "integer":
#       value = field.value_integer
#   # etc.
#
# You can now use:
#   value = field.value  # Works for any ContentField type
#   # IntelliSense will now show .value as available on ContentField instances!
#
# Example with type checking:
#   if isinstance(field, StringField):
#       string_value: Optional[str] = field.value  # Type is known
#   elif isinstance(field, NumberField):
#       number_value: Optional[float] = field.value  # Type is known


# Extended AnalyzeInput with mutually exclusive url/data parameters
class AnalyzeInput(AnalyzeInputGenerated):
    """Extended AnalyzeInput with mutually exclusive url and data parameters."""
    
    @overload
    def __init__(self, *, url: str, name: Optional[str] = None) -> None:
        """Initialize with URL parameter.
        
        :param url: The URL of the input to analyze
        :type url: str
        :param name: Name of the input
        :type name: Optional[str]
        """
    
    @overload
    def __init__(self, *, data: bytes, name: Optional[str] = None) -> None:
        """Initialize with data parameter.
        
        :param data: Base64-encoded binary content of the input to analyze
        :type data: bytes
        :param name: Name of the input
        :type name: Optional[str]
        """
    
    def __init__(self, *, url: Optional[str] = None, data: Optional[bytes] = None, name: Optional[str] = None) -> None:
        """Initialize AnalyzeInput with mutually exclusive url or data parameter.
        
        :param url: The URL of the input to analyze
        :type url: Optional[str]
        :param data: Base64-encoded binary content of the input to analyze
        :type data: Optional[bytes]
        :param name: Name of the input
        :type name: Optional[str]
        :raises ValueError: If both url and data are provided, or neither is provided
        """
        # Validate mutually exclusive parameters
        if url is not None and data is not None:
            raise ValueError("Cannot specify both 'url' and 'data' parameters. Please provide either 'url' or 'data', but not both.")
        
        if url is None and data is None:
            raise ValueError("Must specify either 'url' or 'data' parameter.")
        
        # Call parent constructor with validated parameters
        # At this point, we know exactly one of url or data is not None
        if url is not None:
            super().__init__(url=url, data=None, name=name)
        else:  # data is not None
            super().__init__(url="", data=data, name=name)
