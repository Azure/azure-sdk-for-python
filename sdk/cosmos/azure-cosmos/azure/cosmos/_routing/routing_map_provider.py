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
from .collection_routing_map import CollectionRoutingMap, _build_routing_map_from_ranges
from . import routing_range  # pylint: disable=unused-import
from .routing_range import (
    PartitionKeyRange,
    _is_sorted_and_non_overlapping,
    _subtract_range,
)
from ..exceptions import CosmosHttpResponseError

if TYPE_CHECKING:
    from .._cosmos_client_connection import CosmosClientConnection
# pylint: disable=protected-access, line-too-long


logger = logging.getLogger(__name__)
class PartitionKeyRangeCache(object):
    """
    PartitionKeyRangeCache provides list of effective partition key ranges for a
    collection.

    This implementation loads and caches the collection routing map per
    collection on demand.
    """
    page_size_change_feed = "-1"  # Return all available changes

    def __init__(self, client: Any):
        """
        Constructor
        """

        self._document_client = client

        # keeps the cached collection routing map by collection id
        self._collection_routing_map_by_item: Dict[str, CollectionRoutingMap] = {}
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

    # pylint: disable=invalid-name
    def get_routing_map(
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
        :return: The cached CollectionRoutingMap for the collection, or None if retrieval fails.
        :rtype: azure.cosmos.routing.collection_routing_map.CollectionRoutingMap or None
        """

        collection_id = _base.GetResourceIdOrFullNameFromLink(collection_link)

        # First check (no lock) for the fast path.
        # If no refresh is forced and the map is already cached, return it
        # immediately without acquiring the lock to avoid contention.
        if not force_refresh:
            cached_map = self._collection_routing_map_by_item.get(collection_id)
            if cached_map:
                return cached_map

        # Acquire a lock specific to this collection ID. This prevents race
        # conditions where multiple threads try to refresh the same map.
        collection_lock = self._get_lock_for_collection(collection_id)
        with collection_lock:
            # Second check (with lock) to see if another thread already did the work.
            existing_routing_map = self._collection_routing_map_by_item.get(collection_id)

            # Determine if a refresh or initial load is needed.
            # Note: _is_cache_stale() only compares ETags — it returns False when the cache is empty.
            # That's intentional: the empty-cache case is handled separately by is_initial_load.
            is_initial_load = not existing_routing_map
            needs_refresh = force_refresh and self._is_cache_stale(collection_id, previous_routing_map)

            if is_initial_load or needs_refresh:
                # If refresh is forced by a stale previous_routing_map, use it as the base for the incremental
                # update.
                # Otherwise, use the map currently in the cache.
                base_routing_map: Optional[CollectionRoutingMap]
                if needs_refresh and previous_routing_map:
                    base_routing_map = previous_routing_map
                else:
                    base_routing_map = existing_routing_map

                new_routing_map = self._fetch_routing_map(
                    collection_link,
                    collection_id,
                    base_routing_map,
                    feed_options,
                    **kwargs
                )

                if new_routing_map:
                    self._collection_routing_map_by_item[collection_id] = new_routing_map

            return self._collection_routing_map_by_item.get(collection_id)

    def _is_cache_stale(
            self,
            collection_id: str,
            previous_routing_map: Optional[CollectionRoutingMap]
    ) -> bool:
        """Checks if the cached routing map is stale by comparing ETags.

        This method only concerns itself with ETag comparison. It returns False
        when there is no previous_routing_map or when the cache is empty (no
        current_map). Returning False for an empty cache is intentional — this
        method's contract is strictly "are two existing maps equal?", not "does
        the cache need populating". The caller (get_routing_map) handles the
        empty-cache case separately via its own ``is_initial_load`` check.

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
        return (previous_routing_map.change_feed_etag ==
                current_map.change_feed_etag)

    # pylint: disable=too-many-statements
    def _fetch_routing_map(
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
        :param feed_options: Options for the change feed request.
        :type feed_options: dict or None
        :return: The new or updated CollectionRoutingMap, or None if retrieval fails.
        :rtype: azure.cosmos.routing.collection_routing_map.CollectionRoutingMap or None
        """
        ranges: List[Dict[str, Any]] = []
        response_headers: Dict[str, Any] = {}

        def capture_response_hook(hook_headers: Dict[str, Any], _):
            """Hook to capture response headers.

            :param dict hook_headers: The response headers to capture.
            :param _: Unused parameter (response body).
            :type _: Any
            """
            nonlocal response_headers
            response_headers = hook_headers

        # Pop any upstream response_hook from kwargs to avoid a TypeError
        # when we pass our own capture_response_hook explicitly to _ReadPartitionKeyRanges.
        # If an upstream hook exists, chain it so both hooks are called.
        upstream_hook = kwargs.pop('response_hook', None)
        if upstream_hook:
            original_capture = capture_response_hook

            def _chained_response_hook(hook_headers: Dict[str, Any], body,
                                       _upstream=upstream_hook):
                original_capture(hook_headers, body)
                if _upstream is not None:
                    _upstream(hook_headers, body)

            capture_response_hook = _chained_response_hook  # type: ignore[misc]

        # Sanitize options to only include those relevant for a PKRange read.
        change_feed_options = _base.format_pk_range_options(feed_options if feed_options is not None else {})

        # Set the flag to prevent infinite recursion: if this PK range fetch itself gets a 410,
        # the downstream retry loop in _DefaultQueryExecutionContext will see this flag and skip
        # calling refresh_routing_map_provider() again, which would re-enter _fetch_routing_map().
        change_feed_options["_internal_pk_range_fetch"] = True

        # Prepare headers for change feed
        headers = kwargs.get('headers', {}).copy()
        headers[http_constants.HttpHeaders.PageSize] = self.page_size_change_feed
        headers[http_constants.HttpHeaders.AIM] = http_constants.HttpHeaders.IncrementalFeedHeaderValue

        if previous_routing_map and previous_routing_map.change_feed_etag:
            headers[http_constants.HttpHeaders.IfNoneMatch] = previous_routing_map.change_feed_etag
        else:
            # Ensure no stale IfNoneMatch header leaks from a previous incremental attempt
            # into a full-load request. Without this, a recursive fallback call (with
            # previous_routing_map=None) would inherit the old ETag from kwargs, causing the
            # service to return only a delta instead of the complete set of ranges.
            headers.pop(http_constants.HttpHeaders.IfNoneMatch, None)

        kwargs['headers'] = headers

        try:
            pk_range_generator = self._document_client._ReadPartitionKeyRanges(
                collection_link,
                change_feed_options,
                response_hook=capture_response_hook,
                **kwargs
            )
            ranges.extend(list(pk_range_generator))

        except CosmosHttpResponseError as e:
            logger.error("Failed to read partition key ranges for collection '%s': %s", collection_link, e)
            raise

        new_etag = response_headers.get(http_constants.HttpHeaders.ETag)

        if not previous_routing_map:
            # Initial load - create complete routing map from full range set
            routing_map = _build_routing_map_from_ranges(ranges, collection_id, new_etag, collection_link, logger)
            if not routing_map:
                return None
        else:
            # Incremental update - combine with existing map
            range_tuples = []
            for r in ranges:
                # For incremental updates, the range_info (server endpoint) is not in the response.
                # We find the parent range in the old map to get the associated range_info.
                parents = r.get(PartitionKeyRange.Parents)
                if parents:  # This is a new partition from a split or merge
                    # Iterate through all parents to find one in our cache.
                    # For splits, parents[0] is the direct parent and is always cached.
                    # For merges, parents is a flat union that includes ancestors the SDK
                    # may have already evicted (e.g., grandparents). The actual replaced
                    # ranges may be at any position in the list.
                    range_info = None
                    for parent_id in parents:
                        if parent_id in previous_routing_map._rangeById:
                            parent_range_tuple = previous_routing_map._rangeById[parent_id]
                            range_info = parent_range_tuple[1]
                            break
                    if range_info is not None:
                        range_tuples.append((r, range_info))
                    else:
                        logger.warning(
                            "Incremental update failed: None of the parent ranges %s found in "
                            "routing map for collection '%s'. Falling back to full refresh.",
                            parents, collection_link
                        )
                        # Fall back to a full refresh.
                        return self._fetch_routing_map(collection_link, collection_id, None,
                                                                      feed_options, **kwargs)
                else:
                    # No parents — this range is not from a split or merge.
                    # No known service behavior produces a range with no parents in an
                    # incremental change feed response. Fall back to a full refresh as
                    # a defensive measure; the try_combine() completeness check would
                    # catch inconsistencies anyway, but failing fast avoids masking
                    # unexpected service behavior.
                    logger.warning(
                        "Incremental update encountered range '%s' with no parents for "
                        "collection '%s'. Falling back to full refresh.",
                        r.get('id', '<unknown>'), collection_link
                    )
                    return self._fetch_routing_map(collection_link, collection_id, None,
                                                                  feed_options, **kwargs)

            routing_map = previous_routing_map.try_combine(range_tuples, new_etag or "")
            if not routing_map:
                # Incremental merge resulted in an incomplete map.
                # Fall back to a full refresh.
                logger.warning(
                    "Incremental merge resulted in incomplete routing map for collection '%s'. "
                    "Falling back to full refresh.",
                    collection_link
                )
                return self._fetch_routing_map(collection_link, collection_id, None, feed_options, **kwargs)

        return routing_map

    def get_overlapping_ranges(self, collection_link, partition_key_ranges, feed_options, **kwargs):
        """Given a partition key range and a collection, return the list of
        overlapping partition key ranges.

        :param str collection_link: The link to the collection.
        :param list partition_key_ranges: List of partition key ranges to check for overlaps.
        :param dict feed_options: Options for the feed request.
        :return: List of overlapping partition key ranges.
        :rtype: list
        """
        if not partition_key_ranges:
            return []  # Avoid unnecessary network call if there are no ranges to check

        routing_map = self.get_routing_map(collection_link, feed_options, **kwargs)

        ranges = routing_map.get_overlapping_ranges(partition_key_ranges)
        return ranges

    def get_range_by_partition_key_range_id(
            self,
            collection_link: str,
            partition_key_range_id: str,
            feed_options: Dict[str, Any],
            **kwargs: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        routing_map = self.get_routing_map(
            collection_link,
            feed_options,
            force_refresh=False,
            previous_routing_map=None,
            **kwargs
        )
        if not routing_map:
            return None

        return routing_map.get_range_by_partition_key_range_id(partition_key_range_id)




class SmartRoutingMapProvider(PartitionKeyRangeCache):
    """
    Efficiently uses PartitionKeyRangeCache and minimizes the unnecessary
    invocation of CollectionRoutingMap.get_overlapping_ranges()
    """

    def get_overlapping_ranges(self, collection_link, partition_key_ranges, feed_options=None, **kwargs):
        if not partition_key_ranges:
            return []  # Return empty list directly instead of delegating to parent

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
            # when the iteration is exhausted we get here. There is nothing else to be done
            pass

        return target_partition_key_ranges
