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
from azure.core.utils import CaseInsensitiveDict
from .. import _base, http_constants
from .collection_routing_map import CollectionRoutingMap
from ..exceptions import CosmosHttpResponseError
from ._routing_map_provider_common import (
    prepare_fetch_options_and_headers,
    process_fetched_ranges,
    is_cache_unchanged_since_previous,
    determine_refresh_action,
    get_smart_overlapping_ranges,
    _NeedFullRefresh,
)

if TYPE_CHECKING:
    from .._cosmos_client_connection import CosmosClientConnection
# pylint: disable=protected-access, line-too-long


logger = logging.getLogger(__name__)
# Number of extra incremental attempts after an incomplete incremental merge
# before falling back to a full routing-map refresh.
_INCOMPLETE_ROUTING_MAP_MAX_RETRIES = 1
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

    def _is_cache_stale(
            self,
            collection_id: str,
            previous_routing_map: Optional[CollectionRoutingMap]
    ) -> bool:
        """Compatibility shim for legacy call sites and tests.

        :param str collection_id: The collection identifier used as the cache key.
        :param previous_routing_map: The previously observed routing map, if any.
        :type previous_routing_map: CollectionRoutingMap or None
        :return: ``True`` when cached and previous maps have the same generation ETag.
        :rtype: bool
        """
        return is_cache_unchanged_since_previous(
            self._collection_routing_map_by_item,
            collection_id,
            previous_routing_map,
        )

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
            # Second check (with lock) — use shared helper for the decision logic.
            should_fetch, base_routing_map = determine_refresh_action(
                self._collection_routing_map_by_item,
                collection_id,
                force_refresh,
                previous_routing_map,
            )

            if should_fetch:
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
        current_previous_map = previous_routing_map
        incomplete_attempt_count = 0

        while True:
            request_kwargs = dict(kwargs)
            response_headers: CaseInsensitiveDict = CaseInsensitiveDict()
            request_kwargs['_internal_response_headers_capture'] = response_headers

            # Prepare sanitised options and headers for the PK-range fetch.
            change_feed_options = prepare_fetch_options_and_headers(
                current_previous_map, feed_options, request_kwargs
            )

            ranges: List[Dict[str, Any]] = []
            try:
                pk_range_generator = self._document_client._ReadPartitionKeyRanges(
                    collection_link,
                    change_feed_options,
                    **request_kwargs
                )
                ranges.extend(list(pk_range_generator))

            except CosmosHttpResponseError as e:
                logger.error(  # pylint: disable=do-not-log-exceptions-if-not-debug,do-not-log-raised-errors
                    "Failed to read partition key ranges for collection '%s': %s", collection_link, e)
                raise

            new_etag = response_headers.get(http_constants.HttpHeaders.ETag)

            try:
                return process_fetched_ranges(
                    ranges, current_previous_map, collection_id, collection_link, new_etag
                )
            except _NeedFullRefresh:
                if current_previous_map is not None and incomplete_attempt_count < _INCOMPLETE_ROUTING_MAP_MAX_RETRIES:
                    incomplete_attempt_count += 1
                    logger.warning(
                        "Incremental routing-map refresh incomplete for collection '%s'. "
                        "Retrying incremental fetch (attempt %d/%d).",
                        collection_link,
                        incomplete_attempt_count,
                        _INCOMPLETE_ROUTING_MAP_MAX_RETRIES,
                    )
                    continue

                if current_previous_map is not None:
                    logger.error(
                        "Incremental routing-map refresh remained incomplete for collection '%s' "
                        "after %d retry attempt(s). Falling back to full refresh.",
                        collection_link,
                        incomplete_attempt_count,
                    )
                    current_previous_map = None
                    continue

                raise

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
        if routing_map is None:
            return []

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
            return []

        gen = get_smart_overlapping_ranges(partition_key_ranges)
        try:
            query_range = next(gen)
            while True:
                overlapping = PartitionKeyRangeCache.get_overlapping_ranges(
                    self, collection_link, [query_range], feed_options, **kwargs
                )
                query_range = gen.send(overlapping)
        except StopIteration as e:
            return e.value
