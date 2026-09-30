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


from collections import namedtuple

# ``status`` is included so callers can detect non-online ranges (e.g.
# splitting / offline) without re-fetching the raw service payload. It is
# the only PKR field beyond id/min/max/parents kept in the cache today;
# default ``None`` keeps construction sites that don't pass it backward
# compatible.
_PKRangeBase = namedtuple(
    '_PKRangeBase',
    ['id', 'minInclusive', 'maxExclusive', 'parents', 'status', 'throughputFraction'],
    defaults=(None, None),
)


class PKRange(_PKRangeBase):
    """Compact partition key range with dict-compatible access."""
    __slots__ = ()

    def __getitem__(self, key):
        if isinstance(key, (int, slice)):
            return super().__getitem__(key)
        try:
            return getattr(self, key)
        except AttributeError as exc:
            raise KeyError(key) from exc

    def get(self, key, default=None):
        return getattr(self, key, default)

    def __contains__(self, key):
        """Return True only if ``key`` names a field that has a non-empty value.

        Diverges intentionally from ``dict``-style semantics: an absent or
        empty (``None`` / ``()``) field reports as not-present, so callers may
        use ``key in pkr`` as a single truthy presence check (the same
        expression that earlier worked against raw service dicts where the
        field was simply missing when empty).

        :param str key: The field name to check.
        :returns: True if the field is present and has a non-empty value.
        :rtype: bool
        """
        if key not in self._fields:
            return False
        val = getattr(self, key)
        return val is not None and val != ()

    def items(self):
        return zip(self._fields, self)

    def __eq__(self, other):
        if isinstance(other, dict):
            for f in ('id', 'minInclusive', 'maxExclusive'):
                if self.get(f) != other.get(f):
                    return False
            self_parents = self.parents or ()
            other_parents = other.get('parents') or ()
            return tuple(self_parents) == tuple(other_parents)
        return super().__eq__(other)

    def __hash__(self):
        return super().__hash__()

    @classmethod
    def from_dict(cls, raw):
        """Build a compact ``PKRange`` from a raw service-response dict.

        Centralized factory used by both the full-build path
        (``collection_routing_map._build_routing_map_from_ranges``) and the
        incremental-merge path (``_routing_map_provider_common.process_fetched_ranges``)
        so the field-mapping policy lives in exactly one place.

        :param dict raw: A raw partition-key-range dict from the service response.
        :returns: A compact ``PKRange`` namedtuple.
        :rtype: PKRange
        """
        return cls(
            id=raw[PartitionKeyRange.Id],
            minInclusive=raw[PartitionKeyRange.MinInclusive],
            maxExclusive=raw[PartitionKeyRange.MaxExclusive],
            parents=tuple(raw.get(PartitionKeyRange.Parents) or ()),
            status=raw.get(PartitionKeyRange.Status),
            throughputFraction=raw.get(PartitionKeyRange.ThroughputFraction),
        )


class PartitionKeyRange(object):
    """Partition Key Range Constants"""

    MinInclusive = "minInclusive"
    MaxExclusive = "maxExclusive"
    Id = "id"
    Parents = "parents"
    Status = "status"
    ThroughputFraction = "throughputFraction"


class Range(object):
    """Range of a partition key."""
    # __slots__ reduces per-instance memory from ~250 bytes to ~64 bytes.
    # Significant when 100K+ partition ranges are cached per client.
    __slots__ = ('min', 'max', 'isMinInclusive', 'isMaxInclusive')

    MinPath = "min"
    MaxPath = "max"
    IsMinInclusivePath = "isMinInclusive"
    IsMaxInclusivePath = "isMaxInclusive"

    def __init__(self, range_min, range_max, isMinInclusive, isMaxInclusive):
        if range_min is None:
            raise ValueError("min is missing")
        if range_max is None:
            raise ValueError("max is missing")

        upper_min = range_min.upper()
        self.min = range_min if range_min == upper_min else upper_min
        upper_max = range_max.upper()
        self.max = range_max if range_max == upper_max else upper_max
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
    def get_full_range(cls):
        """Gets a Range object that covers the entire possible range of partition key values.

        :return: A Range object that covers the entire possible range of partition key values.
        :rtype: ~azure.cosmos._routing.routing_range.Range
        """
        return cls(range_min="", range_max="FF", isMinInclusive=True, isMaxInclusive=False)

    @classmethod
    def PartitionKeyRangeToRange(cls, partition_key_range):
        self = cls(
            partition_key_range[PartitionKeyRange.MinInclusive].upper(),
            partition_key_range[PartitionKeyRange.MaxExclusive].upper(),
            True,
            False,
        )
        return self

    @classmethod
    def ParseFromDict(cls, range_as_dict):
        self = cls(
            range_as_dict[Range.MinPath].upper(),
            range_as_dict[Range.MaxPath].upper(),
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

        return binascii.hexlify(byte_array).decode().upper()

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
    def _compare_helper(a: str, b: str):
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


def _second_range_is_after_first_range(range1, range2):
    """Checks if range2 starts strictly after range1 ends (no overlap).

    :param Range range1: The first range.
    :param Range range2: The second range.
    :return: True if range2 is entirely after range1, False if they overlap.
    :rtype: bool
    """
    if range1.max > range2.min:
        return False

    if range2.min == range1.max and range1.isMaxInclusive and range2.isMinInclusive:
        return False

    return True


def _is_sorted_and_non_overlapping(ranges):
    """Validates that a list of ranges is sorted and non-overlapping.

    :param list ranges: List of Range objects.
    :return: True if sorted and non-overlapping, False otherwise.
    :rtype: bool
    """
    for idx, r in list(enumerate(ranges))[1:]:
        previous_r = ranges[idx - 1]
        if not _second_range_is_after_first_range(previous_r, r):
            return False
    return True


def _subtract_range(r, partition_key_range):
    """Evaluates and returns r - partition_key_range

    :param dict partition_key_range: Partition key range.
    :param Range r: query range.
    :return: The subtract r - partition_key_range.
    :rtype: Range
    """
    left = max(partition_key_range[PartitionKeyRange.MaxExclusive], r.min)

    if left == r.min:
        leftInclusive = r.isMinInclusive
    else:
        leftInclusive = False

    queryRange = Range(left, r.max, leftInclusive, r.isMaxInclusive)
    return queryRange


class PartitionKeyRangeWrapper(object):
    """Internal class for a representation of a unique partition for an account
    """

    def __init__(self, partition_key_range: Range, collection_rid: str) -> None:
        self.partition_key_range = partition_key_range
        self.collection_rid = collection_rid


    def __str__(self) -> str:
        return (
            f"PartitionKeyRangeWrapper("
            f"partition_key_range={self.partition_key_range}, "
            f"collection_rid={self.collection_rid}, "
        )

    def __eq__(self, other):
        if not isinstance(other, PartitionKeyRangeWrapper):
            return False
        return self.partition_key_range == other.partition_key_range and self.collection_rid == other.collection_rid

    def __hash__(self):
        return hash((self.partition_key_range, self.collection_rid))
