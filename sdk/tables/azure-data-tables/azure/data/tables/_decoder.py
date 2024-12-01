# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from typing import Any, Mapping, Protocol, Union, Dict, Callable, cast
from datetime import datetime, timezone
from uuid import UUID
from base64 import b64decode

from ._entity import EntityProperty, EdmType, TableEntity

DecoderMapType = Dict[Union[str, EdmType], Callable[[Union[str, bool, int, float]], Any]]


class TablesEntityDatetime(datetime):

    @property
    def tables_service_value(self) -> str:
        # pylint: disable=attribute-defined-outside-init
        try:
            return cast(str, self._service_value)  # type: ignore[attr-defined]
        except AttributeError:
            return ""


NO_ODATA = {
    int: EdmType.INT32,
    str: EdmType.STRING,
    bool: EdmType.BOOLEAN,
    float: EdmType.DOUBLE,
}


class TableEntityDecoder(Protocol):
    def __call__(self, response_data: Mapping[str, Any], /) -> TableEntity: ...


class _TableEntityDecoder:
    def __init__(
        self,
        *,
        trim_timestamp: bool = True,
        trim_odata: bool = True,
        convert_map: DecoderMapType,
    ) -> None:
        self._trim_timestamp = trim_timestamp
        self._trim_odata = trim_odata
        self._edm_types: Dict[EdmType, Callable[[Any], Any]] = {
            EdmType.BINARY: b64decode,
            EdmType.INT32: int,
            EdmType.INT64: self._decode_int64,
            EdmType.DOUBLE: float,
            EdmType.DATETIME: deserialize_iso,
            EdmType.GUID: UUID,
            EdmType.STRING: str,
            EdmType.BOOLEAN: bool,
        }
        self._property_types: Dict[str, Callable[[Any], Any]] = {"Timestamp": deserialize_iso}
        for key, value in convert_map.items():
            if isinstance(key, str):
                self._property_types[key] = value
            else:
                self._edm_types[key] = value

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
        entity._metadata = {"etag": None, "timestamp": None}
        for key, value in response_data.items():
            if key.startswith("odata.") and key != "odata.metadata":
                if self._trim_odata:
                    entity._metadata[key[6:]] = value  # type: ignore[literal-required]
                else:
                    entity[key] = value
            elif key.endswith("@odata.type"):
                continue
            else:
                try:
                    entity[key] = self._property_types[key](value)
                    continue
                except KeyError:
                    pass
                edm_type = EdmType(response_data.get(key + "@odata.type", NO_ODATA[type(value)]))
                entity[key] = self._edm_types[edm_type](value)
        if self._trim_timestamp:
            entity._metadata["timestamp"] = entity.pop("Timestamp")
        return entity

    def _decode_int64(self, value: str) -> EntityProperty:
        return EntityProperty(int(value), EdmType.INT64)


def deserialize_iso(value: str) -> TablesEntityDatetime:
    # pylint:disable=protected-access,assigning-non-slot
    # Cosmos returns this with a decimal point that throws an error on deserialization
    cleaned_value = _clean_up_dotnet_timestamps(value)
    try:
        dt_obj = TablesEntityDatetime.strptime(cleaned_value, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)
    except ValueError:
        dt_obj = TablesEntityDatetime.strptime(cleaned_value, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    dt_obj._service_value = value  # type: ignore[attr-defined]
    return dt_obj


def _clean_up_dotnet_timestamps(value):
    # .NET has more decimal places than Python supports in datetime objects, this truncates
    # values after 6 decimal places.
    value = value.split(".")
    if len(value) == 2:
        ms = value[-1].replace("Z", "")[:6] + "Z"
        return ".".join([value[0], ms])
    return value[0]
