# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from typing import Any, Optional, Mapping, Union, Dict, Callable, cast
from datetime import datetime, timezone
from urllib.parse import quote
from uuid import UUID

from ._common_conversion import _decode_base64_to_bytes
from ._entity import EntityProperty, EdmType, TableEntity, EntityMetadata

DecoderMapType = Dict[EdmType, Callable[[Union[str, bool, int, float]], Any]]


class TablesEntityDatetime(datetime):
    _service_value: str

    @property
    def tables_service_value(self) -> str:
        try:
            return self._service_value
        except AttributeError:
            return ""


NO_ODATA = {
    int: EdmType.INT32,
    str: EdmType.STRING,
    bool: EdmType.BOOLEAN,
    float: EdmType.DOUBLE,
}


class TableEntityDecoder:
    def __init__(
        self,
        *,
        flatten_result_entity: bool = False,
        convert_map: Optional[DecoderMapType] = None,
    ) -> None:
        self.convert_map = convert_map
        self.flatten_result_entity = flatten_result_entity

    def __call__(  # pylint: disable=too-many-branches, too-many-statements
        self, response_data: Mapping[str, Any]
    ) -> TableEntity:
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

        :param response_data: The entity in response.
        :type response_data: Mapping[str, Any]
        :return: An entity dict with additional metadata.
        :rtype: dict[str, Any]
        """
        entity = TableEntity()

        properties = {}
        edmtypes = {}
        odata = {}

        for name, value in response_data.items():
            if name.startswith("odata."):
                odata[name[6:]] = value
            elif name.endswith("@odata.type"):
                edmtypes[name[:-11]] = value
            else:
                properties[name] = value

        # Partitionkey is a known property
        partition_key = properties.pop("PartitionKey", None)
        if partition_key is not None:
            entity["PartitionKey"] = partition_key

        # Timestamp is a known property
        timestamp = properties.pop("Timestamp", None)

        for name, value in properties.items():
            mtype = edmtypes.get(name)

            if not mtype:
                mtype = NO_ODATA[type(value)]

            convert = None
            default_convert = None
            if self.convert_map:
                try:
                    convert = self.convert_map[mtype]
                except KeyError:
                    pass
            if convert:
                new_property = convert(value)
            else:
                try:
                    default_convert = _ENTITY_TO_PYTHON_CONVERSIONS[mtype]
                except KeyError as e:
                    raise TypeError(f"Unsupported edm type: {mtype}") from e
                if default_convert is not None:
                    new_property = default_convert(self, value)
                else:
                    new_property = EntityProperty(mtype, value)
            entity[name] = new_property

        # extract etag from entry
        etag = odata.pop("etag", None)
        odata.pop("metadata", None)
        if timestamp:
            if not etag:
                etag = "W/\"datetime'" + quote(timestamp) + "'\""
            timestamp = self.from_entity_datetime(timestamp)
        odata.update({"etag": etag, "timestamp": timestamp})
        if self.flatten_result_entity:
            for name, value in odata.items():
                entity[name] = value
        entity._metadata = cast(EntityMetadata, odata)  # pylint: disable=protected-access
        return entity

    def from_entity_binary(self, value: str) -> bytes:
        return _decode_base64_to_bytes(value)

    def from_entity_int32(self, value: Union[int, str]) -> int:
        return int(value)

    def from_entity_int64(self, value: str) -> EntityProperty:
        return EntityProperty(int(value), EdmType.INT64)

    def from_entity_datetime(self, value: str) -> Optional[TablesEntityDatetime]:
        return deserialize_iso(value)

    def from_entity_guid(self, value: str) -> UUID:
        return UUID(value)

    def from_entity_str(self, value: Union[str, bytes]) -> str:
        if isinstance(value, bytes):
            return value.decode("utf-8")
        return value


_ENTITY_TO_PYTHON_CONVERSIONS = {
    EdmType.BINARY: TableEntityDecoder.from_entity_binary,
    EdmType.INT32: TableEntityDecoder.from_entity_int32,
    EdmType.INT64: TableEntityDecoder.from_entity_int64,
    EdmType.DOUBLE: lambda _, v: float(v),
    EdmType.DATETIME: TableEntityDecoder.from_entity_datetime,
    EdmType.GUID: TableEntityDecoder.from_entity_guid,
    EdmType.STRING: TableEntityDecoder.from_entity_str,
    EdmType.BOOLEAN: lambda _, v: v,
}


def deserialize_iso(value: Optional[str]) -> Optional[TablesEntityDatetime]:
    if not value:
        return None
    # Cosmos returns this with a decimal point that throws an error on deserialization
    cleaned_value = _clean_up_dotnet_timestamps(value)
    try:
        dt_obj = TablesEntityDatetime.strptime(cleaned_value, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)
    except ValueError:
        dt_obj = TablesEntityDatetime.strptime(cleaned_value, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    dt_obj._service_value = value  # pylint:disable=protected-access,assigning-non-slot
    return dt_obj


def _clean_up_dotnet_timestamps(value):
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
