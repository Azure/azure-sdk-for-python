# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from typing import (
    Any,
    ChainMap,
    Optional,
    SupportsBytes,
    SupportsFloat,
    SupportsInt,
    Tuple,
    Mapping,
    Union,
    Dict,
    Type,
    Callable,
    MutableMapping,
    cast,
)
from uuid import UUID
from datetime import datetime
from enum import Enum
from math import isnan

from ._entity import EdmType
from ._decoder import TablesEntityDatetime
from ._common_conversion import _encode_base64, _to_utc_datetime
from ._constants import MAX_INT64, MIN_INT64, _ERROR_VALUE_TOO_LARGE

_ODATA_SUFFIX = "@odata.type"
SupportedDataTypes = Union[str, bool, int, float, None]
EncodeCallable = Callable[[str, Any], Tuple[Optional[EdmType], SupportedDataTypes]]
EncoderMapType = MutableMapping[Union[Type, EdmType, str], EncodeCallable]


class EdmTypes(ChainMap[Union[Type, EdmType, str], EncodeCallable]):
    def __setitem__(self, key: Union[Type, EdmType, str], value: EncodeCallable):
        if isinstance(key, EdmType):
            self.maps[1][key] = value
        elif isinstance(key, str):
            self.maps[2][key] = value
        else:
            self.maps[0][key] = value

    def __delitem__(self, key: Union[Type, EdmType, str]):
        if isinstance(key, EdmType):
            if key in self.maps[1]:
                del self.maps[1][key]
                return
        elif isinstance(key, str):
            if key in self.maps[2]:
                del self.maps[2][key]
                return
        else:
            if key in self.maps[0]:
                del self.maps[0][key]
        raise KeyError(key)


class TableEntityEncoder:
    types: EncoderMapType

    def __init__(self, *, convert_map: EncoderMapType) -> None:
        self._property_types: Dict[str, EncodeCallable] = {}
        self._obj_types: Dict[Type, EncodeCallable] = {
            int: TableEntityEncoder.int32,
            bool: TableEntityEncoder.boolean,
            datetime: TableEntityEncoder.datetime,
            TablesEntityDatetime: TableEntityEncoder.datetime,
            float: TableEntityEncoder.double,
            UUID: TableEntityEncoder.guid,
            str: TableEntityEncoder.string,
            bytes: TableEntityEncoder.binary,
        }
        self._edm_types: MutableMapping[EdmType, EncodeCallable] = {
            EdmType.BINARY: TableEntityEncoder.binary,
            EdmType.BOOLEAN: TableEntityEncoder.boolean,
            EdmType.DATETIME: TableEntityEncoder.datetime,
            EdmType.DOUBLE: TableEntityEncoder.double,
            EdmType.GUID: TableEntityEncoder.guid,
            EdmType.INT32: TableEntityEncoder.int32,
            EdmType.INT64: TableEntityEncoder.int64,
            EdmType.STRING: TableEntityEncoder.string,
        }
        self.types = EdmTypes(
            cast(EncoderMapType, self._obj_types),
            cast(EncoderMapType, self._edm_types),
            cast(EncoderMapType, self._property_types),
        )
        self.types.update(convert_map)

    def __call__(self, entity: Mapping[str, Any]) -> Dict[str, SupportedDataTypes]:
        encoded = {}
        for key, value in entity.items():
            odata_key = f"{key}{_ODATA_SUFFIX}"
            try:
                if value is None or key.endswith(_ODATA_SUFFIX):
                    encoded[key] = value
                    continue
            except AttributeError:
                pass
            if odata_key in entity:
                encoded[key] = self._edm_types[EdmType(entity[odata_key])](key, value)[1]
                continue
            edm_type, encoded_value = self._encode(key, value)
            encoded[key] = encoded_value
            if edm_type:
                encoded[odata_key] = edm_type.value
        return encoded

    def _encode(self, key: str, value: Any) -> Tuple[Optional[EdmType], SupportedDataTypes]:
        try:
            return self._property_types[key](key, value)
        except KeyError:
            pass
        try:
            return self._obj_types[type(value)](key, value)
        except KeyError as e:
            if isinstance(value, tuple):
                return self._entity_tuple(key, value)
            if isinstance(value, Enum):
                return self._encode(key, value.value)
            for obj_type, converter in self._obj_types.items():
                if isinstance(value, obj_type):
                    return converter(key, value)
            raise TypeError(f"No encoder found for value '{value}' of type '{type(value)}'.") from e

    def _entity_tuple(self, key: str, value: Tuple[Any, Union[str, EdmType]]) -> Tuple[EdmType, SupportedDataTypes]:
        if len(value) == 2:
            unencoded_value = value[0]
            unencoded_edm = EdmType(value[1])  # should raise error for unknown edmtypes
        else:
            raise ValueError("Tuple should have 2 items")
        if unencoded_value is None:
            return unencoded_edm, unencoded_value
        encoded_edm, encoded_value = self._edm_types[unencoded_edm](key, unencoded_value)
        return encoded_edm or unencoded_edm, encoded_value

    @staticmethod
    def binary(*value: Union[str, SupportsBytes]) -> Tuple[EdmType, str]:
        return EdmType.BINARY, _encode_base64(value[-1])

    @staticmethod
    def boolean(*value: Union[str, bool]) -> Tuple[None, Union[bool, str]]:
        try:
            return None, value[-1]
        except IndexError as e:
            raise TypeError("to_bool() missing 1 required positional argument: 'value'") from e

    @staticmethod
    def datetime(*value: Union[str, datetime]) -> Tuple[EdmType, str]:
        try:
            dt_value = value[-1]
        except IndexError as e:
            raise TypeError("to_datetime() missing 1 required positional argument: 'value'") from e
        if isinstance(dt_value, str):
            # Pass a serialized datetime straight through
            return EdmType.DATETIME, dt_value
        if isinstance(dt_value, TablesEntityDatetime) and dt_value.tables_service_value:
            # Check is this is a 'round-trip' datetime, and if so
            # pass through the original value.
            return EdmType.DATETIME, dt_value.tables_service_value
        return EdmType.DATETIME, _to_utc_datetime(dt_value)

    @staticmethod
    def double(*value: Union[str, SupportsFloat]) -> Tuple[EdmType, Union[str, float]]:
        try:
            float_value = value[-1]
        except IndexError as e:
            raise TypeError("to_float() missing 1 required positional argument: 'value'") from e
        if isinstance(float_value, str):
            # Pass a serialized value straight through
            return EdmType.DOUBLE, float_value
        if isnan(float_value):
            return EdmType.DOUBLE, "NaN"
        if float_value == float("inf"):
            return EdmType.DOUBLE, "Infinity"
        if float_value == float("-inf"):
            return EdmType.DOUBLE, "-Infinity"
        return EdmType.DOUBLE, float(float_value)

    @staticmethod
    def guid(*value: Any) -> Tuple[EdmType, str]:
        try:
            return EdmType.GUID, str(value[-1])
        except IndexError as e:
            raise TypeError("to_guid() missing 1 required positional argument: 'value'") from e

    @staticmethod
    def int32(*value: Union[str, SupportsInt]) -> Tuple[None, int]:
        try:
            int_value = int(value[-1])
        except IndexError as e:
            raise TypeError("to_int32() missing 1 required positional argument: 'value'") from e
        if int_value >= MAX_INT64 or int_value < MIN_INT64:
            raise TypeError(_ERROR_VALUE_TOO_LARGE.format(str(value), EdmType.INT32))
        return None, int_value

    @staticmethod
    def int64(*value: Any) -> Tuple[EdmType, str]:
        try:
            return EdmType.INT64, str(value[-1])
        except IndexError as e:
            raise TypeError("to_int64() missing 1 required positional argument: 'value'") from e

    @staticmethod
    def string(*value: Any) -> Tuple[None, str]:
        try:
            return None, str(value[-1])
        except IndexError as e:
            raise TypeError("to_str() missing 1 required positional argument: 'value'") from e
