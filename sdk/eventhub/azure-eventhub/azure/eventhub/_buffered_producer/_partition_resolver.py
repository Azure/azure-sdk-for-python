# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""
jenkins-hash lookup3 algorithm implementation
"""

from threading import Lock
import struct

c_signed_short = struct.Struct(">h")


def rot(x, k):
    return (x << k) | (x >> (32 - k))


def mix(a, b, c):
    a &= 0xFFFFFFFF
    b &= 0xFFFFFFFF
    c &= 0xFFFFFFFF
    a -= c
    a &= 0xFFFFFFFF
    a ^= rot(c, 4)
    a &= 0xFFFFFFFF
    c += b
    c &= 0xFFFFFFFF
    b -= a
    b &= 0xFFFFFFFF
    b ^= rot(a, 6)
    b &= 0xFFFFFFFF
    a += c
    a &= 0xFFFFFFFF
    c -= b
    c &= 0xFFFFFFFF
    c ^= rot(b, 8)
    c &= 0xFFFFFFFF
    b += a
    b &= 0xFFFFFFFF
    a -= c
    a &= 0xFFFFFFFF
    a ^= rot(c, 16)
    a &= 0xFFFFFFFF
    c += b
    c &= 0xFFFFFFFF
    b -= a
    b &= 0xFFFFFFFF
    b ^= rot(a, 19)
    b &= 0xFFFFFFFF
    a += c
    a &= 0xFFFFFFFF
    c -= b
    c &= 0xFFFFFFFF
    c ^= rot(b, 4)
    c &= 0xFFFFFFFF
    b += a
    b &= 0xFFFFFFFF
    return a, b, c


def final(a, b, c):
    a &= 0xFFFFFFFF
    b &= 0xFFFFFFFF
    c &= 0xFFFFFFFF
    c ^= b
    c &= 0xFFFFFFFF
    c -= rot(b, 14)
    c &= 0xFFFFFFFF
    a ^= c
    a &= 0xFFFFFFFF
    a -= rot(c, 11)
    a &= 0xFFFFFFFF
    b ^= a
    b &= 0xFFFFFFFF
    b -= rot(a, 25)
    b &= 0xFFFFFFFF
    c ^= b
    c &= 0xFFFFFFFF
    c -= rot(b, 16)
    c &= 0xFFFFFFFF
    a ^= c
    a &= 0xFFFFFFFF
    a -= rot(c, 4)
    a &= 0xFFFFFFFF
    b ^= a
    b &= 0xFFFFFFFF
    b -= rot(a, 14)
    b &= 0xFFFFFFFF
    c ^= b
    c &= 0xFFFFFFFF
    c -= rot(b, 24)
    c &= 0xFFFFFFFF
    return a, b, c


def compute_hash(data, init_val=0, init_val2=0):
    # pylint: disable=too-many-statements,docstring-missing-param,docstring-missing-rtype,docstring-missing-return
    """
    implementation by:
    https://stackoverflow.com/questions/3279615/python-implementation-of-jenkins-hash
    """
    length = lenpos = len(data)

    a = b = c = 0xDEADBEEF + length + init_val

    c += init_val2
    c &= 0xFFFFFFFF

    p = 0  # string offset
    while lenpos > 12:
        a += ord(data[p + 0]) + (ord(data[p + 1]) << 8) + (ord(data[p + 2]) << 16) + (ord(data[p + 3]) << 24)
        a &= 0xFFFFFFFF
        b += ord(data[p + 4]) + (ord(data[p + 5]) << 8) + (ord(data[p + 6]) << 16) + (ord(data[p + 7]) << 24)
        b &= 0xFFFFFFFF
        c += ord(data[p + 8]) + (ord(data[p + 9]) << 8) + (ord(data[p + 10]) << 16) + (ord(data[p + 11]) << 24)
        c &= 0xFFFFFFFF
        a, b, c = mix(a, b, c)
        p += 12
        lenpos -= 12

    if lenpos == 12:
        c += ord(data[p + 8]) + (ord(data[p + 9]) << 8) + (ord(data[p + 10]) << 16) + (ord(data[p + 11]) << 24)
        b += ord(data[p + 4]) + (ord(data[p + 5]) << 8) + (ord(data[p + 6]) << 16) + (ord(data[p + 7]) << 24)
        a += ord(data[p + 0]) + (ord(data[p + 1]) << 8) + (ord(data[p + 2]) << 16) + (ord(data[p + 3]) << 24)
    if lenpos == 11:
        c += ord(data[p + 8]) + (ord(data[p + 9]) << 8) + (ord(data[p + 10]) << 16)
        b += ord(data[p + 4]) + (ord(data[p + 5]) << 8) + (ord(data[p + 6]) << 16) + (ord(data[p + 7]) << 24)
        a += ord(data[p + 0]) + (ord(data[p + 1]) << 8) + (ord(data[p + 2]) << 16) + (ord(data[p + 3]) << 24)
    if lenpos == 10:
        c += ord(data[p + 8]) + (ord(data[p + 9]) << 8)
        b += ord(data[p + 4]) + (ord(data[p + 5]) << 8) + (ord(data[p + 6]) << 16) + (ord(data[p + 7]) << 24)
        a += ord(data[p + 0]) + (ord(data[p + 1]) << 8) + (ord(data[p + 2]) << 16) + (ord(data[p + 3]) << 24)
    if lenpos == 9:
        c += ord(data[p + 8])
        b += ord(data[p + 4]) + (ord(data[p + 5]) << 8) + (ord(data[p + 6]) << 16) + (ord(data[p + 7]) << 24)
        a += ord(data[p + 0]) + (ord(data[p + 1]) << 8) + (ord(data[p + 2]) << 16) + (ord(data[p + 3]) << 24)
    if lenpos == 8:
        b += ord(data[p + 4]) + (ord(data[p + 5]) << 8) + (ord(data[p + 6]) << 16) + (ord(data[p + 7]) << 24)
        a += ord(data[p + 0]) + (ord(data[p + 1]) << 8) + (ord(data[p + 2]) << 16) + (ord(data[p + 3]) << 24)
    if lenpos == 7:
        b += ord(data[p + 4]) + (ord(data[p + 5]) << 8) + (ord(data[p + 6]) << 16)
        a += ord(data[p + 0]) + (ord(data[p + 1]) << 8) + (ord(data[p + 2]) << 16) + (ord(data[p + 3]) << 24)
    if lenpos == 6:
        b += (ord(data[p + 5]) << 8) + ord(data[p + 4])
        a += ord(data[p + 0]) + (ord(data[p + 1]) << 8) + (ord(data[p + 2]) << 16) + (ord(data[p + 3]) << 24)
    if lenpos == 5:
        b += ord(data[p + 4])
        a += ord(data[p + 0]) + (ord(data[p + 1]) << 8) + (ord(data[p + 2]) << 16) + (ord(data[p + 3]) << 24)
    if lenpos == 4:
        a += ord(data[p + 0]) + (ord(data[p + 1]) << 8) + (ord(data[p + 2]) << 16) + (ord(data[p + 3]) << 24)
    if lenpos == 3:
        a += ord(data[p + 0]) + (ord(data[p + 1]) << 8) + (ord(data[p + 2]) << 16)
    if lenpos == 2:
        a += ord(data[p + 0]) + (ord(data[p + 1]) << 8)
    if lenpos == 1:
        a += ord(data[p + 0])

    a &= 0xFFFFFFFF
    b &= 0xFFFFFFFF
    c &= 0xFFFFFFFF
    if lenpos == 0:
        return c, b

    a, b, c = final(a, b, c)

    return c, b


def generate_hash_code(partition_key):
    if not partition_key:
        return 0

    hash_tuple = compute_hash(partition_key, 0, 0)
    hash_value = (hash_tuple[0] ^ hash_tuple[1]) & 0xFFFF
    return c_signed_short.unpack(struct.pack(">H", hash_value))[0]


class PartitionResolver:
    def __init__(self, partitions):
        self._idx = -1
        self._partitions = partitions
        self._partitions_cnt = len(self._partitions)
        self._lock = Lock()

    def get_next_partition_id(self):
        """
        round-robin partition assignment

        :return: The next partition id.
        :rtype: str
        """
        with self._lock:
            self._idx += 1
            self._idx %= self._partitions_cnt
            return self._partitions[self._idx]

    def get_partition_id_by_partition_key(self, partition_key):
        hash_code = generate_hash_code(partition_key)
        return self._partitions[abs(hash_code % self._partitions_cnt)]
