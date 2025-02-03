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
from ._enums import SchemaContentTypeValues


class SchemaFormat(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Represents the format of the schema to be stored by the Schema Registry service."""

    AVRO = "Avro"
    """Represents the Apache Avro schema format."""
    JSON = "Json"
    """Represents the JSON schema format."""
    CUSTOM = "Custom"
    """Represents a custom schema format."""


# Normalizing the schema content type strings for whitespace and case insensitive comparison.
class NormalizedSchemaContentTypes(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Describes closed list of normalized schema content type values."""

    AVRO = SchemaContentTypeValues.AVRO.value.replace(" ", "").lower()
    """Avro encoding."""
    JSON = SchemaContentTypeValues.JSON.value.replace(" ", "").lower()
    """JSON encoding"""
    CUSTOM = SchemaContentTypeValues.CUSTOM.value.replace(" ", "").lower()
    """Plain text custom encoding."""


__all__: List[str] = []  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
