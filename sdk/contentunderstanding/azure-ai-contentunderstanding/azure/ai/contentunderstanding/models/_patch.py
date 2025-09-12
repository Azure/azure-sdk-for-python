# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from typing import List, Optional, Any, Union, overload

__all__: List[str] = [
    "StringField", "IntegerField", "NumberField", "BooleanField", 
    "DateField", "TimeField", "ArrayField", "ObjectField", "AnalyzeInput"
]  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
    pass


# Import the generated classes and monkey-patch them
from ._models import (
    StringField, IntegerField, NumberField, BooleanField, 
    DateField, TimeField, ArrayField, ObjectField, ContentField,
    AnalyzeInput as AnalyzeInputGenerated
)


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
    """Get the number value of this field."""
    return self.value_number

setattr(NumberField, 'value', property(_number_field_value))


# Monkey-patch the BooleanField class to add the value property
def _boolean_field_value(self) -> Optional[bool]:
    """Get the boolean value of this field."""
    return self.value_boolean

setattr(BooleanField, 'value', property(_boolean_field_value))


# Monkey-patch the DateField class to add the value property
def _date_field_value(self) -> Optional[Any]:
    """Get the date value of this field."""
    return self.value_date

setattr(DateField, 'value', property(_date_field_value))


# Monkey-patch the TimeField class to add the value property
def _time_field_value(self) -> Optional[Any]:
    """Get the time value of this field."""
    return self.value_time

setattr(TimeField, 'value', property(_time_field_value))


# Monkey-patch the ArrayField class to add the value property
def _array_field_value(self) -> Optional[List[Any]]:
    """Get the array value of this field."""
    return self.value_array

setattr(ArrayField, 'value', property(_array_field_value))


# Monkey-patch the ObjectField class to add the value property
def _object_field_value(self) -> Optional[dict[str, Any]]:
    """Get the object value of this field."""
    return self.value_object

setattr(ObjectField, 'value', property(_object_field_value))


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
        pass
    
    @overload
    def __init__(self, *, data: bytes, name: Optional[str] = None) -> None:
        """Initialize with data parameter.
        
        :param data: Base64-encoded binary content of the input to analyze
        :type data: bytes
        :param name: Name of the input
        :type name: Optional[str]
        """
        pass
    
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
