# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=redefined-builtin,disable=unused-argument

from typing import Dict

from azure.ai.ml._restclient.v2023_02_01_preview.models import IndexColumn, FeatureDataType

from azure.ai.ml.entities._mixins import RestTranslatableMixin
from azure.ai.ml._utils._experimental import experimental

from .data_column_type import DataColumnType

DataColumnTypeMap: Dict[DataColumnType, FeatureDataType] = {
    DataColumnType.string: FeatureDataType.STRING,
    DataColumnType.integer: FeatureDataType.INTEGER,
    DataColumnType.long: FeatureDataType.LONG,
    DataColumnType.float: FeatureDataType.FLOAT,
    DataColumnType.double: FeatureDataType.DOUBLE,
    DataColumnType.binary: FeatureDataType.BINARY,
    DataColumnType.datetime: FeatureDataType.DATETIME,
    DataColumnType.boolean: FeatureDataType.BOOLEAN,
}

FeatureDataTypeMap: Dict[str, DataColumnType] = {
    "String": DataColumnType.string,
    "Integer": DataColumnType.integer,
    "Long": DataColumnType.long,
    "Float": DataColumnType.float,
    "Double": DataColumnType.double,
    "Binary": DataColumnType.binary,
    "Datetime": DataColumnType.datetime,
    "Boolean": DataColumnType.boolean,
}


@experimental
class DataColumn(RestTranslatableMixin):
    """A dataframe column
    :param name: The column name
    :type name: str, required
    :param type: Column data type
    :type type: str, one of [string, integer, long, float, double, binary, datetime, boolean] or
    ~azure.ai.ml.entities.DataColumnType, optional"""

    def __init__(self, *, name: str, type: DataColumnType = None, **kwargs):
        self.name = name
        self.type = type

    def _to_rest_object(self) -> IndexColumn:
        return IndexColumn(column_name=self.name, data_type=DataColumnTypeMap.get(self.type, None))

    @classmethod
    def _from_rest_object(cls, obj: IndexColumn) -> "DataColumn":
        return DataColumn(name=obj.column_name, type=FeatureDataTypeMap.get(obj.data_type, None))
