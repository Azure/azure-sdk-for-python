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

"""Shared (sync/async-agnostic) helpers for routing map provider logic.

This module contains the pure-logic pieces that are identical between the sync
and async ``PartitionKeyRangeCache`` / ``SmartRoutingMapProvider`` classes.
Extracting them here eliminates code duplication and ensures bug-fixes apply
to both code paths simultaneously.
"""

import logging
import random
from typing import Any, Dict, List, Optional, Tuple

from .. import _base, http_constants
from ..exceptions import CosmosHttpResponseError
from .collection_routing_map import (
    CollectionRoutingMap,
    _build_routing_map_from_ranges,
    _OverlapDetected,  # noqa: F401  # re-exported for provider modules and tests
    _GapDetected,  # noqa: F401  # re-exported for provider modules and tests
)
from . import routing_range
from .routing_range import (
    PKRange,
    PartitionKeyRange,
    _is_sorted_and_non_overlapping,
    _subtract_range,
)

logger = logging.getLogger(__name__)

PAGE_SIZE_CHANGE_FEED = "-1"  # Return all available changes

# Maximum retry attempts for transient full-load /pkranges inconsistencies
# (overlap OR gap) before surfacing a transient HTTP 503. Centralised here so
# the sync and async providers share one source of truth.
_TRANSIENT_SNAPSHOT_RETRY_MAX_ATTEMPTS = 3
# Initial backoff between inconsistency retries; doubles each attempt. With
# ``_TRANSIENT_SNAPSHOT_RETRY_MAX_ATTEMPTS = 3``, attempt 3 raises 503 before
# sleeping, so only the post-attempt-1 and post-attempt-2 backoffs are slept --
# deterministic worst case is the sum of the first two schedule entries
# (``_TRANSIENT_SNAPSHOT_RETRY_INITIAL_BACKOFF_SECONDS`` and that value
# doubled); expected wall time is half of that under full jitter.
_TRANSIENT_SNAPSHOT_RETRY_INITIAL_BACKOFF_SECONDS = 0.5


def _jittered_backoff(backoff_seconds: float) -> float:
    """Return a uniformly-jittered backoff in the range ``[0, backoff_seconds]``.

    Implements the "full jitter" strategy so concurrent retriers in different
    processes do not retry in lockstep against the same gateway node.

    :param float backoff_seconds: Deterministic upper bound for the backoff,
        in seconds. Must be non-negative.
    :return: A uniformly-distributed sleep value in ``[0, backoff_seconds]``.
    :rtype: float
    """
    return random.uniform(0, backoff_seconds)


def _handle_transient_snapshot_retry_decision(
    *,
    retry_attempt_count: int,
    collection_link: str,
    logger: logging.Logger,  # pylint: disable=redefined-outer-name
) -> float:
    """Decide what to do after the full-load builder reported a transient
    snapshot inconsistency (overlap or gap).

    Returns a jittered backoff for the caller to sleep before the next
    attempt; raises :class:`CosmosHttpResponseError` (HTTP 503) once
    ``_TRANSIENT_SNAPSHOT_RETRY_MAX_ATTEMPTS`` is reached. Under the default
    budget the final attempt raises 503 before sleeping, so only the first
    ``_TRANSIENT_SNAPSHOT_RETRY_MAX_ATTEMPTS - 1`` attempts produce a sleep
    (deterministic upper bounds doubling from
    ``_TRANSIENT_SNAPSHOT_RETRY_INITIAL_BACKOFF_SECONDS``). The caller
    performs the actual sleep (``time.sleep`` vs ``await asyncio.sleep``),
    which is the only line that differs between the sync and async
    providers.

    :keyword int retry_attempt_count: Attempts so far, including the one
        that just failed. Pass ``1`` after the first failure.
    :keyword str collection_link: Used in log messages and the 503 body.
    :keyword logging.Logger logger: Caller's module-level logger.
    :return: Jittered backoff seconds in ``[0, deterministic_upper_bound]``.
    :rtype: float
    :raises CosmosHttpResponseError: When the attempt budget is exhausted.
    """
    if retry_attempt_count >= _TRANSIENT_SNAPSHOT_RETRY_MAX_ATTEMPTS:
        logger.error(
            "Full-load routing-map fetch for collection '%s' detected a "
            "transient snapshot inconsistency (overlap or gap) on every "
            "one of %d attempt(s). Surfacing as transient HTTP 503 so the "
            "caller's retry policy can take over.",
            collection_link,
            retry_attempt_count,
        )
        raise CosmosHttpResponseError(
            status_code=http_constants.StatusCodes.SERVICE_UNAVAILABLE,
            message=(
                "Failed to build routing map for collection '{}': transient "
                "snapshot inconsistency (overlap or gap) persisted across {} "
                "full-load attempt(s). Surfaced as a retryable transient "
                "error so the upstream retry policy can take over."
            ).format(collection_link, retry_attempt_count),
        )

    deterministic_backoff = (
        _TRANSIENT_SNAPSHOT_RETRY_INITIAL_BACKOFF_SECONDS * (2 ** (retry_attempt_count - 1))
    )
    jittered_backoff = _jittered_backoff(deterministic_backoff)
    logger.warning(
        "Full-load routing-map fetch for collection '%s' detected a transient "
        "snapshot inconsistency (overlap or gap) (attempt %d/%d). Sleeping "
        "%.2fs (jittered from upper bound %.2fs) and retrying.",
        collection_link,
        retry_attempt_count,
        _TRANSIENT_SNAPSHOT_RETRY_MAX_ATTEMPTS,
        jittered_backoff,
        deterministic_backoff,
    )
    return jittered_backoff




def is_cache_unchanged_since_previous(
    collection_routing_map_by_item: Dict[str, CollectionRoutingMap],
    collection_id: str,
    previous_routing_map: Optional[CollectionRoutingMap],
) -> bool:
    """Check whether cached and previous maps belong to the same generation.

    This function only concerns itself with ETag comparison.  It returns
    ``False`` when there is no *previous_routing_map* or when the cache is
    empty.  Returning ``False`` for an empty cache is intentional -- this
    function's contract is strictly "are two existing maps equal?", not
    "does the cache need populating".  The caller handles the empty-cache
    case separately via its own ``is_initial_load`` check.

    :param dict collection_routing_map_by_item: The cache dictionary.
    :param str collection_id: The ID of the collection.
    :param previous_routing_map: The routing map that was used in the
        previous operation.
    :type previous_routing_map:
        ~azure.cosmos._routing.collection_routing_map.CollectionRoutingMap
        or None
    :return: ``True`` when both maps exist and have equal change-feed ETags.
    :rtype: bool
    """
    if not previous_routing_map:
        return False

    current_map = collection_routing_map_by_item.get(collection_id)
    if not current_map:
        return False

    return previous_routing_map.change_feed_etag == current_map.change_feed_etag




def prepare_fetch_options_and_headers(
    previous_routing_map: Optional[CollectionRoutingMap],
    feed_options: Optional[Dict[str, Any]],
    kwargs: Dict[str, Any],
) -> Dict[str, Any]:
    """Prepare sanitised feed options and headers for a PK-range fetch.

    This mutates *kwargs* in-place (sets ``headers``).

    :param previous_routing_map: The base routing map for incremental
        updates, or ``None`` for a full load.
    :type previous_routing_map:
        ~azure.cosmos._routing.collection_routing_map.CollectionRoutingMap
        or None
    :param dict feed_options: Raw feed options from the caller.
    :param dict kwargs: Keyword arguments (mutated -- ``headers`` is set).
    :return: The sanitised ``change_feed_options`` dict.
    :rtype: dict
    """
    change_feed_options = _base.format_pk_range_options(
        feed_options if feed_options is not None else {}
    )
    change_feed_options["_internal_pk_range_fetch"] = True

    headers = kwargs.get('headers', {}).copy()
    headers[http_constants.HttpHeaders.PageSize] = PAGE_SIZE_CHANGE_FEED
    headers[http_constants.HttpHeaders.AIM] = (
        http_constants.HttpHeaders.IncrementalFeedHeaderValue
    )

    if previous_routing_map and previous_routing_map.change_feed_etag:
        headers[http_constants.HttpHeaders.IfNoneMatch] = (
            previous_routing_map.change_feed_etag
        )
    else:
        headers.pop(http_constants.HttpHeaders.IfNoneMatch, None)

    kwargs['headers'] = headers
    return change_feed_options




def _resolve_endpoint(client: Any) -> str:
    """Return a cache key for ``client``'s endpoint.

    Falls back to ``__unknown_<id>__`` when ``client`` has no ``url_connection``
    so unknown/mocked clients are isolated rather than collapsed into a single
    shared cache entry.

    Centralized here so the sync (``routing_map_provider``) and async
    (``aio.routing_map_provider``) modules use exactly the same fallback shape
    — a divergence here would silently fragment the per-endpoint shared cache.

    :param client: The CosmosClient (or compatible) instance whose endpoint
        will be used as the shared-cache key.
    :type client: Any
    :returns: The endpoint URL string, or a per-instance fallback key when the
        client does not expose ``url_connection``.
    :rtype: str
    """
    try:
        return client.url_connection
    except AttributeError:
        return f"__unknown_{id(client)}__"


class _IncrementalMergeFailed(Exception):
    """Private exception type raised by :func:`process_fetched_ranges` when the
    incremental update cannot resolve all partition key ranges.

    The caller decides how to recover: retry the incremental fetch
    (if attempts remain) or fall back to a full routing-map refresh."""


def process_fetched_ranges(
    ranges: List[Dict[str, Any]],
    previous_routing_map: Optional[CollectionRoutingMap],
    collection_id: str,
    collection_link: str,
    new_etag: Optional[str],
) -> CollectionRoutingMap:
    """Turn raw PK-range results into a :class:`CollectionRoutingMap`.

    Handles both initial-load (when *previous_routing_map* is ``None``)
    and incremental-update paths.

    :param list ranges: The raw partition key range dicts returned by the service.
    :param previous_routing_map: The existing routing map for incremental updates,
        or ``None`` for initial load.
    :type previous_routing_map:
        ~azure.cosmos._routing.collection_routing_map.CollectionRoutingMap
        or None
    :param str collection_id: The ID of the collection.
    :param str collection_link: The link to the collection.
    :param str new_etag: The ETag from the change feed response, or ``None``.
    :return: The new/updated routing map.
    :rtype: ~azure.cosmos._routing.collection_routing_map.CollectionRoutingMap
    :raises _IncrementalMergeFailed: When the incremental path cannot
        resolve all ranges.  The caller catches this and either retries
        the incremental fetch or falls back to a full refresh.
    """
    if not previous_routing_map:
        # Initial load -- build the complete map.
        return _build_routing_map_from_ranges(
            ranges, collection_id, new_etag, collection_link, logger
        )

    if new_etag is None:
        logger.warning(
            "Incremental routing-map refresh for collection '%s' returned no ETag; "
            "preserving previous ETag '%s'.",
            collection_link,
            previous_routing_map.change_feed_etag,
        )

    # Incremental update -- preserve prior ETag if service omitted one.
    effective_etag = (
        new_etag
        if new_etag is not None
        else previous_routing_map.change_feed_etag
    )

    # Fast path for 304/empty incremental responses: keep the same map object
    # when topology and ETag are unchanged.
    if not ranges and effective_etag == previous_routing_map.change_feed_etag:
        return previous_routing_map

    # Incremental update -- merge deltas into the existing map.
    # Resolve parent chains transitively within this single delta so cascading
    # splits (A->B+C and B->D+E in one payload) can be merged incrementally.
    range_tuples: List[Tuple[Any, Any]] = []
    known_range_info_by_id = {
        pkr_id: pkr_tuple[1]
        for pkr_id, pkr_tuple in previous_routing_map._rangeById.items()  # pylint: disable=protected-access
    }
    unresolved = list(ranges)
    while unresolved:
        progress_made = False
        next_unresolved: List[Dict[str, Any]] = []
        for r in unresolved:
            parents = r.get(PartitionKeyRange.Parents) or []
            range_info = None
            if not parents:
                range_info = known_range_info_by_id.get(r.get(PartitionKeyRange.Id))
            for parent_id in parents:
                if parent_id in known_range_info_by_id:
                    range_info = known_range_info_by_id[parent_id]
                    break

            if range_info is None:
                next_unresolved.append(r)
                continue

            range_tuples.append((PKRange.from_dict(r), range_info))
            known_range_info_by_id[r[PartitionKeyRange.Id]] = range_info
            progress_made = True

        if not next_unresolved:
            break

        if not progress_made:
            first_unresolved = next_unresolved[0]
            logger.warning(
                "Incremental update failed: None of the parent ranges %s found in routing map "
                "for collection '%s' (range id '%s'). Falling back to full refresh.",
                first_unresolved.get(PartitionKeyRange.Parents) or [],
                collection_link,
                first_unresolved.get(PartitionKeyRange.Id),
            )
            raise _IncrementalMergeFailed()

        unresolved = next_unresolved

    try:
        result = previous_routing_map.try_combine(range_tuples, effective_etag)
    except ValueError as overlap_error:
        # Convert the overlap ``ValueError`` from ``try_combine`` into
        # ``_IncrementalMergeFailed`` so the caller retries the incremental
        # fetch and ultimately falls back to the full-load path (which has
        # its own ``_OverlapDetected`` retry + 503 safety net). Narrow to
        # the literal ``"Ranges overlap"`` prefix (kept stable in
        # ``is_complete_set_of_range`` and pinned by the regression tests)
        # so any future unrelated ``ValueError`` surfaces as a real bug.
        if not str(overlap_error).startswith("Ranges overlap"):
            raise
        logger.warning(
            "Incremental merge for collection '%s' produced overlapping ranges: %s. "
            "Converting to _IncrementalMergeFailed so the caller retries / "
            "falls back to a full refresh.",
            collection_link, str(overlap_error),
        )
        raise _IncrementalMergeFailed() from overlap_error
    if not result:
        logger.warning(
            "Incremental merge resulted in incomplete routing map for "
            "collection '%s'. Falling back to full refresh.",
            collection_link,
        )
        raise _IncrementalMergeFailed()

    return result



def determine_refresh_action(
    collection_routing_map_by_item: Dict[str, CollectionRoutingMap],
    collection_id: str,
    force_refresh: bool,
    previous_routing_map: Optional[CollectionRoutingMap],
) -> Tuple[bool, Optional[CollectionRoutingMap]]:
    """Decide whether a fetch is needed and which base map to use.

    Called **inside** the per-collection lock.

    :param dict collection_routing_map_by_item: The cache dictionary mapping
        collection IDs to their routing maps.
    :param str collection_id: The ID of the collection.
    :param bool force_refresh: Whether to force a refresh of the routing map.
    :param previous_routing_map: The routing map from the previous operation,
        used to detect staleness, or ``None``.
    :type previous_routing_map:
        ~azure.cosmos._routing.collection_routing_map.CollectionRoutingMap
        or None
    :return: A tuple of ``(should_fetch, base_routing_map)``.
    :rtype: tuple[bool, CollectionRoutingMap | None]
    """
    existing_routing_map = collection_routing_map_by_item.get(collection_id)

    is_initial_load = not existing_routing_map
    should_refresh_unchanged_cache = force_refresh and is_cache_unchanged_since_previous(
        collection_routing_map_by_item, collection_id, previous_routing_map
    )
    # Force-refresh callers may not have a previous map (for example, first 410 on
    # a collection when context only includes collection_link). Still issue a
    # targeted fetch so this does not degrade into a no-op.
    should_force_refresh_without_previous = (
        force_refresh and existing_routing_map is not None and previous_routing_map is None
    )

    if not (is_initial_load or should_refresh_unchanged_cache or should_force_refresh_without_previous):
        return False, None

    if should_refresh_unchanged_cache and previous_routing_map:
        base_routing_map: Optional[CollectionRoutingMap] = previous_routing_map
    else:
        base_routing_map = existing_routing_map

    return True, base_routing_map



def get_smart_overlapping_ranges(partition_key_ranges):
    """Core generator for :class:`SmartRoutingMapProvider.get_overlapping_ranges`.

    This is a *generator* that drives the iteration logic, yielding each
    ``queryRange`` to the caller who performs the (possibly async) lookup
    and sends the result back via ``.send()``.

    Protocol::

        gen = get_smart_overlapping_ranges(partition_key_ranges)
        query_range = next(gen)          # first range to look up
        while True:
            result = do_lookup(query_range)  # sync or await
            query_range = gen.send(result)   # next range (or StopIteration)
        # StopIteration.value is the final target_partition_key_ranges list

    The caller **must** handle the empty-input case before calling this
    function, because a generator function in Python always returns a
    generator object (never a plain list).

    :param list partition_key_ranges: Sorted, non-overlapping list of ranges.
        Must not be empty.
    :return: A generator that yields query ranges and ultimately returns
        the list of target partition key ranges via ``StopIteration.value``.
    :rtype: list
    :raises ValueError: If the ranges are not sorted and non-overlapping.
    """

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
                queryRange = _subtract_range(
                    currentProvidedRange, target_partition_key_ranges[-1]
                )
            else:
                queryRange = currentProvidedRange

            # Yield the queryRange to the caller; receive overlappingRanges back.
            overlappingRanges = yield queryRange

            assert overlappingRanges, (
                "code bug: returned overlapping ranges for "
                "queryRange {} is empty".format(queryRange)
            )
            target_partition_key_ranges.extend(overlappingRanges)

            lastKnownTargetRange = routing_range.Range.PartitionKeyRangeToRange(
                target_partition_key_ranges[-1]
            )
            assert currentProvidedRange.max <= lastKnownTargetRange.max, (
                "code bug: returned overlapping ranges {} does not contain "
                "the requested range {}".format(overlappingRanges, queryRange)
            )

            currentProvidedRange = next(it)

            while currentProvidedRange.max <= lastKnownTargetRange.max:
                currentProvidedRange = next(it)
    except StopIteration:
        pass

    return target_partition_key_ranges
