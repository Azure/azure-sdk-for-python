# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=redefined-builtin,disable=unused-argument

from typing import Dict

from azure.ai.ml._restclient.v2023_02_01_preview.models import IndexColumn, FeatureDataType

from azure.ai.ml.entities._mixins import RestTranslatableMixin
from azure.ai.ml._utils._experimental import experimental

from .data_column_type import _DataColumnType

DataColumnTypeMap: Dict[_DataColumnType, FeatureDataType] = {
    _DataColumnType.string: FeatureDataType.STRING,
    _DataColumnType.integer: FeatureDataType.INTEGER,
    _DataColumnType.long: FeatureDataType.LONG,
    _DataColumnType.float: FeatureDataType.FLOAT,
    _DataColumnType.double: FeatureDataType.DOUBLE,
    _DataColumnType.binary: FeatureDataType.BINARY,
    _DataColumnType.datetime: FeatureDataType.DATETIME,
    _DataColumnType.boolean: FeatureDataType.BOOLEAN,
}

FeatureDataTypeMap: Dict[str, _DataColumnType] = {
    "String": _DataColumnType.string,
    "Integer": _DataColumnType.integer,
    "Long": _DataColumnType.long,
    "Float": _DataColumnType.float,
    "Double": _DataColumnType.double,
    "Binary": _DataColumnType.binary,
    "Datetime": _DataColumnType.datetime,
    "Boolean": _DataColumnType.boolean,
}


@experimental
class _DataColumn(RestTranslatableMixin):
    """A dataframe column
    :param name: The column name
    :type name: str, required
    :param type: Column data type
    :type type: str, one of [string, integer, long, float, double, binary, datetime, boolean] or
    ~azure.ai.ml.entities._DataColumnType, optional"""

    def __init__(self, *, name: str, type: _DataColumnType = None, **kwargs):
        self.name = name
        self.type = type

    def _to_rest_object(self) -> IndexColumn:
        return IndexColumn(column_name=self.name, data_type=DataColumnTypeMap.get(self.type, None))

    @classmethod
    def _from_rest_object(cls, obj: IndexColumn) -> "_DataColumn":
        return _DataColumn(name=obj.column_name, type=FeatureDataTypeMap.get(obj.data_type, None))
