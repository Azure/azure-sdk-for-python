# The MIT License (MIT)
# Copyright (c) 2014 Microsoft Corporation

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
"""Create partition keys in the Azure Cosmos DB SQL API service.
"""
from io import BytesIO
import binascii
import struct
from typing import IO, Sequence, Type, Union, overload, List, cast
from typing_extensions import Literal

from ._cosmos_integers import _UInt64, _UInt128
from ._cosmos_murmurhash3 import murmurhash3_128 as _murmurhash3_128
from ._routing.routing_range import Range as _Range


_MaximumExclusiveEffectivePartitionKey = 0xFF
_MinimumInclusiveEffectivePartitionKey = 0x00
_MaxStringChars = 100
_MaxStringBytesToAppend = 100
_MaxPartitionKeyBinarySize = \
    (1  # type marker
     + 9  # hash value
     + 1  # type marker
     + _MaxStringBytesToAppend
     + 1  # trailing zero
     ) * 3


class _PartitionKeyComponentType:
    Undefined = 0x0
    Null = 0x1
    PFalse = 0x2
    PTrue = 0x3
    MinNumber = 0x4
    Number = 0x5
    MaxNumber = 0x6
    MinString = 0x7
    String = 0x8
    MaxString = 0x9
    Int64 = 0xA
    Int32 = 0xB
    Int16 = 0xC
    Int8 = 0xD
    Uint64 = 0xE
    Uint32 = 0xF
    Uint16 = 0x10
    Uint8 = 0x11
    Binary = 0x12
    Guid = 0x13
    Float = 0x14
    Infinity = 0xFF


class NonePartitionKeyValue:
    """Represents None value for partitionKey when it's missing in a container.
    """


class _Empty:
    """Represents empty value for partitionKey when it's missing in an item belonging
    to a migrated container.
    """


class _Undefined:
    """Represents undefined value for partitionKey when it's missing in an item belonging
    to a multi-partition container.
    """


class _Infinity:
    """Represents infinity value for partitionKey."""


class PartitionKey(dict):
    """Key used to partition a container into logical partitions.

    See https://learn.microsoft.com/azure/cosmos-db/partitioning-overview#choose-partitionkey
    for information on how to choose partition keys.

    :ivar str path: The path of the partition key
    :ivar str kind: What kind of partition key is being defined (default: "Hash")
    :ivar int version: The version of the partition key (default: 2)
    """

    @overload
    def __init__(self, path: List[str], *, kind: Literal["MultiHash"] = "MultiHash", version: int = 2) -> None:
        ...

    @overload
    def __init__(self, path: str, *, kind: Literal["Hash"] = "Hash", version: int = 2) -> None:
        ...

    def __init__(self, *args, **kwargs):
        path = args[0] if args else kwargs['path']
        kind = args[1] if len(args) > 1 else kwargs.get('kind', 'Hash' if isinstance(path, str) else 'MultiHash')
        version = args[2] if len(args) > 2 else kwargs.get('version', 2)
        super().__init__(paths=[path] if isinstance(path, str) else path, kind=kind, version=version)

    def __repr__(self) -> str:
        return "<PartitionKey [{}]>".format(self.path)[:1024]

    @property
    def kind(self) -> Literal["MultiHash", "Hash"]:
        return self["kind"]

    @kind.setter
    def kind(self, value: Literal["MultiHash", "Hash"]) -> None:
        self["kind"] = value

    @property
    def path(self) -> str:
        if self.kind == "MultiHash":
            return ''.join(self["paths"])
        return self["paths"][0]

    @path.setter
    def path(self, value: Union[str, List[str]]) -> None:
        if isinstance(value, str):
            self["paths"] = [value]
        else:
            self["paths"] = value

    @property
    def version(self) -> int:
        return self["version"]

    @version.setter
    def version(self, value: int) -> None:
        self["version"] = value

    def _get_epk_range_for_prefix_partition_key(
        self,
        pk_value: Sequence[Union[None, bool, int, float, str, _Undefined, Type[NonePartitionKeyValue]]]
    ) -> _Range:
        if self.kind != "MultiHash":
            raise ValueError(
                "Effective Partition Key Range for Prefix Partition Keys is only supported for Hierarchical Partition Keys.")  # pylint: disable=line-too-long
        len_pk_value = len(pk_value)
        len_paths = len(self["paths"])
        if len_pk_value >= len_paths:
            raise ValueError(
                f"{len_pk_value} partition key components provided. Expected less than {len_paths} " +
                "components (number of container partition key definition components)."
            )
        # Prefix Partitions always have exclusive max
        min_epk = self._get_effective_partition_key_string(pk_value)
        if min_epk == _MinimumInclusiveEffectivePartitionKey:
            min_epk = ""
            return _Range(min_epk, min_epk, True, False)

        if min_epk == _MaximumExclusiveEffectivePartitionKey:
            return _Range("FF", "FF", True, False)

        max_epk = str(min_epk) + "FF"
        return _Range(min_epk, max_epk, True, False)

    def _get_epk_range_for_partition_key(
            self,
            pk_value: Union[str, int, float, bool, Sequence[Union[str, int, float, bool, None]], Type[NonePartitionKeyValue]] # pylint: disable=line-too-long
    ) -> _Range:
        if self._is_prefix_partition_key(pk_value):
            return self._get_epk_range_for_prefix_partition_key(
                cast(Sequence[Union[None, bool, int, float, str, Type[NonePartitionKeyValue]]], pk_value))

        # else return point range
        effective_partition_key_string =\
            self._get_effective_partition_key_string(
                cast(List[Union[None, bool, int, float, str, _Undefined, Type[NonePartitionKeyValue]]], [pk_value]))
        return _Range(effective_partition_key_string, effective_partition_key_string, True, True)

    def _get_effective_partition_key_for_hash_partitioning(self) -> str:
        # We shouldn't be supporting V1
        return ""

    def _get_effective_partition_key_string(
        self,
        pk_value: Sequence[Union[None, bool, int, float, str, _Undefined, Type[NonePartitionKeyValue]]]
    ) -> Union[int, str]:
        if not pk_value:
            return _MinimumInclusiveEffectivePartitionKey

        if isinstance(self, _Infinity):
            return _MaximumExclusiveEffectivePartitionKey

        kind = self.kind
        if kind == 'Hash':
            version = self.version or 2
            if version == 1:
                return self._get_effective_partition_key_for_hash_partitioning()
            if version == 2:
                return self._get_effective_partition_key_for_hash_partitioning_v2(pk_value)
        elif kind == 'MultiHash':
            return self._get_effective_partition_key_for_multi_hash_partitioning_v2(pk_value)
        return _to_hex_encoded_binary_string(pk_value)

    def _write_for_hashing_v2(
        self,
        value: Union[None, bool, int, float, str, _Undefined, Type[NonePartitionKeyValue]],
        writer: IO[bytes]
    ) -> None:
        if value is True:
            writer.write(bytes([_PartitionKeyComponentType.PTrue]))
        elif value is False:
            writer.write(bytes([_PartitionKeyComponentType.PFalse]))
        elif value is None or value == {} or value == NonePartitionKeyValue:
            writer.write(bytes([_PartitionKeyComponentType.Null]))
        elif isinstance(value, int):
            writer.write(bytes([_PartitionKeyComponentType.Number]))
            writer.write(value.to_bytes(8, 'little'))  # assuming value is a 64-bit integer
        elif isinstance(value, float):
            writer.write(bytes([_PartitionKeyComponentType.Number]))
            writer.write(struct.pack('<d', value))
        elif isinstance(value, str):
            writer.write(bytes([_PartitionKeyComponentType.String]))
            writer.write(value.encode('utf-8'))
            writer.write(bytes([0xFF]))
        elif isinstance(value, _Undefined):
            writer.write(bytes([_PartitionKeyComponentType.Undefined]))

    def _get_effective_partition_key_for_hash_partitioning_v2(
        self,
        pk_value: Sequence[Union[None, bool, int, float, str, _Undefined, Type[NonePartitionKeyValue]]]
    ) -> str:
        with BytesIO() as ms:
            for component in pk_value:
                self._write_for_hashing_v2(component, ms)

            ms_bytes = ms.getvalue()
            hash128 = _murmurhash3_128(bytearray(ms_bytes), _UInt128(0, 0))
            hash_bytes = _UInt128.to_byte_array(hash128)
            hash_bytes.reverse()

            # Reset 2 most significant bits, as max exclusive value is 'FF'.
            # Plus one more just in case.
            hash_bytes[0] &= 0x3F

        return ''.join('{:02X}'.format(x) for x in hash_bytes)

    def _get_effective_partition_key_for_multi_hash_partitioning_v2(
        self,
        pk_value: Sequence[Union[None, bool, int, float, str, _Undefined, Type[NonePartitionKeyValue]]]
    ) -> str:
        sb = []
        for value in pk_value:
            ms = BytesIO()
            binary_writer = ms  # In Python, you can write bytes directly to a BytesIO object

            # Assuming paths[i] is the correct object to call write_for_hashing_v2 on
            self._write_for_hashing_v2(value, binary_writer)

            ms_bytes = ms.getvalue()
            hash128 = _murmurhash3_128(bytearray(ms_bytes), _UInt128(0, 0))
            hash_v_bytes = hash128.to_byte_array()
            hash_v = list(reversed(hash_v_bytes))

            # Reset 2 most significant bits, as max exclusive value is 'FF'.
            # Plus one more just in case.
            hash_v[0] &= 0x3F
            sb.append(_to_hex(bytearray(hash_v), 0, len(hash_v)))

        return ''.join(sb).upper()

    def _is_prefix_partition_key(
            self,
            partition_key: Union[str, int, float, bool, Sequence[Union[str, int, float, bool, None]], Type[NonePartitionKeyValue]]) -> bool:  # pylint: disable=line-too-long
        if self.kind != "MultiHash":
            return False
        ret = ((isinstance(partition_key, Sequence) and
                not isinstance(partition_key, str)) and len(self['paths']) != len(partition_key))
        return ret


def _return_undefined_or_empty_partition_key(is_system_key: bool) -> Union[_Empty, _Undefined]:
    if is_system_key:
        return _Empty()
    return _Undefined()


def _to_hex(bytes_object: bytearray, start: int, length: int) -> str:
    return binascii.hexlify(bytes_object[start:start + length]).decode()


def _to_hex_encoded_binary_string(components: Sequence[object]) -> str:
    buffer_bytes = bytearray(_MaxPartitionKeyBinarySize)
    ms = BytesIO(buffer_bytes)

    for component in components:
        if isinstance(component, (bool, int, float, str, _Infinity, _Undefined)):
            _write_for_binary_encoding(component, ms)
        else:
            raise TypeError(f"Unexpected type for PK component: {type(component)}")

    return _to_hex(buffer_bytes[:ms.tell()], 0, ms.tell())


def _write_for_binary_encoding(
    value: Union[bool, int, float, str, _Infinity, _Undefined],
    binary_writer: IO[bytes]
) -> None:
    if isinstance(value, bool):
        binary_writer.write(bytes([(_PartitionKeyComponentType.PTrue if value else _PartitionKeyComponentType.PFalse)]))

    elif isinstance(value, _Infinity):
        binary_writer.write(bytes([_PartitionKeyComponentType.Infinity]))

    elif isinstance(value, (int, float)):  # Assuming number value is int or float
        binary_writer.write(bytes([_PartitionKeyComponentType.Number]))
        payload = _UInt64.encode_double_as_uint64(value)  # Function to be defined elsewhere

        # Encode first chunk with 8-bits of payload
        binary_writer.write(bytes([(payload >> (64 - 8))]))
        payload <<= 8

        # Encode remaining chunks with 7 bits of payload followed by single "1" bit each.
        byte_to_write = 0
        first_iteration = True
        while payload != 0:
            if not first_iteration:
                binary_writer.write(bytes([byte_to_write]))
            else:
                first_iteration = False

            byte_to_write = (payload >> (64 - 8)) | 0x01
            payload <<= 7

        # Except for last chunk that ends with "0" bit.
        binary_writer.write(bytes([(byte_to_write & 0xFE)]))

    elif isinstance(value, str):
        binary_writer.write(bytes([_PartitionKeyComponentType.String]))
        utf8_value = value.encode('utf-8')
        short_string = len(utf8_value) <= _MaxStringBytesToAppend

        for index in range(short_string and len(utf8_value) or _MaxStringBytesToAppend + 1):
            char_byte = utf8_value[index]
            if char_byte < 0xFF:
                char_byte += 1
            binary_writer.write(bytes([char_byte]))

        if short_string:
            binary_writer.write(bytes([0x00]))

    elif isinstance(value, _Undefined):
        binary_writer.write(bytes([_PartitionKeyComponentType.Undefined]))
