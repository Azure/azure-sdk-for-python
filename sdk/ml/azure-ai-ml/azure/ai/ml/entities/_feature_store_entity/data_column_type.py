# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from enum import Enum

from azure.core import CaseInsensitiveEnumMeta
from azure.ai.ml._utils._experimental import experimental


@experimental
class DataColumnType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    STRING = 'STRING'
    INTEGER = 'INTEGER'
    LONG = 'LONG'
    FLOAT = 'FLOAT'
    DOUBLE = 'DOUBLE'
    BINARY = 'BINARY'
    DATETIME = 'DATETIME'
    BOOLEAN = 'BOOLEAN'
