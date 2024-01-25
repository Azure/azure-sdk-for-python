# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=redefined-builtin,disable=unused-argument

from typing import Any, Dict, Optional, Union

from azure.ai.ml._restclient.v2023_10_01.models import FeatureDataType, IndexColumn
from azure.ai.ml.entities._mixins import RestTranslatableMixin
from azure.ai.ml.exceptions import ErrorCategory, ErrorTarget, ValidationErrorType, ValidationException

from .data_column_type import DataColumnType

DataColumnTypeMap: Dict[DataColumnType, FeatureDataType] = {
    DataColumnType.STRING: FeatureDataType.STRING,
    DataColumnType.INTEGER: FeatureDataType.INTEGER,
    DataColumnType.LONG: FeatureDataType.LONG,
    DataColumnType.FLOAT: FeatureDataType.FLOAT,
    DataColumnType.DOUBLE: FeatureDataType.DOUBLE,
    DataColumnType.BINARY: FeatureDataType.BINARY,
    DataColumnType.DATETIME: FeatureDataType.DATETIME,
    DataColumnType.BOOLEAN: FeatureDataType.BOOLEAN,
}

FeatureDataTypeMap: Dict[str, DataColumnType] = {
    "String": DataColumnType.STRING,
    "Integer": DataColumnType.INTEGER,
    "Long": DataColumnType.LONG,
    "Float": DataColumnType.FLOAT,
    "Double": DataColumnType.DOUBLE,
    "Binary": DataColumnType.BINARY,
    "Datetime": DataColumnType.DATETIME,
    "Boolean": DataColumnType.BOOLEAN,
}


class DataColumn(RestTranslatableMixin):
    """A dataframe column

    :param name: The column name
    :type name: str
    :param type: The column data type. Defaults to None.
    :type type: Optional[union[str, ~azure.ai.ml.entities.DataColumnType]]
    :param kwargs: A dictionary of additional configuration parameters.
    :type kwargs: dict
    :raises ValidationException: Raised if type is specified and is not a valid DataColumnType or str.

    .. admonition:: Example:

        .. literalinclude:: ../samples/ml_samples_featurestore.py
            :start-after: [START configure_feature_store_entity]
            :end-before: [END configure_feature_store_entity]
            :language: Python
            :dedent: 8
            :caption: Using DataColumn when creating an index column for a feature store entity
    """

    def __init__(self, *, name: str, type: Optional[Union[str, DataColumnType]] = None, **kwargs: Any):
        if isinstance(type, str):
            type = DataColumnType[type]
        elif not isinstance(type, DataColumnType):
            msg = f"Type should be DataColumnType enum string or enum type, found {type}"
            raise ValidationException(
                message=msg,
                no_personal_data_message=msg,
                error_type=ValidationErrorType.INVALID_VALUE,
                target=ErrorTarget.DATA,
                error_category=ErrorCategory.USER_ERROR,
            )

        self.name = name
        self.type = type

    def _to_rest_object(self) -> IndexColumn:
        return IndexColumn(column_name=self.name, data_type=DataColumnTypeMap.get(self.type, None))

    @classmethod
    def _from_rest_object(cls, obj: IndexColumn) -> "DataColumn":
        return DataColumn(name=obj.column_name, type=FeatureDataTypeMap.get(obj.data_type, None))
