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
import time
import logging
from typing import Dict, Any, Optional, List, TYPE_CHECKING
from azure.core.utils import CaseInsensitiveDict
from .. import _base, http_constants
from .collection_routing_map import CollectionRoutingMap
from ..exceptions import CosmosHttpResponseError
from ._routing_map_provider_common import (
    _resolve_endpoint,
    prepare_fetch_options_and_headers,
    process_fetched_ranges,
    is_cache_unchanged_since_previous,
    determine_refresh_action,
    get_smart_overlapping_ranges,
    _IncrementalMergeFailed,
    _OverlapDetected,
    _GapDetected,
    _handle_transient_snapshot_retry_decision,
    _DrainPageDecision,
    evaluate_drain_page,
)

if TYPE_CHECKING:
    from .._cosmos_client_connection import CosmosClientConnection

# Module-level shared state, keyed by endpoint URL. All four dicts and the
# refcount are mutated only while holding ``_shared_cache_lock``. Sharing across
# every CosmosClient that targets the same endpoint is what eliminates the
# per-client duplicate copies of the routing map (the memory win driving this
# change), and what lets concurrent readers single-flight a single refresh.

# endpoint -> { collection_id -> CollectionRoutingMap }. The actual cached
# routing maps. The inner dict is shared by every client for that endpoint, so
# a routing-map populated by one client is immediately visible to all others.
_shared_routing_map_cache: dict = {}

# endpoint -> { collection_id -> threading.Lock }. Per-collection refresh lock.
# Concurrent calls to refresh the routing map for the same (endpoint, collection)
# block on this lock so only one of them issues the network call; the rest read
# the freshly-populated cache after they wake up.
_shared_collection_locks: Dict[str, Dict[str, threading.Lock]] = {}

# endpoint -> threading.Lock. Guards the creation of new entries in the inner
# dict of ``_shared_collection_locks``. Without this, two threads racing on a
# brand-new collection_id could each create a different Lock object and defeat
# the single-flight invariant (each thread would wait on its own lock and both
# would fall through to issue the network refresh).
_shared_locks_locks: Dict[str, threading.Lock] = {}

# endpoint -> int. Number of live ``PartitionKeyRangeCache`` instances using
# this endpoint. Incremented on construction and decremented in ``release``
# (called from ``CosmosClient.__exit__`` / ``close`` / ``__del__``). When the
# count hits zero we drop the entry from all four dicts so an idle endpoint
# does not pin memory forever. ``clear_cache`` does NOT touch this count — it
# only wipes routing-map contents.
_shared_cache_refcounts: Dict[str, int] = {}

# Process-wide lock guarding the four dicts above. The async module
# (``aio/routing_map_provider.py``) has its own independent set, so sync
# and async clients targeting the same endpoint do not share state.
#
# Reentrant (``RLock``) to tolerate same-thread re-entry (for example
# ``__del__`` -> ``release()``) if future refactors add allocation points
# inside this critical section.
_shared_cache_lock = threading.RLock()


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
        self._endpoint = _resolve_endpoint(client)
        self._released = False

        # Share routing map cache, per-collection locks, and the lock that
        # protects lock creation across clients for this endpoint.
        # Defaults are allocated before locking so this block stays dict-only.
        new_routing_map: Dict[str, CollectionRoutingMap] = {}
        new_collection_locks: Dict[str, threading.Lock] = {}
        new_locks_lock = threading.Lock()

        with _shared_cache_lock:
            # ``setdefault`` preserves existing endpoint entries.
            routing_map = _shared_routing_map_cache.setdefault(
                self._endpoint, new_routing_map)
            collection_locks = _shared_collection_locks.setdefault(
                self._endpoint, new_collection_locks)
            locks_lock = _shared_locks_locks.setdefault(
                self._endpoint, new_locks_lock)
            # Preserve existing refcount instead of reinitializing.
            _shared_cache_refcounts[self._endpoint] = (
                _shared_cache_refcounts.get(self._endpoint, 0) + 1
            )

            self._collection_routing_map_by_item = routing_map
            self._collection_locks: Dict[str, threading.Lock] = collection_locks
            self._locks_lock: threading.Lock = locks_lock

    def clear_cache(self):
        """Clear the shared routing map cache for this endpoint.

        Uses in-place ``.clear()`` on the routing-map dict to preserve all
        client references to the same dict object, so concurrent clients
        sharing the endpoint continue to share a single cache instance.

        The per-collection locks dict is intentionally **not** cleared here:
        an in-flight ``_fetch_routing_map`` caller holds one of those locks
        and will write its result into the (now-empty) shared cache when it
        completes. Keeping the lock in place ensures that any concurrent
        arrival serialises behind the in-flight refresh (single-flight
        invariant) instead of racing it with a fresh lock. The locks dict
        is evicted in ``release()`` once the endpoint refcount hits zero.
        """
        with _shared_cache_lock:
            if self._endpoint in _shared_routing_map_cache:
                _shared_routing_map_cache[self._endpoint].clear()

    def release(self) -> None:
        """Decrement the per-endpoint refcount and evict shared state at zero.

        Safe to call multiple times concurrently. Best-effort: never raises.

        The ``_released`` check-and-set is performed *inside* the shared
        cache lock to close the TOCTOU window between two concurrent callers
        (e.g. ``CosmosClient.__exit__`` racing the GC's ``__del__``). Without
        the lock, both callers could pass the early-return guard before
        either set the flag, then both would decrement the refcount.
        """
        endpoint = self._endpoint
        try:
            with _shared_cache_lock:
                if self._released:
                    return
                self._released = True
                count = _shared_cache_refcounts.get(endpoint, 0) - 1
                if count <= 0:
                    _shared_cache_refcounts.pop(endpoint, None)
                    _shared_routing_map_cache.pop(endpoint, None)
                    _shared_collection_locks.pop(endpoint, None)
                    _shared_locks_locks.pop(endpoint, None)
                else:
                    _shared_cache_refcounts[endpoint] = count
        except Exception:  # pylint: disable=broad-except
            # release() may be called from __del__ during interpreter shutdown
            # where module globals may already be torn down.
            pass

    def __del__(self):
        # Defensive fallback in case the owning client teardown path didn't
        # call release(). Must never raise.
        try:
            self.release()
        except Exception:  # pylint: disable=broad-except
            pass

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
                # ``_fetch_routing_map`` always returns a populated
                # ``CollectionRoutingMap`` on success and raises otherwise --
                # No defensive None-check needed; one
                # would only mask a future regression by silently leaving
                # the cache empty instead of surfacing the failure.
                self._collection_routing_map_by_item[collection_id] = new_routing_map

            return self._collection_routing_map_by_item.get(collection_id)


    # pylint: disable=too-many-statements,too-many-locals
    def _fetch_routing_map(
            self,
            collection_link: str,
            collection_id: str,
            previous_routing_map: Optional[CollectionRoutingMap],
            feed_options: Optional[Dict[str, Any]],
            **kwargs
    ) -> CollectionRoutingMap:

        """Fetches or updates the routing map using an incremental change feed.

        This method handles both the initial loading of a collection's routing
        map and subsequent incremental updates. If a previous_routing_map is
        provided, it fetches only the changes since that map was generated.
        Otherwise, it performs a full read of all partition key ranges. In case
        of inconsistencies during an incremental update, it automatically falls
        back to a full refresh.

        Always returns a populated :class:`CollectionRoutingMap` on success.
        Failure modes raise an exception rather than returning ``None``:
        ``CosmosHttpResponseError`` for the underlying network call (including
        the transient HTTP 503 raised once the snapshot-inconsistency retry
        budget is exhausted), or the internal ``_IncrementalMergeFailed``
        signal when the incremental-merge path cannot make progress and there
        is no previous map to fall back on.

        :param str collection_link: The link to the collection.
        :param str collection_id: The unique identifier of the collection.
        :param previous_routing_map: The routing map to be updated. If None, a full load is performed.
        :type previous_routing_map: azure.cosmos.routing.collection_routing_map.CollectionRoutingMap
        :param feed_options: Options for the change feed request.
        :type feed_options: dict or None
        :return: The new or updated CollectionRoutingMap.
        :rtype: azure.cosmos.routing.collection_routing_map.CollectionRoutingMap
        :raises CosmosHttpResponseError: If the underlying ``/pkranges`` fetch
            fails, or if every snapshot-inconsistency retry exhausts the
            budget (surfaced as HTTP 503 so the upstream retry policy can
            take over).
        """
        current_previous_map = previous_routing_map
        incomplete_attempt_count = 0
        inconsistency_attempt_count = 0

        while True:
            ranges: List[Dict[str, Any]] = []
            # Start the change-feed drain at the previous map's etag (if any).
            # On subsequent drain pages we advance this with the etag returned
            # for the previous page so the service returns "what's new since X"
            # until it eventually responds with 304 / no new ranges, mirroring
            # the .NET and Go SDK behaviour and the async provider.
            current_if_none_match = (
                current_previous_map.change_feed_etag if current_previous_map else None
            )
            new_etag = current_if_none_match
            # Track whether the service ever surfaced an ETag header during this
            # drain attempt. If it never did, we want ``process_fetched_ranges``
            # to surface the "no ETag" observability warning rather than
            # silently treating ``current_if_none_match`` as the fresh etag.
            seen_any_etag = False

            # Hoist: ``prepare_fetch_options_and_headers`` is loop-invariant
            # for this drain attempt -- ``change_feed_options`` depends only on
            # ``feed_options`` and the headers it builds depend only on
            # ``current_previous_map.change_feed_etag``, neither of which
            # change inside the inner drain loop. Compute them once here; the
            # only per-page mutation is the ``If-None-Match`` override below.
            base_kwargs_for_headers: Dict[str, Any] = dict(kwargs)
            change_feed_options = prepare_fetch_options_and_headers(
                current_previous_map, feed_options, base_kwargs_for_headers
            )
            base_headers: Dict[str, Any] = base_kwargs_for_headers['headers']

            while True:
                request_kwargs = dict(kwargs)
                # Shallow-copy ``base_headers`` so the per-iter
                # ``If-None-Match`` override does not bleed across iterations.
                request_kwargs['headers'] = dict(base_headers)
                response_headers: CaseInsensitiveDict = CaseInsensitiveDict()
                request_kwargs['_internal_response_headers_capture'] = response_headers
                # Sidecar list -- populated by _Request with the raw wire
                # status. Lets us terminate on literal 304 (matching peer
                # SDKs) instead of inferring it from an empty ItemPaged page.
                status_capture: List[Optional[int]] = [None]
                request_kwargs['_internal_response_status_capture'] = status_capture

                # Override If-None-Match with the running etag from the drain
                # so each page advances. ``prepare_fetch_options_and_headers``
                # only sets it from ``current_previous_map.change_feed_etag``
                # which never advances during this drain.
                drain_headers = request_kwargs['headers']
                if current_if_none_match:
                    drain_headers[http_constants.HttpHeaders.IfNoneMatch] = current_if_none_match
                else:
                    drain_headers.pop(http_constants.HttpHeaders.IfNoneMatch, None)

                page_ranges: List[Dict[str, Any]] = []
                try:
                    pk_range_generator = self._document_client._ReadPartitionKeyRanges(
                        collection_link,
                        change_feed_options,
                        **request_kwargs
                    )
                    page_ranges.extend(list(pk_range_generator))
                except CosmosHttpResponseError as e:
                    logger.error(  # pylint: disable=do-not-log-exceptions-if-not-debug,do-not-log-raised-errors
                        "Failed to read partition key ranges for collection '%s': %s",
                        collection_link, e)
                    raise

                ranges.extend(page_ranges)

                decision, new_etag, current_if_none_match, seen_any_etag = evaluate_drain_page(
                    page_new_etag=response_headers.get(http_constants.HttpHeaders.ETag),
                    current_if_none_match=current_if_none_match,
                    new_etag=new_etag,
                    seen_any_etag=seen_any_etag,
                    status_code=status_capture[0],
                )
                if decision == _DrainPageDecision.STOP_DRAINED:
                    break

            try:
                effective_new_etag = new_etag if seen_any_etag else None
                return process_fetched_ranges(
                    ranges, current_previous_map, collection_id, collection_link, effective_new_etag
                )
            except _IncrementalMergeFailed:
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
            except (_OverlapDetected, _GapDetected):
                # Reset to ``None`` so the next attempt runs a full refresh
                # instead of merging onto the same inconsistent base.
                inconsistency_attempt_count += 1
                backoff = _handle_transient_snapshot_retry_decision(
                    retry_attempt_count=inconsistency_attempt_count,
                    collection_link=collection_link,
                    logger=logger,
                )
                time.sleep(backoff)
                current_previous_map = None
                continue

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
