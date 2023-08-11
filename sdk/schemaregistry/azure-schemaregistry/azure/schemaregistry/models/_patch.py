# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from typing import List, Any
from enum import Enum

from azure.core import CaseInsensitiveEnumMeta

__all__: List[str] = [
    "SchemaProperties",
    "Schema",
    "SchemaFormat",
    "ApiVersion",
    "DEFAULT_VERSION",
]  # Add all objects you want publicly available to users at this package level

def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """

class SchemaProperties(object):
    """
    Meta properties of a schema.

    :ivar id: References specific schema in registry namespace.
    :vartype id: str
    :ivar format: Format for the schema being stored.
    :vartype format: ~azure.schemaregistry.SchemaFormat
    :ivar group_name: Schema group under which schema is stored.
    :vartype group_name: str
    :ivar name: Name of schema.
    :vartype name: str
    :ivar version: Version of schema.
    :vartype version: int
    """

    def __init__(self, **kwargs: Any) -> None:
        self.id = kwargs.pop("id")
        self.format = kwargs.pop("format")
        self.group_name = kwargs.pop("group_name")
        self.name = kwargs.pop("name")
        self.version = kwargs.pop("version")

    def __repr__(self):
        return (
            f"SchemaProperties(id={self.id}, format={self.format}, "
            f"group_name={self.group_name}, name={self.name}, version={self.version})"[
                :1024
            ]
        )

class Schema(object):
    """
    The schema content of a schema, along with id and meta properties.

    :ivar definition: The content of the schema.
    :vartype definition: str
    :ivar properties: The properties of the schema.
    :vartype properties: SchemaProperties
    """

    def __init__(self, **kwargs: Any) -> None:
        self.definition = kwargs.pop("definition")
        self.properties = kwargs.pop("properties")

    def __repr__(self):
        return f"Schema(definition={self.definition}, properties={self.properties})"[:1024]

class SchemaFormat(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """
    Represents the format of the schema to be stored by the Schema Registry service.
    """

    AVRO = "Avro"
    """Represents the Apache Avro schema format."""

    JSON = "Json"
    """Represents the JSON schema format."""

    CUSTOM = "Custom"
    """Represents a custom schema format."""

class ApiVersion(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """
    Represents the Schema Registry API version to use for requests.
    """

    V2021_10 = "2021-10"
    V2022_10 = "2022-10"
    """This is the default version."""

DEFAULT_VERSION = ApiVersion.V2022_10
