# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from enum import Enum

from azure.ai.ml._utils._experimental import experimental
from azure.core import CaseInsensitiveEnumMeta


@experimental
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

    def __str__(self):
        return self.value
