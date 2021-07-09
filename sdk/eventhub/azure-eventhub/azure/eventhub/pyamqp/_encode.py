#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

import calendar
import struct
import uuid
from datetime import datetime
from typing import Iterable, Union, Tuple, Dict  # pylint: disable=unused-import

import six

from .types import TYPE, VALUE, AMQPTypes, FieldDefinition, ObjDefinition, ConstructorBytes
from .message import Header, Properties, Message
from . import performatives
from . import outcomes
from . import endpoints
from . import error


_FRAME_OFFSET = b"\x02"
_FRAME_TYPE = b'\x00'


def _construct(byte, construct):
    # type: (bytes, bool) -> bytes
    return byte if construct else b''


def encode_null(output, *args, **kwargs):  # pylint: disable=unused-argument
    # type: (bytes, Any, Any) -> bytes
    """
    encoding code="0x40" category="fixed" width="0" label="the null value"
    """
    return output + ConstructorBytes.null


def encode_boolean(output, value, with_constructor=True, **kwargs):  # pylint: disable=unused-argument
    # type: (bytes, bool, bool, Any) -> bytes
    """
    <encoding name="true" code="0x41" category="fixed" width="0" label="the boolean value true"/>
    <encoding name="false" code="0x42" category="fixed" width="0" label="the boolean value false"/>
    <encoding code="0x56" category="fixed" width="1"
        label="boolean with the octet 0x00 being false and octet 0x01 being true"/>
    """
    value = bool(value)
    if with_constructor:
        output += _construct(ConstructorBytes.bool, with_constructor)
        if value:
            return output + b'\x01'
        return output + b'\x00'
    if value:
        return output + ConstructorBytes.bool_true
    return output + ConstructorBytes.bool_false


def encode_ubyte(output, value, with_constructor=True, **kwargs):  # pylint: disable=unused-argument
    # type: (bytes, Union[int, bytes], bool, Any) -> bytes
    """
    <encoding code="0x50" category="fixed" width="1" label="8-bit unsigned integer"/>
    """
    try:
        value = int(value)
    except ValueError:
        value = ord(value)
    try:
        output += _construct(ConstructorBytes.ubyte, with_constructor)
        return output + struct.pack('>B', abs(value))
    except struct.error:
        raise ValueError("Unsigned byte value must be 0-255")


def encode_ushort(output, value, with_constructor=True, **kwargs):  # pylint: disable=unused-argument
    # type: (bytes, int, bool, Any) -> bytes
    """
    <encoding code="0x60" category="fixed" width="2" label="16-bit unsigned integer in network byte order"/>
    """
    value = int(value)
    try:
        output += _construct(ConstructorBytes.ushort, with_constructor)
        return output + struct.pack('>H', abs(value))
    except struct.error:
        raise ValueError("Unsigned byte value must be 0-65535")


def encode_uint(output, value, with_constructor=True, use_smallest=True):
    # type: (bytes, int, bool, bool) -> bytes
    """
    <encoding name="uint0" code="0x43" category="fixed" width="0" label="the uint value 0"/>
    <encoding name="smalluint" code="0x52" category="fixed" width="1"
        label="unsigned integer value in the range 0 to 255 inclusive"/>
    <encoding code="0x70" category="fixed" width="4" label="32-bit unsigned integer in network byte order"/>
    """
    value = int(value)
    if value == 0:
        return output + ConstructorBytes.uint_0
    try:
        if use_smallest and value <= 255:
            output += _construct(ConstructorBytes.uint_small, with_constructor)
            return output + struct.pack('>B', abs(value))
        output += _construct(ConstructorBytes.uint_large, with_constructor)
        return output + struct.pack('>I', abs(value))
    except struct.error:
        raise ValueError("Value supplied for unsigned int invalid: {}".format(value))


def encode_ulong(output, value, with_constructor=True, use_smallest=True):
    # type: (bytes, int, bool, bool) -> bytes
    """
    <encoding name="ulong0" code="0x44" category="fixed" width="0" label="the ulong value 0"/>
    <encoding name="smallulong" code="0x53" category="fixed" width="1"
        label="unsigned long value in the range 0 to 255 inclusive"/>
    <encoding code="0x80" category="fixed" width="8" label="64-bit unsigned integer in network byte order"/>
    """
    try:
        value = long(value)
    except NameError:
        value = int(value)
    if value == 0:
        return output + ConstructorBytes.ulong_0
    try:
        if use_smallest and value <= 255:
            output += _construct(ConstructorBytes.ulong_small, with_constructor)
            return output + struct.pack('>B', abs(value))
        output += _construct(ConstructorBytes.ulong_large, with_constructor)
        return output + struct.pack('>Q', abs(value))
    except struct.error:
        raise ValueError("Value supplied for unsigned long invalid: {}".format(value))


def encode_byte(output, value, with_constructor=True, **kwargs):  # pylint: disable=unused-argument
    # type: (bytes, int, bool, Any) -> bytes
    """
    <encoding code="0x51" category="fixed" width="1" label="8-bit two's-complement integer"/>
    """
    value = int(value)
    try:
        output += _construct(ConstructorBytes.byte, with_constructor)
        return output + struct.pack('>b', value)
    except struct.error:
        raise ValueError("Byte value must be -128-127")


def encode_short(output, value, with_constructor=True, **kwargs):  # pylint: disable=unused-argument
    # type: (bytes, int, bool, Any) -> bytes
    """
    <encoding code="0x61" category="fixed" width="2" label="16-bit two's-complement integer in network byte order"/>
    """
    value = int(value)
    try:
        output += _construct(ConstructorBytes.short, with_constructor)
        return output + struct.pack('>h', value)
    except struct.error:
        raise ValueError("Short value must be -32768-32767")


def encode_int(output, value, with_constructor=True, use_smallest=True):
    # type: (bytes, int, bool, bool) -> bytes
    """
    <encoding name="smallint" code="0x54" category="fixed" width="1" label="8-bit two's-complement integer"/>
    <encoding code="0x71" category="fixed" width="4" label="32-bit two's-complement integer in network byte order"/>
    """
    value = int(value)
    try:
        if use_smallest and (-128 <= value <= 127):
            output += _construct(ConstructorBytes.int_small, with_constructor)
            return output + struct.pack('>b', value)
        output += _construct(ConstructorBytes.int_large, with_constructor)
        return output + struct.pack('>i', value)
    except struct.error:
        raise ValueError("Value supplied for int invalid: {}".format(value))


def encode_long(output, value, with_constructor=True, use_smallest=True):
    # type: (bytes, int, bool, bool) -> bytes
    """
    <encoding name="smalllong" code="0x55" category="fixed" width="1" label="8-bit two's-complement integer"/>
    <encoding code="0x81" category="fixed" width="8" label="64-bit two's-complement integer in network byte order"/>
    """
    try:
        value = long(value)
    except NameError:
        value = int(value)
    try:
        if use_smallest and (-128 <= value <= 127):
            output += _construct(ConstructorBytes.long_small, with_constructor)
            return output + struct.pack('>b', value)
        output += _construct(ConstructorBytes.long_large, with_constructor)
        return output + struct.pack('>q', value)
    except struct.error:
        raise ValueError("Value supplied for long invalid: {}".format(value))

def encode_float(output, value, with_constructor=True, **kwargs):  # pylint: disable=unused-argument
    # type: (bytes, float, bool, Any) -> bytes
    """
    <encoding name="ieee-754" code="0x72" category="fixed" width="4" label="IEEE 754-2008 binary32"/>
    """
    value = float(value)
    output += _construct(ConstructorBytes.float, with_constructor)
    return output + struct.pack('>f', value)


def encode_double(output, value, with_constructor=True, **kwargs):  # pylint: disable=unused-argument
    # type: (bytes, float, bool, Any) -> bytes
    """
    <encoding name="ieee-754" code="0x82" category="fixed" width="8" label="IEEE 754-2008 binary64"/>
    """
    value = float(value)
    output += _construct(ConstructorBytes.double, with_constructor)
    return output + struct.pack('>d', value)


def encode_timestamp(output, value, with_constructor=True, **kwargs):  # pylint: disable=unused-argument
    # type: (bytes, Union[int, datetime], bool, Any) -> bytes
    """
    <encoding name="ms64" code="0x83" category="fixed" width="8"
        label="64-bit two's-complement integer representing milliseconds since the unix epoch"/>
    """
    if isinstance(value, datetime):
        value = (calendar.timegm(value.utctimetuple()) * 1000) + (value.microsecond/1000)
    value = int(value)
    output += _construct(ConstructorBytes.timestamp, with_constructor)
    return output + struct.pack('>q', value)


def encode_uuid(output, value, with_constructor=True, **kwargs):  # pylint: disable=unused-argument
    # type: (bytes, Union[uuid.UUID, str, bytes], bool, Any) -> bytes
    """
    <encoding code="0x98" category="fixed" width="16" label="UUID as defined in section 4.1.2 of RFC-4122"/>
    """
    if isinstance(value, six.text_type):
        value = uuid.UUID(value).bytes
    elif isinstance(value, uuid.UUID):
        value = value.bytes
    elif isinstance(value, six.binary_type):
        value = uuid.UUID(bytes=value).bytes
    else:
        raise TypeError("Invalid UUID type: {}".format(type(value)))
    output += _construct(ConstructorBytes.uuid, with_constructor)
    return output + value


def encode_binary(output, value, with_constructor=True, use_smallest=True):
    # type: (bytes, Union[bytes, bytearray], bool, bool)
    """
    <encoding name="vbin8" code="0xa0" category="variable" width="1" label="up to 2^8 - 1 octets of binary data"/>
    <encoding name="vbin32" code="0xb0" category="variable" width="4" label="up to 2^32 - 1 octets of binary data"/>
    """
    length = len(value)
    if use_smallest and length <= 255:
        output += _construct(ConstructorBytes.binary_small, with_constructor)
        output += struct.pack('>B', length)
        return output + value
    try:
        output += _construct(ConstructorBytes.binary_large, with_constructor)
        output += struct.pack('>L', length)
        return output + value
    except struct.error:
        raise ValueError("Binary data to long to encode")


def encode_string(output, value, with_constructor=True, use_smallest=True):
    # type: (bytes, Union[bytes, str], bool, bool)
    """
    <encoding name="str8-utf8" code="0xa1" category="variable" width="1"
        label="up to 2^8 - 1 octets worth of UTF-8 Unicode (with no byte order mark)"/>
    <encoding name="str32-utf8" code="0xb1" category="variable" width="4"
        label="up to 2^32 - 1 octets worth of UTF-8 Unicode (with no byte order mark)"/>
    """
    if isinstance(value, six.text_type):
        value = value.encode('utf-8')
    length = len(value)
    if use_smallest and length <= 255:
        output += _construct(ConstructorBytes.string_small, with_constructor)
        output += struct.pack('>B', length)
        return output + value
    try:
        output += _construct(ConstructorBytes.string_large, with_constructor)
        output += struct.pack('>L', length)
        return output + value
    except struct.error:
        raise ValueError("String value too long to encode.")


def encode_symbol(output, value, with_constructor=True, use_smallest=True):
    # type: (bytes, Union[bytes, str], bool, bool) -> bytes
    """
    <encoding name="sym8" code="0xa3" category="variable" width="1"
        label="up to 2^8 - 1 seven bit ASCII characters representing a symbolic value"/>
    <encoding name="sym32" code="0xb3" category="variable" width="4"
        label="up to 2^32 - 1 seven bit ASCII characters representing a symbolic value"/>
    """
    if isinstance(value, six.text_type):
        value = value.encode('utf-8')
    length = len(value)
    if use_smallest and length <= 255:
        output += _construct(ConstructorBytes.symbol_small, with_constructor)
        output += struct.pack('>B', length)
        return output + value
    try:
        output += _construct(ConstructorBytes.symbol_large, with_constructor)
        output += struct.pack('>L', length)
        return output + value
    except struct.error:
        raise ValueError("Symbol value too long to encode.")


def encode_list(output, value, with_constructor=True, use_smallest=True):
    # type: (bytes, Iterable[Any], bool, bool) -> bytes
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
        return output + ConstructorBytes.list_0
    encoded_size = 0
    encoded_values = []
    for item in value:
        encoded_values.append(encode_value(b"", item, with_constructor=True))
        encoded_size += len(encoded_values[-1])
    if use_smallest and count <= 255 and encoded_size < 255:
        output += _construct(ConstructorBytes.list_small, with_constructor)
        output += struct.pack('>B', encoded_size + 1)
        output += struct.pack('>B', count)
    else:
        try:
            output += _construct(ConstructorBytes.list_large, with_constructor)
            output += struct.pack('>L', encoded_size + 4)
            output += struct.pack('>L', count)
        except struct.error:
            raise ValueError("List is too large or too long to be encoded.")
    return output + b"".join(encoded_values)


def encode_map(output, value, with_constructor=True, use_smallest=True):
    # type: (bytes, Union[Dict[Any, Any], Iterable[Tuple[Any, Any]]], bool, bool) -> bytes
    """
    <encoding name="map8" code="0xc1" category="compound" width="1"
        label="up to 2^8 - 1 octets of encoded map data"/>
    <encoding name="map32" code="0xd1" category="compound" width="4"
        label="up to 2^32 - 1 octets of encoded map data"/>
    """
    count = len(value) * 2
    encoded_size = 0
    encoded_values = []
    try:
        items = value.items()
    except AttributeError:
        items = value
    for key, data in items:
        encoded_values.append(encode_value(b"", key, with_constructor=True))
        encoded_size += len(encoded_values[-1])
        encoded_values.append(encode_value(b"", data, with_constructor=True))
        encoded_size += len(encoded_values[-1])
    if use_smallest and count <= 255 and encoded_size < 255:
        output += _construct(ConstructorBytes.map_small, with_constructor)
        output += struct.pack('>B', encoded_size + 1)
        output += struct.pack('>B', count)
    else:
        try:
            output += _construct(ConstructorBytes.map_large, with_constructor)
            output += struct.pack('>L', encoded_size + 4)
            output += struct.pack('>L', count)
        except struct.error:
            raise ValueError("Map is too large or too long to be encoded.")
    return output + b"".join(encoded_values)


def _check_element_type(item, element_type):
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


def encode_array(output, value, with_constructor=True, use_smallest=True):
    # type: (bytes, Iterable[Any], bool, bool) -> bytes
    """
    <encoding name="map8" code="0xE0" category="compound" width="1"
        label="up to 2^8 - 1 octets of encoded map data"/>
    <encoding name="map32" code="0xF0" category="compound" width="4"
        label="up to 2^32 - 1 octets of encoded map data"/>
    """
    count = len(value)
    encoded_size = 0
    encoded_values = []
    first_item = True
    element_type = None
    for item in value:
        element_type = _check_element_type(item, element_type)
        encoded_values.append(encode_value(b"", item, with_constructor=first_item, use_smallest=False))
        encoded_size += len(encoded_values[-1])
        first_item = False
        if item is None:
            encoded_size -= 1
            break
    if use_smallest and count <= 255 and encoded_size < 255:
        output += _construct(ConstructorBytes.array_small, with_constructor)
        output += struct.pack('>B', encoded_size + 1)
        output += struct.pack('>B', count)
    else:
        try:
            output += _construct(ConstructorBytes.array_large, with_constructor)
            output += struct.pack('>L', encoded_size + 4)
            output += struct.pack('>L', count)
        except struct.error:
            raise ValueError("Array is too large or too long to be encoded.")
    return output + b"".join(encoded_values)


def encode_described(output, value, _=None, **kwargs):
    # type: (bytes, Tuple(Any, Any), bool, Any) -> bytes
    output += ConstructorBytes.descriptor
    output = encode_value(output, value[0], **kwargs)
    output = encode_value(output, value[1], **kwargs)
    return output


def encode_fields(value):
    # type: (Optional[Dict[str, Any]]) -> Dict[str, Any]
    """A mapping from field name to value.

    The fields type is a map where the keys are restricted to be of type symbol (this excludes the possibility
    of a null key).  There is no further restriction implied by the fields type on the allowed values for the
    entries or the set of allowed keys.

    <type name="fields" class="restricted" source="map"/>
    """
    if not value:
        return {TYPE: AMQPTypes.null, VALUE: None}
    fields = {TYPE: AMQPTypes.map, VALUE:[]}
    for key, data in value.items():
        if isinstance(key, six.text_type):
            key = key.encode('utf-8')
        fields[VALUE].append(({TYPE: AMQPTypes.symbol, VALUE: key}, data))
    return fields


def encode_annotations(value):
    # type: (Optional[Dict[str, Any]]) -> Dict[str, Any]
    """The annotations type is a map where the keys are restricted to be of type symbol or of type ulong.

    All ulong keys, and all symbolic keys except those beginning with "x-" are reserved.
    On receiving an annotations map containing keys or values which it does not recognize, and for which the
    key does not begin with the string 'x-opt-' an AMQP container MUST detach the link with the not-implemented
    amqp-error.

    <type name="annotations" class="restricted" source="map"/>
    """
    if not value:
        return {TYPE: AMQPTypes.null, VALUE: None}
    fields = {TYPE: AMQPTypes.map, VALUE:[]}
    for key, data in value.items():
        if isinstance(key, int):
            fields[VALUE].append(({TYPE: AMQPTypes.ulong, VALUE: key}, {TYPE: None, VALUE: data}))
        else:
            if isinstance(key, six.text_type):
                key = key.encode('utf-8')
            fields[VALUE].append(({TYPE: AMQPTypes.symbol, VALUE: key}, {TYPE: None, VALUE: data}))
    return fields


def encode_application_properties(value):
    # type: (Optional[Dict[str, Any]]) -> Dict[str, Any]
    """The application-properties section is a part of the bare message used for structured application data.

    <type name="application-properties" class="restricted" source="map" provides="section">
        <descriptor name="amqp:application-properties:map" code="0x00000000:0x00000074"/>
    </type>

    Intermediaries may use the data within this structure for the purposes of filtering or routing.
    The keys of this map are restricted to be of type string (which excludes the possibility of a null key)
    and the values are restricted to be of simple types only, that is (excluding map, list, and array types).
    """
    if not value:
        return {TYPE: AMQPTypes.null, VALUE: None}
    fields = {TYPE: AMQPTypes.map, VALUE:[]}
    for key, data in value.items():
        fields[VALUE].append(({TYPE: AMQPTypes.string, VALUE: key}, data))
    return fields


def encode_message_id(value):
    # type: (Any) -> Dict[str, Union[int, uuid.UUID, bytes, str]]
    """
    <type name="message-id-ulong" class="restricted" source="ulong" provides="message-id"/>
    <type name="message-id-uuid" class="restricted" source="uuid" provides="message-id"/>
    <type name="message-id-binary" class="restricted" source="binary" provides="message-id"/>
    <type name="message-id-string" class="restricted" source="string" provides="message-id"/>
    """
    if isinstance(value, int):
        return {TYPE: AMQPTypes.ulong, VALUE: value}
    elif isinstance(value, uuid.UUID):
        return {TYPE: AMQPTypes.uuid, VALUE: value}
    elif isinstance(value, six.binary_type):
        return {TYPE: AMQPTypes.binary, VALUE: value}
    elif isinstance(value, six.text_type):
        return {TYPE: AMQPTypes.string, VALUE: value}
    raise TypeError("Unsupported Message ID type.")


def encode_node_properties(value):
    # type: (Optional[Dict[str, Any]]) -> Dict[str, Any]
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
    # type: (Optional[Dict[str, Any]]) -> Dict[str, Any]
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
            if isinstance(name, six.text_type):
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


def encode_unknown(output, value, **kwargs):
    # type: (Optional[Any]) -> Dict[str, Any]
    """
    Dynamic encoding according to the type of `value`.
    """
    if value is None:
        output = encode_null(output, **kwargs)
    elif isinstance(value, bool):
        output = encode_boolean(output, value, **kwargs)
    elif isinstance(value, six.string_types):
        output = encode_string(output, value, **kwargs)
    elif isinstance(value, uuid.UUID):
        output = encode_uuid(output, value, **kwargs)
    elif isinstance(value, (bytearray, six.binary_type)):
        output = encode_binary(output, value, **kwargs)
    elif isinstance(value, float):
        output = encode_double(output, value, **kwargs)
    elif isinstance(value, six.integer_types):
        output = encode_int(output, value, **kwargs)
    elif isinstance(value, datetime):
        output = encode_timestamp(output, value, **kwargs)
    elif isinstance(value, list):
        output = encode_list(output, value, **kwargs)
    elif isinstance(value, tuple):
        output = encode_described(output, value, **kwargs)
    elif isinstance(value, dict):
        output = encode_map(output, value, **kwargs)
    else:
        raise TypeError("Unable to encode unknown value: {}".format(value))
    return output


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


def encode_value(output, value, **kwargs):
    # type: (bytes, Any, Any) -> bytes
    try:
        output = _ENCODE_MAP[value[TYPE]](output, value[VALUE], **kwargs)
    except (KeyError, TypeError):
        output = encode_unknown(output, value, **kwargs)
    return output


def describe_performative(performative):
    # type: (Performative) -> Tuple(bytes, bytes)
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


def encode_payload(output, payload):
    # type: (bytes, Message) -> bytes

    if payload[0]:  # header
        # TODO: Header and Properties encoding can be optimized to
        #  1. not encoding trailing None fields
        #  2. encoding bool without constructor
        output = encode_value(output, describe_performative(payload[0]))

    if payload[2]:  # message annotations
        output = encode_value(output, {
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
        output = encode_value(output, describe_performative(payload[3]))

    if payload[4]:  # application properties
        output = encode_value(output, {
            TYPE: AMQPTypes.described,
            VALUE: (
                {TYPE: AMQPTypes.ulong, VALUE: 0x00000074},
                {TYPE: AMQPTypes.map, VALUE: payload[4]}
            )
        })

    if payload[5]:  # data
        for item_value in payload[5]:
            output = encode_value(output, {
                TYPE: AMQPTypes.described,
                VALUE: (
                    {TYPE: AMQPTypes.ulong, VALUE: 0x00000075},
                    {TYPE: AMQPTypes.binary, VALUE: item_value}
                )
            })

    if payload[6]:  # sequence
        for item_value in payload[6]:
            output = encode_value(output, {
                TYPE: AMQPTypes.described,
                VALUE: (
                    {TYPE: AMQPTypes.ulong, VALUE: 0x00000076},
                    {TYPE: None, VALUE: item_value}
                )
            })

    if payload[7]:  # value
        output = encode_value(output, {
            TYPE: AMQPTypes.described,
            VALUE: (
                {TYPE: AMQPTypes.ulong, VALUE: 0x00000077},
                {TYPE: None, VALUE: payload[7]}
            )
        })

    if payload[8]:  # footer
        output = encode_value(output, {
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
        output = encode_value(output, {
            TYPE: AMQPTypes.described,
            VALUE: (
                {TYPE: AMQPTypes.ulong, VALUE: 0x00000071},
                encode_annotations(payload[1]),
            )
        })

    return output


def encode_frame(frame, frame_type=_FRAME_TYPE):
    # type: (Performative) -> Tuple(bytes, bytes)
    if frame is None:
        size = 8
        header = size.to_bytes(4, 'big') + _FRAME_OFFSET + frame_type
        return header, None

    frame_description = describe_performative(frame)
    frame_data = encode_value(b"", frame_description)
    if isinstance(frame, performatives.TransferFrame):
        frame_data += frame.payload

    size = len(frame_data) + 8
    header = size.to_bytes(4, 'big') + _FRAME_OFFSET + frame_type
    return header, frame_data
