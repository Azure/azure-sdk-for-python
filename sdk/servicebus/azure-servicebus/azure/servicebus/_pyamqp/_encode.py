#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------
# pylint: disable=unused-argument

import calendar
import struct
import uuid
from datetime import datetime
from typing import AnyStr, Optional, Union, Tuple, Dict, Literal, List, TypeVar, Type, overload

from .types import (
    TYPE,
    VALUE,
    AMQPTypes,
    FieldDefinition,
    ObjDefinition,
    AMQP_STRUCTURED_TYPES,
    AMQP_PRIMATIVE_TYPES,
    AMQPDefinedType,
    AMQPFieldType,
    NullDefinedType
)
from .message import Header, Properties, Message
from . import performatives
from . import outcomes
from . import endpoints
from . import error


ENCODABLE_PRIMATIVE_TYPES = Union[AMQPDefinedType[AMQPTypes, AMQP_PRIMATIVE_TYPES], AMQP_PRIMATIVE_TYPES]
ENCODABLE_TYPES = Union[AMQPDefinedType[AMQPTypes, AMQP_STRUCTURED_TYPES], AMQP_STRUCTURED_TYPES]
ENCODABLE_T = TypeVar('ENCODABLE_T', ENCODABLE_TYPES)
ENCODABLE_P = TypeVar('ENCODABLE_P', ENCODABLE_PRIMATIVE_TYPES)

_FRAME_OFFSET = b"\x02"
_FRAME_TYPE = b'\x00'
_CONSTRUCTOR_NULL = b'\x40'
_CONSTRUCTOR_BOOL = b'\x56'
_CONSTRUCTOR_BOOL_TRUE = b'\x41'
_CONSTRUCTOR_BOOL_FALSE = b'\x42'
_CONSTRUCTOR_UBYTE = b'\x50'
_CONSTRUCTOR_BYTE = b'\x51'
_CONSTRUCTOR_USHORT = b'\x60'
_CONSTRUCTOR_SHORT = b'\x61'
_CONSTRUCTOR_UINT_0 = b'\x43'
_CONSTRUCTOR_UINT_SMALL = b'\x52'
_CONSTRUCTOR_INT_SMALL = b'\x54'
_CONSTRUCTOR_UINT_LARGE = b'\x70'
_CONSTRUCTOR_INT_LARGE = b'\x71'
_CONSTRUCTOR_ULONG_0 = b'\x44'
_CONSTRUCTOR_ULONG_SMALL = b'\x53'
_CONSTRUCTOR_LONG_SMALL = b'\x55'
_CONSTRUCTOR_ULONG_LARGE = b'\x80'
_CONSTRUCTOR_LONG_LARGE = b'\x81'
_CONSTRUCTOR_FLOAT = b'\x72'
_CONSTRUCTOR_DOUBLE = b'\x82'
_CONSTRUCTOR_TIMESTAMP = b'\x83'
_CONSTRUCTOR_UUID = b'\x98'
_CONSTRUCTOR_BINARY_SMALL = b'\xA0'
_CONSTRUCTOR_BINARY_LARGE = b'\xB0'
_CONSTRUCTOR_STRING_SMALL = b'\xA1'
_CONSTRUCTOR_STRING_LARGE = b'\xB1'
_CONSTRUCTOR_SYMBOL_SMALL = b'\xA3'
_CONSTRUCTOR_SYMBOL_LARGE = b'\xB3'
_CONSTRUCTOR_LIST_0 = b'\x45'
_CONSTRUCTOR_LIST_SMALL = b'\xC0'
_CONSTRUCTOR_LIST_LARGE = b'\xD0'
_CONSTRUCTOR_MAP_SMALL = b'\xC1'
_CONSTRUCTOR_MAP_LARGE = b'\xD1'
_CONSTRUCTOR_ARRAY_SMALL = b'\xE0'
_CONSTRUCTOR_ARRAY_LARGE = b'\xF0'
_CONSTRUCTOR_DESCRIPTOR = b'\x00'


def _construct(byte: bytes, construct: bool) -> bytes:
    """Add the constructor byte if required."""
    return byte if construct else b''


def encode_null(output: bytearray, _: Literal[None], **kwargs) -> None:
    """Encode a null value.

    encoding code="0x40" category="fixed" width="0" label="the null value"

    :param bytearray output: The bytes encoded so far. The newly encoded value will be appended.
    """
    output.extend(_CONSTRUCTOR_NULL)


def encode_boolean(output: bytearray, value: bool, *, with_constructor: bool = True, **kwargs) -> None:
    """Encode a boolean value. Optionally this will include a constructor byte.

    <encoding name="true" code="0x41" category="fixed" width="0" label="the boolean value true"/>
    <encoding name="false" code="0x42" category="fixed" width="0" label="the boolean value false"/>
    <encoding code="0x56" category="fixed" width="1"
        label="boolean with the octet 0x00 being false and octet 0x01 being true"/>

    :param bytearray output: The bytes encoded so far. The newly encoded value will be appended.
    :param bool value: The data to encode.
    :keyword bool with_constructor: Whether to include the constructor byte. Default is True.
    """
    value = bool(value)
    if with_constructor:
        output.extend(_CONSTRUCTOR_BOOL)
        output.extend(b'\x01' if value else b'\x00')
    else:
        output.extend(_CONSTRUCTOR_BOOL_TRUE if value else _CONSTRUCTOR_BOOL_FALSE)


def encode_ubyte(
        output: bytearray,
        value: Union[int, bytes],
        *,
        with_constructor: bool = True,
        **kwargs
    ) -> None:
    """Encode an unsigned byte value. Optionally this will include the constructor byte.

    <encoding code="0x50" category="fixed" width="1" label="8-bit unsigned integer"/>

    :param bytearray output: The bytes encoded so far. The newly encoded value will be appended.
    :param Union[int, bytes] value: The data to encode. Must be 0-255.
    :keyword bool with_constructor: Whether to include the constructor byte. Default is True.
    """
    try:
        value = int(value)
    except ValueError:
        value = ord(value)
    try:
        output.extend(_construct(_CONSTRUCTOR_UBYTE, with_constructor))
        output.extend(struct.pack('>B', abs(value)))
    except struct.error:
        raise ValueError("Unsigned byte value must be 0-255")


def encode_ushort(output: bytearray, value: int, *, with_constructor: bool = True, **kwargs) -> None:
    """Encode an unsigned short value. Optionally this will include the constructor byte.

    <encoding code="0x60" category="fixed" width="2" label="16-bit unsigned integer in network byte order"/>

    :param bytearray output: The bytes encoded so far. The newly encoded value will be appended.
    :param int value: The data to encode. Must be 0-65535.
    :keyword bool with_constructor: Whether to include the constructor byte. Default is True.
    """
    value = int(value)
    try:
        output.extend(_construct(_CONSTRUCTOR_USHORT, with_constructor))
        output.extend(struct.pack('>H', abs(value)))
    except struct.error:
        raise ValueError("Unsigned short value must be 0-65535")


def encode_uint(
        output: bytearray,
        value: int,
        *,
        with_constructor: bool = True,
        use_smallest: bool = True
    ) -> None:
    """Encode an unsigned int value. Optionally this will include the constructor byte.

    <encoding name="uint0" code="0x43" category="fixed" width="0" label="the uint value 0"/>
    <encoding name="smalluint" code="0x52" category="fixed" width="1"
        label="unsigned integer value in the range 0 to 255 inclusive"/>
    <encoding code="0x70" category="fixed" width="4" label="32-bit unsigned integer in network byte order"/>
    
    :param bytearray output: The bytes encoded so far. The newly encoded value will be appended.
    :param int value: The data to encode.
    :keyword bool with_constructor: Whether to include the constructor byte. Default is True.
    :keyword bool use_smallest: Whether to encode a value with 1 bytes or 4 bytes. The default is to
     use the smallest width possible.
    """
    value = int(value)
    if value == 0:
        output.extend(_CONSTRUCTOR_UINT_0)
        return
    try:
        if use_smallest and value <= 255:
            output.extend(_construct(_CONSTRUCTOR_UINT_SMALL, with_constructor))
            output.extend(struct.pack('>B', abs(value)))
            return
        output.extend(_construct(_CONSTRUCTOR_UINT_LARGE, with_constructor))
        output.extend(struct.pack('>I', abs(value)))
    except struct.error:
        raise ValueError("Value supplied for unsigned int invalid: {}".format(value))


def encode_ulong(
        output: bytearray,
        value: int,
        *,
        with_constructor: bool = True,
        use_smallest: bool = True
    ) -> None:
    """Encode an unsigned long value. Optionally this will include the constructor byte.

    <encoding name="ulong0" code="0x44" category="fixed" width="0" label="the ulong value 0"/>
    <encoding name="smallulong" code="0x53" category="fixed" width="1"
        label="unsigned long value in the range 0 to 255 inclusive"/>
    <encoding code="0x80" category="fixed" width="8" label="64-bit unsigned integer in network byte order"/>

    :param bytearray output: The bytes encoded so far. The newly encoded value will be appended.
    :param int value: The data to encode.
    :keyword bool with_constructor: Whether to include the constructor byte. Default is True.
    :keyword bool use_smallest: Whether to encode a value with 1 bytes or 8 bytes. The default is to
     use the smallest width possible.
    """
    value = int(value)
    if value == 0:
        output.extend(_CONSTRUCTOR_ULONG_0)
        return
    try:
        if use_smallest and value <= 255:
            output.extend(_construct(_CONSTRUCTOR_ULONG_SMALL, with_constructor))
            output.extend(struct.pack('>B', abs(value)))
            return
        output.extend(_construct(_CONSTRUCTOR_ULONG_LARGE, with_constructor))
        output.extend(struct.pack('>Q', abs(value)))
    except struct.error:
        raise ValueError("Value supplied for unsigned long invalid: {}".format(value))


def encode_byte(output: bytearray, value: int, *, with_constructor: bool = True, **kwargs) -> None:
    """Encode a byte value. Optionally this will include the constructor byte.

    <encoding code="0x51" category="fixed" width="1" label="8-bit two's-complement integer"/>

    :param bytearray output: The bytes encoded so far. The newly encoded value will be appended.
    :param int value: The data to encode. Must be -128-127.
    :keyword bool with_constructor: Whether to include the constructor byte. Default is True.
    """
    value = int(value)
    try:
        output.extend(_construct(_CONSTRUCTOR_BYTE, with_constructor))
        output.extend(struct.pack('>b', value))
    except struct.error:
        raise ValueError("Byte value must be -128-127")


def encode_short(output: bytearray, value: int, *, with_constructor: bool = True, **kwargs) -> None:
    """Encode a short value. Optionally this will include the constructor byte.

    <encoding code="0x61" category="fixed" width="2" label="16-bit two's-complement integer in network byte order"/>

    :param bytearray output: The bytes encoded so far. The newly encoded value will be appended.
    :param int value: The data to encode. Must be -32768-32767.
    :keyword bool with_constructor: Whether to include the constructor byte. Default is True.
    """
    value = int(value)
    try:
        output.extend(_construct(_CONSTRUCTOR_SHORT, with_constructor))
        output.extend(struct.pack('>h', value))
    except struct.error:
        raise ValueError("Short value must be -32768-32767")


def encode_int(
        output: bytearray,
        value: int,
        *,
        with_constructor: bool = True,
        use_smallest: bool = True
    ) -> None:
    """Encode an int value. Optionally this will include the constructor byte.

    <encoding name="smallint" code="0x54" category="fixed" width="1" label="8-bit two's-complement integer"/>
    <encoding code="0x71" category="fixed" width="4" label="32-bit two's-complement integer in network byte order"/>

    :param bytearray output: The bytes encoded so far. The newly encoded value will be appended.
    :param int value: The data to encode.
    :keyword bool with_constructor: Whether to include the constructor byte. Default is True.
    :keyword bool use_smallest: Whether to encode a value with 1 bytes or 4 bytes. The default is to
     use the smallest width possible.
    """
    value = int(value)
    try:
        if use_smallest and (-128 <= value <= 127):
            output.extend(_construct(_CONSTRUCTOR_INT_SMALL, with_constructor))
            output.extend(struct.pack('>b', value))
            return
        output.extend(_construct(_CONSTRUCTOR_INT_LARGE, with_constructor))
        output.extend(struct.pack('>i', value))
    except struct.error:
        raise ValueError("Value supplied for int invalid: {}".format(value))


def encode_long(
        output: bytearray,
        value: int,
        *,
        with_constructor: bool = True,
        use_smallest: bool = True
    ) -> None:
    """Encode a long value. Optionally this will include the constructor byte.

    <encoding name="smalllong" code="0x55" category="fixed" width="1" label="8-bit two's-complement integer"/>
    <encoding code="0x81" category="fixed" width="8" label="64-bit two's-complement integer in network byte order"/>

    :param bytearray output: The bytes encoded so far. The newly encoded value will be appended.
    :param int value: The data to encode.
    :keyword bool with_constructor: Whether to include the constructor byte. Default is True.
    :keyword bool use_smallest: Whether to encode a value with 1 bytes or 8 bytes. The default is to
     use the smallest width possible.
    """
    value = int(value)
    try:
        if use_smallest and (-128 <= value <= 127):
            output.extend(_construct(_CONSTRUCTOR_LONG_SMALL, with_constructor))
            output.extend(struct.pack('>b', value))
            return
        output.extend(_construct(_CONSTRUCTOR_LONG_LARGE, with_constructor))
        output.extend(struct.pack('>q', value))
    except struct.error:
        raise ValueError("Value supplied for long invalid: {}".format(value))


def encode_float(output: bytearray, value: float, *, with_constructor: bool = True, **kwargs) -> None:
    """Encode a float value. Optionally this will include the constructor byte.

    <encoding name="ieee-754" code="0x72" category="fixed" width="4" label="IEEE 754-2008 binary32"/>

    :param bytearray output: The bytes encoded so far. The newly encoded value will be appended.
    :param float value: The data to encode.
    :keyword bool with_constructor: Whether to include the constructor byte. Default is True.
    """
    value = float(value)
    output.extend(_construct(_CONSTRUCTOR_FLOAT, with_constructor))
    output.extend(struct.pack('>f', value))


def encode_double(output: bytearray, value: float, *, with_constructor: bool = True, **kwargs) -> None:
    """Encode a double value. Optionally this will include the constructor byte.

    <encoding name="ieee-754" code="0x82" category="fixed" width="8" label="IEEE 754-2008 binary64"/>

    :param bytearray output: The bytes encoded so far. The newly encoded value will be appended.
    :param float value: The data to encode.
    :keyword bool with_constructor: Whether to include the constructor byte. Default is True.
    """
    value = float(value)
    output.extend(_construct(_CONSTRUCTOR_DOUBLE, with_constructor))
    output.extend(struct.pack('>d', value))


def encode_timestamp(
        output: bytearray,
        value: Union[int, datetime],
        *,
        with_constructor: bool = True,
        **kwargs
    ) -> None:
    """Encode a timestamp value. Optionally this will include the constructor byte.

    <encoding name="ms64" code="0x83" category="fixed" width="8"
        label="64-bit two's-complement integer representing milliseconds since the unix epoch"/>

    :param bytearray output: The bytes encoded so far. The newly encoded value will be appended.
    :param Union[int, ~datetime.datetime] value: The data to encode.
    :keyword bool with_constructor: Whether to include the constructor byte. Default is True.
    """
    if isinstance(value, datetime):
        value = (calendar.timegm(value.utctimetuple()) * 1000) + (value.microsecond/1000)
    value = int(value)
    output.extend(_construct(_CONSTRUCTOR_TIMESTAMP, with_constructor))
    output.extend(struct.pack('>q', value))


def encode_uuid(
        output: bytearray,
        value: Union[str, bytes, uuid.UUID],
        *,
        with_constructor: bool = True,
        **kwargs
    ) -> None:
    """Encode a UUID value. Optionally this will include the constructor byte.

    <encoding code="0x98" category="fixed" width="16" label="UUID as defined in section 4.1.2 of RFC-4122"/>

    :param bytearray output: The bytes encoded so far. The newly encoded value will be appended.
    :param Union[str, bytes, ~uuid.UUID] value: The data to encode.
    :keyword bool with_constructor: Whether to include the constructor byte. Default is True.
    """
    if isinstance(value, str):
        value = uuid.UUID(value).bytes
    elif isinstance(value, uuid.UUID):
        value = value.bytes
    elif isinstance(value, bytes):
        value = uuid.UUID(bytes=value).bytes
    else:
        raise TypeError("Invalid UUID type: {}".format(type(value)))
    output.extend(_construct(_CONSTRUCTOR_UUID, with_constructor))
    output.extend(value)


def encode_binary(
        output: bytearray,
        value: Union[bytes, bytearray],
        *,
        with_constructor: bool = True,
        use_smallest: bool = True
    ) -> None:
    """Encode a binary value. Optionally this will include the constructor byte.

    <encoding name="vbin8" code="0xa0" category="variable" width="1" label="up to 2^8 - 1 octets of binary data"/>
    <encoding name="vbin32" code="0xb0" category="variable" width="4" label="up to 2^32 - 1 octets of binary data"/>

    :param bytearray output: The bytes encoded so far. The newly encoded value will be appended.
    :param Union[bytes, bytearray] value: The data to encode.
    :keyword bool with_constructor: Whether to include the constructor byte. Default is True.
    :keyword bool use_smallest: Whether to encode a value with 1 bytes or 4 bytes. The default is to
     use the smallest width possible.
    """
    length = len(value)
    if use_smallest and length <= 255:
        output.extend(_construct(_CONSTRUCTOR_BINARY_SMALL, with_constructor))
        output.extend(struct.pack('>B', length))
        output.extend(value)
        return
    try:
        output.extend(_construct(_CONSTRUCTOR_BINARY_LARGE, with_constructor))
        output.extend(struct.pack('>L', length))
        output.extend(value)
    except struct.error:
        raise ValueError("Binary data to long to encode")


def encode_string(
        output: bytearray,
        value: Union[bytes, str],
        *,
        with_constructor: bool = True,
        use_smallest: bool = True
    ) -> None:
    """Encode a string value. Optionally this will include the constructor byte.

    <encoding name="str8-utf8" code="0xa1" category="variable" width="1"
        label="up to 2^8 - 1 octets worth of UTF-8 Unicode (with no byte order mark)"/>
    <encoding name="str32-utf8" code="0xb1" category="variable" width="4"
        label="up to 2^32 - 1 octets worth of UTF-8 Unicode (with no byte order mark)"/>

    :param bytearray output: The bytes encoded so far. The newly encoded value will be appended.
    :param Union[bytes, str] value: The data to encode.
    :keyword bool with_constructor: Whether to include the constructor byte. Default is True.
    :keyword bool use_smallest: Whether to encode a value with 1 bytes or 4 bytes. The default is to
     use the smallest width possible.
    """
    if isinstance(value, str):
        value = value.encode('utf-8')
    length = len(value)
    if use_smallest and length <= 255:
        output.extend(_construct(_CONSTRUCTOR_STRING_SMALL, with_constructor))
        output.extend(struct.pack('>B', length))
        output.extend(value)
        return
    try:
        output.extend(_construct(_CONSTRUCTOR_STRING_LARGE, with_constructor))
        output.extend(struct.pack('>L', length))
        output.extend(value)
    except struct.error:
        raise ValueError("String value too long to encode.")


def encode_symbol(
        output: bytearray,
        value: Union[bytes, str],
        *,
        with_constructor: bool = True,
        use_smallest: bool = True
    ) -> None:
    """Encode a symbol value. Optionally this will include the constructor byte.

    <encoding name="sym8" code="0xa3" category="variable" width="1"
        label="up to 2^8 - 1 seven bit ASCII characters representing a symbolic value"/>
    <encoding name="sym32" code="0xb3" category="variable" width="4"
        label="up to 2^32 - 1 seven bit ASCII characters representing a symbolic value"/>

    :param bytearray output: The bytes encoded so far. The newly encoded value will be appended.
    :param Union[bytes, str] value: The data to encode.
    :keyword bool with_constructor: Whether to include the constructor byte. Default is True.
    :keyword bool use_smallest: Whether to encode a value with 1 bytes or 4 bytes. The default is to
     use the smallest width possible.
    """
    if isinstance(value, str):
        value = value.encode('utf-8')
    length = len(value)
    if use_smallest and length <= 255:
        output.extend(_construct(_CONSTRUCTOR_SYMBOL_SMALL, with_constructor))
        output.extend(struct.pack('>B', length))
        output.extend(value)
        return
    try:
        output.extend(_construct(_CONSTRUCTOR_SYMBOL_LARGE, with_constructor))
        output.extend(struct.pack('>L', length))
        output.extend(value)
    except struct.error:
        raise ValueError("Symbol value too long to encode.")


def encode_list(
        output: bytearray,
        value: List[ENCODABLE_TYPES],
        *,
        with_constructor: bool = True,
        use_smallest: bool = True
    ) -> None:
    """Encode a list value. Optionally this will include the constructor byte.

    <encoding name="list0" code="0x45" category="fixed" width="0"
        label="the empty list (i.e. the list with no elements)"/>
    <encoding name="list8" code="0xc0" category="compound" width="1"
        label="up to 2^8 - 1 list elements with total size less than 2^8 octets"/>
    <encoding name="list32" code="0xd0" category="compound" width="4"
        label="up to 2^32 - 1 list elements with total size less than 2^32 octets"/>

    :param bytearray output: The bytes encoded so far. The newly encoded value will be appended.
    :param List[ENCODABLE_TYPES] value: The data to encode.
    :keyword bool with_constructor: Whether to include the constructor byte. Default is True.
    :keyword bool use_smallest: Whether to encode a value with 1 bytes or 4 bytes. The default is to
     use the smallest width possible.
    """
    count = len(value)
    if use_smallest and count == 0:
        output.extend(_CONSTRUCTOR_LIST_0)
        return
    encoded_size = 0
    encoded_values = bytearray()
    for item in value:
        encode_value(encoded_values, item, with_constructor=True)
    encoded_size += len(encoded_values)
    if use_smallest and count <= 255 and encoded_size < 255:
        output.extend(_construct(_CONSTRUCTOR_LIST_SMALL, with_constructor))
        output.extend(struct.pack('>B', encoded_size + 1))
        output.extend(struct.pack('>B', count))
    else:
        try:
            output.extend(_construct(_CONSTRUCTOR_LIST_LARGE, with_constructor))
            output.extend(struct.pack('>L', encoded_size + 4))
            output.extend(struct.pack('>L', count))
        except struct.error:
            raise ValueError("List is too large or too long to be encoded.")
    output.extend(encoded_values)


def encode_map(
        output: bytearray,
        value: Union[Dict[ENCODABLE_TYPES, ENCODABLE_TYPES], List[Tuple[ENCODABLE_TYPES, ENCODABLE_TYPES]]],
        *,
        with_constructor: bool = True,
        use_smallest: bool = True
    ) -> None:
    """Encode a map value. Optionally this will include the constructor byte.

    <encoding name="map8" code="0xc1" category="compound" width="1"
        label="up to 2^8 - 1 octets of encoded map data"/>
    <encoding name="map32" code="0xd1" category="compound" width="4"
        label="up to 2^32 - 1 octets of encoded map data"/>

    :param bytearray output: The bytes encoded so far. The newly encoded value will be appended.
    :param value: The data to encode.
    :paramtype value: Union[Dict[ENCODABLE_TYPES, ENCODABLE_TYPES], List[Tuple[ENCODABLE_TYPES, ENCODABLE_TYPES]]]
    :keyword bool with_constructor: Whether to include the constructor byte. Default is True.
    :keyword bool use_smallest: Whether to encode a value with 1 bytes or 4 bytes. The default is to
     use the smallest width possible.
    """
    count = len(value) * 2
    encoded_size = 0
    encoded_values = bytearray()
    try:
        items = value.items()
    except AttributeError:
        items = value
    for key, data in items:
        encode_value(encoded_values, key, with_constructor=True)
        encode_value(encoded_values, data, with_constructor=True)
    encoded_size = len(encoded_values)
    if use_smallest and count <= 255 and encoded_size < 255:
        output.extend(_construct(_CONSTRUCTOR_MAP_SMALL, with_constructor))
        output.extend(struct.pack('>B', encoded_size + 1))
        output.extend(struct.pack('>B', count))
    else:
        try:
            output.extend(_construct(_CONSTRUCTOR_MAP_LARGE, with_constructor))
            output.extend(struct.pack('>L', encoded_size + 4))
            output.extend(struct.pack('>L', count))
        except struct.error:
            raise ValueError("Map is too large or too long to be encoded.")
    output.extend(encoded_values)


def _check_element_type(item: ENCODABLE_T, element_type: Optional[Type[ENCODABLE_T]]) -> Type[ENCODABLE_T]:
    """Validate the an item in the array is consistent with the other array items.

    This method will be called on every item in the array. For the first item, it
    will determine the type, and that will be used to validate all subsequent items.
    
    :param item: An item in the array.
    :param element_type: The class type of previous items in the array to validate.
    :returns: The classtype of the array item.
    """
    if not element_type:
        try:
            return item['TYPE']
        except (KeyError, TypeError):
            return type(item)
    try:
        if item['TYPE'] != element_type:
            raise TypeError("All elements in an array must be the same type.")
    except (KeyError, TypeError):
        if not isinstance(item, element_type):
            raise TypeError("All elements in an array must be the same type.")
    return element_type


def encode_array(
        output: bytearray,
        value: List[ENCODABLE_TYPES],
        *,
        with_constructor: bool = True,
        use_smallest: bool = True
    ) -> None:
    """Encode an array value. Optionally this will include the constructor byte.

    <encoding name="map8" code="0xE0" category="compound" width="1"
        label="up to 2^8 - 1 octets of encoded map data"/>
    <encoding name="map32" code="0xF0" category="compound" width="4"
        label="up to 2^32 - 1 octets of encoded map data"/>

    :param bytearray output: The bytes encoded so far. The newly encoded value will be appended.
    :param List[ENCODABLE_TYPES] value: The data to encode.
    :keyword bool with_constructor: Whether to include the constructor byte. Default is True.
    :keyword bool use_smallest: Whether to encode a value with 1 bytes or 4 bytes. The default is to
     use the smallest width possible.
    """
    count = len(value)
    encoded_size = 0
    encoded_values = bytearray()
    first_item = True  # Only the first item in an array has a constructor byte.
    element_type = None  # Arrays must be homogeneous, so we enforce consistent content type.
    for item in value:
        element_type = _check_element_type(item, element_type)
        encode_value(encoded_values, item, with_constructor=first_item, use_smallest=False)
        first_item = False
        if item is None:
            encoded_size -= 1
            break
    encoded_size += len(encoded_values)
    if use_smallest and count <= 255 and encoded_size < 255:
        output.extend(_construct(_CONSTRUCTOR_ARRAY_SMALL, with_constructor))
        output.extend(struct.pack('>B', encoded_size + 1))
        output.extend(struct.pack('>B', count))
    else:
        try:
            output.extend(_construct(_CONSTRUCTOR_ARRAY_LARGE, with_constructor))
            output.extend(struct.pack('>L', encoded_size + 4))
            output.extend(struct.pack('>L', count))
        except struct.error:
            raise ValueError("Array is too large or too long to be encoded.")
    output.extend(encoded_values)


def encode_described(
        output: bytearray,
        value: Tuple[ENCODABLE_TYPES, ENCODABLE_TYPES],
        **kwargs
    ) -> None:
    """Encode a described value.
    
    :param bytearray output: The bytes encoded so far. The newly encoded value will be appended.
    :param value: The data to encode. This is a tuple of two values, the descriptor (usually symbol
     or ulong) and the described.
    :paramtype value: Tuple[ENCODABLE_TYPES, ENCODABLE_TYPES]
    """
    output.extend(_CONSTRUCTOR_DESCRIPTOR)
    encode_value(output, value[0], **kwargs)
    encode_value(output, value[1], **kwargs)


def encode_fields(
        value: Optional[Dict[AnyStr, ENCODABLE_T]]
    ) -> Union[NullDefinedType, AMQPFieldType[ENCODABLE_T]]:
    """A mapping from field name to value.

    The fields type is a map where the keys are restricted to be of type symbol (this excludes the possibility
    of a null key).  There is no further restriction implied by the fields type on the allowed values for the
    entries or the set of allowed keys.

    <type name="fields" class="restricted" source="map"/>

    :param value: The optional dictionary to be encoded as fields. Keys must be string or
     bytes. If empty or None, a null value will be encoded.
    :paramtype value: Optional[Dict[Union[str, bytes], ENCODABLE_TYPES]]
    :returns: An encoded mapping of symbols to AMQP types.
    """
    if not value:
        return {TYPE: AMQPTypes.null, VALUE: None}
    fields = {TYPE: AMQPTypes.map, VALUE:[]}
    for key, data in value.items():
        if isinstance(key, str):
            key = key.encode('utf-8')
        fields[VALUE].append(({TYPE: AMQPTypes.symbol, VALUE: key}, data))
    return fields


def encode_annotations(
        value: Optional[Dict[Union[int, AnyStr], ENCODABLE_T]]
    ):
    """The annotations type is a map where the keys are restricted to be of type symbol or of type ulong.

    All ulong keys, and all symbolic keys except those beginning with "x-" are reserved.
    On receiving an annotations map containing keys or values which it does not recognize, and for which the
    key does not begin with the string 'x-opt-' an AMQP container MUST detach the link with the not-implemented
    amqp-error.

    <type name="annotations" class="restricted" source="map"/>

    :param value: The optional dictionary to be encoded as annotations. Keys must be int, string or
     bytes. If empty or None, a null value will be encoded.
    :paramtype value: Optional[Dict[Union[int, str, bytes], ENCODABLE_TYPES]]
    :returns: An encoded mapping of symbols or ulong to AMQP types.
    """
    if not value:
        return {TYPE: AMQPTypes.null, VALUE: None}
    fields = {TYPE: AMQPTypes.map, VALUE:[]}
    for key, data in value.items():
        if isinstance(key, int):
            field_key = {TYPE: AMQPTypes.ulong, VALUE: key}
        else:
            field_key = {TYPE: AMQPTypes.symbol, VALUE: key}
        try:
            fields[VALUE].append((field_key, {TYPE: data[TYPE], VALUE: data[VALUE]}))
        except (KeyError, TypeError):
            fields[VALUE].append((field_key, {TYPE: None, VALUE: data}))
    return fields


def encode_application_properties(
        value: Optional[Dict[Union[str, bytes], ENCODABLE_P]]
    ):
    """The application-properties section is a part of the bare message used for structured application data.

    <type name="application-properties" class="restricted" source="map" provides="section">
        <descriptor name="amqp:application-properties:map" code="0x00000000:0x00000074"/>
    </type>

    Intermediaries may use the data within this structure for the purposes of filtering or routing.
    The keys of this map are restricted to be of type string (which excludes the possibility of a null key)
    and the values are restricted to be of simple types only, that is (excluding map, list, and array types).

    :param value: The optional dictionary to be encoded as fields. Keys must be string or
     bytes. Values must be AMQP primitive types. If empty or None, a null value will be encoded.
    :paramtype value: Optional[Dict[Union[str, bytes], ENCODABLE_TYPES]]
    :returns: An encoded mapping of strings to AMQP primitive types.
    """
    if not value:
        return {TYPE: AMQPTypes.null, VALUE: None}
    fields = {TYPE: AMQPTypes.map, VALUE:[]}
    for key, data in value.items():
        fields[VALUE].append(({TYPE: AMQPTypes.string, VALUE: key}, data))
    return fields

@overload
def encode_message_id(value: str) -> AMQPDefinedType[Literal[AMQPTypes.string], str]:
    ...
@overload
def encode_message_id(value: bytes) -> AMQPDefinedType[Literal[AMQPTypes.binary], bytes]:
    ...
@overload
def encode_message_id(value: uuid.uuid.UUID) -> AMQPDefinedType[Literal[AMQPTypes.uuid], uuid.uuid.UUID]:
    ...
@overload
def encode_message_id(value: int) -> AMQPDefinedType[Literal[AMQPTypes.ulong], int]:
    ...
def encode_message_id(
        value: Union[str, bytes, uuid.UUID, int]
    ) -> AMQPDefinedType[AMQPTypes, Union[str, bytes, uuid.UUID, int]]:
    """Encode a message ID value.

    <type name="message-id-ulong" class="restricted" source="ulong" provides="message-id"/>
    <type name="message-id-uuid" class="restricted" source="uuid" provides="message-id"/>
    <type name="message-id-binary" class="restricted" source="binary" provides="message-id"/>
    <type name="message-id-string" class="restricted" source="string" provides="message-id"/>

    :param value: The Message ID value. This must be a string, bytes, UUID or int. Note that
     in this case string and bytes will be encoded differently - as string and binary respectively.
    :returns: An encoded mapping according to the input primitive type.
    """
    if isinstance(value, int):
        return {TYPE: AMQPTypes.ulong, VALUE: value}
    elif isinstance(value, uuid.UUID):
        return {TYPE: AMQPTypes.uuid, VALUE: value}
    elif isinstance(value, bytes):
        return {TYPE: AMQPTypes.binary, VALUE: value}
    elif isinstance(value, str):
        return {TYPE: AMQPTypes.string, VALUE: value}
    raise TypeError("Unsupported Message ID type.")


def encode_node_properties(
        value: Optional[Dict[AnyStr, ENCODABLE_T]]
    ) -> Union[NullDefinedType, AMQPFieldType[ENCODABLE_T]]:
    """Properties of a node.

    <type name="node-properties" class="restricted" source="fields"/>
    
    A symbol-keyed map containing properties of a node used when requesting creation or reporting
    the creation of a dynamic node. The following common properties are defined::
    
        - `lifetime-policy`: The lifetime of a dynamically generated node. Definitionally, the lifetime will
          never be less than the lifetime of the link which caused its creation, however it is possible to extend
          the lifetime of dynamically created node using a lifetime policy. The value of this entry MUST be of a type
          which provides the lifetime-policy archetype. The following standard lifetime-policies are defined below:
          delete-on-close, delete-on-no-links, delete-on-no-messages or delete-on-no-links-or-messages.
        
        - `supported-dist-modes`: The distribution modes that the node supports. The value of this entry MUST be one or
          more symbols which are valid distribution-modes. That is, the value MUST be of the same type as would be valid
          in a field defined with the following attributes:
          type="symbol" multiple="true" requires="distribution-mode"
    """
    if not value:
        return {TYPE: AMQPTypes.null, VALUE: None}
    # TODO
    fields = {TYPE: AMQPTypes.map, VALUE:[]}
    # fields[{TYPE: AMQPTypes.symbol, VALUE: b'lifetime-policy'}] = {
    #     TYPE: AMQPTypes.described,
    #     VALUE: (
    #         {TYPE: AMQPTypes.ulong, VALUE: value['lifetime_policy']},
    #         {TYPE: AMQPTypes.list, VALUE: []}
    #     )
    # }
    # fields[{TYPE: AMQPTypes.symbol, VALUE: b'supported-dist-modes'}] = {}
    return fields


def encode_filter_set(value):
    """A set of predicates to filter the Messages admitted onto the Link.

    <type name="filter-set" class="restricted" source="map"/>

    A set of named filters. Every key in the map MUST be of type symbol, every value MUST be either null or of a
    described type which provides the archetype filter. A filter acts as a function on a message which returns a
    boolean result indicating whether the message can pass through that filter or not. A message will pass
    through a filter-set if and only if it passes through each of the named filters. If the value for a given key is
    null, this acts as if there were no such key present (i.e., all messages pass through the null filter).

    Filter types are a defined extension point. The filter types that a given source supports will be indicated
    by the capabilities of the source.
    """
    if not value:
        return {TYPE: AMQPTypes.null, VALUE: None}
    fields = {TYPE: AMQPTypes.map, VALUE:[]}
    for name, data in value.items():
        if data is None:
            described_filter = {TYPE: AMQPTypes.null, VALUE: None}
        else:
            if isinstance(name, str):
                name = name.encode('utf-8')
            descriptor, filter_value = data
            described_filter = {
                TYPE: AMQPTypes.described,
                VALUE: (
                    {TYPE: AMQPTypes.symbol, VALUE: descriptor},
                    filter_value
                )
            }
        fields[VALUE].append(({TYPE: AMQPTypes.symbol, VALUE: name}, described_filter))
    return fields


def encode_unknown(output: bytearray, value: AMQP_STRUCTURED_TYPES, **kwargs) -> None:
    """Dynamic encoding according to the type of `value`."""
    if value is None:
        encode_null(output, **kwargs)
    elif isinstance(value, bool):
        encode_boolean(output, value, **kwargs)
    elif isinstance(value, str):
        encode_string(output, value, **kwargs)
    elif isinstance(value, uuid.UUID):
        encode_uuid(output, value, **kwargs)
    elif isinstance(value, (bytearray, bytes)):
        encode_binary(output, value, **kwargs)
    elif isinstance(value, float):
        encode_double(output, value, **kwargs)
    elif isinstance(value, int):
        encode_int(output, value, **kwargs)
    elif isinstance(value, datetime):
        encode_timestamp(output, value, **kwargs)
    elif isinstance(value, list):
        encode_list(output, value, **kwargs)
    elif isinstance(value, tuple):
        encode_described(output, value, **kwargs)
    elif isinstance(value, dict):
        encode_map(output, value, **kwargs)
    else:
        raise TypeError("Unable to encode unknown value: {}".format(value))


_FIELD_DEFINITIONS = {
    FieldDefinition.fields: encode_fields,
    FieldDefinition.annotations: encode_annotations,
    FieldDefinition.message_id: encode_message_id,
    FieldDefinition.app_properties: encode_application_properties,
    FieldDefinition.node_properties: encode_node_properties,
    FieldDefinition.filter_set: encode_filter_set,
}

_ENCODE_MAP = {
    None: encode_unknown,
    AMQPTypes.null: encode_null,
    AMQPTypes.boolean: encode_boolean,
    AMQPTypes.ubyte: encode_ubyte,
    AMQPTypes.byte: encode_byte,
    AMQPTypes.ushort: encode_ushort,
    AMQPTypes.short: encode_short,
    AMQPTypes.uint: encode_uint,
    AMQPTypes.int: encode_int,
    AMQPTypes.ulong: encode_ulong,
    AMQPTypes.long: encode_long,
    AMQPTypes.float: encode_float,
    AMQPTypes.double: encode_double,
    AMQPTypes.timestamp: encode_timestamp,
    AMQPTypes.uuid: encode_uuid,
    AMQPTypes.binary: encode_binary,
    AMQPTypes.string: encode_string,
    AMQPTypes.symbol: encode_symbol,
    AMQPTypes.list: encode_list,
    AMQPTypes.map: encode_map,
    AMQPTypes.array: encode_array,
    AMQPTypes.described: encode_described,
}


def encode_value(output: bytearray, value: ENCODABLE_TYPES, **kwargs) -> None:
    """Encode a value."""
    try:
        _ENCODE_MAP[value[TYPE]](output, value[VALUE], **kwargs)
    except (KeyError, TypeError):
        encode_unknown(output, value, **kwargs)


def describe_performative(performative: performatives.Performative):
    body = []
    for index, value in enumerate(performative):
        field = performative._definition[index]
        if value is None:
            body.append({TYPE: AMQPTypes.null, VALUE: None})
        elif field is None:
            continue
        elif isinstance(field.type, FieldDefinition):
            if field.multiple:
                body.append({TYPE: AMQPTypes.array, VALUE: [_FIELD_DEFINITIONS[field.type](v) for v in value]})
            else:
                body.append(_FIELD_DEFINITIONS[field.type](value))
        elif isinstance(field.type, ObjDefinition):
            body.append(describe_performative(value))
        else:
            if field.multiple:
                body.append({TYPE: AMQPTypes.array, VALUE: [{TYPE: field.type, VALUE: v} for v in value]})
            else:
                body.append({TYPE: field.type, VALUE: value})

    return {
        TYPE: AMQPTypes.described,
        VALUE: (
            {TYPE: AMQPTypes.ulong, VALUE: performative._code},
            {TYPE: AMQPTypes.list, VALUE: body}
        )
    }


def encode_payload(output: bytearray, payload: Message) -> bytearray:
    """Encode a Message as payload bytes."""
    if payload[0]:  # header
        # TODO: Header and Properties encoding can be optimized to
        #  1. not encoding trailing None fields
        #  2. encoding bool without constructor
        encode_value(output, describe_performative(payload[0]))

    if payload[2]:  # message annotations
        encode_value(output, {
            TYPE: AMQPTypes.described,
            VALUE: (
                {TYPE: AMQPTypes.ulong, VALUE: 0x00000072},
                encode_annotations(payload[2]),
            )
        })

    if payload[3]:  # properties
        # TODO: Header and Properties encoding can be optimized to
        #  1. not encoding trailing None fields
        #  2. encoding bool without constructor
        encode_value(output, describe_performative(payload[3]))

    if payload[4]:  # application properties
        encode_value(output, {
            TYPE: AMQPTypes.described,
            VALUE: (
                {TYPE: AMQPTypes.ulong, VALUE: 0x00000074},
                {TYPE: AMQPTypes.map, VALUE: payload[4]}
            )
        })

    if payload[5]:  # data
        for item_value in payload[5]:
            encode_value(output, {
                TYPE: AMQPTypes.described,
                VALUE: (
                    {TYPE: AMQPTypes.ulong, VALUE: 0x00000075},
                    {TYPE: AMQPTypes.binary, VALUE: item_value}
                )
            })

    if payload[6]:  # sequence
        for item_value in payload[6]:
            encode_value(output, {
                TYPE: AMQPTypes.described,
                VALUE: (
                    {TYPE: AMQPTypes.ulong, VALUE: 0x00000076},
                    {TYPE: None, VALUE: item_value}
                )
            })

    if payload[7]:  # value
        encode_value(output, {
            TYPE: AMQPTypes.described,
            VALUE: (
                {TYPE: AMQPTypes.ulong, VALUE: 0x00000077},
                {TYPE: None, VALUE: payload[7]}
            )
        })

    if payload[8]:  # footer
        encode_value(output, {
            TYPE: AMQPTypes.described,
            VALUE: (
                {TYPE: AMQPTypes.ulong, VALUE: 0x00000078},
                encode_annotations(payload[8]),
            )
        })

    # TODO:
    #  currently the delivery annotations must be finally encoded instead of being encoded at the 2nd position
    #  otherwise the event hubs service would ignore the delivery annotations
    #  -- received message doesn't have it populated
    #  check with service team?
    if payload[1]:  # delivery annotations
        encode_value(output, {
            TYPE: AMQPTypes.described,
            VALUE: (
                {TYPE: AMQPTypes.ulong, VALUE: 0x00000071},
                encode_annotations(payload[1]),
            )
        })

    return output


def encode_frame(
        frame: performatives.Performative,
        frame_type: bytes = _FRAME_TYPE
    ) -> Tuple[bytes, Optional[bytes]]:
    """Encode a frame."""
    # TODO: allow passing type specific bytes manually, e.g. Empty Frame needs padding
    if frame is None:
        size = 8
        header = size.to_bytes(4, 'big') + _FRAME_OFFSET + frame_type
        return header, None

    frame_description = describe_performative(frame)
    frame_data = bytearray()
    encode_value(frame_data, frame_description)
    if isinstance(frame, performatives.TransferFrame):
        frame_data += frame.payload

    size = len(frame_data) + 8
    header = size.to_bytes(4, 'big') + _FRAME_OFFSET + frame_type
    return header, frame_data
