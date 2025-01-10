# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from dataclasses import fields, is_dataclass
from typing import (
    Any,
    Mapping,
    Union,
    Dict,
    Callable,
    Type,
    is_typeddict,
    Required,
    NotRequired,
    Optional,
    Literal
)
from datetime import timezone
from uuid import UUID
from base64 import b64decode

from ._common_conversion import _annotations, _get_annotation_type
from ._entity import (
    EntityProperty,
    EdmType,
    TableEntity,
    TablesEntityDatetime,
)

DecodeCallable = Union[Callable[[str], Any], Callable[[int], Any], Callable[[bool], Any], Callable[[float], Any]]
DecoderMapType = Mapping[Union[Type, EdmType], DecodeCallable]
NO_ODATA = {
    int: EdmType.INT32,
    str: EdmType.STRING,
    bool: EdmType.BOOLEAN,
    float: EdmType.DOUBLE,
}


def _no_op(_: Any) -> None:
    return None


class TableEntityDecoder:
    def __init__(self, *, convert_map: DecoderMapType, entity_format: Any) -> None:
        self._decode_types: Dict[Union[Type, EdmType], DecodeCallable] = {
            EdmType.BINARY: b64decode,
            EdmType.INT32: int,
            EdmType.INT64: self._decode_int64,
            EdmType.DOUBLE: float,
            EdmType.DATETIME: deserialize_iso,
            EdmType.GUID: UUID,
            EdmType.STRING: str,
            EdmType.BOOLEAN: self._decode_boolean,
        }
        self._decode_types.update(convert_map)
        self._property_types: Dict[str, DecodeCallable] = {"Timestamp": _no_op}
        if entity_format:
            if is_typeddict(entity_format):
                # Scrape type encoding from typeddict defintion
                for property_name, property_type in _annotations(entity_format):
                    property_type = _get_annotation_type(property_type)
                    self._add_property_type(property_name, property_type)
            elif is_dataclass(entity_format):
                # Scrape type decoding from a dataclass definition
                for entity_field in fields(entity_format):
                    property_type = _get_annotation_type(entity_field.type)
                    self._add_property_type(entity_field.name, property_type)
            else:
                # Finally, we'll check if it's a simply dict of properties to types.
                try:
                    for property_name, property_type in entity_format.items():
                        property_type = _get_annotation_type(property_type)
                        self._add_property_type(property_name, property_type)
                except (AttributeError, TypeError):
                    raise TypeError(
                        "The 'entity_format' should be a TypedDict, dataclass definition, "
                        "or dict in the format '{\"PropertyName\": type}'"
                    )

    def _add_property_type(self, property_name: str, property_type: Union[Type, EdmType]) -> None:
        try:
            self._property_types[property_name] = self._decode_types[property_type]
        except KeyError as e:
            raise ValueError(
                f"Unexpected type in entity format: '{property_type}', please provide decoder."
            ) from e   


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
            if key.startswith("odata."):
                # TODO: replace with match statement once we drop 3.9
                if key == "odata.etag":
                    entity._metadata["etag"] = value
                elif key == "odata.type":
                    entity._metadata["type"] = value
                elif key == "odata.id":
                    entity._metadata["id"] = value
                elif key == "odata.editLink":
                    entity._metadata["editLink"] = value
            elif key.endswith("@odata.type"):
                continue
            else:
                if key == "Timestamp":
                    entity._metadata["timestamp"] = deserialize_iso(value)
                try:
                    value = self._property_types[key](value)
                    if value is None:
                        continue
                    entity[key] = value
                except KeyError:
                    edm_type = EdmType(response_data.get(key + "@odata.type", NO_ODATA[type(value)]))
                    entity[key] = self._decode_types[edm_type](value)
        return entity

    def _decode_int64(self, value: str) -> EntityProperty:
        return EntityProperty(int(value), EdmType.INT64)

    def _decode_boolean(self, value: Union[str, bool, int]) -> bool:
        try:
            value = value.lower()  # type: ignore[union-attr]
        except AttributeError:
            return bool(value)
        if value == "true":
            return True
        if value == "false":
            return False
        return bool(value)


def deserialize_iso(value: str) -> TablesEntityDatetime:
    # pylint:disable=protected-access,assigning-non-slot
    # Cosmos returns this with a decimal point that throws an error on deserialization
    cleaned_value = _clean_up_dotnet_timestamps(value)
    try:
        dt_obj = TablesEntityDatetime.strptime(cleaned_value, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)
    except ValueError:
        dt_obj = TablesEntityDatetime.strptime(cleaned_value, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    dt_obj._service_value = value
    return dt_obj


def _clean_up_dotnet_timestamps(value):
    # .NET has more decimal places than Python supports in datetime objects, this truncates
    # values after 6 decimal places.
    value = value.split(".")
    if len(value) == 2:
        ms = value[-1].replace("Z", "")[:6] + "Z"
        return ".".join([value[0], ms])
    return value[0]
