# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from typing import Any, Optional, Tuple, Mapping, Union, Dict, Type, Callable, MutableMapping
from uuid import UUID
from datetime import datetime
from enum import Enum
from math import isnan

from ._entity import EdmType, TableEntity, EntityProperty
from ._common_conversion import _encode_base64, _to_utc_datetime
from ._constants import MAX_INT64, MIN_INT64, _ERROR_VALUE_TOO_LARGE

_ODATA_SUFFIX = "@odata.type"
EncoderMapType = MutableMapping[
    Union[Type, EdmType], Callable[[Any], Tuple[Optional[EdmType], Union[str, bool, int, float, None]]]
]


class TableEntityEncoder:
    def __init__(self, *, convert_map: Optional[EncoderMapType] = None) -> None:
        self.convert_map = convert_map

    def __call__(self, entity: Union[TableEntity, Mapping[str, Any]]) -> Dict[str, Union[str, int, float, bool]]:
        """Encode an entity object into JSON format to send out.
        The entity format is:

        .. code-block:: json

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

        :param entity: A table entity.
        :type entity: ~azure.data.tables.TableEntity or Mapping[str, Any]
        :return: An entity with property's metadata in JSON format.
        :rtype: dict
        """
        encoded = {}
        for key, value in entity.items():
            if value is None:
                edm_type = None
            else:
                # Find the converter function from customer provided convert_map first,
                # if not find, try with the default convert_map _PYTHON_TO_ENTITY_CONVERSIONS
                convert = None
                default_convert = None
                if self.convert_map:
                    try:
                        convert = self.convert_map[type(value)]
                    except KeyError:
                        if isinstance(value, Enum) and self.convert_map.get(Enum):
                            convert = self.convert_map[Enum]
                        if isinstance(value, datetime) and self.convert_map.get(datetime):
                            convert = self.convert_map[datetime]
                if convert:
                    edm_type, value = convert(value)
                else:
                    try:
                        default_convert = _PYTHON_TO_ENTITY_CONVERSIONS[type(value)]
                    except KeyError:
                        if isinstance(value, Enum):
                            default_convert = _PYTHON_TO_ENTITY_CONVERSIONS[Enum]
                        if isinstance(value, datetime):
                            default_convert = _PYTHON_TO_ENTITY_CONVERSIONS[datetime]
                    if default_convert:
                        edm_type, value = default_convert(self, value)  # mypy: ignore[call-arg]
                    else:
                        raise TypeError(f"No encoder found for value '{value}' of type '{type(value)}'.")
            try:
                odata = f"{key}{_ODATA_SUFFIX}"
                if _ODATA_SUFFIX in key or odata in entity:
                    encoded[key] = value
                    continue
                # The edm type is decided by value
                # For example, when value=EntityProperty(str(uuid.uuid4), "Edm.Guid"),
                # the type is string instead of Guid after encoded
                if edm_type:
                    encoded[odata] = edm_type.value if hasattr(edm_type, "value") else edm_type
            except TypeError:
                pass
            encoded[key] = value
        return encoded

    def to_entity_binary(self, value):
        return EdmType.BINARY, _encode_base64(value)

    def to_entity_bool(self, value):
        return None, value

    def to_entity_datetime(self, value):
        if isinstance(value, str):
            # Pass a serialized datetime straight through
            return EdmType.DATETIME, value
        try:
            # Check is this is a 'round-trip' datetime, and if so
            # pass through the original value.
            if value.tables_service_value:
                return EdmType.DATETIME, value.tables_service_value
        except AttributeError:
            pass
        return EdmType.DATETIME, _to_utc_datetime(value)

    def to_entity_float(self, value):
        if isinstance(value, str):
            # Pass a serialized value straight through
            return EdmType.DOUBLE, value
        if isnan(value):
            return EdmType.DOUBLE, "NaN"
        if value == float("inf"):
            return EdmType.DOUBLE, "Infinity"
        if value == float("-inf"):
            return EdmType.DOUBLE, "-Infinity"
        return EdmType.DOUBLE, value

    def to_entity_guid(self, value):
        return EdmType.GUID, str(value)

    def to_entity_int32(self, value):
        int_value = int(value)
        if int_value >= MAX_INT64 or int_value < MIN_INT64:
            raise TypeError(_ERROR_VALUE_TOO_LARGE.format(str(value), EdmType.INT32))
        return None, int_value

    def to_entity_int64(self, value):
        return EdmType.INT64, str(value)

    def to_entity_str(self, value):
        return None, str(value)

    def to_entity_enum(self, value):
        if self.convert_map:
            try:
                convert = self.convert_map[type(value.value)]
                return convert(value.value)
            except KeyError:
                pass
        try:
            convert = _PYTHON_TO_ENTITY_CONVERSIONS[type(value.value)]
            return convert(self, value.value)
        except KeyError as e:
            raise TypeError("Unsupported enum type") from e

    def to_entity_tuple(self, value):
        if len(value) == 2:
            unencoded_value = value[0]
            edm_type = EdmType(value[1])  # should raise error for unknown edmtypes
        else:
            raise ValueError("Tuple should have 2 items")
        if unencoded_value is None:
            return edm_type, unencoded_value
        if self.convert_map:
            try:
                convert = self.convert_map[edm_type]
                return convert(unencoded_value)
            except KeyError:
                pass
        try:
            convert = _PYTHON_TO_ENTITY_CONVERSIONS[edm_type]
            return convert(self, unencoded_value)
        except KeyError as e:
            raise TypeError("Unsupported tuple type") from e


# Conversion from Python type to a function which returns a tuple of the
# type string and content string.
# And conversion from Edm type to a function which returns a tuple of the
# type string and content string. These conversions are only used when the
# full EdmProperty tuple is specified. As a result, in this case we ALWAYS add
# the Odata type tag, even for field types where it's not necessary. This is why
# boolean and int32 have special processing below, as we would not normally add the
# Odata type tags for these to keep payload size minimal.
# This is also necessary for CLI compatibility.
_PYTHON_TO_ENTITY_CONVERSIONS = {
    int: TableEntityEncoder.to_entity_int32,
    bool: TableEntityEncoder.to_entity_bool,
    datetime: TableEntityEncoder.to_entity_datetime,
    float: TableEntityEncoder.to_entity_float,
    UUID: TableEntityEncoder.to_entity_guid,
    Enum: TableEntityEncoder.to_entity_enum,
    str: TableEntityEncoder.to_entity_str,
    bytes: TableEntityEncoder.to_entity_binary,
    tuple: TableEntityEncoder.to_entity_tuple,
    EntityProperty: TableEntityEncoder.to_entity_tuple,
    EdmType.BINARY: TableEntityEncoder.to_entity_binary,
    EdmType.BOOLEAN: lambda _, v: (EdmType.BOOLEAN, v),
    EdmType.DATETIME: TableEntityEncoder.to_entity_datetime,
    EdmType.DOUBLE: TableEntityEncoder.to_entity_float,
    EdmType.GUID: TableEntityEncoder.to_entity_guid,
    EdmType.INT32: lambda _, v: (EdmType.INT32, TableEntityEncoder.to_entity_int32(_, int(v))[1]),
    EdmType.INT64: TableEntityEncoder.to_entity_int64,
    EdmType.STRING: lambda _, v: (EdmType.STRING, str(v)),
}
