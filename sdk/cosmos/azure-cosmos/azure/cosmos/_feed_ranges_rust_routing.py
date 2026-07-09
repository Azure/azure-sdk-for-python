# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
"""Shared Rust-routing helpers for ``ContainerProxy.read_feed_ranges`` (sync + aio).

Both the sync and async read_feed_ranges call into this one module so the two paths build
the same request and return the exact same feed-range values. Without it, each would carry
its own copy of the can-use / build / parse logic; the two could drift, and the Rust path
could hand back feed-range values that differ from the legacy path -- which breaks customers
who reuse a feed-range value in a later call."""
from __future__ import annotations

from typing import Any, Mapping, Optional, cast

from . import _base as base
from ._backend.base import OP_READ_FEED_RANGES, PreparedRequest
from ._change_feed.feed_range_internal import FeedRangeInternalEpk
from ._helpers._body_wire import serialize_body_to_bytes
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
