# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import calendar
import struct
import uuid
from datetime import datetime
from typing_extensions import (
    AnyStr,
    Generic,
    Mapping,
    MutableSequence,
    TypeVar,
    Union,
    Tuple,
    Dict,
    Any,
    Optional,
    List,
    Protocol,
    Type,
    Buffer
)
from dataclasses import fields

from ._types_v2 import (
    ConstructorBytes,
    AMQPDefinition,
    AMQPTypes,
    AMQP_BASIC_TYPES,
    AMQP_FULL_TYPES,
    AMQP_DEFINED_TYPES,
    TYPE_KEY,
    VALUE_KEY
)
from ._frames_v2 import Performative
from ._message_v2 import Message


_FRAME_OFFSET = b"\x02"
_FRAME_TYPE = b"\x00"


_InputType = TypeVar("_InputType", bound=AMQP_DEFINED_TYPES)
class _EncodeCallable(Protocol, Generic[_InputType]):
    def __call__(
        self,
        output: Buffer,
        value: _InputType,
        *,
        with_constructor: bool = True,
        use_smallest: bool = True
    ) -> None:
        ...


def _construct(byte: bytes, construct: bool) -> bytes:
    return byte if construct else b""


def _encode_null(output: Buffer, _, **__) -> None:
    """
    encoding code="0x40" category="fixed" width="0" label="the null value"
    """
    output.extend(ConstructorBytes.null)


def _encode_boolean(
    output: Buffer,
    value: bool,
    *,
    with_constructor: bool = True,
    **_
) -> None:
    """
    <encoding name="true" code="0x41" category="fixed" width="0" label="the boolean value true"/>
    <encoding name="false" code="0x42" category="fixed" width="0" label="the boolean value false"/>
    <encoding code="0x56" category="fixed" width="1"
        label="boolean with the octet 0x00 being false and octet 0x01 being true"/>
    """
    value = bool(value)
    if with_constructor:
        output.extend(_construct(ConstructorBytes.bool, with_constructor))
        output.extend(b"\x01" if value else b"\x00")
    else:
        output.extend(ConstructorBytes.bool_true if value else ConstructorBytes.bool_false)


def _encode_ubyte(
    output: Buffer,
    value: Union[int, bytes],
    *,
    with_constructor: bool = True,
    **_
) -> None:
    """
    <encoding code="0x50" category="fixed" width="1" label="8-bit unsigned integer"/>
    """
    try:
        value = int(value)
    except ValueError:
        value = ord(value)
    try:
        output.extend(_construct(ConstructorBytes.ubyte, with_constructor))
        output.extend(struct.pack(">B", abs(value)))
    except struct.error as error:
        raise ValueError(f"Unsigned byte value must be 0-255, got {value}.") from error


def _encode_ushort(
    output: Buffer,
    value: int,
    *,
    with_constructor: bool = True,
    **_
) -> None:
    """
    <encoding code="0x60" category="fixed" width="2" label="16-bit unsigned integer in network byte order"/>
    """
    value = int(value)
    try:
        output.extend(_construct(ConstructorBytes.ushort, with_constructor))
        output.extend(struct.pack(">H", abs(value)))
    except struct.error as error:
        raise ValueError(f"Unsigned byte value must be 0-65535, got {value}.") from error


def _encode_uint(
    output: Buffer,
    value: int,
    *,
    with_constructor: bool = True,
    use_smallest: bool = True
) -> None:
    """
    <encoding name="uint0" code="0x43" category="fixed" width="0" label="the uint value 0"/>
    <encoding name="smalluint" code="0x52" category="fixed" width="1"
        label="unsigned integer value in the range 0 to 255 inclusive"/>
    <encoding code="0x70" category="fixed" width="4" label="32-bit unsigned integer in network byte order"/>
    """
    value = int(value)
    if value == 0:
        output.extend(ConstructorBytes.uint_0)
        return
    try:
        if use_smallest and value <= 255:
            output.extend(_construct(ConstructorBytes.uint_small, with_constructor))
            output.extend(struct.pack(">B", abs(value)))
            return
        output.extend(_construct(ConstructorBytes.uint_large, with_constructor))
        output.extend(struct.pack(">I", abs(value)))
    except struct.error as error:
        raise ValueError(f"Value supplied for unsigned int invalid: {value}.") from error


def _encode_ulong(
    output: Buffer,
    value: int,
    *,
    with_constructor: bool = True,
    use_smallest: bool = True
) -> None:
    """
    <encoding name="ulong0" code="0x44" category="fixed" width="0" label="the ulong value 0"/>
    <encoding name="smallulong" code="0x53" category="fixed" width="1"
        label="unsigned long value in the range 0 to 255 inclusive"/>
    <encoding code="0x80" category="fixed" width="8" label="64-bit unsigned integer in network byte order"/>
    """
    value = int(value)
    if value == 0:
        output.extend(ConstructorBytes.ulong_0)
        return
    try:
        if use_smallest and value <= 255:
            output.extend(_construct(ConstructorBytes.ulong_small, with_constructor))
            output.extend(struct.pack(">B", abs(value)))
            return
        output.extend(_construct(ConstructorBytes.ulong_large, with_constructor))
        output.extend(struct.pack(">Q", abs(value)))
    except struct.error as error:
        raise ValueError(f"Value supplied for unsigned long invalid: {value}") from error


def _encode_byte(
    output: Buffer,
    value: int,
    *,
    with_constructor: bool = True,
    **_
) -> None:
    """
    <encoding code="0x51" category="fixed" width="1" label="8-bit two's-complement integer"/>
    """
    value = int(value)
    try:
        output.extend(_construct(ConstructorBytes.byte, with_constructor))
        output.extend(struct.pack(">b", value))
    except struct.error as error:
        raise ValueError(f"Byte value must be -128-127, got {value}.") from error


def _encode_short(
    output: Buffer,
    value: int,
    *,
    with_constructor: bool = True,
    **_
) -> None:
    """
    <encoding code="0x61" category="fixed" width="2" label="16-bit two's-complement integer in network byte order"/>
    """
    value = int(value)
    try:
        output.extend(_construct(ConstructorBytes.short, with_constructor))
        output.extend(struct.pack(">h", value))
    except struct.error as error:
        raise ValueError(f"Short value must be -32768-32767, got {value}.") from error


def _encode_int(
    output: Buffer,
    value: int,
    *,
    with_constructor: bool = True,
    use_smallest: bool = True
):
    """
    <encoding name="smallint" code="0x54" category="fixed" width="1" label="8-bit two's-complement integer"/>
    <encoding code="0x71" category="fixed" width="4" label="32-bit two's-complement integer in network byte order"/>
    """
    value = int(value)
    try:
        if use_smallest and (-128 <= value <= 127):
            output.extend(_construct(ConstructorBytes.int_small, with_constructor))
            output.extend(struct.pack(">b", value))
            return
        output.extend(_construct(ConstructorBytes.int_large, with_constructor))
        output.extend(struct.pack(">i", value))
    except struct.error as error:
        raise ValueError(f"Value supplied for int invalid: {value}") from error


def _encode_long(
    output: Buffer,
    value: Union[int, datetime],
    *,
    with_constructor: bool = True,
    use_smallest: bool = True
) -> None:
    """
    <encoding name="smalllong" code="0x55" category="fixed" width="1" label="8-bit two's-complement integer"/>
    <encoding code="0x81" category="fixed" width="8" label="64-bit two's-complement integer in network byte order"/>
    """
    if isinstance(value, datetime):
        value = (calendar.timegm(value.utctimetuple()) * 1000) + (value.microsecond / 1000)
    value = int(value)
    try:
        if use_smallest and (-128 <= value <= 127):
            output.extend(_construct(ConstructorBytes.long_small, with_constructor))
            output.extend(struct.pack(">b", value))
            return
        output.extend(_construct(ConstructorBytes.long_large, with_constructor))
        output.extend(struct.pack(">q", value))
    except struct.error as error:
        raise ValueError(f"Value supplied for long invalid: {value}") from error


def _encode_float(
    output: Buffer,
    value: float,
    *,
    with_constructor: bool = True,
    **_
) -> None:
    """
    <encoding name="ieee-754" code="0x72" category="fixed" width="4" label="IEEE 754-2008 binary32"/>
    """
    value = float(value)
    try:
        output.extend(_construct(ConstructorBytes.float, with_constructor))
        output.extend(struct.pack(">f", value))
    except struct.error as error:
        raise ValueError(f"Value supplied for float invalid: {value}") from error


def _encode_double(
    output: Buffer,
    value: float,
    *,
    with_constructor: bool = True,
    **_
) -> None:
    """
    <encoding name="ieee-754" code="0x82" category="fixed" width="8" label="IEEE 754-2008 binary64"/>
    """
    value = float(value)
    try:
        output.extend(_construct(ConstructorBytes.double, with_constructor))
        output.extend(struct.pack(">d", value))
    except struct.error as error:
        raise ValueError(f"Value supplied for double invalid: {value}") from error


def _encode_timestamp(
    output: Buffer,
    value: Union[int, datetime],
    *,
    with_constructor: bool = True,
    **_
) -> None:
    """
    <encoding name="ms64" code="0x83" category="fixed" width="8"
        label="64-bit two's-complement integer representing milliseconds since the unix epoch"/>
    """
    if isinstance(value, datetime):
        value = (calendar.timegm(value.utctimetuple()) * 1000) + (value.microsecond / 1000)
    value = int(value)
    try:
        output.extend(_construct(ConstructorBytes.timestamp, with_constructor))
        output.extend(struct.pack(">q", value))
    except struct.error as error:
        raise ValueError(f"Value supplied for timestamp invalid: {value}") from error


def _encode_uuid(
    output: Buffer,
    value: Union[uuid.UUID, str, bytes],
    *,
    with_constructor: bool = True,
    **_
) -> None:
    """
    <encoding code="0x98" category="fixed" width="16" label="UUID as defined in section 4.1.2 of RFC-4122"/>
    """
    if isinstance(value, str):
        value = uuid.UUID(value).bytes
    elif isinstance(value, uuid.UUID):
        value = value.bytes
    elif isinstance(value, bytes):
        value = uuid.UUID(bytes=value).bytes
    else:
        raise TypeError(f"Invalid UUID type: {type(value)}")
    output.extend(_construct(ConstructorBytes.uuid, with_constructor))
    output.extend(value)


def _encode_binary(
    output: Buffer,
    value: Union[bytes, bytearray],
    *,
    with_constructor: bool = True,
    use_smallest: bool = True
) -> None:
    """
    <encoding name="vbin8" code="0xa0" category="variable" width="1" label="up to 2^8 - 1 octets of binary data"/>
    <encoding name="vbin32" code="0xb0" category="variable" width="4" label="up to 2^32 - 1 octets of binary data"/>
    """
    length = len(value)
    if use_smallest and length <= 255:
        output.extend(_construct(ConstructorBytes.binary_small, with_constructor))
        output.extend(struct.pack(">B", length))
        output.extend(value)
        return
    try:
        output.extend(_construct(ConstructorBytes.binary_large, with_constructor))
        output.extend(struct.pack(">L", length))
        output.extend(value)
    except struct.error as error:
        raise ValueError("Binary data to long to encode") from error


def _encode_string(
    output: Buffer,
    value: AnyStr,
    *,
    with_constructor: bool = True,
    use_smallest: bool = True
) -> None:
    """
    <encoding name="str8-utf8" code="0xa1" category="variable" width="1"
        label="up to 2^8 - 1 octets worth of UTF-8 Unicode (with no byte order mark)"/>
    <encoding name="str32-utf8" code="0xb1" category="variable" width="4"
        label="up to 2^32 - 1 octets worth of UTF-8 Unicode (with no byte order mark)"/>
    """
    if isinstance(value, str):
        value = value.encode("utf-8")
    length = len(value)
    if use_smallest and length <= 255:
        output.extend(_construct(ConstructorBytes.string_small, with_constructor))
        output.extend(struct.pack(">B", length))
        output.extend(value)
        return
    try:
        output.extend(_construct(ConstructorBytes.string_large, with_constructor))
        output.extend(struct.pack(">L", length))
        output.extend(value)
    except struct.error as error:
        raise ValueError("String value too long to encode.") from error


def _encode_symbol(
    output: Buffer,
    value: AnyStr,
    *,
    with_constructor: bool = True,
    use_smallest: bool = True
) -> None:
    """
    <encoding name="sym8" code="0xa3" category="variable" width="1"
        label="up to 2^8 - 1 seven bit ASCII characters representing a symbolic value"/>
    <encoding name="sym32" code="0xb3" category="variable" width="4"
        label="up to 2^32 - 1 seven bit ASCII characters representing a symbolic value"/>
    """
    if isinstance(value, str):
        value = value.encode("utf-8")
    length = len(value)
    if use_smallest and length <= 255:
        output.extend(_construct(ConstructorBytes.symbol_small, with_constructor))
        output.extend(struct.pack(">B", length))
        output.extend(value)
        return
    try:
        output.extend(_construct(ConstructorBytes.symbol_large, with_constructor))
        output.extend(struct.pack(">L", length))
        output.extend(value)
    except struct.error as error:
        raise ValueError("Symbol value too long to encode.") from error


def _encode_list(
    output: Buffer,
    value: MutableSequence[AMQP_DEFINED_TYPES],
    *,
    with_constructor: bool = True,
    use_smallest: bool = True
) -> None:
    """
    <encoding name="list0" code="0x45" category="fixed" width="0"
        label="the empty list (i.e. the list with no elements)"/>
    <encoding name="list8" code="0xc0" category="compound" width="1"
        label="up to 2^8 - 1 list elements with total size less than 2^8 octets"/>
    <encoding name="list32" code="0xd0" category="compound" width="4"
        label="up to 2^32 - 1 list elements with total size less than 2^32 octets"/>
    """
    count = len(value)
    if use_smallest and count == 0:
        output.extend(ConstructorBytes.list_0)
        return
    encoded_size = 0
    encoded_values = bytearray()
    for item in value:
        _encode_value(encoded_values, item, with_constructor=True)
    encoded_size += len(encoded_values)
    if use_smallest and count <= 255 and encoded_size < 255:
        output.extend(_construct(ConstructorBytes.list_small, with_constructor))
        output.extend(struct.pack(">B", encoded_size + 1))
        output.extend(struct.pack(">B", count))
    else:
        try:
            output.extend(_construct(ConstructorBytes.list_large, with_constructor))
            output.extend(struct.pack(">L", encoded_size + 4))
            output.extend(struct.pack(">L", count))
        except struct.error as error:
            raise ValueError("List is too large or too long to be encoded.") from error
    output.extend(encoded_values)

def _encode_map(
    output: Buffer,
    value: Mapping[Union[AMQPDefinition, AMQP_BASIC_TYPES], AMQP_DEFINED_TYPES],
    *,
    with_constructor: bool = True,
    use_smallest: bool = True
) -> None:
    """
    <encoding name="map8" code="0xc1" category="compound" width="1"
        label="up to 2^8 - 1 octets of encoded map data"/>
    <encoding name="map32" code="0xd1" category="compound" width="4"
        label="up to 2^32 - 1 octets of encoded map data"/>
    """
    count = len(value) * 2
    encoded_size = 0
    encoded_values = bytearray()
    for key, data in value.items():
        _encode_value(encoded_values, key, with_constructor=True)
        _encode_value(encoded_values, data, with_constructor=True)
    encoded_size = len(encoded_values)
    if use_smallest and count <= 255 and encoded_size < 255:
        output.extend(_construct(ConstructorBytes.map_small, with_constructor))
        output.extend(struct.pack(">B", encoded_size + 1))
        output.extend(struct.pack(">B", count))
    else:
        try:
            output.extend(_construct(ConstructorBytes.map_large, with_constructor))
            output.extend(struct.pack(">L", encoded_size + 4))
            output.extend(struct.pack(">L", count))
        except struct.error:
            raise ValueError("Map is too large or too long to be encoded.")
    output.extend(encoded_values)


def _check_element_type(
    item: AMQP_DEFINED_TYPES,
    element_type: Optional[Union[AMQPTypes, Type]]
) -> Union[AMQPTypes, Type]:
    if not element_type:
        try:
            return item[TYPE_KEY]
        except (KeyError, TypeError):
            return type(item)
    try:
        if item[TYPE_KEY] != element_type:
            raise TypeError(
                f"All elements in an array must be the same type. Expected '{element_type}', got '{item[TYPE_KEY]}'."
            )
    except (KeyError, TypeError):
        if not isinstance(item, element_type):
            raise TypeError(
                f"All elements in an array must be the same type. Expected '{element_type}', got '{type(item)}'."
            )
    return element_type


def _encode_array(
    output: Buffer, 
    value: MutableSequence[AMQP_DEFINED_TYPES],
    *,
    with_constructor: bool = True,
    use_smallest: bool = True
) -> None:
    """
    <encoding name="array8" code="0xe0" category="array" width="1"
        label="up to 2^8 - 1 array elements with total size less than 2^8 octets"/>
    <encoding name="array32" code="0xf0" category="array" width="4"
        label="up to 2^32 - 1 array elements with total size less than 2^32 octets"/>
    """
    count = len(value)
    encoded_size = 0
    encoded_values = bytearray()
    first_item = True
    element_type = None
    for item in value:
        element_type = _check_element_type(item, element_type)
        _encode_value(
            encoded_values, item, with_constructor=first_item, use_smallest=False
        )
        first_item = False
        if item is None:
            encoded_size -= 1
            break
    encoded_size += len(encoded_values)
    if use_smallest and count <= 255 and encoded_size < 255:
        output.extend(_construct(ConstructorBytes.array_small, with_constructor))
        output.extend(struct.pack(">B", encoded_size + 1))
        output.extend(struct.pack(">B", count))
    else:
        try:
            output.extend(_construct(ConstructorBytes.array_large, with_constructor))
            output.extend(struct.pack(">L", encoded_size + 4))
            output.extend(struct.pack(">L", count))
        except struct.error as error:
            raise ValueError("Array is too large or too long to be encoded.") from error
    output.extend(encoded_values)


def _encode_described(
    output: Buffer,
    value: Tuple[Union[AMQPDefinition, AMQP_BASIC_TYPES], AMQP_DEFINED_TYPES],
    **kwargs: Any
) -> None:
    output.extend(ConstructorBytes.descriptor)
    _encode_value(output, value[0], **kwargs)
    _encode_value(output, value[1], **kwargs)


def _encode_fields(
    output: Buffer,
    value: Mapping[AnyStr, AMQP_DEFINED_TYPES],
    **_
) -> None:
    """A mapping from field name to value.

    The fields type is a map where the keys are restricted to be of type symbol (this excludes the possibility
    of a null key).  There is no further restriction implied by the fields type on the allowed values for the
    entries or the set of allowed keys.

    <type name="fields" class="restricted" source="map"/>
    """
    fields: Dict[AMQPDefinition[AMQPTypes.symbol, AnyStr], AMQP_DEFINED_TYPES] = {
        {TYPE_KEY: AMQPTypes.symbol, VALUE_KEY: key}: data for key, data in value.items()
    }
    _encode_map(output, fields)


def _encode_annotations(
    output: Buffer,
    value: Mapping[Union[AnyStr, int], AMQP_DEFINED_TYPES],
    **_
) -> None:
    """The annotations type is a map where the keys are restricted to be of type symbol or of type ulong.

    All ulong keys, and all symbolic keys except those beginning with "x-" are reserved.
    On receiving an annotations map containing keys or values which it does not recognize, and for which the
    key does not begin with the string 'x-opt-' an AMQP container MUST detach the link with the not-implemented
    amqp-error.

    <type name="annotations" class="restricted" source="map"/>
    """
    annotations: Dict[
        Union[AMQPDefinition[AMQPTypes.symbol, AnyStr], AMQPDefinition[AMQPTypes.ulong, int]],
        AMQP_DEFINED_TYPES
    ] = {
        {TYPE_KEY: AMQPTypes.ulong, VALUE_KEY: k} if isinstance(k, int) else {TYPE_KEY: AMQPTypes.symbol, VALUE_KEY: k}: v for k, v in value.items()
    }
    _encode_map(output, annotations)


def _encode_application_properties(
    output: Buffer,
    value: Mapping[AnyStr, Union[AMQPDefinition, AMQP_BASIC_TYPES]],
    **_
) -> None:
    """The application-properties section is a part of the bare message used for structured application data.

    <type name="application-properties" class="restricted" source="map" provides="section">
        <descriptor name="amqp:application-properties:map" code="0x00000000:0x00000074"/>
    </type>

    Intermediaries may use the data within this structure for the purposes of filtering or routing.
    The keys of this map are restricted to be of type string (which excludes the possibility of a null key)
    and the values are restricted to be of simple types only, that is (excluding map, list, and array types).
    """
    properties: Dict[AMQPDefinition[AMQPTypes.string, AnyStr], Any] = {
        {TYPE_KEY: AMQPTypes.string, VALUE_KEY: key}: data for key, data in value.items()
    }
    _encode_map(output, properties)


def _encode_message_id(
    output: Buffer,
    value: Union[int, uuid.UUID, bytes, str],
    **_
) -> None:
    """
    <type name="message-id-ulong" class="restricted" source="ulong" provides="message-id"/>
    <type name="message-id-uuid" class="restricted" source="uuid" provides="message-id"/>
    <type name="message-id-binary" class="restricted" source="binary" provides="message-id"/>
    <type name="message-id-string" class="restricted" source="string" provides="message-id"/>
    """
    if isinstance(value, int):
        _encode_ulong(output, value)
    if isinstance(value, uuid.UUID):
        _encode_uuid(output, value)
    if isinstance(value, bytes):
        _encode_binary(output, value)
    if isinstance(value, str):
        _encode_string(output, value)
    raise TypeError("Unsupported Message ID type.")


def _encode_node_properties(output: Buffer, value: Any, **_) -> None:
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
    raise NotImplementedError("Encoding node properties is not currently supported.")


def _encode_filter_set(
    output: Buffer,
    value: Mapping[AnyStr, Optional[Tuple[AnyStr, AMQP_DEFINED_TYPES]]],
    **_
) -> None:
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
    filters: Dict[AMQPDefinition[AMQPTypes.symbol, AnyStr], AMQPDefinition] = {}
    for name, data in value.items():
        if data is None:
            described_filter = {TYPE_KEY: AMQPTypes.null, VALUE_KEY: None}
        else:
            descriptor, filter_value = data
            described_filter = {
                TYPE_KEY: AMQPTypes.described,
                VALUE_KEY: ({TYPE_KEY: AMQPTypes.symbol, VALUE_KEY: descriptor}, filter_value),
            }
        filters[{TYPE_KEY: AMQPTypes.symbol, VALUE_KEY: name}] = described_filter
    _encode_map(output, filters)


def _encode_unknown(
    output: Buffer,
    value: AMQP_FULL_TYPES,
    **kwargs: Any
) -> None:
    """
    Dynamic encoding according to the type of `value`.
    """
    if value is None:
        _encode_null(output, **kwargs)
    elif isinstance(value, bool):
        _encode_boolean(output, value, **kwargs)
    elif isinstance(value, str):
        _encode_string(output, value, **kwargs)
    elif isinstance(value, uuid.UUID):
        _encode_uuid(output, value, **kwargs)
    elif isinstance(value, (bytearray, bytes)):
        _encode_binary(output, value, **kwargs)
    elif isinstance(value, float):
        _encode_double(output, value, **kwargs)
    elif isinstance(value, int):
        _encode_int(output, value, **kwargs)
    elif isinstance(value, datetime):
        _encode_timestamp(output, value, **kwargs)
    elif isinstance(value, MutableSequence):
        _encode_list(output, value, **kwargs)
    elif isinstance(value, tuple):
        _encode_described(output, value, **kwargs)
    elif isinstance(value, Mapping):
        _encode_map(output, value, **kwargs)
    else:
        raise TypeError(f"Unable to encode unknown value: {value}")


_ENCODE_MAP: Dict[AMQPTypes, _EncodeCallable] = {
    AMQPTypes.null: _encode_null,
    AMQPTypes.boolean: _encode_boolean,
    AMQPTypes.ubyte: _encode_ubyte,
    AMQPTypes.byte: _encode_byte,
    AMQPTypes.ushort: _encode_ushort,
    AMQPTypes.short: _encode_short,
    AMQPTypes.uint: _encode_uint,
    AMQPTypes.int: _encode_int,
    AMQPTypes.ulong: _encode_ulong,
    AMQPTypes.long: _encode_long,
    AMQPTypes.float: _encode_float,
    AMQPTypes.double: _encode_double,
    AMQPTypes.timestamp: _encode_timestamp,
    AMQPTypes.uuid: _encode_uuid,
    AMQPTypes.binary: _encode_binary,
    AMQPTypes.string: _encode_string,
    AMQPTypes.symbol: _encode_symbol,
    AMQPTypes.list: _encode_list,
    AMQPTypes.map: _encode_map,
    AMQPTypes.array: _encode_array,
    AMQPTypes.described: _encode_described,
    AMQPTypes.fields: _encode_fields,
    AMQPTypes.annotations: _encode_annotations,
    AMQPTypes.message_id: _encode_message_id,
    AMQPTypes.app_properties: _encode_application_properties,
    AMQPTypes.node_properties: _encode_node_properties,
    AMQPTypes.filter_set: _encode_filter_set,
}


def _encode_value(output: Buffer, value: AMQPDefinition, **kwargs) -> None:
    try:
        _ENCODE_MAP[value[TYPE_KEY]](output, value[VALUE_KEY], **kwargs)
    except (KeyError, TypeError):
        _encode_unknown(output, value, **kwargs)


def encode_payload(output: Buffer, payload: Message) -> Buffer:
    if payload.header:
        # TODO: Header encoding can be optimized to encode bool without constructor
        _encode_value(output, payload.header._describe())
    if payload.message_annotations:
        _encode_described(
            output,
            (
                {TYPE_KEY: AMQPTypes.ulong, VALUE_KEY: 0x00000072},
                _encode_annotations(payload.message_annotations),
            )
        )
    if payload.properties:
        _encode_value(output, payload.properties._describe())
    if payload.application_properties:
        _encode_described(
            output,
            (
                {TYPE_KEY: AMQPTypes.ulong, VALUE_KEY: 0x00000074},
                _encode_application_properties(payload.application_properties),
            )
        )
    if payload.data:
        for item_value in payload.data:
            _encode_described(
                output,
                (
                    {TYPE_KEY: AMQPTypes.ulong, VALUE_KEY: 0x00000075},
                    {TYPE_KEY: AMQPTypes.binary, VALUE_KEY: item_value},
                )
            )
    if payload.sequence:
        for item_value in payload.sequence:
            _encode_described(
                output,
                (
                    {TYPE_KEY: AMQPTypes.ulong, VALUE_KEY: 0x00000076},
                    item_value,
                )
            )
    if payload.value:
        _encode_described(
            output,
            (
                {TYPE_KEY: AMQPTypes.ulong, VALUE_KEY: 0x00000077},
                payload.value,
            )
        )
    if payload.footer:
        _encode_described(
            output,
            (
                {TYPE_KEY: AMQPTypes.ulong, VALUE_KEY: 0x00000078},
                _encode_annotations(payload.footer),
            )
        )
    if payload.delivery_annotations:
        _encode_described(
            output,
            (
                {TYPE_KEY: AMQPTypes.ulong, VALUE_KEY: 0x00000071},
                _encode_annotations(payload.delivery_annotations),
            )
        )
    return output


def encode_frame(
    frame: Optional[Performative],
    frame_type: bytes = _FRAME_TYPE
) -> Tuple[bytes, Optional[Buffer]]:
    if frame is None:
        size = 8
        header = size.to_bytes(4, "big") + _FRAME_OFFSET + frame_type
        return header, None

    frame_description = frame._describe()
    frame_data = bytearray()
    _encode_value(frame_data, frame_description)

    if frame._code == 20:  # TransferFrame
        frame_data += frame.payload

    size = len(frame_data) + 8
    header = size.to_bytes(4, "big") + _FRAME_OFFSET + frame_type
    return header, frame_data

__all__ = [
    'encode_frame',
    'encode_payload'
]
