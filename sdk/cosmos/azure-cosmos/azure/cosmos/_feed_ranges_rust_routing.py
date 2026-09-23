# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
"""Share feed-range preparation and response parsing between sync and async calls.

The customer app can save a feed-range dictionary and pass it to a later
operation. Both client types must therefore return the same dictionary format,
including uppercase range bounds, as the legacy path.

Eligibility checks report whether inputs can use the Rust path; the caller
applies the migration policy before execution. Builders produce PreparedRequest
objects without calling the binding. Parsers read the decoded response body.
This module does not choose service-backend regions or replicas.
"""

from __future__ import annotations

from ._backend.partition_key_input import BindingPartitionKey

from typing import Any, Mapping

from . import _base as base
from ._backend.constants import is_rust_backend
from ._backend.operations import (
    OP_FEED_RANGE_FROM_PARTITION_KEY,
    OP_IS_FEED_RANGE_SUBSET,
    OP_READ_FEED_RANGES,
)
from ._backend.contracts import PreparedRequest
from ._change_feed.feed_range_internal import FeedRangeInternalEpk
from ._helpers._wire_encoding import serialize_body_to_bytes
from ._helpers._partition_key import normalize_partition_key
from ._routing.routing_range import Range


def can_use_rust_backend_for_read_feed_ranges(
    *,
    backend: Any,
    kwargs: Mapping[str, Any],
) -> bool:
    """Check that the selected Python backend is Rust-backed and no extra options remain."""
    if not is_rust_backend(backend):
        return False
    # This request carries the container link and forceRefresh, not arbitrary
    # options. Let the caller's operation policy handle unsupported arguments.
    return len(kwargs) == 0


def validate_read_feed_ranges_force_refresh(force_refresh: bool) -> None:
    """Require True or False; do not silently turn values such as 1 into True."""
    if not isinstance(force_refresh, bool):
        raise TypeError("read_feed_ranges force_refresh must be a bool.")


def build_read_feed_ranges_prepared_request(
    *,
    container_link: str,
    force_refresh: bool,
) -> PreparedRequest:
    """Build a prepared request for the read_feed_ranges binding function.

    For example, force_refresh=True becomes {"forceRefresh": true} in JSON body
    bytes. This records the request; it does not refresh metadata here.
    """
    validate_read_feed_ranges_force_refresh(force_refresh)
    normalized_container_link = base.TrimBeginningAndEndingSlashes(container_link)
    body_bytes = serialize_body_to_bytes({"forceRefresh": force_refresh})
    return PreparedRequest(
        op=OP_READ_FEED_RANGES,
        container_link=normalized_container_link,
        body_bytes=body_bytes,
        partition_key=BindingPartitionKey("cross_partition"),
        headers={},
        item_id=None,
    )


def parse_read_feed_ranges_payload(payload: Mapping[str, Any]) -> list[dict[str, Any]]:
    """Convert a decoded {"PartitionKeyRanges": [...]} body to feed-range dictionaries.

    Check the expected field types and uppercase the bounds. For example, a
    returned minInclusive of "ab" becomes "AB" in the customer-facing range.
    """
    if not isinstance(payload, Mapping):
        raise ValueError("read_feed_ranges Rust payload must be an object.")
    raw_ranges = payload.get("PartitionKeyRanges")
    if not isinstance(raw_ranges, list) or not raw_ranges:
        raise ValueError(
            "read_feed_ranges Rust payload must include a nonempty list field 'PartitionKeyRanges'."
        )

    feed_ranges: list[dict[str, Any]] = []
    for index, partition_key_range in enumerate(raw_ranges):
        if not isinstance(partition_key_range, Mapping):
            raise ValueError(
                "read_feed_ranges Rust payload entry at index {} must be an object.".format(
                    index
                )
            )
        min_inclusive = partition_key_range.get("minInclusive")
        max_exclusive = partition_key_range.get("maxExclusive")
        if not isinstance(min_inclusive, str) or not isinstance(max_exclusive, str):
            raise ValueError(
                "read_feed_ranges Rust payload entry at index {} must include string "
                "'minInclusive' and 'maxExclusive'.".format(index)
            )
        # Match Range.PartitionKeyRangeToRange on the legacy path. The customer
        # app can compare saved dictionaries or pass them back unchanged.
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
    """Check whether the selected Python backend is Rust-backed."""
    return is_rust_backend(backend)


def build_feed_range_from_partition_key_prepared_request(
    *,
    container_link: str,
    partition_key_value: Any,
) -> PreparedRequest:
    """Prepare a partition-key value for the feed_range_from_partition_key binding function.

    For example, "customer-17" becomes a BindingPartitionKey. Computing its
    feed range happens later through the binding, not in this builder.
    """
    normalized_container_link = base.TrimBeginningAndEndingSlashes(container_link)
    partition_key = normalize_partition_key(partition_key_value)
    return PreparedRequest(
        op=OP_FEED_RANGE_FROM_PARTITION_KEY,
        container_link=normalized_container_link,
        body_bytes=b"",
        partition_key=partition_key,
        headers={},
        item_id=None,
    )


def parse_feed_range_from_partition_key_payload(
    payload: Mapping[str, Any],
) -> dict[str, Any]:
    """Check a decoded {"Range": {...]} body and return a feed-range dictionary.

    Keep the supplied inclusion flags and uppercase both bounds, matching the
    legacy format used by a customer app that saves or reuses this value.
    """
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
    # Match Range.ParseFromDict's uppercase bounds, but check fields above so
    # a malformed response raises a clear ValueError rather than a missing-key error.
    return FeedRangeInternalEpk(
        Range(min_bound.upper(), max_bound.upper(), is_min_inclusive, is_max_inclusive)
    ).to_dict()


def can_use_rust_backend_for_is_feed_range_subset(
    *,
    backend: Any,
    parent_feed_range: dict[str, Any],
    child_feed_range: dict[str, Any],
) -> bool:
    """Check for the Range dictionary format accepted by the Rust path.

    Both ranges must have exactly the expected keys, boolean inclusion flags,
    and hexadecimal bounds of even length. A False result does not execute a
    legacy request; the caller decides what its migration policy permits.
    """
    if not is_rust_backend(backend):
        return False
    for value in (parent_feed_range, child_feed_range):
        if not isinstance(value, dict) or set(value) != {"Range"}:
            return False
        interval = value.get("Range") if isinstance(value, dict) else None
        if not isinstance(interval, dict) or set(interval) != {
            "min",
            "max",
            "isMinInclusive",
            "isMaxInclusive",
        }:
            return False
        if any(
            not isinstance(interval.get(key), bool)
            for key in ("isMinInclusive", "isMaxInclusive")
        ):
            return False
        for key in ("min", "max"):
            bound = interval.get(key)
            if (
                not isinstance(bound, str)
                or len(bound) % 2
                or any(char not in "0123456789abcdefABCDEF" for char in bound)
            ):
                return False
        normalized = Range.ParseFromDict(interval).to_normalized_range()
        if normalized.min > normalized.max:
            return False
    return True


def build_is_feed_range_subset_prepared_request(
    *,
    parent_feed_range: dict[str, Any],
    child_feed_range: dict[str, Any],
) -> PreparedRequest:
    """Prepare two feed ranges for the is_feed_range_subset binding function.

    Body bytes contain {"parent": <feed-range dict>, "child": <feed-range dict>}.
    The binding's range comparison is local and does not contact the service
    backend, so the container link is empty. This builder only prepares inputs.
    """
    body_bytes = serialize_body_to_bytes(
        {"parent": parent_feed_range, "child": child_feed_range}
    )
    return PreparedRequest(
        op=OP_IS_FEED_RANGE_SUBSET,
        container_link="",
        body_bytes=body_bytes,
        partition_key=BindingPartitionKey("cross_partition"),
        headers={},
        item_id=None,
    )


def parse_is_feed_range_subset_payload(payload: Mapping[str, Any]) -> bool:
    """Read True or False from a decoded {"IsSubset": <bool>} response body."""
    is_subset = payload.get("IsSubset")
    if not isinstance(is_subset, bool):
        raise ValueError(
            "is_feed_range_subset Rust payload must include a boolean field 'IsSubset'."
        )
    return is_subset
