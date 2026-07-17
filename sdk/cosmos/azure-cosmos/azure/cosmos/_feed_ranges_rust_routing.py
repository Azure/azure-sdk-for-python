# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
"""Shared Rust-routing helpers for feed-range methods (sync + aio).

Both sync and async feed-range methods call into this one module so the two paths build
the same requests and return the exact same feed-range values. Without it, each would carry
its own copy of the can-use / build / parse logic; the two could drift, and the Rust path
could hand back feed-range values that differ from the legacy path -- which breaks customers
who reuse a feed-range value in a later call."""
from __future__ import annotations

from typing import Any, Mapping, Optional, cast

from . import _base as base
from ._backend.base import (
    OP_FEED_RANGE_FROM_PARTITION_KEY,
    OP_IS_FEED_RANGE_SUBSET,
    OP_READ_FEED_RANGES,
    PreparedRequest,
)
from ._change_feed.feed_range_internal import FeedRangeInternalEpk
from ._helpers._body_wire import serialize_body_to_bytes
from ._helpers._pk_wire import serialize_partition_key_to_wire
from ._helpers._response_parse import parse_backend_response
from ._routing.routing_range import Range


def can_use_rust_backend_for_read_feed_ranges(
    *,
    backend: Any,
    kwargs: Mapping[str, Any],
) -> bool:
    """Return True when ``read_feed_ranges`` can use the Rust backend."""
    if backend is None:
        return False
    # Legacy read_feed_ranges forwards unknown kwargs into routing-map reads.
    # Keep those calls on legacy until each knob is explicitly mirrored on Rust.
    # This per-call gate is migration scaffolding: it shrinks as knobs are mirrored and
    # goes away once the Rust path reaches full parity.
    return len(kwargs) == 0


def build_read_feed_ranges_prepared_request(
    *,
    container_link: str,
    force_refresh: bool,
) -> PreparedRequest:
    """Build the PreparedRequest consumed by the binding's read_feed_ranges entry point."""
    normalized_container_link = base.TrimBeginningAndEndingSlashes(container_link)
    body_bytes = serialize_body_to_bytes({"forceRefresh": bool(force_refresh)})
    return PreparedRequest(
        op=OP_READ_FEED_RANGES,
        container_link=normalized_container_link,
        body_bytes=body_bytes,
        partition_key_header="[]",
        headers={},
        item_id=None,
    )


def parse_read_feed_ranges_payload(payload: Mapping[str, Any]) -> list[dict[str, Any]]:
    """Convert the Rust payload ``{"PartitionKeyRanges":[...]}`` to public feed-range dicts."""
    raw_ranges = payload.get("PartitionKeyRanges")
    if not isinstance(raw_ranges, list):
        raise ValueError(
            "read_feed_ranges Rust payload must include a list field 'PartitionKeyRanges'."
        )

    feed_ranges: list[dict[str, Any]] = []
    for index, partition_key_range in enumerate(raw_ranges):
        if not isinstance(partition_key_range, Mapping):
            raise ValueError(
                "read_feed_ranges Rust payload entry at index {} must be an object.".format(index)
            )
        min_inclusive = partition_key_range.get("minInclusive")
        max_exclusive = partition_key_range.get("maxExclusive")
        if not isinstance(min_inclusive, str) or not isinstance(max_exclusive, str):
            raise ValueError(
                "read_feed_ranges Rust payload entry at index {} must include string "
                "'minInclusive' and 'maxExclusive'.".format(index)
            )
        # Legacy read_feed_ranges uppercases both EPK bounds (see
        # Range.PartitionKeyRangeToRange). The feed-range dict is an opaque value
        # customers feed back into get_latest_session_token and compare across
        # calls, so the Rust path must normalize identically or the base64 value
        # diverges byte-for-byte between backends.
        feed_ranges.append(
            FeedRangeInternalEpk(
                Range(min_inclusive.upper(), max_exclusive.upper(), True, False)
            ).to_dict()
        )
    return feed_ranges


def can_use_rust_backend_for_feed_range_from_partition_key(
    *,
    backend: Any,
) -> bool:
    """Return True when ``feed_range_from_partition_key`` can use the Rust backend."""
    return backend is not None


def build_feed_range_from_partition_key_prepared_request(
    *,
    container_link: str,
    partition_key_value: Any,
) -> PreparedRequest:
    """Build the PreparedRequest consumed by the binding's feed_range_from_partition_key entry point."""
    normalized_container_link = base.TrimBeginningAndEndingSlashes(container_link)
    partition_key_header = serialize_partition_key_to_wire(partition_key_value)
    return PreparedRequest(
        op=OP_FEED_RANGE_FROM_PARTITION_KEY,
        container_link=normalized_container_link,
        body_bytes=b"",
        partition_key_header=partition_key_header,
        headers={},
        item_id=None,
    )


def parse_feed_range_from_partition_key_payload(payload: Mapping[str, Any]) -> dict[str, Any]:
    """Convert the Rust payload ``{"Range": {...}}`` to the public feed-range dict."""
    raw_range = payload.get("Range")
    if not isinstance(raw_range, Mapping):
        raise ValueError(
            "feed_range_from_partition_key Rust payload must include an object field 'Range'."
        )
    min_bound = raw_range.get("min")
    max_bound = raw_range.get("max")
    if not isinstance(min_bound, str) or not isinstance(max_bound, str):
        raise ValueError(
            "feed_range_from_partition_key Rust payload 'Range' must include string 'min' and 'max'."
        )
    is_min_inclusive = raw_range.get("isMinInclusive")
    is_max_inclusive = raw_range.get("isMaxInclusive")
    if not isinstance(is_min_inclusive, bool) or not isinstance(is_max_inclusive, bool):
        raise ValueError(
            "feed_range_from_partition_key Rust payload 'Range' must include boolean "
            "'isMinInclusive' and 'isMaxInclusive'."
        )
    # The dict this returns is the public feed-range value, e.g.
    #   {"Range": {"min": "3FA10C8B2D9E4F17A0", "max": "3FA10C8B2D9E4F17A1",
    #              "isMinInclusive": True, "isMaxInclusive": False}}
    # The hex min/max are the (uppercased) start/end of the slice the partition key hashes into;
    # customers never read inside them -- they use the whole dict as one opaque label for "this
    # key's slice" and rely on it coming back the SAME every time it is produced for the same key,
    # including across the legacy and Rust backends. They use that label three ways:
    #   1. equality against a value saved earlier / in another process -- "does this worker still
    #      own this key's slice, or did it move?";
    #   2. overlap against the container's full slice list from read_feed_ranges -- which physical
    #      partition owns this key, hence which worker;
    #   3. as the target handed to get_latest_session_token, which overlap-matches it against the
    #      (feed range, session token) pairs the app collected and returns the newest token for
    #      that slice, so the next read of the key is session-consistent.
    # Legacy uppercases both EPK bounds (see Range.ParseFromDict). If the Rust path did not
    # normalize identically the value would diverge byte-for-byte, and then (1) reports "moved"
    # for an unchanged slice, (2) picks the wrong physical slice, and (3) either raises
    # "There were no overlapping feed ranges with the target." or returns the wrong token -- all
    # silent wrong results, no error at the call itself. Building the Range here (instead of via
    # from_json) also lets us validate each inner key up front and raise the same clear ValueError
    # as parse_read_feed_ranges_payload, rather than letting a malformed payload surface as a bare
    # KeyError from Range.ParseFromDict.
    return FeedRangeInternalEpk(
        Range(min_bound.upper(), max_bound.upper(), is_min_inclusive, is_max_inclusive)
    ).to_dict()


def can_use_rust_backend_for_is_feed_range_subset(
    *,
    backend: Any,
) -> bool:
    """Return True when ``is_feed_range_subset`` can use the Rust backend."""
    return backend is not None


def build_is_feed_range_subset_prepared_request(
    *,
    parent_feed_range: dict[str, Any],
    child_feed_range: dict[str, Any],
) -> PreparedRequest:
    """Build the PreparedRequest consumed by the binding's is_feed_range_subset entry point.

    is_feed_range_subset is a pure client-side check with no network call, so there is no
    container to target: the two feed-range dicts ride in the body as
    ``{"parent": <feed-range dict>, "child": <feed-range dict>}`` and the container link and
    partition-key header are left empty."""
    body_bytes = serialize_body_to_bytes(
        {"parent": parent_feed_range, "child": child_feed_range}
    )
    return PreparedRequest(
        op=OP_IS_FEED_RANGE_SUBSET,
        container_link="",
        body_bytes=body_bytes,
        partition_key_header="[]",
        headers={},
        item_id=None,
    )


def parse_is_feed_range_subset_payload(payload: Mapping[str, Any]) -> bool:
    """Read the boolean answer from the Rust payload ``{"IsSubset": <bool>}``."""
    is_subset = payload.get("IsSubset")
    if not isinstance(is_subset, bool):
        raise ValueError(
            "is_feed_range_subset Rust payload must include a boolean field 'IsSubset'."
        )
    return is_subset


def try_read_feed_ranges_with_rust_backend(
    *,
    client_connection: Any,
    container_link: str,
    force_refresh: bool,
) -> Optional[list[dict[str, Any]]]:
    """Execute ``read_feed_ranges`` through Rust, or return None to use legacy fallback."""
    backend = getattr(client_connection, "_backend", None)
    if backend is None:
        return None
    prepared = build_read_feed_ranges_prepared_request(
        container_link=container_link,
        force_refresh=force_refresh,
    )
    backend_response = backend.execute(prepared)
    if backend_response is None:
        return None
    parsed = parse_backend_response(
        backend_response,
        client_connection=client_connection,
        response_hook=None,
    )
    return parse_read_feed_ranges_payload(cast(dict[str, Any], parsed))


def try_feed_range_from_partition_key_with_rust_backend(
    *,
    client_connection: Any,
    container_link: str,
    partition_key_value: Any,
) -> Optional[dict[str, Any]]:
    """Execute ``feed_range_from_partition_key`` through Rust, or return None to use legacy fallback."""
    backend = getattr(client_connection, "_backend", None)
    if backend is None:
        return None
    prepared = build_feed_range_from_partition_key_prepared_request(
        container_link=container_link,
        partition_key_value=partition_key_value,
    )
    backend_response = backend.execute(prepared)
    if backend_response is None:
        return None
    parsed = parse_backend_response(
        backend_response,
        client_connection=client_connection,
        response_hook=None,
    )
    return parse_feed_range_from_partition_key_payload(cast(dict[str, Any], parsed))


def try_is_feed_range_subset_with_rust_backend(
    *,
    client_connection: Any,
    parent_feed_range: dict[str, Any],
    child_feed_range: dict[str, Any],
) -> Optional[bool]:
    """Execute ``is_feed_range_subset`` through Rust, or return None to use legacy fallback."""
    backend = getattr(client_connection, "_backend", None)
    if backend is None:
        return None
    prepared = build_is_feed_range_subset_prepared_request(
        parent_feed_range=parent_feed_range,
        child_feed_range=child_feed_range,
    )
    try:
        backend_response = backend.execute(prepared)
    except ValueError:
        # Rust rejected the feed-range inputs (a malformed dict, inverted bounds
        # where min > max, or a non-hex EPK). The legacy compare is more permissive
        # on these nonsensical opaque values -- it never validates min <= max -- so
        # fall back to it for exact parity instead of surfacing a Rust-only error.
        return None
    if backend_response is None:
        return None
    # Pass client_connection=None so parse_backend_response does NOT write
    # last_response_headers. The legacy is_feed_range_subset is a pure client-side
    # computation that never touches last_response_headers, so the Rust path must
    # not either -- otherwise it would clobber the headers left by the caller's
    # previous real operation with this call's empty (no-wire) header set.
    parsed = parse_backend_response(
        backend_response,
        client_connection=None,
        response_hook=None,
    )
    return parse_is_feed_range_subset_payload(cast(dict[str, Any], parsed))


async def try_read_feed_ranges_with_rust_backend_async(
    *,
    client_connection: Any,
    container_link: str,
    force_refresh: bool,
) -> Optional[list[dict[str, Any]]]:
    """Async sibling of ``try_read_feed_ranges_with_rust_backend``."""
    backend = getattr(client_connection, "_backend", None)
    if backend is None:
        return None
    prepared = build_read_feed_ranges_prepared_request(
        container_link=container_link,
        force_refresh=force_refresh,
    )
    backend_response = await backend.execute(prepared)
    if backend_response is None:
        return None
    parsed = parse_backend_response(
        backend_response,
        client_connection=client_connection,
        response_hook=None,
    )
    return parse_read_feed_ranges_payload(cast(dict[str, Any], parsed))


async def try_feed_range_from_partition_key_with_rust_backend_async(
    *,
    client_connection: Any,
    container_link: str,
    partition_key_value: Any,
) -> Optional[dict[str, Any]]:
    """Async sibling of ``try_feed_range_from_partition_key_with_rust_backend``."""
    backend = getattr(client_connection, "_backend", None)
    if backend is None:
        return None
    prepared = build_feed_range_from_partition_key_prepared_request(
        container_link=container_link,
        partition_key_value=partition_key_value,
    )
    backend_response = await backend.execute(prepared)
    if backend_response is None:
        return None
    parsed = parse_backend_response(
        backend_response,
        client_connection=client_connection,
        response_hook=None,
    )
    return parse_feed_range_from_partition_key_payload(cast(dict[str, Any], parsed))


async def try_is_feed_range_subset_with_rust_backend_async(
    *,
    client_connection: Any,
    parent_feed_range: dict[str, Any],
    child_feed_range: dict[str, Any],
) -> Optional[bool]:
    """Async sibling of ``try_is_feed_range_subset_with_rust_backend``."""
    backend = getattr(client_connection, "_backend", None)
    if backend is None:
        return None
    prepared = build_is_feed_range_subset_prepared_request(
        parent_feed_range=parent_feed_range,
        child_feed_range=child_feed_range,
    )
    try:
        backend_response = await backend.execute(prepared)
    except ValueError:
        # See the sync twin: Rust rejects inverted / malformed feed ranges that the
        # more permissive legacy compare accepts, so fall back for exact parity.
        return None
    if backend_response is None:
        return None
    # See the sync twin: client_connection=None so the Rust path leaves
    # last_response_headers untouched, matching the legacy pure-computation path.
    parsed = parse_backend_response(
        backend_response,
        client_connection=None,
        response_hook=None,
    )
    return parse_is_feed_range_subset_payload(cast(dict[str, Any], parsed))
