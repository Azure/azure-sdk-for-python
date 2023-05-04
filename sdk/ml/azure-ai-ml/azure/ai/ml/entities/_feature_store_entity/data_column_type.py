# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from enum import Enum

from azure.core import CaseInsensitiveEnumMeta
from azure.ai.ml._utils._experimental import experimental


@experimental
class DataColumnType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    STRING = 1
    INTEGER = 2
    LONG = 3
    FLOAT = 4
    DOUBLE = 5
    BINARY = 6
    DATETIME = 7
    BOOLEAN = 8
