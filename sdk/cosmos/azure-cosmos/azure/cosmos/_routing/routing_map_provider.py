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
import threading
import logging
from typing import Dict, Any, Optional, List, TYPE_CHECKING
from .. import _base, http_constants
from .collection_routing_map import CollectionRoutingMap
from . import routing_range
from .routing_range import PartitionKeyRange
from ..exceptions import CosmosHttpResponseError

if TYPE_CHECKING:
    from ..cosmos_client import CosmosClient
# pylint: disable=protected-access

logger = logging.getLogger(__name__)
class PartitionKeyRangeCache(object):
    """
    PartitionKeyRangeCache provides list of effective partition key ranges for a
    collection.

    This implementation loads and caches the collection routing map per
    collection on demand.
    """
    PAGE_SIZE_CHANGE_FEED = "-1"  # Return all available changes

    def __init__(self, client: "CosmosClient"):
        """
        Constructor
        """

        self._documentClient = client

        # keeps the cached collection routing map by collection id
        self._collection_routing_map_by_item = {}
        # A lock to control access to the locks dictionary itself
        self._locks_lock = threading.Lock()
        # A dictionary to hold a lock for each collection ID
        self._collection_locks: Dict[str, threading.Lock] = {}

    def _get_lock_for_collection(self, collection_id: str) -> threading.Lock:

        """Safely gets or creates a lock for a given collection ID.

        This method ensures that there is a unique lock for each collection ID,
        preventing race conditions when multiple threads attempt to access or
        modify the routing map for the same collection simultaneously. It uses a
        lock to protect the dictionary of collection-specific locks during access
        and creation.

        :param str collection_id: The unique identifier for the collection.
        :return: A lock object specific to the given collection ID.
        :rtype: threading.Lock
        """
        with self._locks_lock:
            if collection_id not in self._collection_locks:
                self._collection_locks[collection_id] = threading.Lock()
            return self._collection_locks[collection_id]

    def get_or_refresh_routing_map_for_collection(
            self,
            collection_link: str,
            feed_options: Optional[Dict[str, Any]],
            force_refresh: bool = False,
            previous_routing_map: Optional[CollectionRoutingMap] = None,
            **kwargs: Any
    ) -> Optional[CollectionRoutingMap]:
        """Gets the routing map for a collection, refreshing it if necessary.

        This method retrieves the CollectionRoutingMap for a given collection.
        If the map is not cached, is explicitly forced to refresh, or is
        detected as stale, it will be fetched or updated using an incremental
        change feed. This operation is thread-safe per collection.

        :param str collection_link: The link of the collection for which to retrieve the routing map.
        :param dict feed_options: The feed options for the change feed request.
        :param bool force_refresh: If True, forces a refresh of the routing map.
        :param previous_routing_map: An optional previously known routing map, used to check for staleness.
        :type previous_routing_map: azure.cosmos.routing.collection_routing_map.CollectionRoutingMap
        :param kwargs: Additional keyword arguments for the underlying requests.
        :return: The cached CollectionRoutingMap for the collection, or None if retrieval fails.
        :rtype: azure.cosmos.routing.collection_routing_map.CollectionRoutingMap or None
        """

        collection_id = _base.GetResourceIdOrFullNameFromLink(collection_link)
        # Acquire a lock specific to this collection ID. This prevents race
        # conditions where multiple threads try to refresh the same map.
        collection_lock = self._get_lock_for_collection(collection_id)
        with collection_lock:
            existing_routing_map = self._collection_routing_map_by_item.get(collection_id)

            # Determine if a refresh or initial load is needed.
            is_initial_load = not existing_routing_map
            needs_refresh = force_refresh or self.should_force_refresh(collection_id, previous_routing_map)

            if is_initial_load or needs_refresh:
                # If refresh is forced by a stale previous_routing_map, use it as the base for the incremental update.
                # Otherwise, use the map currently in the cache.
                if needs_refresh and previous_routing_map:
                    base_routing_map = previous_routing_map
                else:
                    base_routing_map = existing_routing_map

                new_routing_map = self._get_routing_map_with_change_feed(
                    collection_link,
                    collection_id,
                    base_routing_map,
                    feed_options,
                    **kwargs
                )

                if new_routing_map:
                    self._collection_routing_map_by_item[collection_id] = new_routing_map

            return self._collection_routing_map_by_item.get(collection_id)

    def should_force_refresh(
            self,
            collection_id: str,
            previous_routing_map: Optional[CollectionRoutingMap]
    ) -> bool:
        """Determines if a forced refresh of the routing map is necessary.

        This method checks if the currently cached routing map is potentially
        stale compared to a provided `previous_routing_map`. A forced refresh
        is triggered if both maps exist and share the same ETag for the change
        feed. This indicates that the cache has not been updated since the
        event that deemed the `previous_routing_map` as stale.

        :param str collection_id: The unique identifier for the collection.
        :param previous_routing_map: The routing map that is suspected to be stale.
        :type previous_routing_map: azure.cosmos.routing.collection_routing_map.CollectionRoutingMap
        :return: True if a refresh should be forced, otherwise False.
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

    def _get_routing_map_with_change_feed(
            self,
            collection_link: str,
            collection_id: str,
            previous_routing_map: Optional[CollectionRoutingMap],
            feed_options: Optional[Dict[str, Any]],
            **kwargs
    ) -> Optional[CollectionRoutingMap]:

        """Fetches or updates the routing map using an incremental change feed.

        This method handles both the initial loading of a collection's routing
        map and subsequent incremental updates. If a previous_routing_map is
        provided, it fetches only the changes since that map was generated.
        Otherwise, it performs a full read of all partition key ranges. In case
        of inconsistencies during an incremental update, it automatically falls
        back to a full refresh.

        :param str collection_link: The link to the collection.
        :param str collection_id: The unique identifier of the collection.
        :param previous_routing_map: The routing map to be updated. If None, a full load is performed.
        :type previous_routing_map: azure.cosmos.routing.collection_routing_map.CollectionRoutingMap
        :param dict feed_options: Options for the change feed request.
        :param kwargs: Additional keyword arguments for the underlying client request.
        :return: The new or updated CollectionRoutingMap, or None if an update fails and fallback is triggered.
        :rtype: azure.cosmos.routing.collection_routing_map.CollectionRoutingMap or None
        """
        ranges: List[Dict[str, Any]] = []
        response_headers: Dict[str, Any] = {}

        def capture_response_hook(headers: Dict[str, Any], _):
            """Hook to capture response headers."""
            nonlocal response_headers
            response_headers = headers

        # Sanitize options to only include those relevant for a PKRange read.
        change_feed_options = _base.format_pk_range_options(feed_options if feed_options is not None else {})

        # Prepare headers for change feed
        headers = kwargs.get('headers', {}).copy()
        headers[http_constants.HttpHeaders.PageSize] = self.PAGE_SIZE_CHANGE_FEED
        headers[http_constants.HttpHeaders.AIM] = http_constants.HttpHeaders.IncrementalFeedHeaderValue

        if previous_routing_map and previous_routing_map.change_feed_next_if_none_match:
            headers[http_constants.HttpHeaders.IfNoneMatch] = previous_routing_map.change_feed_next_if_none_match

        kwargs['headers'] = headers

        try:
            pk_range_generator = self._documentClient._ReadPartitionKeyRanges(
                collection_link,
                change_feed_options,
                response_hook=capture_response_hook,
                **kwargs
            )
            ranges.extend(list(pk_range_generator))

        except CosmosHttpResponseError as e:
            raise

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
                        # This would be an inconsistent state from the server. Force a full refresh by clearing the cache for the collection and retrying.
                        logger.warning(
                            f"Incremental update failed: Parent range '{parent_id}' not found in routing map "
                            f"for collection '{collection_link}'. Falling back to full refresh."
                        )
                        self._collection_routing_map_by_item.pop(collection_id, None)
                        return self._get_routing_map_with_change_feed(collection_link, collection_id, None,
                                                                      feed_options, **kwargs)
                else:
                    range_id = r[PartitionKeyRange.Id]
                    if range_id in previous_routing_map._rangeById:
                        existing_range_tuple = previous_routing_map._rangeById[range_id]
                        range_info = existing_range_tuple[1]
                        range_tuples.append((r, range_info))
                    else:
                        logger.warning(
                            f"Incremental update failed: Existing range '{range_id}' not found in routing map "
                            f"for collection '{collection_link}'. Falling back to full refresh."
                        )
                        self._collection_routing_map_by_item.pop(collection_id, None)
                        return self._get_routing_map_with_change_feed(collection_link, collection_id, None,
                                                                      feed_options, **kwargs)

            routing_map = previous_routing_map.try_combine(range_tuples, new_etag or "")
        if not routing_map:
            # This can happen if the combination results in an incomplete map.
            # Force a full refresh by clearing the cache for the collection and retrying.
            logger.warning(
                f"Incremental merge resulted in incomplete routing map for collection '{collection_link}'. "
                f"Falling back to full refresh."
            )
            self._collection_routing_map_by_item.pop(collection_id, None)
            return self._get_routing_map_with_change_feed(collection_link, collection_id, None, feed_options, **kwargs)

        return routing_map

    def get_overlapping_ranges(self, collection_link, partition_key_ranges, feed_options, **kwargs):
        """Given a partition key range and a collection, return the list of
        overlapping partition key ranges.
        """
        if not partition_key_ranges:
            return []  # Avoid unnecessary network call if there are no ranges to check

        routing_map = self.get_or_refresh_routing_map_for_collection(collection_link, feed_options, **kwargs)
        if not routing_map:
            raise RuntimeError(f"Routing map for collection {collection_link} not found.")

        ranges = routing_map.get_overlapping_ranges(partition_key_ranges)
        return ranges

    def get_range_by_partition_key_range_id(
            self,
            collection_link: str,
            partition_key_range_id: str,
            feed_options: Dict[str, Any],
            **kwargs: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        routing_map = self.get_or_refresh_routing_map_for_collection(
            collection_link=collection_link,
            feed_options=feed_options,
            **kwargs
        )
        if not routing_map:
            return None

        return routing_map.get_range_by_partition_key_range_id(partition_key_range_id)

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

    def get_overlapping_ranges(self, collection_link, partition_key_ranges, feed_options=None, **kwargs):
        if not partition_key_ranges:
            return super(SmartRoutingMapProvider, self).get_overlapping_ranges(
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
                # This line calls its parent's get_overlapping_ranges method inside a loop. While it correctly requests the
                # routing_map on each call, it overwrites the routing_map variable in every iteration.
                # This means only the routing_map from the very last call will be retained and returned. If the query spans
                # ranges that are covered by different routing map versions (e.g., due to a split happening during the query),
                # this could lead to using a stale or incomplete map.
                overlappingRanges = (
                    PartitionKeyRangeCache.get_overlapping_ranges(
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
