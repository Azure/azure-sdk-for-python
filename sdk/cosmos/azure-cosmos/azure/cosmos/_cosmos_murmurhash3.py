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

# Implementation of the MurmurHash3 128-bit hash function.

# MurmurHash is a non-cryptographic hash function suitable for general hash-based lookup. The name comes from two basic
# operations, multiply (MU) and rotate (R), used in its inner loop. Unlike cryptographic hash functions, it is not
# specifically designed to be difficult to reverse by an adversary, making it unsuitable for cryptographic purposes.

 # This contains a Python port of the 128-bit hash function from Austin Appleby's original C++ code in SMHasher.

 # This is public domain code with no copyrights. From home page of
 # <a href="https://github.com/aappleby/smhasher">SMHasher</a>:
 #  "All MurmurHash versions are public domain software, and the author disclaims all copyright to their code."
from ._cosmos_integers import UInt128, UInt64


def rotate_left_64(val, shift):
    return (val << shift) | (val >> (64 - shift))


def mix(value):
    value ^= value >> 33
    value *= 0xff51afd7ed558ccd
    value = value & 0xFFFFFFFFFFFFFFFF
    value ^= value >> 33
    value *= 0xc4ceb9fe1a85ec53
    value = value & 0xFFFFFFFFFFFFFFFF
    value ^= value >> 33
    return value


def murmurhash3_128(span: bytearray, seed: UInt128) -> UInt128:
    """
    Python implementation of 128 bit murmurhash3 from Dot Net SDK. To match with other SDKs, It is recommended to
    do the following with number values, especially floats as other SDKs use Doubles
    -> bytearray(struct.pack("d", #)) where # represents any number. The d will treat it as a double.

    :param bytearray span:
        bytearray of value to hash
    :param UInt128 seed:
        seed value for murmurhash3, takes in a UInt128 value from Cosmos Integers
    :return:
        The hash value as a UInt128
    :rtype:
        UInt128"""
    c1 = UInt64(0x87c37b91114253d5)
    c2 = UInt64(0x4cf5ad432745937f)
    h1 = UInt64(seed.get_low())
    h2 = UInt64(seed.get_high())

    position = 0
    while position < len(span) - 15:
        k1 = UInt64(int.from_bytes(span[position: position + 8], 'little'))
        k2 = UInt64(int.from_bytes(span[position + 8: position + 16], 'little'))

        k1 *= c1
        k1.value = rotate_left_64(k1.value, 31)
        k1 *= c2
        h1 ^= k1
        h1.value = rotate_left_64(h1.value, 27)
        h1 += h2
        h1 = h1 * 5 + UInt64(0x52dce729)

        k2 *= c2
        k2.value = rotate_left_64(k2.value, 33)
        k2 *= c1
        h2 ^= k2
        h2.value = rotate_left_64(h2.value, 31)
        h2 += h1
        h2 = h2 * 5 + UInt64(0x38495ab5)

        position += 16

    k1 = UInt64(0)
    k2 = UInt64(0)
    n = len(span) & 15
    if n >= 15:
        k2 ^= UInt64(span[position + 14] << 48)
    if n >= 14:
        k2 ^= UInt64(span[position + 13] << 40)
    if n >= 13:
        k2 ^= UInt64(span[position + 12] << 32)
    if n >= 12:
        k2 ^= UInt64(span[position + 11] << 24)
    if n >= 11:
        k2 ^= UInt64(span[position + 10] << 16)
    if n >= 10:
        k2 ^= UInt64(span[position + 9] << 8)
    if n >= 9:
        k2 ^= UInt64(span[position + 8] << 0)

    k2 *= c2
    k2.value = rotate_left_64(k2.value, 33)
    k2 *= c1
    h2 ^= k2

    if n >= 8:
        k1 ^= UInt64(span[position + 7] << 56)
    if n >= 7:
        k1 ^= UInt64(span[position + 6] << 48)
    if n >= 6:
        k1 ^= UInt64(span[position + 5] << 40)
    if n >= 5:
        k1 ^= UInt64(span[position + 4] << 32)
    if n >= 4:
        k1 ^= UInt64(span[position + 3] << 24)
    if n >= 3:
        k1 ^= UInt64(span[position + 2] << 16)
    if n >= 2:
        k1 ^= UInt64(span[position + 1] << 8)
    if n >= 1:
        k1 ^= UInt64(span[position + 0] << 0)

    k1 *= c1
    k1.value = rotate_left_64(k1.value, 31)
    k1 *= c2
    h1 ^= k1

    # Finalization
    h1 ^= UInt64(len(span))
    h2 ^= UInt64(len(span))
    h1 += h2
    h2 += h1
    h1 = mix(h1)
    h2 = mix(h2)
    h1 += h2
    h2 += h1

    return UInt128.create(int(h1.value), int(h2.value))
