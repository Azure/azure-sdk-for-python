# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import struct
import uuid
import logging
import decimal
from typing import (
    Callable,
    List,
    Optional,
    Tuple,
    Dict,
    Any,
    Union,
    cast,
    TYPE_CHECKING,
)

from typing_extensions import Literal


from .message import Message, Header, Properties

if TYPE_CHECKING:
    from .message import MessageDict

_LOGGER = logging.getLogger(__name__)
_HEADER_PREFIX = memoryview(b"AMQP")
_COMPOSITES = {
    35: "received",
    36: "accepted",
    37: "rejected",
    38: "released",
    39: "modified",
}

c_unsigned_char = struct.Struct(">B")
c_signed_char = struct.Struct(">b")
c_unsigned_short = struct.Struct(">H")
c_signed_short = struct.Struct(">h")
c_unsigned_int = struct.Struct(">I")
c_signed_int = struct.Struct(">i")
c_unsigned_long = struct.Struct(">L")
c_unsigned_long_long = struct.Struct(">Q")
c_signed_long_long = struct.Struct(">q")
c_float = struct.Struct(">f")
c_double = struct.Struct(">d")

DECIMAL128_EXPONENT_MAX = 6144
DECIMAL128_EXPONENT_MIN = -6143
DECIMAL128_MAX_DIGITS = 34
DECIMAL128_BIAS = 6176



def _decode_null(buffer: memoryview) -> Tuple[memoryview, None]:
    return buffer, None


def _decode_true(buffer: memoryview) -> Tuple[memoryview, Literal[True]]:
    return buffer, True


def _decode_false(buffer: memoryview) -> Tuple[memoryview, Literal[False]]:
    return buffer, False


def _decode_zero(buffer: memoryview) -> Tuple[memoryview, Literal[0]]:
    return buffer, 0


def _decode_empty(buffer: memoryview) -> Tuple[memoryview, List[Any]]:
    return buffer, []


def _decode_boolean(buffer: memoryview) -> Tuple[memoryview, bool]:
    return buffer[1:], buffer[:1] == b"\x01"


def _decode_ubyte(buffer: memoryview) -> Tuple[memoryview, int]:
    return buffer[1:], buffer[0]


def _decode_ushort(buffer: memoryview) -> Tuple[memoryview, int]:
    return buffer[2:], c_unsigned_short.unpack(buffer[:2])[0]


def _decode_uint_small(buffer: memoryview) -> Tuple[memoryview, int]:
    return buffer[1:], buffer[0]


def _decode_uint_large(buffer: memoryview) -> Tuple[memoryview, int]:
    return buffer[4:], c_unsigned_int.unpack(buffer[:4])[0]


def _decode_ulong_small(buffer: memoryview) -> Tuple[memoryview, int]:
    return buffer[1:], buffer[0]


def _decode_ulong_large(buffer: memoryview) -> Tuple[memoryview, int]:
    return buffer[8:], c_unsigned_long_long.unpack(buffer[:8])[0]


def _decode_byte(buffer: memoryview) -> Tuple[memoryview, int]:
    return buffer[1:], c_signed_char.unpack(buffer[:1])[0]


def _decode_short(buffer: memoryview) -> Tuple[memoryview, int]:
    return buffer[2:], c_signed_short.unpack(buffer[:2])[0]


def _decode_int_small(buffer: memoryview) -> Tuple[memoryview, int]:
    return buffer[1:], c_signed_char.unpack(buffer[:1])[0]


def _decode_int_large(buffer: memoryview) -> Tuple[memoryview, int]:
    return buffer[4:], c_signed_int.unpack(buffer[:4])[0]


def _decode_long_small(buffer: memoryview) -> Tuple[memoryview, int]:
    return buffer[1:], c_signed_char.unpack(buffer[:1])[0]


def _decode_long_large(buffer: memoryview) -> Tuple[memoryview, int]:
    return buffer[8:], c_signed_long_long.unpack(buffer[:8])[0]


def _decode_float(buffer: memoryview) -> Tuple[memoryview, float]:
    return buffer[4:], c_float.unpack(buffer[:4])[0]


def _decode_double(buffer: memoryview) -> Tuple[memoryview, float]:
    return buffer[8:], c_double.unpack(buffer[:8])[0]


def _decode_timestamp(buffer: memoryview) -> Tuple[memoryview, int]:
    return buffer[8:], c_signed_long_long.unpack(buffer[:8])[0]


def _decode_uuid(buffer: memoryview) -> Tuple[memoryview, uuid.UUID]:
    return buffer[16:], uuid.UUID(bytes=buffer[:16].tobytes())


def _decode_binary_small(buffer: memoryview) -> Tuple[memoryview, bytes]:
    length_index = buffer[0] + 1
    return buffer[length_index:], buffer[1:length_index].tobytes()


def _decode_binary_large(buffer: memoryview) -> Tuple[memoryview, bytes]:
    length_index = c_unsigned_long.unpack(buffer[:4])[0] + 4
    return buffer[length_index:], buffer[4:length_index].tobytes()

def _decode_decimal128(buffer: memoryview) -> Tuple[memoryview, decimal.Decimal]:
    """
    Decode a Decimal128 value from the buffer.

    The Decimal128 encoding is a 16-byte encoding that represents a 34-digit decimal number.
    The encoding uses the IEEE 754-2008 decimal128 format.
    See: https://docs.oasis-open.org/amqp/core/v1.0/os/amqp-core-types-v1.0-os.html#type-decimal128

    :param buffer: The buffer containing the Decimal128 encoded value.
    :type buffer: memoryview
    :return: A tuple containing the remaining buffer and the decoded decimal.Decimal value.
    :rtype: Tuple[memoryview, decimal.Decimal]
    """

    # per the spec decimal128 has a width of 16 bytes
    dec_value = bytearray(buffer[:16])

    # Determine the sign of the decimal number
    sign = 1 if dec_value[0] & 0x80 else 0
    biased_exponent = 0

    # Check if the exponent is not a special value
    if dec_value[0] & 0x60 != 0x60:
        # Extract the biased exponent from the first two bytes
        biased_exponent = ((dec_value[0] & 0x7F) << 9) | ((dec_value[1] & 0xFE) >> 1)
        dec_value[0] = 0
        dec_value[1] &= 0x01
    elif dec_value[0] & 0x78 != 0:
        # Handle special values (NaN and Infinity)
        if (dec_value[0] & 0x78) == 0x78:
            return buffer[16:], decimal.Decimal('NaN')
        return buffer[16:], decimal.Decimal('-Infinity')
    else:
        # If the exponent is zero, return zero
        return buffer[16:], decimal.Decimal(0)

    # Calculate the actual exponent by subtracting the bias
    exponent = biased_exponent - DECIMAL128_BIAS

    # Extract the significant digits from the remaining 14 bytes
    hi = c_unsigned_int.unpack(dec_value[4:8])[0]
    middle = c_unsigned_int.unpack(dec_value[8:12])[0]
    lo = c_unsigned_int.unpack(dec_value[12:16])[0]
    digits = tuple(int(digit) for digit in f"{hi:08}{middle:08}{lo:08}".lstrip('0'))

    # Create a decimal context with the appropriate precision and exponent range
    decimal_ctx = decimal.Context(
        prec = DECIMAL128_MAX_DIGITS,
        Emin = DECIMAL128_EXPONENT_MIN,
        Emax = DECIMAL128_EXPONENT_MAX,
        capitals =  1,
        clamp = 1,
    )

    # Create the decimal value using the context
    with decimal.localcontext(decimal_ctx) as ctx:
        return buffer[16:], ctx.create_decimal((sign, digits, exponent))

def _decode_list_small(buffer: memoryview) -> Tuple[memoryview, List[Any]]:
    count = buffer[1]
    buffer = buffer[2:]
    values = [None] * count
    for i in range(count):
        buffer, values[i] = _DECODE_BY_CONSTRUCTOR[buffer[0]](buffer[1:])
    return buffer, values


def _decode_list_large(buffer: memoryview) -> Tuple[memoryview, List[Any]]:
    count = c_unsigned_long.unpack(buffer[4:8])[0]
    buffer = buffer[8:]
    values = [None] * count
    for i in range(count):
        buffer, values[i] = _DECODE_BY_CONSTRUCTOR[buffer[0]](buffer[1:])
    return buffer, values


def _decode_map_small(buffer: memoryview) -> Tuple[memoryview, Dict[Any, Any]]:
    count = int(buffer[1] / 2)
    buffer = buffer[2:]
    values = {}
    for _ in range(count):
        buffer, key = _DECODE_BY_CONSTRUCTOR[buffer[0]](buffer[1:])
        buffer, value = _DECODE_BY_CONSTRUCTOR[buffer[0]](buffer[1:])
        values[key] = value
    return buffer, values


def _decode_map_large(buffer: memoryview) -> Tuple[memoryview, Dict[Any, Any]]:
    count = int(c_unsigned_long.unpack(buffer[4:8])[0] / 2)
    buffer = buffer[8:]
    values = {}
    for _ in range(count):
        buffer, key = _DECODE_BY_CONSTRUCTOR[buffer[0]](buffer[1:])
        buffer, value = _DECODE_BY_CONSTRUCTOR[buffer[0]](buffer[1:])
        values[key] = value
    return buffer, values


def _decode_array_small(buffer: memoryview) -> Tuple[memoryview, List[Any]]:
    count = buffer[1]  # Ignore first byte (size) and just rely on count
    if count:
        subconstructor = buffer[2]
        buffer = buffer[3:]
        values = [None] * count
        for i in range(count):
            buffer, values[i] = _DECODE_BY_CONSTRUCTOR[subconstructor](buffer)
        return buffer, values
    return buffer[2:], []


def _decode_array_large(buffer: memoryview) -> Tuple[memoryview, List[Any]]:
    count = c_unsigned_long.unpack(buffer[4:8])[0]
    if count:
        subconstructor = buffer[8]
        buffer = buffer[9:]
        values = [None] * count
        for i in range(count):
            buffer, values[i] = _DECODE_BY_CONSTRUCTOR[subconstructor](buffer)
        return buffer, values
    return buffer[8:], []


def _decode_described(buffer: memoryview) -> Tuple[memoryview, object]:
    # TODO: to move the cursor of the buffer to the described value based on size of the
    #  descriptor without decoding descriptor value
    composite_type = buffer[0]
    buffer, descriptor = _DECODE_BY_CONSTRUCTOR[composite_type](buffer[1:])
    buffer, value = _DECODE_BY_CONSTRUCTOR[buffer[0]](buffer[1:])
    try:
        composite_type = cast(int, _COMPOSITES[descriptor])
        return buffer, {composite_type: value}
    except KeyError:
        return buffer, value


def decode_payload(buffer: memoryview) -> Message:
    message: Dict[str, Union[Properties, Header, Dict, bytes, List]] = {}
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
                cast(List, message["data"]).append(value)
            except KeyError:
                message["data"] = [value]
        elif descriptor == 118:
            try:
                cast(List, message["sequence"]).append(value)
            except KeyError:
                message["sequence"] = [value]
        elif descriptor == 119:
            message["value"] = value
        elif descriptor == 120:
            message["footer"] = value
    # TODO: we can possibly swap out the Message construct with a TypedDict
    #  for both input and output so we get the best of both.
    # casting to TypedDict with named fields to allow for unpacking with **
    message_properties = cast("MessageDict", message)
    return Message(**message_properties)


def decode_frame(data: memoryview) -> Tuple[int, List[Any]]:
    # Ignore the first two bytes, they will always be the constructors for
    # described type then ulong.
    frame_type = data[2]
    compound_list_type = data[3]
    if compound_list_type == 0xD0:
        # list32 0xd0: data[4:8] is size, data[8:12] is count
        count = c_signed_int.unpack(data[8:12])[0]
        buffer = data[12:]
    else:
        # list8 0xc0: data[4] is size, data[5] is count
        count = data[5]
        buffer = data[6:]
    fields: List[Optional[memoryview]] = [None] * count
    for i in range(count):
        buffer, fields[i] = _DECODE_BY_CONSTRUCTOR[buffer[0]](buffer[1:])
    if frame_type == 20:
        fields.append(buffer)
    return frame_type, fields


def decode_empty_frame(header: memoryview) -> Tuple[int, bytes]:
    if header[0:4] == _HEADER_PREFIX:
        return 0, header.tobytes()
    if header[5] == 0:
        return 1, b"EMPTY"
    raise ValueError("Received unrecognized empty frame")


_DECODE_BY_CONSTRUCTOR: List[Callable] = cast(List[Callable], [None] * 256)
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
_DECODE_BY_CONSTRUCTOR[148] = _decode_decimal128
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
