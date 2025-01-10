# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from dataclasses import fields, is_dataclass
from typing import (
    Any,
    Optional,
    SupportsBytes,
    SupportsFloat,
    SupportsInt,
    is_typeddict,
    Tuple,
    Mapping,
    Union,
    Dict,
    Type,
    Callable,
    Required,
    NotRequired,
    Literal,
    Optional,
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
from ._common_conversion import (
    _encode_base64,
    _to_utc_datetime,
    _annotations,
    _get_annotation_type,
    SupportedDataTypes
)
from ._constants import MAX_INT32, MIN_INT32, MAX_INT64, MIN_INT64, _ERROR_VALUE_TOO_LARGE

_ODATA_SUFFIX = "@odata.type"

EncodeCallable = Callable[[Any], Tuple[Optional[EdmType], SupportedDataTypes]]
EncoderMapType = Mapping[Type, Union[EncodeCallable, EdmType]]


class TableEntityJSONEncoder(JSONEncoder):
    """A JSON encoder that's capable of serializing datetime objects and bytes."""

    def default(self, o: Any) -> Any:
        if isinstance(o, datetime):
            if isinstance(o, TablesEntityDatetime) and o.tables_service_value:
                # Check is this is a 'round-trip' datetime, and if so
                # pass through the original value.
                return o.tables_service_value
            return _to_utc_datetime(o)
        if isinstance(o, UUID):
            return str(o)
        if isinstance(o, (bytes, bytearray)):
            return b64encode(o).decode()
        return super().default(o)


class TableEntityEncoder:

    def __init__(self, *, convert_map: EncoderMapType, entity_format) -> None:
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
        self._edm_types: Dict[EdmType, Callable[[Any], Tuple[Optional[EdmType], SupportedDataTypes]]] = {
            EdmType.BINARY: self._encode_binary,
            EdmType.BOOLEAN: self._encode_boolean,
            EdmType.DATETIME: self._encode_datetime,
            EdmType.DOUBLE: self._encode_double,
            EdmType.GUID: self._encode_guid,
            EdmType.INT32: self._encode_int32,
            EdmType.INT64: self._encode_int64,
            EdmType.STRING: self._encode_string,
        }
        self._obj_types.update(convert_map)
        self._property_types: Dict[str, Union[EncodeCallable, EdmType]] = {}
        if entity_format:
            if is_typeddict(entity_format):
                # Scrape type encoding from typeddict defintion
                for property_name, property_type in _annotations(entity_format):
                    property_type = _get_annotation_type(property_type)
                    self._add_property_type(property_name, property_type)

            elif is_dataclass(entity_format):
                # Scrape type encoding from a dataclass definition
                for entity_field in fields(entity_format):
                    property_type = _get_annotation_type(entity_field.type)
                    property_name = entity_field.name
                    self._add_property_type(property_name, property_type)
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
            self._property_types[property_name] = self._edm_types[property_type]
            return
        except KeyError:
            pass
        try:
            self._property_types[property_name] = self._obj_types[property_type]
        except KeyError as e:
            raise ValueError(
                f"Unexpected type in entity format: '{property_type}', please provide encoder."
            )

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
                    edm_type, encoded_value = self._encode_by_type(value)
                encoded[key] = encoded_value
                if edm_type:
                    encoded[odata_key] = edm_type.value
            return encoded
        if len(args) == 2:
            key, value = cast(Tuple[str, Any], args)  # pylint:disable=unbalanced-tuple-unpacking
            return self._encode_by_name(key, value)
        raise TypeError(f"Expected either 1 or 2 positional parameters, received: {len(args)}.")

    def _convert(
        self, value: Any, converter: Union[EdmType, EncodeCallable]
    ) -> Tuple[Optional[EdmType], SupportedDataTypes]:
        if isinstance(converter, EdmType):
            return self._edm_types[converter](value)
        return converter(value)

    def _encode_by_name(self, key: str, value: Any) -> Tuple[Optional[EdmType], SupportedDataTypes]:
        try:
            return self._convert(value, self._property_types[key])
        except KeyError as e:
            raise KeyError(f"No property encoder found for value '{key}'.") from e

    def _encode_by_type(self, value: Any) -> Tuple[Optional[EdmType], SupportedDataTypes]:
        try:
            return self._convert(value, self._obj_types[type(value)])
        except KeyError as e:
            if isinstance(value, Enum):
                # This is bad, but it's a bug that shipped GA so keeping for backwards compatibility
                # and we'll document how to correctly handle enums.
                return self._encode_string(value)
            raise TypeError(f"No encoder found for value '{value}' of type '{type(value)}'.") from e

    def _encode_tuple(self, value: Tuple[Any, Union[str, EdmType]]) -> Tuple[EdmType, SupportedDataTypes]:
        if len(value) == 2:
            unencoded_value = value[0]
            unencoded_edm = EdmType(value[1])  # this will raise error for invalid edmtypes
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

    def _encode_datetime(self, value: Union[str, datetime]) -> Tuple[EdmType, str]:
        if isinstance(value, str):
            # Pass a serialized value straight through
            return EdmType.DATETIME, value
        if isinstance(value, TablesEntityDatetime) and value.tables_service_value:
            return EdmType.DATETIME, value.tables_service_value
        return EdmType.DATETIME, _to_utc_datetime(value)

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
        if int_value >= MAX_INT32 or int_value < MIN_INT32:
            raise TypeError(_ERROR_VALUE_TOO_LARGE.format(str(value), EdmType.INT32))
        return None, int_value

    def _encode_int64(self, value: SupportsInt) -> Tuple[EdmType, str]:
        int_value = int(value)
        if int_value >= MAX_INT64 or int_value < MIN_INT64:
            raise TypeError(_ERROR_VALUE_TOO_LARGE.format(str(value), EdmType.INT64))
        return EdmType.INT64, str(value)

    def _encode_string(self, value: Any) -> Tuple[None, str]:
        return None, str(value)
