# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from enum import Enum

from azure.core import CaseInsensitiveEnumMeta

from azure.ai.ml._utils._experimental import experimental


@experimental
class DataColumnType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    STRING = "string"
    INTEGER = "integer"
    LONG = "long"
    FLOAT = "float"
    DOUBLE = "double"
    BINARY = "binary"
    DATETIME = "datetime"
    BOOLEAN = "boolean"

    def __str__(self):
        return self.value
