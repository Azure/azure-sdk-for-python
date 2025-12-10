# The MIT License (MIT)
# Copyright (c) 2021 Microsoft Corporation

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
import asyncio  # pylint: disable=do-not-import-asyncio
import logging
from typing import Dict, Any, Optional, List, TYPE_CHECKING
from ..routing_range import PartitionKeyRange
from ... import _base, http_constants
from ..collection_routing_map import CollectionRoutingMap
from .. import routing_range
if TYPE_CHECKING:
    from ...aio._cosmos_client_connection_async import CosmosClientConnection
# pylint: disable=protected-access

logger = logging.getLogger(__name__)
class PartitionKeyRangeCache(object):
    """
    PartitionKeyRangeCache provides list of effective partition key ranges for a
    collection.

    This implementation loads and caches the collection routing map per
    collection on demand.
    """

    page_size_change_feed = "-1"  # Return all available changes

    def __init__(self, client: "CosmosClientConnection"):
        """
        Constructor
        """

        self._document_client = client

        # keeps the cached collection routing map by collection id
        self._collection_routing_map_by_item: Dict[str, CollectionRoutingMap] = {}
        # A lock to control access to the locks dictionary itself
        self._locks_lock = asyncio.Lock()
        # A dictionary to hold a lock for each collection ID
        self._collection_locks: Dict[str, asyncio.Lock] = {}

    async def _get_lock_for_collection(self, collection_id: str) -> asyncio.Lock:
        """Safely gets or creates a lock for a given collection ID.

        :param str collection_id: The ID of the collection.
        :return: An asyncio.Lock specific to the collection ID.
        :rtype: asyncio.Lock
        """
        async with self._locks_lock:
            if collection_id not in self._collection_locks:
                self._collection_locks[collection_id] = asyncio.Lock()
            return self._collection_locks[collection_id]

    async def get_overlapping_ranges(self, collection_link, partition_key_ranges, feed_options=None, **kwargs):
        """Efficiently gets overlapping ranges for a collection.

        Overrides the parent method to optimize performance by minimizing unnecessary
        invocations of CollectionRoutingMap.get_overlapping_ranges().

        :param str collection_link: The link to the collection.
        :param list partition_key_ranges: A list of sorted, non-overlapping ranges to find overlaps for.
        :param Optional[Dict[str, Any]] feed_options: Optional query options used when fetching the routing map.
        :return: A list of overlapping partition key ranges from the collection.
        :rtype: list
        :raises RuntimeError: If the routing map for the collection is not found.
        """

        if not partition_key_ranges:
            return []  # Return empty list instead of all ranges

        routing_map = await self.get_or_refresh_routing_map_for_collection(collection_link, feed_options, **kwargs)
        if not routing_map:
            raise RuntimeError(f"Routing map for collection {collection_link} not found.")

        ranges = routing_map.get_overlapping_ranges(partition_key_ranges)
        return ranges

    # pylint: disable=invalid-name
    async def get_or_refresh_routing_map_for_collection(
            self,
            collection_link: str,
            feed_options: Optional[Dict[str, Any]],
            force_refresh: bool = False,
            previous_routing_map: Optional[CollectionRoutingMap] = None,
            **kwargs: Any
    ) -> Optional[CollectionRoutingMap]:
        """Gets or refreshes the routing map for a collection.

        This method handles the logic for fetching, caching, and updating the
        collection's routing map. It uses a locking mechanism to prevent race
        conditions during concurrent updates.

        :param str collection_link: The link to the collection.
        :param Optional[Dict[str, Any]] feed_options: Optional query options.
        :param bool force_refresh: If True, forces a refresh of the routing map.
        :param Optional[CollectionRoutingMap] previous_routing_map: The last known routing map,
            used for incremental updates.
        :return: The updated or cached CollectionRoutingMap, or None if it couldn't be retrieved.
        :rtype: Optional[CollectionRoutingMap]
        """
        collection_id = _base.GetResourceIdOrFullNameFromLink(collection_link)

        # First check (no lock) for the fast path.
        if not force_refresh:
            cached_map = self._collection_routing_map_by_item.get(collection_id)
            if cached_map:
                return cached_map

        # Acquire lock only when a refresh or initial load is likely needed.
        collection_lock = await self._get_lock_for_collection(collection_id)
        async with collection_lock:
            # Second check (with lock) to see if another coroutine already did the work.
            existing_routing_map = self._collection_routing_map_by_item.get(collection_id)

            is_initial_load = not existing_routing_map
            needs_refresh = force_refresh or self.should_force_refresh(collection_id, previous_routing_map)

            if is_initial_load or needs_refresh:
                # Perform the expensive refresh operation while holding the lock.
                base_routing_map: Optional[CollectionRoutingMap]
                if needs_refresh and previous_routing_map:
                    base_routing_map = previous_routing_map
                else:
                    base_routing_map = existing_routing_map

                new_routing_map = await self._get_routing_map_with_change_feed(
                    collection_link,
                    collection_id,
                    base_routing_map,
                    feed_options,
                    **kwargs
                )

                # Update the cache.
                if new_routing_map:
                    self._collection_routing_map_by_item[collection_id] = new_routing_map

            return self._collection_routing_map_by_item.get(collection_id)

    def should_force_refresh(
            self,
            collection_id: str,
            previous_routing_map: Optional[CollectionRoutingMap]
    ) -> bool:
        """Determines if a forced refresh of the routing map is necessary.

        This check is crucial for handling scenarios where a client might be operating
        with a stale routing map, for example, after a partition split. It compares the
        ETag (change_feed_next_if_none_match) of the previously used routing map with
        the one currently in the cache. If the ETags are identical, it implies that no
        new routing information has been fetched since the last operation, suggesting
        the cache might be stale and a refresh is needed to ensure the client has the
        most up-to-date view of the collection's partitions.

        :param str collection_id: The ID of the collection.
        :param previous_routing_map: The routing map that was used in the previous operation.
        :type previous_routing_map: azure.cosmos.routing.collection_routing_map.CollectionRoutingMap or None
        :return: True if a refresh should be forced, False otherwise.
        :rtype: bool
        """
        if not previous_routing_map:
            return False

        current_map = self._collection_routing_map_by_item.get(collection_id)
        if not current_map:
            return False

        # If ETags match, cache might be stale
        return (previous_routing_map.change_feed_next_if_none_match ==
                current_map.change_feed_next_if_none_match)

    async def _get_routing_map_with_change_feed(
            self,
            collection_link: str,
            collection_id: str,
            previous_routing_map: Optional[CollectionRoutingMap],
            feed_options: Optional[Dict[str, Any]],
            **kwargs
    ) -> Optional[CollectionRoutingMap]:
        """Fetches the routing map using an incremental change feed.

        This method is responsible for obtaining the collection's routing map. It
        optimizes this process by using the partition key range change feed.

        If no previous_routing_map is provided (initial load), it fetches the
        complete set of partition key ranges and constructs a new routing map.

        If a previous_routing_map is provided, it performs an incremental update.
        It sends the ETag of the previous map in an If-None-Match header. The
        server then returns only the changes that have occurred since that ETag.
        The method then attempts to merge these changes into the existing map.

        In cases where an incremental update is not possible (e.g., inconsistent
        state, parent range not found), it logs a warning and falls back to
        performing a full refresh by recursively calling itself without a
        previous_routing_map.

        :param str collection_link: The link to the collection.
        :param str collection_id: The ID of the collection.
        :param previous_routing_map: The last known routing map for incremental updates.
        :type previous_routing_map: azure.cosmos.routing.collection_routing_map.CollectionRoutingMap or None
        :param feed_options: Options for the change feed request.
        :type feed_options: dict or None
        :return: The updated or newly created CollectionRoutingMap, or None if the update fails.
        :rtype: azure.cosmos.routing.collection_routing_map.CollectionRoutingMap or None
        :raises CosmosHttpResponseError: If the underlying request to fetch ranges fails.
        """
        ranges: List[Dict[str, Any]] = []
        response_headers: Dict[str, Any] = {}

        def capture_response_hook(headers: Dict[str, Any], _):
            """Hook to capture response headers.

            :param Dict[str, Any] headers: The response headers to capture.
            :param Any _: Unused response parameter (typically the response body or item).
            """
            nonlocal response_headers
            response_headers = headers

        # Sanitize options to only include those relevant for a PKRange read.
        change_feed_options = _base.format_pk_range_options(feed_options if feed_options is not None else {})

        # Prepare headers for change feed
        headers = kwargs.get('headers', {}).copy()
        headers[http_constants.HttpHeaders.PageSize] = self.page_size_change_feed
        headers[http_constants.HttpHeaders.AIM] = http_constants.HttpHeaders.IncrementalFeedHeaderValue

        if previous_routing_map and previous_routing_map.change_feed_next_if_none_match:
            headers[http_constants.HttpHeaders.IfNoneMatch] = previous_routing_map.change_feed_next_if_none_match

        kwargs['headers'] = headers

        pk_range_generator = self._document_client._ReadPartitionKeyRanges(
            collection_link,
            change_feed_options,
            response_hook=capture_response_hook,
            **kwargs
        )
        async for item in pk_range_generator:
            ranges.append(item)

        new_etag = response_headers.get(http_constants.HttpHeaders.ETag)

        if not previous_routing_map:
            # Initial load - create complete routing map
            gone_range_ids = set()
            for r in ranges:
                if PartitionKeyRange.Parents in r and r[PartitionKeyRange.Parents]:
                    gone_range_ids.update(r[PartitionKeyRange.Parents])

            filtered_ranges = [r for r in ranges if r[PartitionKeyRange.Id] not in gone_range_ids]
            range_tuples = [(r, True) for r in filtered_ranges]

            routing_map = CollectionRoutingMap.CompleteRoutingMap(
                range_tuples,
                collection_id,
                new_etag
            )
        else:
            # Incremental update - combine with existing map
            range_tuples = []
            for r in ranges:
                # For incremental updates, the range_info (server endpoint) is not in the response.
                # We find the parent range in the old map to get the associated range_info.
                parents = r.get(PartitionKeyRange.Parents)
                if parents:  # This is a new partition from a split
                    parent_id = parents[0]
                    if parent_id in previous_routing_map._rangeById:
                        parent_range_tuple = previous_routing_map._rangeById[parent_id]
                        range_info = parent_range_tuple[1]  # Get the range_info from the parent
                        range_tuples.append((r, range_info))
                    else:
                        # This would be an inconsistent state from the server. Force a full refresh
                        # by clearing the cache for the collection and retrying.
                        logger.warning(
                            "Incremental update failed: Parent range '%s' not found in routing map "
                            "for collection '%s'. Falling back to full refresh.",
                            parent_id,
                            collection_link
                        )
                        self._collection_routing_map_by_item.pop(collection_id, None)
                        return await self._get_routing_map_with_change_feed(collection_link, collection_id, None,
                                                                      feed_options, **kwargs)
                else:  # This is an existing partition, unaffected by the split
                    # The change feed may return ranges that were not split but are adjacent
                    # to a split. This block handles such cases. Since the range itself hasn't
                    # changed, we expect to find it in our previous routing map.
                    range_id = r[PartitionKeyRange.Id]
                    if range_id in previous_routing_map._rangeById:
                        # We retrieve the existing range_info from the old map
                        # because the incremental feed response for existing ranges does not include it.
                        existing_range_tuple = previous_routing_map._rangeById[range_id]
                        range_info = existing_range_tuple[1]
                        range_tuples.append((r, range_info))
                    else:
                        # If an existing range returned by the change feed is NOT in our previous map,
                        # it signifies an inconsistent state. This is unexpected and indicates a problem,
                        # so we trigger a full refresh of the routing map to recover.
                        logger.warning(
                            "Incremental update failed: Existing range '%s' not found in routing map "
                            "for collection '%s'. Falling back to full refresh.",
                            range_id,
                            collection_link
                        )
                        self._collection_routing_map_by_item.pop(collection_id, None)
                        return await self._get_routing_map_with_change_feed(collection_link, collection_id, None,
                                                                      feed_options, **kwargs)

            routing_map = previous_routing_map.try_combine(range_tuples, new_etag or "")
        if not routing_map:
            # This can happen if the combination results in an incomplete map.
            # Force a full refresh by clearing the cache for the collection and retrying.
            logger.warning(
                "Incremental merge resulted in incomplete routing map for collection '%s'. "
                "Falling back to full refresh.",
                collection_link
            )
            self._collection_routing_map_by_item.pop(collection_id, None)
            return await self._get_routing_map_with_change_feed(
                collection_link, collection_id, None, feed_options, **kwargs
            )

        return routing_map

    async def get_range_by_partition_key_range_id(
            self,
            collection_link: str,
            partition_key_range_id: int,
            feed_options: Dict[str, Any],
            **kwargs: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        routing_map = await self.get_or_refresh_routing_map_for_collection(
            collection_link,
            feed_options,
            force_refresh=False,
            previous_routing_map=None,
            **kwargs
        )
        if not routing_map:
            return None

        return routing_map.get_range_by_partition_key_range_id(partition_key_range_id)

    @staticmethod
    def _discard_parent_ranges(partitionKeyRanges):
        parentIds = set()
        for r in partitionKeyRanges:
            if isinstance(r, dict) and routing_range.PartitionKeyRange.Parents in r:
                for parentId in r[routing_range.PartitionKeyRange.Parents]:
                    parentIds.add(parentId)
        return (r for r in partitionKeyRanges if r[routing_range.PartitionKeyRange.Id] not in parentIds)


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

    async def get_overlapping_ranges(self, collection_link, partition_key_ranges, feed_options=None, **kwargs):
        if not partition_key_ranges:
            return await super(SmartRoutingMapProvider, self).get_overlapping_ranges(
                collection_link, [], feed_options, **kwargs
            )

        if not _is_sorted_and_non_overlapping(partition_key_ranges):
            raise ValueError("the list of ranges is not a non-overlapping sorted ranges")

        target_partition_key_ranges = []
        it = iter(partition_key_ranges)
        try:
            currentProvidedRange = next(it)
            while True:
                if currentProvidedRange.isEmpty():
                    currentProvidedRange = next(it)
                    continue

                if target_partition_key_ranges:
                    queryRange = _subtract_range(currentProvidedRange, target_partition_key_ranges[-1])
                else:
                    queryRange = currentProvidedRange

                # This line calls its parent's get_overlapping_ranges method inside a loop. While it correctly
                # requests the routing_map on each call, it overwrites the routing_map variable in every iteration.
                # This means only the routing_map from the very last call will be retained and returned.
                # If the query spans ranges that are covered by different routing map versions
                # (e.g.due to a split happening during the query),this could lead to using a stale or incomplete map.
                overlappingRanges = (
                    await PartitionKeyRangeCache.get_overlapping_ranges(
                        self,
                        collection_link,
                        [queryRange],
                        feed_options,
                        **kwargs))
                assert overlappingRanges, "code bug: returned overlapping ranges for queryRange {} is empty".format(
                    queryRange
                )
                target_partition_key_ranges.extend(overlappingRanges)

                lastKnownTargetRange = routing_range.Range.PartitionKeyRangeToRange(target_partition_key_ranges[-1])
                assert (
                        currentProvidedRange.max <= lastKnownTargetRange.max
                ), "code bug: returned overlapping ranges {} does not contain the requested range {}".format(
                    overlappingRanges, queryRange
                )

                currentProvidedRange = next(it)

                while currentProvidedRange.max <= lastKnownTargetRange.max:
                    currentProvidedRange = next(it)
        except StopIteration:
            pass

        return target_partition_key_ranges
