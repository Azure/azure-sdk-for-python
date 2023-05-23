# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from enum import Enum
from typing import Any

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

    @classmethod
    def _missing_(cls, value: object) -> Any:
        return super()._missing_(value)
