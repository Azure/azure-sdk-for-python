# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from typing import List

from enum import Enum
from azure.core import CaseInsensitiveEnumMeta


class SchemaFormat(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Represents the format of the schema to be stored by the Schema Registry service."""

    AVRO = "Avro"
    """Represents the Apache Avro schema format."""
    JSON = "Json"
    """Represents the JSON schema format."""
    CUSTOM = "Custom"
    """Represents a custom schema format."""
    PROTOBUF = "Protobuf"
    """Represents a protobuf schema format."""


__all__: List[str] = []  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
