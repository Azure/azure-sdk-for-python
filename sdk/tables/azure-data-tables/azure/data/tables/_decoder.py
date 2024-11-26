# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from typing import Any, Optional, Tuple, Mapping, Union, TypeVar, Dict, Type, Callable
from datetime import datetime, timezone
from urllib.parse import quote
from uuid import UUID

from ._common_conversion import _decode_base64_to_bytes
from ._entity import EntityProperty, EdmType, TableEntity, EntityMetadata


class TablesEntityDatetime(datetime):
    @property
    def tables_service_value(self):
        try:
            return self._service_value
        except AttributeError:
            return ""


class TableEntityDecoder():
    def __init__(
        self,
        convert_map: Optional[Dict[Union[Type, EdmType], Callable[[Any], Tuple[Optional[EdmType], Any]]]],
        flatten_result_entity: bool
    ) -> None:
        self.convert_map = convert_map
        self.flatten_result_entity = flatten_result_entity

    def __call__(self, entry_element: Union[TableEntity, Mapping[str, Any]]) -> Dict[str, Union[str, int, float, bool]]:
        """Convert json response to entity.
        The entity format is:
        {
        "Address":"Mountain View",
        "Age":23,
        "AmountDue":200.23,
        "CustomerCode@odata.type":"Edm.Guid",
        "CustomerCode":"c9da6455-213d-42c9-9a79-3e9149a57833",
        "CustomerSince@odata.type":"Edm.DateTime",
        "CustomerSince":"2008-07-10T00:00:00",
        "IsActive":true,
        "NumberOfOrders@odata.type":"Edm.Int64",
        "NumberOfOrders":"255",
        "PartitionKey":"my_partition_key",
        "RowKey":"my_row_key"
        }

        :param entry_element: The entity in response.
        :type entry_element: Mapping[str, Any]
        :return: An entity dict with additional metadata.
        :rtype: dict[str, Any]
        """
        if self.flatten_result_entity:
            entity = {}
        else:
            entity = TableEntity()

        properties = {}
        edmtypes = {}
        odata = {}

        for name, value in entry_element.items():
            if name.startswith("odata."):
                odata[name[6:]] = value
            elif name.endswith("@odata.type"):
                edmtypes[name[:-11]] = value
            else:
                properties[name] = value

        # TODO: investigate whether we can entirely remove lines 160-168
        # Partition key is a known property
        partition_key = properties.pop("PartitionKey", None)
        if partition_key is not None:
            entity["PartitionKey"] = partition_key

        # Row key is a known property
        row_key = properties.pop("RowKey", None)
        if row_key is not None:
            entity["RowKey"] = row_key

        # Timestamp is a known property
        timestamp = properties.pop("Timestamp", None)

        for name, value in properties.items():
            mtype = edmtypes.get(name)

            # Add type for Int32/64
            if isinstance(value, int) and mtype is None:
                mtype = EdmType.INT32

                if value >= 2**31 or value < (-(2**31)):
                    mtype = EdmType.INT64

            # Add type for String
            if isinstance(value, str) and mtype is None:
                mtype = EdmType.STRING

            # no type info, property should parse automatically
            if not mtype:
                entity[name] = value
            elif mtype in [EdmType.STRING, EdmType.INT32]:
                entity[name] = value
            else:  # need an object to hold the property
                convert = None
                if self.convert_map:
                    convert = self.convert_map.get(mtype)
                if convert:
                    new_property = convert(value)
                else:
                    convert = _ENTITY_TO_PYTHON_CONVERSIONS.get(mtype)
                    if convert:
                        new_property = convert(self, value)
                    else:
                        new_property = EntityProperty(mtype, value)
                entity[name] = new_property

        # extract etag from entry
        etag = odata.pop("etag", None)
        odata.pop("metadata", None)
        if timestamp:
            if not etag:
                etag = "W/\"datetime'" + quote(timestamp) + "'\""
            timestamp = self._from_entity_datetime(timestamp)
        odata.update({"etag": etag, "timestamp": timestamp})
        if self.flatten_result_entity:
            for name, value in odata.items():
                entity[name] = value
        else:
            entity._metadata = odata  # pylint: disable=protected-access
        return entity


    def get_enum_value(self, value):
        if value is None or value in ["None", ""]:
            return None
        try:
            return value.value
        except AttributeError:
            return value


    def _from_entity_binary(self, value: str) -> bytes:
        return _decode_base64_to_bytes(value)


    def _from_entity_int32(self, value: str) -> int:
        return int(value)


    def _from_entity_int64(self, value: str) -> EntityProperty:
        return EntityProperty(int(value), EdmType.INT64)


    def _from_entity_datetime(self, value):
        # Cosmos returns this with a decimal point that throws an error on deserialization
        cleaned_value = self.clean_up_dotnet_timestamps(value)
        try:
            dt_obj = TablesEntityDatetime.strptime(cleaned_value, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)
        except ValueError:
            dt_obj = TablesEntityDatetime.strptime(cleaned_value, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
        dt_obj._service_value = value  # pylint:disable=protected-access,assigning-non-slot
        return dt_obj


    def clean_up_dotnet_timestamps(self, value):
        # .NET has more decimal places than Python supports in datetime objects, this truncates
        # values after 6 decimal places.
        value = value.split(".")
        ms = ""
        if len(value) == 2:
            ms = value[-1].replace("Z", "")
            if len(ms) > 6:
                ms = ms[:6]
            ms = ms + "Z"
            return ".".join([value[0], ms])

        return value[0]


    def deserialize_iso(self, value):
        if not value:
            return value
        return self._from_entity_datetime(value)


    def _from_entity_guid(self, value):
        return UUID(value)


    def _from_entity_str(self, value: Union[str, bytes]) -> str:
        if isinstance(value, bytes):
            return value.decode("utf-8")
        return value

_ENTITY_TO_PYTHON_CONVERSIONS = {
    EdmType.BINARY: TableEntityDecoder._from_entity_binary,
    EdmType.INT32: TableEntityDecoder._from_entity_int32,
    EdmType.INT64: TableEntityDecoder._from_entity_int64,
    EdmType.DOUBLE: lambda _, v: float(v),
    EdmType.DATETIME: TableEntityDecoder._from_entity_datetime,
    EdmType.GUID: TableEntityDecoder._from_entity_guid,
    EdmType.STRING: TableEntityDecoder._from_entity_str,
}

def deserialize_iso(value):
    if not value:
        return value
    return TableEntityDecoder()._from_entity_datetime(value)
