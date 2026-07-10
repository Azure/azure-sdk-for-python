# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Azure AI OpenAI extension types and helpers."""

from ._version import VERSION
from ._wire import enum_value, get_field, is_type, set_field, to_wire_dict

__version__ = VERSION

__all__ = [
    "VERSION",
    "enum_value",
    "get_field",
    "is_type",
    "set_field",
    "to_wire_dict",
]
