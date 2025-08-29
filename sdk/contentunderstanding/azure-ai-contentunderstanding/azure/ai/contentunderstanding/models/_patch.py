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
    "DateField", "TimeField", "ArrayField", "ObjectField"
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
    DateField, TimeField, ArrayField, ObjectField, ContentField
)


# Monkey-patch the StringField class to add the value property
def _string_field_value(self) -> Optional[str]:
    """Get the string value of this field."""
    return self.value_string

StringField.value = property(_string_field_value)


# Monkey-patch the IntegerField class to add the value property
def _integer_field_value(self) -> Optional[int]:
    """Get the integer value of this field."""
    return self.value_integer

IntegerField.value = property(_integer_field_value)


# Monkey-patch the NumberField class to add the value property
def _number_field_value(self) -> Optional[float]:
    """Get the number value of this field."""
    return self.value_number

NumberField.value = property(_number_field_value)


# Monkey-patch the BooleanField class to add the value property
def _boolean_field_value(self) -> Optional[bool]:
    """Get the boolean value of this field."""
    return self.value_boolean

BooleanField.value = property(_boolean_field_value)


# Monkey-patch the DateField class to add the value property
def _date_field_value(self) -> Optional[Any]:
    """Get the date value of this field."""
    return self.value_date

DateField.value = property(_date_field_value)


# Monkey-patch the TimeField class to add the value property
def _time_field_value(self) -> Optional[Any]:
    """Get the time value of this field."""
    return self.value_time

TimeField.value = property(_time_field_value)


# Monkey-patch the ArrayField class to add the value property
def _array_field_value(self) -> Optional[List[Any]]:
    """Get the array value of this field."""
    return self.value_array

ArrayField.value = property(_array_field_value)


# Monkey-patch the ObjectField class to add the value property
def _object_field_value(self) -> Optional[dict[str, Any]]:
    """Get the object value of this field."""
    return self.value_object

ObjectField.value = property(_object_field_value)


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
