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

"""Internal class for collection routing map implementation in the Azure Cosmos
database service.
"""

import bisect
from azure.cosmos._routing import routing_range
from azure.cosmos._routing.routing_range import PartitionKeyRange


class CollectionRoutingMap(object):
    """Stores partition key ranges in an efficient way with some additional
    information and provides convenience methods for working with set of ranges.
    """

    MinimumInclusiveEffectivePartitionKey = ""
    MaximumExclusiveEffectivePartitionKey = "FF"

    def __init__(
        self, range_by_id, range_by_info, ordered_partition_key_ranges, ordered_partition_info, collection_unique_id
    ):
        self._rangeById = range_by_id
        self._rangeByInfo = range_by_info
        self._orderedPartitionKeyRanges = ordered_partition_key_ranges

        self._orderedRanges = [
            routing_range.Range(pkr[PartitionKeyRange.MinInclusive], pkr[PartitionKeyRange.MaxExclusive], True, False)
            for pkr in ordered_partition_key_ranges
        ]
        self._orderedPartitionInfo = ordered_partition_info
        self._collectionUniqueId = collection_unique_id

    @classmethod
    def CompleteRoutingMap(cls, partition_key_range_info_tuple_list, collection_unique_id):
        rangeById = {}
        rangeByInfo = {}

        sortedRanges = []
        for r in partition_key_range_info_tuple_list:
            rangeById[r[0][PartitionKeyRange.Id]] = r
            rangeByInfo[r[1]] = r[0]
            sortedRanges.append(r)

        sortedRanges.sort(key=lambda r: r[0][PartitionKeyRange.MinInclusive])
        partitionKeyOrderedRange = [r[0] for r in sortedRanges]
        orderedPartitionInfo = [r[1] for r in sortedRanges]

        if not CollectionRoutingMap.is_complete_set_of_range(partitionKeyOrderedRange):
            return None
        return cls(rangeById, rangeByInfo, partitionKeyOrderedRange, orderedPartitionInfo, collection_unique_id)

    def get_ordered_partition_key_ranges(self):
        """Gets the ordered partition key ranges

        :return: Ordered list of partition key ranges.
        :rtype: list
        """
        return self._orderedPartitionKeyRanges

    def get_range_by_effective_partition_key(self, effective_partition_key_value):
        """Gets the range containing the given partition key

        :param str effective_partition_key_value: The partition key value.
        :return: The partition key range.
        :rtype: dict
        """
        if CollectionRoutingMap.MinimumInclusiveEffectivePartitionKey == effective_partition_key_value:
            return self._orderedPartitionKeyRanges[0]

        if CollectionRoutingMap.MaximumExclusiveEffectivePartitionKey == effective_partition_key_value:
            return None

        sortedLow = [(r.min, not r.isMinInclusive) for r in self._orderedRanges]

        index = bisect.bisect_right(sortedLow, (effective_partition_key_value, True))
        if index > 0:
            index = index - 1
        return self._orderedPartitionKeyRanges[index]

    def get_range_by_partition_key_range_id(self, partition_key_range_id):
        """Gets the partition key range given the partition key range id

        :param str partition_key_range_id: The partition key range id.
        :return: The partition key range.
        :rtype: dict
        """
        t = self._rangeById.get(partition_key_range_id)

        if t is None:
            return None
        return t[0]

    def get_overlapping_ranges(self, provided_partition_key_ranges):
        """Gets the partition key ranges overlapping the provided ranges

        :param list provided_partition_key_ranges: List of partition key ranges.
        :return: List of partition key ranges, where each is a dict.
        :rtype: list
        """

        if isinstance(provided_partition_key_ranges, routing_range.Range):
            return self.get_overlapping_ranges([provided_partition_key_ranges])

        minToPartitionRange = {}

        sortedLow = [(r.min, not r.isMinInclusive) for r in self._orderedRanges]
        sortedHigh = [(r.max, r.isMaxInclusive) for r in self._orderedRanges]

        for providedRange in provided_partition_key_ranges:
            minIndex = bisect.bisect_right(sortedLow, (providedRange.min, not providedRange.isMinInclusive))
            if minIndex > 0:
                minIndex = minIndex - 1

            maxIndex = bisect.bisect_left(sortedHigh, (providedRange.max, providedRange.isMaxInclusive))
            if maxIndex >= len(sortedHigh):
                maxIndex = maxIndex - 1

            for i in range(minIndex, maxIndex + 1):
                if routing_range.Range.overlaps(self._orderedRanges[i], providedRange):
                    minToPartitionRange[
                        self._orderedPartitionKeyRanges[i][PartitionKeyRange.MinInclusive]
                    ] = self._orderedPartitionKeyRanges[i]

        overlapping_partition_key_ranges = list(minToPartitionRange.values())

        def getKey(r):
            return r[PartitionKeyRange.MinInclusive]

        overlapping_partition_key_ranges.sort(key=getKey)
        return overlapping_partition_key_ranges

    @staticmethod
    def is_complete_set_of_range(ordered_partition_key_range_list):
        isComplete = False
        if ordered_partition_key_range_list:

            firstRange = ordered_partition_key_range_list[0]
            lastRange = ordered_partition_key_range_list[-1]
            isComplete = (
                firstRange[PartitionKeyRange.MinInclusive] == CollectionRoutingMap.MinimumInclusiveEffectivePartitionKey
            )
            isComplete &= (
                lastRange[PartitionKeyRange.MaxExclusive] == CollectionRoutingMap.MaximumExclusiveEffectivePartitionKey
            )

            for i in range(1, len(ordered_partition_key_range_list)):
                previousRange = ordered_partition_key_range_list[i - 1]
                currentRange = ordered_partition_key_range_list[i]
                isComplete &= (
                    previousRange[PartitionKeyRange.MaxExclusive] == currentRange[PartitionKeyRange.MinInclusive]
                )

                if not isComplete:
                    if previousRange[PartitionKeyRange.MaxExclusive] > currentRange[PartitionKeyRange.MinInclusive]:
                        raise ValueError("Ranges overlap")
                    break

        return isComplete
