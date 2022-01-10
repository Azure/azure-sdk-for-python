#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------
# pylint: disable=redefined-builtin, import-error

import struct
import uuid
import logging
from typing import List, Union, Tuple, Dict, Callable  # pylint: disable=unused-import


from .message import Message, Header, Properties

_LOGGER = logging.getLogger(__name__)
_HEADER_PREFIX = memoryview(b'AMQP')
_COMPOSITES = {
    35: 'received',
    36: 'accepted',
    37: 'rejected',
    38: 'released',
    39: 'modified',
}

c_unsigned_char = struct.Struct('>B')
c_signed_char = struct.Struct('>b')
c_unsigned_short = struct.Struct('>H')
c_signed_short = struct.Struct('>h')
c_unsigned_int = struct.Struct('>I')
c_signed_int = struct.Struct('>i')
c_unsigned_long = struct.Struct('>L')
c_unsigned_long_long = struct.Struct('>Q')
c_signed_long_long = struct.Struct('>q')
c_float = struct.Struct('>f')
c_double = struct.Struct('>d')


def _decode_null(buffer):
    # type: (memoryview) -> Tuple[memoryview, None]
    return buffer, None


def _decode_true(buffer):
    # type: (memoryview) -> Tuple[memoryview, bool]
    return buffer, True


def _decode_false(buffer):
    # type: (memoryview) -> Tuple[memoryview, bool]
    return buffer, False


def _decode_zero(buffer):
    # type: (memoryview) -> Tuple[memoryview, int]
    return buffer, 0


def _decode_empty(buffer):
    # type: (memoryview) -> Tuple[memoryview, List[None]]
    return buffer, []


def _decode_boolean(buffer):
    # type: (memoryview) -> Tuple[memoryview, bool]
    return buffer[1:], buffer[:1] == b'\x01'


def _decode_ubyte(buffer):
    # type: (memoryview) -> Tuple[memoryview, int]
    return buffer[1:], buffer[0]


def _decode_ushort(buffer):
    # type: (memoryview) -> Tuple[memoryview, int]
    return buffer[2:], c_unsigned_short.unpack(buffer[:2])[0]


def _decode_uint_small(buffer):
    # type: (memoryview) -> Tuple[memoryview, int]
    return buffer[1:], buffer[0]


def _decode_uint_large(buffer):
    # type: (memoryview) -> Tuple[memoryview, int]
    return buffer[4:], c_unsigned_int.unpack(buffer[:4])[0]


def _decode_ulong_small(buffer):
    # type: (memoryview) -> Tuple[memoryview, int]
    return buffer[1:], buffer[0]


def _decode_ulong_large(buffer):
    # type: (memoryview) -> Tuple[memoryview, int]
    return buffer[8:], c_unsigned_long_long.unpack(buffer[:8])[0]


def _decode_byte(buffer):
    # type: (memoryview) -> Tuple[memoryview, int]
    return buffer[1:], c_signed_char.unpack(buffer[:1])[0]


def _decode_short(buffer):
    # type: (memoryview) -> Tuple[memoryview, int]
    return buffer[2:], c_signed_short.unpack(buffer[:2])[0]


def _decode_int_small(buffer):
    # type: (memoryview) -> Tuple[memoryview, int]
    return buffer[1:], c_signed_char.unpack(buffer[:1])[0]


def _decode_int_large(buffer):
    # type: (memoryview) -> Tuple[memoryview, int]
    return buffer[4:], c_signed_int.unpack(buffer[:4])[0]


def _decode_long_small(buffer):
    # type: (memoryview) -> Tuple[memoryview, int]
    return buffer[1:], c_signed_char.unpack(buffer[:1])[0]


def _decode_long_large(buffer):
    # type: (memoryview) -> Tuple[memoryview, int]
    return buffer[8:], c_signed_long_long.unpack(buffer[:8])[0]


def _decode_float(buffer):
    # type: (memoryview) -> Tuple[memoryview, float]
    return buffer[4:], c_float.unpack(buffer[:4])[0]


def _decode_double(buffer):
    # type: (memoryview) -> Tuple[memoryview, float]
    return buffer[8:], c_double.unpack(buffer[:8])[0]


def _decode_timestamp(buffer):
    # type: (memoryview) -> Tuple[memoryview, int]
    return buffer[8:], c_signed_long_long.unpack(buffer[:8])[0]


def _decode_uuid(buffer):
    # type: (memoryview) -> Tuple[memoryview, uuid.UUID]
    return buffer[16:], uuid.UUID(bytes=buffer[:16].tobytes())


def _decode_binary_small(buffer):
    # type: (memoryview) -> Tuple[memoryview, bytes]
    length_index = buffer[0] + 1
    return buffer[length_index:], buffer[1:length_index].tobytes()


def _decode_binary_large(buffer):
    # type: (memoryview) -> Tuple[memoryview, bytes]
    length_index = c_unsigned_long.unpack(buffer[:4])[0] + 4
    return buffer[length_index:], buffer[4:length_index].tobytes()


def _decode_list_small(buffer):
    # type: (memoryview) -> Tuple[memoryview, List[Any]]
    count = buffer[1]
    buffer = buffer[2:]
    values = [None] * count
    for i in range(count):
        buffer, values[i] = _DECODE_BY_CONSTRUCTOR[buffer[0]](buffer[1:])
    return buffer, values


def _decode_list_large(buffer):
    # type: (memoryview) -> Tuple[memoryview, List[Any]]
    count = c_unsigned_long.unpack(buffer[4:8])[0]
    buffer = buffer[8:]
    values = [None] * count
    for i in range(count):
        buffer, values[i] = _DECODE_BY_CONSTRUCTOR[buffer[0]](buffer[1:])
    return buffer, values


def _decode_map_small(buffer):
    # type: (memoryview) -> Tuple[memoryview, Dict[Any, Any]]
    count = int(buffer[1]/2)
    buffer = buffer[2:]
    values = {}
    for  _ in range(count):
        buffer, key = _DECODE_BY_CONSTRUCTOR[buffer[0]](buffer[1:])
        buffer, value = _DECODE_BY_CONSTRUCTOR[buffer[0]](buffer[1:])
        values[key] = value
    return buffer, values


def _decode_map_large(buffer):
    # type: (memoryview) -> Tuple[memoryview, Dict[Any, Any]]
    count = int(c_unsigned_long.unpack(buffer[4:8])[0]/2)
    buffer = buffer[8:]
    values = {}
    for  _ in range(count):
        buffer, key = _DECODE_BY_CONSTRUCTOR[buffer[0]](buffer[1:])
        buffer, value = _DECODE_BY_CONSTRUCTOR[buffer[0]](buffer[1:])
        values[key] = value
    return buffer, values


def _decode_array_small(buffer):
    # type: (memoryview) -> Tuple[memoryview, List[Any]]
    count = buffer[1]  # Ignore first byte (size) and just rely on count
    if count:
        subconstructor = buffer[2]
        buffer = buffer[3:]
        values = [None] * count
        for i in range(count):
            buffer, values[i] = _DECODE_BY_CONSTRUCTOR[subconstructor](buffer)
        return buffer, values
    return buffer[2:], []


def _decode_array_large(buffer):
    # type: (memoryview) -> Tuple[memoryview, List[Any]]
    count = c_unsigned_long.unpack(buffer[4:8])[0]
    if count:
        subconstructor = buffer[8]
        buffer = buffer[9:]
        values = [None] * count
        for i in range(count):
            buffer, values[i] = _DECODE_BY_CONSTRUCTOR[subconstructor](buffer)
        return buffer, values
    return buffer[8:], []


def _decode_described(buffer):
    # type: (memoryview) -> Tuple[memoryview, Any]
    # TODO: to move the cursor of the buffer to the described value based on size of the
    #  descriptor without decoding descriptor value
    composite_type = buffer[0]
    buffer, descriptor = _DECODE_BY_CONSTRUCTOR[composite_type](buffer[1:])
    buffer, value = _DECODE_BY_CONSTRUCTOR[buffer[0]](buffer[1:])
    try:
        composite_type = _COMPOSITES[descriptor]
        return buffer, {composite_type: value}
    except KeyError:
        return buffer, value


def decode_payload(buffer):
    # type: (memoryview) -> Message
    message = {}
    while buffer:
        # Ignore the first two bytes, they will always be the constructors for
        # described type then ulong.
        descriptor = buffer[2]
        buffer, value = _DECODE_BY_CONSTRUCTOR[buffer[3]](buffer[4:])
        if descriptor == 112:
            message["header"] = Header(*value)
        elif descriptor == 113:
            message["delivery_annotations"] = value
        elif descriptor == 114:
            message["message_annotations"] = value
        elif descriptor == 115:
            message["properties"] = Properties(*value)
        elif descriptor == 116:
            message["application_properties"] = value
        elif descriptor == 117:
            try:
                message["data"].append(value)
            except KeyError:
                message["data"] = [value]
        elif descriptor == 118:
            try:
                message["sequence"].append(value)
            except KeyError:
                message["sequence"] = [value]
        elif descriptor == 119:
            message["value"] = value
        elif descriptor == 120:
            message["footer"] = value
    # TODO: we can possibly swap out the Message construct with a TypedDict
    #  for both input and output so we get the best of both.
    return Message(**message)


def decode_frame(data):
    # type: (memoryview) -> Tuple[int, List[Any]]
    # Ignore the first two bytes, they will always be the constructors for
    # described type then ulong.
    frame_type = data[2]
    compound_list_type = data[3]
    if compound_list_type == 0xd0:
        # list32 0xd0: data[4:8] is size, data[8:12] is count
        count = c_signed_int.unpack(data[8:12])[0]
        buffer = data[12:]
    else:
        # list8 0xc0: data[4] is size, data[5] is count
        count = data[5]
        buffer = data[6:]
    fields = [None] * count
    for i in range(count):
        buffer, fields[i] = _DECODE_BY_CONSTRUCTOR[buffer[0]](buffer[1:])
    if frame_type == 20:
        fields.append(buffer)
    return frame_type, fields


def decode_empty_frame(header):
    # type: (memory) -> bytes
    if header[0:4] == _HEADER_PREFIX:
        return 0, header.tobytes()
    if header[5] == 0:
        return 1, b"EMPTY"
    raise ValueError("Received unrecognized empty frame")


_DECODE_BY_CONSTRUCTOR = [None] * 256  # type: List[Callable[memoryview]]
_DECODE_BY_CONSTRUCTOR[0] = _decode_described
_DECODE_BY_CONSTRUCTOR[64] = _decode_null
_DECODE_BY_CONSTRUCTOR[65] = _decode_true
_DECODE_BY_CONSTRUCTOR[66] = _decode_false
_DECODE_BY_CONSTRUCTOR[67] = _decode_zero
_DECODE_BY_CONSTRUCTOR[68] = _decode_zero
_DECODE_BY_CONSTRUCTOR[69] = _decode_empty
_DECODE_BY_CONSTRUCTOR[80] = _decode_ubyte
_DECODE_BY_CONSTRUCTOR[81] = _decode_byte
_DECODE_BY_CONSTRUCTOR[82] = _decode_uint_small
_DECODE_BY_CONSTRUCTOR[83] = _decode_ulong_small
_DECODE_BY_CONSTRUCTOR[84] = _decode_int_small
_DECODE_BY_CONSTRUCTOR[85] = _decode_long_small
_DECODE_BY_CONSTRUCTOR[86] = _decode_boolean
_DECODE_BY_CONSTRUCTOR[96] = _decode_ushort
_DECODE_BY_CONSTRUCTOR[97] = _decode_short
_DECODE_BY_CONSTRUCTOR[112] = _decode_uint_large
_DECODE_BY_CONSTRUCTOR[113] = _decode_int_large
_DECODE_BY_CONSTRUCTOR[114] = _decode_float
_DECODE_BY_CONSTRUCTOR[128] = _decode_ulong_large
_DECODE_BY_CONSTRUCTOR[129] = _decode_long_large
_DECODE_BY_CONSTRUCTOR[130] = _decode_double
_DECODE_BY_CONSTRUCTOR[131] = _decode_timestamp
_DECODE_BY_CONSTRUCTOR[152] = _decode_uuid
_DECODE_BY_CONSTRUCTOR[160] = _decode_binary_small
_DECODE_BY_CONSTRUCTOR[161] = _decode_binary_small
_DECODE_BY_CONSTRUCTOR[163] = _decode_binary_small
_DECODE_BY_CONSTRUCTOR[176] = _decode_binary_large
_DECODE_BY_CONSTRUCTOR[177] = _decode_binary_large
_DECODE_BY_CONSTRUCTOR[179] = _decode_binary_large
_DECODE_BY_CONSTRUCTOR[192] = _decode_list_small
_DECODE_BY_CONSTRUCTOR[193] = _decode_map_small
_DECODE_BY_CONSTRUCTOR[208] = _decode_list_large
_DECODE_BY_CONSTRUCTOR[209] = _decode_map_large
_DECODE_BY_CONSTRUCTOR[224] = _decode_array_small
_DECODE_BY_CONSTRUCTOR[240] = _decode_array_large
