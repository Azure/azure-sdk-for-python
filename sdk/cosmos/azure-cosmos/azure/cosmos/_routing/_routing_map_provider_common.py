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
    _OverlapDetected,  # noqa: F401  # re-exported for sync/async provider modules and tests
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

# Number of times the full-load path will re-fetch ``/pkranges`` when the
# builder reports an overlap (``_OverlapDetected``). Overlap on the full-load
# path is treated as a transient gateway inconsistency, so a small fixed
# retry budget with backoff is preferred over surfacing immediately. After
# this many attempts the caller surfaces a transient HTTP 503 so the
# upstream retry policy can take over.
#
# Defined here (rather than in each provider module) so the sync and async
# providers cannot drift on the retry budget — both import the same constant.
_OVERLAP_RETRY_MAX_ATTEMPTS = 3
# Initial backoff between overlap retries; doubles each attempt. Worst-case
# total sleep under the budget above is ~3.5s (0.5 + 1.0 + 2.0).
_OVERLAP_RETRY_INITIAL_BACKOFF_SECONDS = 0.5


def _jittered_backoff(backoff_seconds: float) -> float:
    """Return a uniformly-jittered backoff in the range ``[0, backoff_seconds]``.

    Implements the "full jitter" strategy: the actual sleep is drawn uniformly
    from zero to the full deterministic backoff. This decorrelates concurrent
    retriers (for example, multiple Cosmos clients running inside a single
    PySpark process that all hit the same gateway node on the same bad
    ``/pkranges`` snapshot at the same instant) so they do not retry in
    lockstep and re-collide on the same gateway node.

    The worst-case sleep per attempt is unchanged (still bounded by the
    deterministic backoff), so the documented retry-budget contract still
    holds; the expected per-attempt sleep is half of it.
    """
    return random.uniform(0, backoff_seconds)


def _handle_overlap_retry_decision(
    *,
    overlap_attempt_count: int,
    collection_link: str,
    logger: logging.Logger,  # pylint: disable=redefined-outer-name
) -> float:
    """Decide what to do after the full-load builder reported an overlap.

    Centralises the sync/async-identical retry policy. Returns the number of
    seconds the caller should sleep before the next attempt. Raises
    :class:`CosmosHttpResponseError` (HTTP 503) when the attempt budget has
    been exhausted; the caller's existing retry policy then handles it as
    a transient error.

    The returned sleep duration is jittered (see :func:`_jittered_backoff`)
    so concurrent retriers do not retry in lockstep. The deterministic
    backoff schedule (0.5s -> 1.0s -> 2.0s, doubling) defines the *upper
    bound* of each attempt's sleep; the actual sleep is drawn uniformly
    from ``[0, that upper bound]``.

    The caller is responsible for the actual sleep (sync ``time.sleep`` or
    ``await asyncio.sleep``). Keeping the sleep at the call site is what
    lets this helper stay free of concurrency-runtime assumptions — the
    only line that has to differ between the sync and async providers.

    :param int overlap_attempt_count: Number of overlap attempts made so far,
        including the one that just failed. Pass ``1`` after the first failure,
        ``2`` after the second, etc.
    :param str collection_link: Used in log messages and the 503 error body
        so the caller knows which collection ran out of budget.
    :param logging.Logger logger: Caller's module-level logger, so messages
        appear under the right ``azure.cosmos._routing.*`` namespace.
    :return: Jittered backoff seconds to sleep before retrying. Guaranteed
        to be in ``[0, deterministic_backoff_for_attempt]``.
    :rtype: float
    :raises CosmosHttpResponseError: When ``overlap_attempt_count`` has reached
        ``_OVERLAP_RETRY_MAX_ATTEMPTS``. Status code is 503 so the upstream
        retry policy classifies it as transient.
    """
    if overlap_attempt_count >= _OVERLAP_RETRY_MAX_ATTEMPTS:
        logger.error(
            "Full-load routing-map fetch for collection '%s' detected "
            "overlapping partition key ranges on every one of %d attempt(s). "
            "Surfacing as transient HTTP 503 so the caller's retry policy "
            "can take over.",
            collection_link,
            overlap_attempt_count,
        )
        raise CosmosHttpResponseError(
            status_code=http_constants.StatusCodes.SERVICE_UNAVAILABLE,
            message=(
                "Failed to build routing map for collection '{}': "
                "overlapping partition key ranges persisted across {} "
                "full-load attempt(s). Surfaced as a retryable transient "
                "error so the upstream retry policy can take over, rather "
                "than allowing the underlying ValueError to escape as a "
                "fatal crash."
            ).format(collection_link, overlap_attempt_count),
        )

    deterministic_backoff = (
        _OVERLAP_RETRY_INITIAL_BACKOFF_SECONDS * (2 ** (overlap_attempt_count - 1))
    )
    jittered_backoff = _jittered_backoff(deterministic_backoff)
    logger.warning(
        "Full-load routing-map fetch for collection '%s' detected overlapping "
        "partition key ranges (attempt %d/%d). Sleeping %.2fs (jittered from "
        "upper bound %.2fs) and retrying.",
        collection_link,
        overlap_attempt_count,
        _OVERLAP_RETRY_MAX_ATTEMPTS,
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
    """Sentinel raised by :func:`process_fetched_ranges` when the
    incremental update cannot resolve all partition key ranges.

    The caller decides how to recover: retry the incremental fetch
    (if attempts remain) or fall back to a full routing-map refresh."""


def process_fetched_ranges(
    ranges: List[Dict[str, Any]],
    previous_routing_map: Optional[CollectionRoutingMap],
    collection_id: str,
    collection_link: str,
    new_etag: Optional[str],
) -> Optional[CollectionRoutingMap]:
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
    :return: The new/updated routing map, or ``None`` when an
        initial load yields no ranges.
    :rtype: ~azure.cosmos._routing.collection_routing_map.CollectionRoutingMap
        or None
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
        # ``try_combine`` validates the merged map via
        # ``CollectionRoutingMap.is_complete_set_of_range`` and raises
        # ``ValueError("Ranges overlap: ...")`` if the merge produces a
        # self-contradictory tiling. This can happen during the incremental
        # path when the delta contains a range whose key span overlaps an
        # existing cached range without either side declaring the other a
        # parent.
        #
        # We must NOT let this ``ValueError`` escape: the cache layer above
        # treats a ``None`` routing map as "no ranges" and would convert
        # the bare exception into a silent empty-result return at
        # ``get_overlapping_ranges``. Convert to ``_IncrementalMergeFailed``
        # so the caller's existing retry loop retries the incremental fetch
        # once and then falls back to the full-load path, which has its own
        # ``_OverlapDetected`` handler with retry+backoff and surfaces a
        # transient HTTP 503 if the inconsistency persists.
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
