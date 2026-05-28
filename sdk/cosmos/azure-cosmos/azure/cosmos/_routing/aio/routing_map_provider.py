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
import threading
from typing import Callable, Dict, Any, NamedTuple, Optional, List, TYPE_CHECKING
from azure.core.utils import CaseInsensitiveDict
from ... import _base, http_constants
from ..collection_routing_map import CollectionRoutingMap
from ...exceptions import CosmosHttpResponseError
from .._routing_map_provider_common import (
    _resolve_endpoint,
    prepare_fetch_options_and_headers,
    process_fetched_ranges,
    is_cache_unchanged_since_previous,
    determine_refresh_action,
    get_smart_overlapping_ranges,
    _IncrementalMergeFailed,
)


if TYPE_CHECKING:
    from ...aio._cosmos_client_connection_async import CosmosClientConnection

# Module-level state keyed by endpoint. Access is guarded by
# ``_shared_cache_lock``.

# endpoint -> { collection_id -> CollectionRoutingMap }. The actual cached
# routing maps. The inner dict is shared by every client for that endpoint, so
# a routing-map populated by one client is immediately visible to all others.
_shared_routing_map_cache: dict = {}

# endpoint -> { (loop_id, collection_id) -> asyncio.Lock }. Locks are scoped
# per loop because ``asyncio.Lock`` objects are loop-bound.
_shared_collection_locks: Dict[str, Dict[tuple, asyncio.Lock]] = {}

# endpoint -> threading.Lock. Guards creation of entries in
# ``_shared_collection_locks``.
_shared_locks_locks: Dict[str, threading.Lock] = {}

# endpoint -> { (loop_id, collection_id) -> _InflightEntry }. Tracks one
# in-flight fetch per (loop, collection) and joined hooks.
_shared_inflight_fetches: Dict[str, Dict[tuple, "_InflightEntry"]] = {}

# endpoint -> int. Number of live async ``PartitionKeyRangeCache`` instances.
# When this reaches zero, shared endpoint state is evicted.
_shared_cache_refcounts: Dict[str, int] = {}

# Process-wide lock for this async module's shared dicts. Sync and async
# routing providers keep separate shared state.
_shared_cache_lock = threading.Lock()


# pylint: disable=protected-access

logger = logging.getLogger(__name__)
# Number of extra incremental attempts after an incomplete incremental merge
# before falling back to a full routing-map refresh.
_INCOMPLETE_ROUTING_MAP_MAX_RETRIES = 1


def _consume_task_exception(task: "asyncio.Task") -> None:
    """Consume task exceptions to avoid noisy asyncio warnings."""
    if task.cancelled():
        return
    try:
        exc = task.exception()
    except asyncio.CancelledError:
        return
    if exc is not None:
        logger.debug(
            "Coalesced PK-range fetch raised after all awaiters unwound: %s",
            exc,
        )


class _InflightEntry(NamedTuple):
    """Per-(loop, collection) value stored in ``_shared_inflight_fetches``.

    Stores the in-flight task and joined ``raw_response_hook`` callbacks.
    """
    task: asyncio.Task
    joined_hooks: List[Optional[Callable[..., None]]]


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

        # Share routing map cache, per-collection asyncio locks, the
        # per-endpoint meta-lock that guards the per-collection-lock dict,
        # and the in-flight fetch-task dict across all clients with the same
        # endpoint. Refcount lets us evict the entry when the last sharing
        # client releases it (see ``release``).
        with _shared_cache_lock:
            if self._endpoint not in _shared_routing_map_cache:
                _shared_routing_map_cache[self._endpoint] = {}
                _shared_collection_locks[self._endpoint] = {}
                _shared_locks_locks[self._endpoint] = threading.Lock()
                _shared_inflight_fetches[self._endpoint] = {}
                _shared_cache_refcounts[self._endpoint] = 0
            _shared_cache_refcounts[self._endpoint] += 1
            self._collection_routing_map_by_item = _shared_routing_map_cache[self._endpoint]
            self._collection_locks: Dict[tuple, asyncio.Lock] = _shared_collection_locks[self._endpoint]
            self._locks_lock: threading.Lock = _shared_locks_locks[self._endpoint]
            self._inflight_fetches: Dict[tuple, _InflightEntry] = _shared_inflight_fetches[self._endpoint]

    def clear_cache(self):
        """Clear the shared routing map cache for this endpoint.

        Uses in-place ``.clear()`` on the routing-map dict to preserve all
        client references to the same dict object, so concurrent clients
        sharing the endpoint continue to share a single cache instance.

        The per-collection locks dict and the in-flight fetch-task dict are
        intentionally **not** cleared here. A fetch task scheduled before
        this call keeps a reference to the (now-empty) cache dict and will
        publish its result into it when it completes; any concurrent arrival
        meanwhile joins that same task instead of racing it. Both auxiliary
        dicts are evicted in ``release()`` once the endpoint refcount hits
        zero.
        """
        with _shared_cache_lock:
            if self._endpoint in _shared_routing_map_cache:
                _shared_routing_map_cache[self._endpoint].clear()

    def release(self) -> None:
        """Decrease endpoint refcount and evict shared state at zero."""
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
                    inflight = _shared_inflight_fetches.pop(endpoint, None)
                    if inflight:
                        # Best-effort cancellation of leftover in-flight tasks.
                        for entry in inflight.values():
                            if not entry.task.done():
                                entry.task.cancel()
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

    async def _get_lock_for_collection(self, collection_id: str) -> asyncio.Lock:
        """Safely gets or creates a lock for a given (loop, collection) pair.

        Scoped to the running event loop so the returned ``asyncio.Lock`` is
        always bound to the loop that will await it — see the comment on
        ``_shared_collection_locks`` for the loop-binding rationale.

        :param str collection_id: The ID of the collection.
        :return: An asyncio.Lock specific to the (loop, collection) pair.
        :rtype: asyncio.Lock
        """
        key = (id(asyncio.get_running_loop()), collection_id)
        with self._locks_lock:
            lock = self._collection_locks.get(key)
            if lock is None:
                lock = asyncio.Lock()
                self._collection_locks[key] = lock
            return lock

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

    async def get_overlapping_ranges(
            self, collection_link, partition_key_ranges,
            feed_options: Optional[Dict[str, Any]] = None, **kwargs):
        """Efficiently gets overlapping ranges for a collection.

        :param str collection_link: The link to the collection.
        :param list partition_key_ranges: A list of sorted, non-overlapping ranges to find overlaps for.
        :param Optional[Dict[str, Any]] feed_options: Optional query options used when fetching the routing map.
        :return: A list of overlapping partition key ranges from the collection.
        :rtype: list
        """

        if not partition_key_ranges:
            return []  # Return empty list directly instead of delegating to parent

        routing_map = await self.get_routing_map(collection_link, feed_options, **kwargs)

        if routing_map is None:
            return []

        ranges = routing_map.get_overlapping_ranges(partition_key_ranges)
        return ranges

    # pylint: disable=invalid-name
    async def get_routing_map(
            self,
            collection_link: str,
            feed_options: Optional[Dict[str, Any]],
            force_refresh: bool = False,
            previous_routing_map: Optional[CollectionRoutingMap] = None,
            **kwargs: Any
    ) -> Optional[CollectionRoutingMap]:
        """Gets or refreshes the routing map for a collection.

        Concurrent callers that arrive while a fetch is already in flight for
        the same collection join that fetch via ``asyncio.shield`` rather than
        issuing their own network round trip. The fetch task owns the cache
        write, so the publish completes even if every awaiting caller is
        cancelled (for example by ``asyncio.wait_for``) before the fetch
        returns. The next caller — whether the original caller retrying or a
        new one — finds the cache populated.

        :param str collection_link: The link to the collection.
        :param Optional[Dict[str, Any]] feed_options: Optional query options.
        :param bool force_refresh: If True, forces a refresh of the routing map.
        :param Optional[CollectionRoutingMap] previous_routing_map: The last known routing map,
            used for incremental updates.
        :return: The updated or cached CollectionRoutingMap, or None if it couldn't be retrieved.
        :rtype: Optional[CollectionRoutingMap]
        """
        collection_id = _base.GetResourceIdOrFullNameFromLink(collection_link)

        # Fast path: cache hit without acquiring any lock.
        if not force_refresh:
            cached_map = self._collection_routing_map_by_item.get(collection_id)
            if cached_map:
                return cached_map

        fetch_task = await self._register_or_join_inflight_fetch(
            collection_id,
            collection_link,
            feed_options,
            force_refresh,
            previous_routing_map,
            kwargs,
        )

        if fetch_task is not None:
            # ``shield`` ensures our cancellation only unwinds *this* awaiter;
            # the underlying task keeps running on the event loop and the
            # cache write inside the task body still happens. Other waiters
            # (and any subsequent caller hitting the now-populated cache) are
            # unaffected by our cancellation.
            fetched_map = await asyncio.shield(fetch_task)
            # Return the task's result directly instead of re-reading from
            # the cache dict. Between the task completing and this line
            # running, any other ready coroutine can execute — including
            # ``clear_cache()`` from a concurrent retry path — which would
            # empty the dict and leave us returning ``None`` despite the
            # fetch having just succeeded. Using the task's return value
            # sidesteps that window entirely. Matches the
            # ``AsyncCacheNonBlocking`` pattern in the Java/.NET SDKs.
            if fetched_map is not None:
                return fetched_map

        return self._collection_routing_map_by_item.get(collection_id)

    async def _register_or_join_inflight_fetch(
            self,
            collection_id: str,
            collection_link: str,
            feed_options: Optional[Dict[str, Any]],
            force_refresh: bool,
            previous_routing_map: Optional[CollectionRoutingMap],
            fetch_kwargs: Dict[str, Any],
    ) -> Optional[asyncio.Task]:
        """Return the in-flight fetch task for this collection, creating one if needed.

        Holding the per-collection lock for just the check-or-create window
        (no network I/O inside the lock) keeps the critical section small.
        The returned task may be one this call just scheduled or one a
        concurrent caller scheduled moments earlier — either way the caller
        should await it through ``asyncio.shield``.

        When a new task is created, this method wraps the originator's
        ``raw_response_hook`` and fans out callbacks to joined callers.

        :param str collection_id: The resolved collection identifier used as the cache key.
        :param str collection_link: The link to the collection.
        :param Optional[Dict[str, Any]] feed_options: Optional query options.
        :param bool force_refresh: Whether the caller asked for a refresh.
        :param Optional[CollectionRoutingMap] previous_routing_map: The caller's last
            observed routing map, used by the refresh-decision helper.
        :param Dict[str, Any] fetch_kwargs: Pipeline kwargs forwarded to the fetch.
        :return: A running ``asyncio.Task`` to await, or ``None`` if no fetch
            is needed (cache was populated by a concurrent caller after the
            fast-path check).
        :rtype: Optional[asyncio.Task]
        """
        inflight_key = (id(asyncio.get_running_loop()), collection_id)
        collection_lock = await self._get_lock_for_collection(collection_id)
        async with collection_lock:
            existing_entry = self._inflight_fetches.get(inflight_key)
            if existing_entry is not None:
                if not existing_entry.task.done():
                    # Join in-flight fetch and register joiner hook if present.
                    joiner_hook = fetch_kwargs.get("raw_response_hook")
                    if joiner_hook is not None:
                        existing_entry.joined_hooks.append(joiner_hook)
                    return existing_entry.task
                # Drop stale completed entry and start a new fetch.
                self._inflight_fetches.pop(inflight_key, None)

            should_fetch, base_routing_map = determine_refresh_action(
                self._collection_routing_map_by_item,
                collection_id,
                force_refresh,
                previous_routing_map,
            )
            if not should_fetch:
                return None

            # Install one shared raw_response_hook that fans out to every
            # caller joined to this fetch. Only one network call happens,
            # so there is only one place hooks can fire; we replay that
            # single response to the originator's hook and to each joiner's
            # hook. Hook exceptions are logged and isolated -- a bad hook
            # in one caller cannot prevent the cache update for the other
            # callers sharing this fetch.
            wrapped_fetch_kwargs = dict(fetch_kwargs)
            originator_hook = wrapped_fetch_kwargs.pop("raw_response_hook", None)
            joined_hooks: List[Optional[Callable[..., None]]] = []

            def _hook_fan_out(response: Any) -> None:
                """Replay the shared response to every caller's raw_response_hook.

                Fires the originator's hook first, then each joiner's hook
                in join order. Exceptions from any hook are logged at
                WARNING with ``exc_info`` and swallowed, so one caller's
                buggy hook cannot break the fetch outcome for the others
                that joined the same network call.
                """
                # Originator's hook runs first so its ordering matches the
                # non-coalesced path where the originator's hook was the
                # only one installed.
                if originator_hook is not None:
                    try:
                        originator_hook(response)
                    except Exception:  # pylint: disable=broad-except
                        logger.warning(
                            "raw_response_hook (originator) raised during "
                            "coalesced PK-range fetch for collection '%s'",
                            collection_link,
                            exc_info=True,
                        )
                # Joiners run in the order they registered. ``list(...)``
                # snapshots the list so a hook that itself triggers another
                # join cannot mutate what we are iterating.
                for joiner_hook in list(joined_hooks):
                    if joiner_hook is None:
                        continue
                    try:
                        joiner_hook(response)
                    except Exception:  # pylint: disable=broad-except
                        logger.warning(
                            "raw_response_hook (joiner) raised during "
                            "coalesced PK-range fetch for collection '%s'",
                            collection_link,
                            exc_info=True,
                        )

            wrapped_fetch_kwargs["raw_response_hook"] = _hook_fan_out

            new_task = asyncio.create_task(
                self._fetch_and_publish(
                    collection_id,
                    collection_link,
                    base_routing_map,
                    feed_options,
                    inflight_key,
                    wrapped_fetch_kwargs,
                )
            )
            # Consume task exceptions so asyncio does not log unretrieved errors.
            new_task.add_done_callback(_consume_task_exception)
            self._inflight_fetches[inflight_key] = _InflightEntry(
                task=new_task,
                joined_hooks=joined_hooks,
            )
            return new_task

    async def _fetch_and_publish(
            self,
            collection_id: str,
            collection_link: str,
            base_routing_map: Optional[CollectionRoutingMap],
            feed_options: Optional[Dict[str, Any]],
            inflight_key: tuple,
            fetch_kwargs: Dict[str, Any],
    ) -> Optional[CollectionRoutingMap]:
        """Run ``_fetch_routing_map`` and publish its result, then free the in-flight slot.

        The cache assignment lives inside this task body so a caller's
        cancellation while awaiting the task cannot interrupt the publish.
        The ``finally`` block always frees the in-flight slot — on success,
        on a fetch error, or on cancellation — so the next caller is free to
        schedule a fresh attempt.

        :param str collection_id: The resolved collection identifier used as the cache key.
        :param str collection_link: The link to the collection.
        :param Optional[CollectionRoutingMap] base_routing_map: The base routing map
            for incremental updates, or ``None`` for a full load.
        :param Optional[Dict[str, Any]] feed_options: Optional query options.
        :param tuple inflight_key: The ``(loop_id, collection_id)`` key into the in-flight dict.
        :param Dict[str, Any] fetch_kwargs: Pipeline kwargs forwarded to the fetch.
        :return: The new routing map, or ``None`` if the fetch produced nothing.
        :rtype: Optional[CollectionRoutingMap]
        """
        try:
            new_routing_map = await self._fetch_routing_map(
                collection_link,
                collection_id,
                base_routing_map,
                feed_options,
                **fetch_kwargs,
            )

            if new_routing_map:
                self._collection_routing_map_by_item[collection_id] = new_routing_map

            return new_routing_map
        finally:
            # ``dict.pop(key, default)`` is a single C-level operation under
            # the GIL, so this cleanup is atomic and needs no explicit lock.
            # The ``None`` default makes it tolerant of the key already being
            # gone. Runs on success, on fetch error, and on cancellation
            # alike, so the next caller can register a fresh fetch
            # immediately.
            self._inflight_fetches.pop(inflight_key, None)


    async def _fetch_routing_map(
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
        :param str collection_id: The ID of the collection.
        :param previous_routing_map: The last known routing map for incremental updates.
        :type previous_routing_map: azure.cosmos.routing.collection_routing_map.CollectionRoutingMap or None
        :param feed_options: Options for the change feed request.
        :type feed_options: dict or None
        :return: The updated or newly created CollectionRoutingMap, or None if the update fails.
        :rtype: azure.cosmos.routing.collection_routing_map.CollectionRoutingMap or None
        :raises CosmosHttpResponseError: If the underlying request to fetch ranges fails.
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
                async for item in pk_range_generator:
                    ranges.append(item)

            except CosmosHttpResponseError as e:
                logger.error(  # pylint: disable=do-not-log-exceptions-if-not-debug,do-not-log-raised-errors
                    "Failed to read partition key ranges for collection '%s': %s", collection_link, e)
                raise

            new_etag = response_headers.get(http_constants.HttpHeaders.ETag)

            try:
                return process_fetched_ranges(
                    ranges, current_previous_map, collection_id, collection_link, new_etag
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

    async def get_range_by_partition_key_range_id(
            self,
            collection_link: str,
            partition_key_range_id: str,
            feed_options: Dict[str, Any],
            **kwargs: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        routing_map = await self.get_routing_map(
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

    async def get_overlapping_ranges(
            self, collection_link, partition_key_ranges,
            feed_options: Optional[Dict[str, Any]] = None, **kwargs):
        if not partition_key_ranges:
            return []

        gen = get_smart_overlapping_ranges(partition_key_ranges)
        try:
            query_range = next(gen)
            while True:
                overlapping = await PartitionKeyRangeCache.get_overlapping_ranges(
                    self, collection_link, [query_range], feed_options, **kwargs
                )
                query_range = gen.send(overlapping)
        except StopIteration as e:
            return e.value
