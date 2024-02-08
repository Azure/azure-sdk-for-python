# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from enum import Enum
from typing import Any

from azure.core import CaseInsensitiveEnumMeta


class DataColumnType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Dataframe Column Type Enum

    .. admonition:: Example:

        .. literalinclude:: ../samples/ml_samples_featurestore.py
            :start-after: [START configure_feature_store_entity]
            :end-before: [END configure_feature_store_entity]
            :language: Python
            :dedent: 8
            :caption: Using DataColumnType when instantiating a DataColumn
    """

    STRING = "string"
    INTEGER = "integer"
    LONG = "long"
    FLOAT = "float"
    DOUBLE = "double"
    BINARY = "binary"
    DATETIME = "datetime"
    BOOLEAN = "boolean"

    def __str__(self) -> Any:
        return self.value
