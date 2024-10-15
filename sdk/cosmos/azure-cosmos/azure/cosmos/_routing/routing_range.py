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

"""Internal class for partition key range implementation in the Azure Cosmos
database service.
"""
import base64
import binascii
import json


class PartitionKeyRange(object):
    """Partition Key Range Constants"""

    MinInclusive = "minInclusive"
    MaxExclusive = "maxExclusive"
    Id = "id"
    Parents = "parents"


class Range(object):
    """description of class"""

    MinPath = "min"
    MaxPath = "max"
    IsMinInclusivePath = "isMinInclusive"
    IsMaxInclusivePath = "isMaxInclusive"

    def __init__(self, range_min, range_max, isMinInclusive, isMaxInclusive):
        if range_min is None:
            raise ValueError("min is missing")
        if range_max is None:
            raise ValueError("max is missing")

        self.min = range_min
        self.max = range_max
        self.isMinInclusive = isMinInclusive
        self.isMaxInclusive = isMaxInclusive

    def contains(self, value):
        minToValueRelation = self.min > value
        maxToValueRelation = self.max > value
        return (
            (self.isMinInclusive and minToValueRelation <= 0) or (not self.isMinInclusive and minToValueRelation < 0)
        ) and (
            (self.isMaxInclusive and maxToValueRelation >= 0) or (not self.isMaxInclusive and maxToValueRelation > 0)
        )

    @classmethod
    def PartitionKeyRangeToRange(cls, partition_key_range):
        self = cls(
            partition_key_range[PartitionKeyRange.MinInclusive],
            partition_key_range[PartitionKeyRange.MaxExclusive],
            True,
            False,
        )
        return self

    @classmethod
    def ParseFromDict(cls, range_as_dict):
        self = cls(
            range_as_dict[Range.MinPath],
            range_as_dict[Range.MaxPath],
            range_as_dict[Range.IsMinInclusivePath],
            range_as_dict[Range.IsMaxInclusivePath],
        )
        return self

    def to_dict(self):
        return {
            self.MinPath: self.min,
            self.MaxPath: self.max,
            self.IsMinInclusivePath: self.isMinInclusive,
            self.IsMaxInclusivePath: self.isMaxInclusive
        }

    def to_normalized_range(self):
        if self.isMinInclusive and not self.isMaxInclusive:
            return self

        normalized_min = self.min
        normalized_max = self.max

        if not self.isMinInclusive:
            normalized_min = self.add_to_effective_partition_key(self.min, -1)

        if self.isMaxInclusive:
            normalized_max = self.add_to_effective_partition_key(self.max, 1)

        return Range(normalized_min, normalized_max, True, False)

    def add_to_effective_partition_key(self, effective_partition_key: str, value: int):
        if value not in (-1, 1):
            raise ValueError("Invalid value - only 1 or -1 is allowed")

        byte_array = self.hex_binary_to_byte_array(effective_partition_key)
        if value == 1:
            for i in range(len(byte_array) -1, -1, -1):
                if byte_array[i] < 255:
                    byte_array[i] += 1
                    break
                byte_array[i] = 0
        else:
            for i in range(len(byte_array) - 1, -1, -1):
                if byte_array[i] != 0:
                    byte_array[i] -= 1
                    break
                byte_array[i] = 255

        return binascii.hexlify(byte_array).decode()

    def hex_binary_to_byte_array(self, hex_binary_string: str):
        if hex_binary_string is None:
            raise ValueError("hex_binary_string is missing")
        if len(hex_binary_string) % 2 != 0:
            raise ValueError("hex_binary_string must not have an odd number of characters")

        return bytearray.fromhex(hex_binary_string)

    @classmethod
    def from_base64_encoded_json_string(cls, data: str):
        try:
            feed_range_json_string = base64.b64decode(data, validate=True).decode('utf-8')
            feed_range_json = json.loads(feed_range_json_string)
            return cls.ParseFromDict(feed_range_json)
        except Exception as exc:
            raise ValueError(f"Invalid feed_range json string {data}") from exc

    def to_base64_encoded_string(self):
        data_json = json.dumps(self.to_dict())
        json_bytes = data_json.encode('utf-8')
        # Encode the bytes to a Base64 string
        base64_bytes = base64.b64encode(json_bytes)
        # Convert the Base64 bytes to a string
        return base64_bytes.decode('utf-8')

    def isSingleValue(self):
        return self.isMinInclusive and self.isMaxInclusive and self.min == self.max

    def isEmpty(self):
        return (not (self.isMinInclusive and self.isMaxInclusive)) and self.min == self.max

    def __hash__(self):
        return hash((self.min, self.max, self.isMinInclusive, self.isMaxInclusive))

    def __str__(self):

        return (
            ("[" if self.isMinInclusive else "(")
            + str(self.min)
            + ","
            + str(self.max)
            + ("]" if self.isMaxInclusive else ")")
        )

    def __eq__(self, other):
        return (
            (self.min == other.min)
            and (self.max == other.max)
            and (self.isMinInclusive == other.isMinInclusive)
            and (self.isMaxInclusive == other.isMaxInclusive)
        )

    @staticmethod
    def _compare_helper(a, b):
        # python 3 compatible
        return (a > b) - (a < b)

    @staticmethod
    def overlaps(range1, range2):
        if range1 is None or range2 is None:
            return False
        if range1.isEmpty() or range2.isEmpty():
            return False

        cmp1 = Range._compare_helper(range1.min, range2.max)
        cmp2 = Range._compare_helper(range2.min, range1.max)

        if cmp1 <= 0 and cmp2 <= 0:
            if (cmp1 == 0 and not (range1.isMinInclusive and range2.isMaxInclusive)) or (
                cmp2 == 0 and not (range2.isMinInclusive and range1.isMaxInclusive)
            ):
                return False
            return True
        return False

    def can_merge(self, other: 'Range') -> bool:
        if self.isSingleValue() and other.isSingleValue():
            return self.min == other.min
        # if share the same boundary, they can merge
        overlap_boundary1 = self.max == other.min and self.isMaxInclusive or other.isMinInclusive
        overlap_boundary2 = other.max == self.min and other.isMaxInclusive or self.isMinInclusive
        if overlap_boundary1 or overlap_boundary2:
            return True
        return self.overlaps(self, other)

    def merge(self, other: 'Range') -> 'Range':
        if not self.can_merge(other):
            raise ValueError("Ranges do not overlap")
        min_val = self.min if self.min < other.min else other.min
        max_val = self.max if self.max > other.max else other.max
        is_min_inclusive = self.isMinInclusive if self.min < other.min else other.isMinInclusive
        is_max_inclusive = self.isMaxInclusive if self.max > other.max else other.isMaxInclusive
        return Range(min_val, max_val, is_min_inclusive, is_max_inclusive)

    def is_subset(self, parent_range: 'Range') -> bool:
        normalized_parent_range = parent_range.to_normalized_range()
        normalized_child_range = self.to_normalized_range()
        return (normalized_parent_range.min <= normalized_child_range.min and
                normalized_parent_range.max >= normalized_child_range.max)
