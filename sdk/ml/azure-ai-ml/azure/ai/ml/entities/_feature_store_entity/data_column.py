# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=redefined-builtin,disable=unused-argument

from typing import Dict, Optional, Union

from azure.ai.ml._restclient.v2023_02_01_preview.models import FeatureDataType, IndexColumn
from azure.ai.ml._utils._experimental import experimental
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


@experimental
class DataColumn(RestTranslatableMixin):
    """A dataframe column
    :param name: The column name
    :type name: str, required
    :param type: Column data type
    :type type: str, one of [string, integer, long, float, double, binary, datetime, boolean] or
    ~azure.ai.ml.entities.DataColumnType, optional"""

    def __init__(self, *, name: str, type: Optional[Union[str, DataColumnType]] = None, **kwargs):
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
