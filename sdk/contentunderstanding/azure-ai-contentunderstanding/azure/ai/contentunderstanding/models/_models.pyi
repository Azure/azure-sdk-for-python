# Stub file for _models.py
# This file declares the .value property added at runtime via patch_sdk()
# Type checkers (MyPy, Pyright) use this to understand the properties exist

from typing import Any, Optional, Dict, List

# ContentField base class
class ContentField:
    value: Any  # Added at runtime via patch_sdk()

# Specific field types with their return types
class StringField(ContentField):
    value: Optional[str]  # Added at runtime via patch_sdk()

class IntegerField(ContentField):
    value: Optional[int]  # Added at runtime via patch_sdk()

class NumberField(ContentField):
    value: Optional[float]  # Added at runtime via patch_sdk()

class BooleanField(ContentField):
    value: Optional[bool]  # Added at runtime via patch_sdk()

class DateField(ContentField):
    value: Optional[str]  # Added at runtime via patch_sdk()

class TimeField(ContentField):
    value: Optional[str]  # Added at runtime via patch_sdk()

class ArrayField(ContentField):
    value: Optional[List[Any]]  # Added at runtime via patch_sdk()

class ObjectField(ContentField):
    value: Optional[Dict[str, Any]]  # Added at runtime via patch_sdk()

class JsonField(ContentField):
    value: Optional[Any]  # Added at runtime via patch_sdk()

