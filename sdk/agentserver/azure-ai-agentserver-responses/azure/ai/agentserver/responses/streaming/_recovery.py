# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Stream recovery utilities for durable responses.

Provides consistency checking, event filtering by sequence number,
and TTL-based expiry for persisted stream events.
"""

from __future__ import annotations

import time
from typing import Any


async def check_stream_consistency(
    *,
    events: list[dict[str, Any]] | None,
    last_sequence_number: int,
) -> bool:
    """Check if persisted stream events are consistent with metadata.

    Consistent means: the persisted events contain at least up to the
    sequence number recorded in task metadata. If the file is missing
    or has fewer events, the stream is inconsistent (data loss occurred).

    :param events: Persisted events, or None if file missing/unreadable.
    :param last_sequence_number: The last sequence number from task metadata.
    :returns: True if consistent, False if data loss detected.
    """
    if last_sequence_number == 0:
        # No events expected — always consistent
        return True

    if events is None or len(events) == 0:
        # File missing but metadata says events exist → inconsistent
        return False

    # Find max sequence in persisted events
    max_seq = max(e.get("sequence_number", 0) for e in events)
    return max_seq >= last_sequence_number


def filter_events_by_sequence(
    events: list[dict[str, Any]],
    starting_after: int,
) -> list[dict[str, Any]]:
    """Filter events to only those with sequence_number > starting_after.

    Used for client reconnection: the client provides the last sequence
    number it received, and only newer events are sent.

    :param events: Full list of persisted events.
    :param starting_after: Sequence number to filter after (exclusive).
    :returns: Events with sequence_number > starting_after, in order.
    """
    return [e for e in events if e.get("sequence_number", 0) > starting_after]


def check_ttl_expired(
    terminal_time: float | None,
    ttl_seconds: float,
) -> bool:
    """Check if stream events have expired based on TTL.

    Events are kept for `ttl_seconds` after the response reaches terminal
    state. After that, they are eligible for cleanup.

    :param terminal_time: Unix timestamp when response reached terminal state,
        or None if still in progress.
    :param ttl_seconds: Time-to-live in seconds after terminal state.
    :returns: True if expired, False if still within TTL window.
    """
    if terminal_time is None:
        # Still in progress — not expired
        return False

    elapsed = time.time() - terminal_time
    return elapsed > ttl_seconds
