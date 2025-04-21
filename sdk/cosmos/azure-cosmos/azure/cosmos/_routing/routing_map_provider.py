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

"""Internal class for partition key range cache implementation in the Azure
Cosmos database service.
"""

from .. import _base
from .collection_routing_map import CollectionRoutingMap
from . import routing_range
from .routing_range import PartitionKeyRange

# pylint: disable=protected-access


class PartitionKeyRangeCache(object):
    """
    PartitionKeyRangeCache provides list of effective partition key ranges for a
    collection.

    This implementation loads and caches the collection routing map per
    collection on demand.
    """

    def __init__(self, client):
        """
        Constructor
        """

        self._documentClient = client

        # keeps the cached collection routing map by collection id
        self._collection_routing_map_by_item = {}

    def get_overlapping_ranges(self, collection_link, partition_key_ranges, **kwargs):
        """Given a partition key range and a collection, return the list of
        overlapping partition key ranges.

        :param str collection_link: The name of the collection.
        :param list partition_key_ranges: List of partition key range.
        :return: List of overlapping partition key ranges.
        :rtype: list
        """
        cl = self._documentClient

        collection_id = _base.GetResourceIdOrFullNameFromLink(collection_link)

        collection_routing_map = self._collection_routing_map_by_item.get(collection_id)
        if collection_routing_map is None:
            collection_pk_ranges = list(cl._ReadPartitionKeyRanges(collection_link, **kwargs))
            # for large collections, a split may complete between the read partition key ranges query page responses,
            # causing the partitionKeyRanges to have both the children ranges and their parents. Therefore, we need
            # to discard the parent ranges to have a valid routing map.
            collection_pk_ranges = PartitionKeyRangeCache._discard_parent_ranges(collection_pk_ranges)
            collection_routing_map = CollectionRoutingMap.CompleteRoutingMap(
                [(r, True) for r in collection_pk_ranges], collection_id
            )
            self._collection_routing_map_by_item[collection_id] = collection_routing_map
        return collection_routing_map.get_overlapping_ranges(partition_key_ranges)

    @staticmethod
    def _discard_parent_ranges(partitionKeyRanges):
        parentIds = set()
        for r in partitionKeyRanges:
            if isinstance(r, dict) and PartitionKeyRange.Parents in r:
                for parentId in r[PartitionKeyRange.Parents]:
                    parentIds.add(parentId)
        return (r for r in partitionKeyRanges if r[PartitionKeyRange.Id] not in parentIds)


def _second_range_is_after_first_range(range1, range2):
    if range1.max > range2.min:
        ##r.min < #previous_r.max
        return False

    if range2.min == range1.max and range1.isMaxInclusive and range2.isMinInclusive:
        # the inclusive ending endpoint of previous_r is the same as the inclusive beginning endpoint of r
        return False

    return True


def _is_sorted_and_non_overlapping(ranges):
    for idx, r in list(enumerate(ranges))[1:]:
        previous_r = ranges[idx - 1]
        if not _second_range_is_after_first_range(previous_r, r):
            return False
    return True


def _subtract_range(r, partition_key_range):
    """Evaluates and returns r - partition_key_range

    :param dict partition_key_range: Partition key range.
    :param routing_range.Range r: query range.
    :return: The subtract r - partition_key_range.
    :rtype: routing_range.Range
    """

    left = max(partition_key_range[routing_range.PartitionKeyRange.MaxExclusive], r.min)

    if left == r.min:
        leftInclusive = r.isMinInclusive
    else:
        leftInclusive = False

    queryRange = routing_range.Range(left, r.max, leftInclusive, r.isMaxInclusive)
    return queryRange


class SmartRoutingMapProvider(PartitionKeyRangeCache):
    """
    Efficiently uses PartitionKeyRangeCache and minimizes the unnecessary
    invocation of CollectionRoutingMap.get_overlapping_ranges()
    """

    def get_overlapping_ranges(self, collection_link, partition_key_ranges, **kwargs):
        """
        Given the sorted ranges and a collection,
        Returns the list of overlapping partition key ranges

        :param str collection_link: The collection link.
        :param (list of routing_range.Range) partition_key_ranges:
            The sorted list of non-overlapping ranges.
        :return: List of partition key ranges.
        :rtype: list of dict
        :raises ValueError:
            If two ranges in partition_key_ranges overlap or if the list is not sorted
        """

        # validate if the list is non-overlapping and sorted
        if not _is_sorted_and_non_overlapping(partition_key_ranges):
            raise ValueError("the list of ranges is not a non-overlapping sorted ranges")

        target_partition_key_ranges = []

        it = iter(partition_key_ranges)
        try:
            currentProvidedRange = next(it)
            while True:
                if currentProvidedRange.isEmpty():
                    # skip and go to the next item\
                    currentProvidedRange = next(it)
                    continue

                if target_partition_key_ranges:
                    queryRange = _subtract_range(currentProvidedRange, target_partition_key_ranges[-1])
                else:
                    queryRange = currentProvidedRange

                overlappingRanges = (
                    PartitionKeyRangeCache.get_overlapping_ranges(self, collection_link, [queryRange], **kwargs))
                assert overlappingRanges, "code bug: returned overlapping ranges for queryRange {} is empty".format(
                    queryRange
                )
                target_partition_key_ranges.extend(overlappingRanges)

                lastKnownTargetRange = routing_range.Range.PartitionKeyRangeToRange(target_partition_key_ranges[-1])

                # the overlapping ranges must contain the requested range
                assert (
                    currentProvidedRange.max <= lastKnownTargetRange.max
                ), "code bug: returned overlapping ranges {} does not contain the requested range {}".format(
                    overlappingRanges, queryRange
                )

                # the current range is contained in target_partition_key_ranges just move forward
                currentProvidedRange = next(it)

                while currentProvidedRange.max <= lastKnownTargetRange.max:
                    # the current range is covered too. just move forward
                    currentProvidedRange = next(it)
        except StopIteration:
            # when the iteration is exhausted we get here. There is nothing else to be done
            pass

        return target_partition_key_ranges
