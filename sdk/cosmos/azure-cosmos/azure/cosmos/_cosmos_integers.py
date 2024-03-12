# The MIT License (MIT)
# Copyright (c) 2023 Microsoft Corporation

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
import struct
from typing import NoReturn, Tuple, Union


class _UInt64:
    def __init__(self, value: int) -> None:
        self._value: int = value & 0xFFFFFFFFFFFFFFFF

    @property
    def value(self) -> int:
        return self._value

    @value.setter
    def value(self, new_value: int) -> None:
        self._value = new_value & 0xFFFFFFFFFFFFFFFF

    def __add__(self, other: Union[int, '_UInt64']) -> '_UInt64':
        result = self.value + (other.value if isinstance(other, _UInt64) else other)
        return _UInt64(result & 0xFFFFFFFFFFFFFFFF)

    def __sub__(self, other: Union[int, '_UInt64']) -> '_UInt64':
        result = self.value - (other.value if isinstance(other, _UInt64) else other)
        return _UInt64(result & 0xFFFFFFFFFFFFFFFF)

    def __mul__(self, other: Union[int, '_UInt64']) -> '_UInt64':
        result = self.value * (other.value if isinstance(other, _UInt64) else other)
        return _UInt64(result & 0xFFFFFFFFFFFFFFFF)

    def __xor__(self, other: Union[int, '_UInt64']) -> '_UInt64':
        result = self.value ^ (other.value if isinstance(other, _UInt64) else other)
        return _UInt64(result & 0xFFFFFFFFFFFFFFFF)

    def __lshift__(self, other: Union[int, '_UInt64']) -> '_UInt64':
        result = self.value << (other.value if isinstance(other, _UInt64) else other)
        return _UInt64(result & 0xFFFFFFFFFFFFFFFF)

    def __rshift__(self, other: Union[int, '_UInt64']) -> '_UInt64':
        result = self.value >> (other.value if isinstance(other, _UInt64) else other)
        return _UInt64(result & 0xFFFFFFFFFFFFFFFF)

    def __and__(self, other: Union[int, '_UInt64']) -> '_UInt64':
        result = self.value & (other.value if isinstance(other, _UInt64) else other)
        return _UInt64(result & 0xFFFFFFFFFFFFFFFF)

    def __or__(self, other: Union[int, '_UInt64']) -> '_UInt64':
        if isinstance(other, _UInt64):
            return _UInt64(self.value | other.value)
        if isinstance(other, int):
            return _UInt64(self.value | other)
        raise TypeError("Unsupported type for OR operation")

    def __invert__(self) -> '_UInt64':
        return _UInt64(~self.value & 0xFFFFFFFFFFFFFFFF)

    @staticmethod
    def encode_double_as_uint64(value: float) -> int:
        value_in_uint64 = struct.unpack('<Q', struct.pack('<d', value))[0]
        mask = 0x8000000000000000
        return (value_in_uint64 ^ mask) if value_in_uint64 < mask else (~value_in_uint64) + 1

    @staticmethod
    def decode_double_from_uint64(value: int) -> int:
        mask = 0x8000000000000000
        value = ~(value - 1) if value < mask else value ^ mask
        return struct.unpack('<d', struct.pack('<Q', value))[0]

    def __int__(self) -> int:
        return self.value


class _UInt128:
    def __init__(self, low: Union[int, _UInt64], high: Union[int, _UInt64]) -> None:
        if isinstance(low, _UInt64):
            self.low = low
        else:
            self.low = _UInt64(low)
        if isinstance(high, _UInt64):
            self.high = high
        else:
            self.high = _UInt64(high)

    def __add__(self, other: '_UInt128') -> '_UInt128':
        low = self.low + other.low
        high = self.high + other.high + _UInt64(int(low.value > 0xFFFFFFFFFFFFFFFF))
        return _UInt128(low & 0xFFFFFFFFFFFFFFFF, high & 0xFFFFFFFFFFFFFFFF)

    def __sub__(self, other: '_UInt128') -> '_UInt128':
        borrow = _UInt64(0)
        if self.low.value < other.low.value:
            borrow = _UInt64(1)

        low = (self.low - other.low) & 0xFFFFFFFFFFFFFFFF
        high = (self.high - other.high - borrow) & 0xFFFFFFFFFFFFFFFF
        return _UInt128(low, high)

    def __mul__(self, other: '_UInt128') -> NoReturn:
        # Multiplication logic here for 128 bits
        raise NotImplementedError()

    def __xor__(self, other: '_UInt128') -> '_UInt128':
        low = self.low ^ other.low
        high = self.high ^ other.high
        return _UInt128(low, high)

    def __and__(self, other: '_UInt128') -> '_UInt128':
        low = self.low & other.low
        high = self.high & other.high
        return _UInt128(low, high)

    def __or__(self, other: '_UInt128') -> '_UInt128':
        low = self.low | other.low
        high = self.high | other.high
        return _UInt128(low, high)

    def __lshift__(self, shift: '_UInt128') -> NoReturn:
        # Left shift logic for 128 bits
        raise NotImplementedError()

    def __rshift__(self, shift: '_UInt128') -> NoReturn:
        # Right shift logic for 128 bits
        raise NotImplementedError()

    def get_low(self) -> _UInt64:
        return self.low

    def get_high(self) -> _UInt64:
        return self.high

    def as_tuple(self) -> Tuple[int, int]:
        return self.low.value, self.high.value

    def as_hex(self) -> str:
        return hex(self.high.value)[2:].zfill(16) + hex(self.low.value)[2:].zfill(16)

    def as_int(self) -> int:
        return (self.high.value << 64) | self.low.value

    def __str__(self) -> str:
        return str(self.as_int())

    def to_byte_array(self) -> bytearray:
        high_bytes = self.high.value.to_bytes(8, byteorder='little')
        low_bytes = self.low.value.to_bytes(8, byteorder='little')
        byte_array = bytearray(low_bytes + high_bytes)
        return byte_array
