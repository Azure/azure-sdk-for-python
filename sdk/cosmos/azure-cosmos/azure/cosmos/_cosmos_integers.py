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


class UInt64:
    def __init__(self, value):
        self.value = value & 0xFFFFFFFFFFFFFFFF

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, new_value):
        self._value = new_value & 0xFFFFFFFFFFFFFFFF

    def __add__(self, other):
        result = self.value + (other.value if isinstance(other, UInt64) else other)
        return UInt64(result & 0xFFFFFFFFFFFFFFFF)

    def __sub__(self, other):
        result = self.value - (other.value if isinstance(other, UInt64) else other)
        return UInt64(result & 0xFFFFFFFFFFFFFFFF)

    def __mul__(self, other):
        result = self.value * (other.value if isinstance(other, UInt64) else other)
        return UInt64(result & 0xFFFFFFFFFFFFFFFF)

    def __xor__(self, other):
        result = self.value ^ (other.value if isinstance(other, UInt64) else other)
        return UInt64(result & 0xFFFFFFFFFFFFFFFF)

    def __lshift__(self, other):
        result = self.value << (other.value if isinstance(other, UInt64) else other)
        return UInt64(result & 0xFFFFFFFFFFFFFFFF)

    def __rshift__(self, other):
        result = self.value >> (other.value if isinstance(other, UInt64) else other)
        return UInt64(result & 0xFFFFFFFFFFFFFFFF)

    def __and__(self, other):
        result = self.value & (other.value if isinstance(other, UInt64) else other)
        return UInt64(result & 0xFFFFFFFFFFFFFFFF)

    def __or__(self, other):
        if isinstance(other, UInt64):
            return UInt64(self.value | other.value)
        elif isinstance(other, int):
            return UInt64(self.value | other)
        else:
            raise TypeError("Unsupported type for OR operation")

    def __invert__(self):
        return UInt64(~self.value & 0xFFFFFFFFFFFFFFFF)

    @staticmethod
    def encode_double_as_uint64(value):
        value_in_uint64 = struct.unpack('<Q', struct.pack('<d', value))[0]
        mask = 0x8000000000000000
        return (value_in_uint64 ^ mask) if value_in_uint64 < mask else (~value_in_uint64) + 1

    @staticmethod
    def decode_double_from_uint64(value):
        mask = 0x8000000000000000
        value = ~(value - 1) if value < mask else value ^ mask
        return struct.unpack('<d', struct.pack('<Q', value))[0]

    def __int__(self):
        return self.value


class UInt128:
    def __init__(self, low, high):
        if isinstance(low, UInt64):
            self.low = low
        else:
            self.low = UInt64(low)

        if isinstance(high, UInt64):
            self.high = high
        else:
            self.high = UInt64(high)

    def __add__(self, other):
        low = self.low + other.low
        high = self.high + other.high + UInt64(int(low.value > 0xFFFFFFFFFFFFFFFF))
        return UInt128(low & 0xFFFFFFFFFFFFFFFF, high & 0xFFFFFFFFFFFFFFFF)

    def __sub__(self, other):
        borrow = UInt64(0)
        if self.low < other.low:
            borrow = UInt64(1)

        low = (self.low - other.low) & 0xFFFFFFFFFFFFFFFF
        high = (self.high - other.high - borrow) & 0xFFFFFFFFFFFFFFFF
        return UInt128(low, high)

    def __mul__(self, other):
        # Multiplication logic here for 128 bits
        pass

    def __xor__(self, other):
        low = self.low ^ other.low
        high = self.high ^ other.high
        return UInt128(low, high)

    def __and__(self, other):
        low = self.low & other.low
        high = self.high & other.high
        return UInt128(low, high)

    def __or__(self, other):
        low = self.low | other.low
        high = self.high | other.high
        return UInt128(low, high)

    def __lshift__(self, shift):
        # Left shift logic for 128 bits
        pass

    def __rshift__(self, shift):
        # Right shift logic for 128 bits
        pass

    def get_low(self):
        return self.low

    def get_high(self):
        return self.high

    def as_tuple(self):
        return self.low.value, self.high.value

    def as_hex(self):
        return hex(self.high.value)[2:].zfill(16) + hex(self.low.value)[2:].zfill(16)

    def as_int(self):
        return (self.high.value << 64) | self.low.value

    def __str__(self):
        return str(self.as_int())

    def to_byte_array(self):
        high_bytes = self.high.value.to_bytes(8, byteorder='little')
        low_bytes = self.low.value.to_bytes(8, byteorder='little')
        return low_bytes + high_bytes

    @staticmethod
    def create(low, high):
        return UInt128(low, high)
