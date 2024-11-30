# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from typing import (
    Any,
    Optional,
    Protocol,
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
    overload,
)
from uuid import UUID
from datetime import datetime
from enum import Enum
from math import isnan
from json import JSONEncoder
from base64 import b64encode

from ._entity import EdmType, EntityProperty
from ._decoder import TablesEntityDatetime
from ._common_conversion import _encode_base64, _to_utc_datetime, SupportedDataTypes
from ._constants import MAX_INT64, MIN_INT64, _ERROR_VALUE_TOO_LARGE

_ODATA_SUFFIX = "@odata.type"

EncodeCallable = Callable[[str, Any], Tuple[Optional[EdmType], SupportedDataTypes]]
EncoderMapType = MutableMapping[Union[Type, str], Union[EncodeCallable, EdmType]]


class TableEntityJSONEncoder(JSONEncoder):
    """A JSON encoder that's capable of serializing datetime objects and bytes."""

    def default(self, o: Any) -> Any:
        if isinstance(o, (bytes, bytearray)):
            return b64encode(o).decode()
        if isinstance(o, datetime):
            if isinstance(o, TablesEntityDatetime) and o.tables_service_value:
                # Check is this is a 'round-trip' datetime, and if so
                # pass through the original value.
                return o.tables_service_value
            return _to_utc_datetime(o)
        return super().default(o)


class TableEntityEncoder(Protocol):
    @overload
    def __call__(self, entity: Mapping[str, Any], /) -> Dict[str, SupportedDataTypes]: ...
    @overload
    def __call__(self, key: str, value: Any, /) -> Tuple[Optional[EdmType], Any]: ...
    def __call__(self, *args): ...


class _TableEntityEncoder(TableEntityEncoder):

    def __init__(self, *, convert_map: EncoderMapType) -> None:
        self._property_types: Dict[str, Union[EncodeCallable, EdmType]] = {}
        self._obj_types: Dict[Type, Union[EncodeCallable, EdmType]] = {
            int: EdmType.INT32,
            bool: EdmType.BOOLEAN,
            datetime: EdmType.DATETIME,
            TablesEntityDatetime: EdmType.DATETIME,
            float: EdmType.DOUBLE,
            UUID: EdmType.GUID,
            str: EdmType.STRING,
            bytes: EdmType.BINARY,
            tuple: self._encode_tuple,
            EntityProperty: self._encode_tuple,
        }
        self._edm_types: MutableMapping[EdmType, Callable[[Any], Tuple[Optional[EdmType], SupportedDataTypes]]] = {
            EdmType.BINARY: self._encode_binary,
            EdmType.BOOLEAN: self._encode_boolean,
            EdmType.DATETIME: self._encode_datetime,
            EdmType.DOUBLE: self._encode_double,
            EdmType.GUID: self._encode_guid,
            EdmType.INT32: self._encode_int32,
            EdmType.INT64: self._encode_int64,
            EdmType.STRING: self._encode_string,
        }
        for key, value in convert_map.items():
            if isinstance(key, str):
                self._property_types[key] = value
            else:
                self._obj_types[key] = value

    @overload
    def __call__(self, entity: Mapping[str, Any], /) -> Dict[str, SupportedDataTypes]: ...
    @overload
    def __call__(self, key: str, value: Any, /) -> Tuple[Optional[EdmType], Any]: ...
    def __call__(self, *args):
        if len(args) == 1:
            entity = cast(Mapping[str, Any], args[0])
            encoded = {}
            for key, value in entity.items():
                odata_key = f"{key}{_ODATA_SUFFIX}"
                try:
                    if value is None or key.endswith(_ODATA_SUFFIX) or odata_key in entity:
                        encoded[key] = value
                        continue
                except AttributeError:
                    pass
                try:
                    edm_type, encoded_value = self._encode_by_name(key, value)
                except KeyError:
                    edm_type, encoded_value = self._encode_by_type(key, value)
                encoded[key] = encoded_value
                if edm_type:
                    encoded[odata_key] = edm_type.value
            return encoded
        if len(args) == 2:
            key, value = cast(Tuple[str, Any], args)  # pylint:disable=unbalanced-tuple-unpacking
            return self._encode_by_name(key, value)
        raise TypeError(f"Expected either 1 or 2 positional parameters, received: {len(args)}.")

    def _convert(
        self, key: str, value: Any, converter: Union[EdmType, EncodeCallable]
    ) -> Tuple[Optional[EdmType], SupportedDataTypes]:
        if isinstance(converter, EdmType):
            return self._edm_types[converter](value)
        return converter(key, value)

    def _encode_by_name(self, key: str, value: Any) -> Tuple[Optional[EdmType], SupportedDataTypes]:
        try:
            return self._convert(key, value, self._property_types[key])
        except KeyError as e:
            raise KeyError(f"No property encoder found for value '{key}'.") from e

    def _encode_by_type(self, key: str, value: Any) -> Tuple[Optional[EdmType], SupportedDataTypes]:
        try:
            return self._convert(key, value, self._obj_types[type(value)])
        except KeyError as e:
            # if isinstance(value, tuple):
            #     return self._entity_tuple(value)
            for obj_type, converter in self._obj_types.items():
                if isinstance(value, obj_type):
                    return self._convert(key, value, converter)
            if isinstance(value, Enum):
                return self._encode_by_type(key, value.value)
            raise TypeError(f"No encoder found for value '{value}' of type '{type(value)}'.") from e

    def _encode_tuple(self, _: str, value: Tuple[Any, Union[str, EdmType]]) -> Tuple[EdmType, SupportedDataTypes]:
        if len(value) == 2:
            unencoded_value = value[0]
            unencoded_edm = EdmType(value[1])  # should raise error for unknown edmtypes
        else:
            raise ValueError("Tuple should have 2 items")
        if unencoded_value is None:
            return unencoded_edm, unencoded_value
        encoded_edm, encoded_value = self._edm_types[unencoded_edm](unencoded_value)
        return encoded_edm or unencoded_edm, encoded_value

    def _encode_binary(self, value: Union[str, SupportsBytes]) -> Tuple[EdmType, str]:
        return EdmType.BINARY, _encode_base64(value)

    def _encode_boolean(self, value: Union[str, bool]) -> Tuple[None, Union[bool, str]]:
        return None, value

    def _encode_datetime(self, value: Union[str, datetime]) -> Tuple[EdmType, Union[str, datetime]]:
        return EdmType.DATETIME, value

    def _encode_double(self, value: Union[str, SupportsFloat]) -> Tuple[EdmType, Union[str, float]]:
        if isinstance(value, str):
            # Pass a serialized value straight through
            return EdmType.DOUBLE, value
        if isnan(value):
            return EdmType.DOUBLE, "NaN"
        if value == float("inf"):
            return EdmType.DOUBLE, "Infinity"
        if value == float("-inf"):
            return EdmType.DOUBLE, "-Infinity"
        return EdmType.DOUBLE, float(value)

    def _encode_guid(self, value: Any) -> Tuple[EdmType, str]:
        return EdmType.GUID, str(value)

    def _encode_int32(self, value: Union[str, SupportsInt]) -> Tuple[None, int]:
        int_value = int(value)
        if int_value >= MAX_INT64 or int_value < MIN_INT64:
            raise TypeError(_ERROR_VALUE_TOO_LARGE.format(str(value), EdmType.INT32))
        return None, int_value

    def _encode_int64(self, value: Any) -> Tuple[EdmType, str]:
        return EdmType.INT64, str(value)

    def _encode_string(self, value: Any) -> Tuple[None, str]:
        return None, str(value)
