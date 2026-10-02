# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

"""Diagnostics and physical-range confirmation for grouped live split tests."""

import asyncio
import json
import time
import unittest
from contextlib import contextmanager

from azure.cosmos import _base
from azure.cosmos.http_constants import HttpHeaders


def _record(stage, outcome, **details):
    print(
        json.dumps(
            {"event": "split_test_stage", "stage": stage, "outcome": outcome, **details}
        ),
        flush=True,
    )


@contextmanager
def split_stage(name, failures=None):
    """Report a stage and optionally collect independent post-split failures."""
    start = time.monotonic()
    _record(name, "started")
    try:
        yield
    except unittest.SkipTest:
        _record(name, "skipped", elapsed_seconds=round(time.monotonic() - start, 1))
        raise
    except Exception as error:
        headers = getattr(error, "headers", None) or {}
        _record(
            name,
            "failed",
            elapsed_seconds=round(time.monotonic() - start, 1),
            error_type=type(error).__name__,
            status_code=getattr(error, "status_code", None),
            sub_status=getattr(error, "sub_status", None),
            activity_id=headers.get(HttpHeaders.ActivityId),
        )
        if failures is None:
            raise
        failures.append((name, error))
    else:
        _record(name, "passed", elapsed_seconds=round(time.monotonic() - start, 1))


def assert_no_stage_failures(failures):
    if failures:
        summary = ", ".join(
            "{} ({})".format(name, type(error).__name__) for name, error in failures
        )
        raise AssertionError("Post-split checks failed: " + summary) from failures[0][1]


def snapshot_split_routing_map(container, collection_rid):
    """Return a reset callback scoped to this container's name/RID cache entries."""
    cache = (
        container.client_connection._routing_map_provider._collection_routing_map_by_item
    )
    keys = (
        _base.GetResourceIdOrFullNameFromLink(container.container_link),
        collection_rid,
    )
    previous = {key: cache[key] for key in keys if key in cache}
    if not previous:
        raise AssertionError(
            "The split test must warm this container's routing map before taking a snapshot"
        )

    def restore():
        # Endpoint-shared maps would otherwise let one behavior refresh routing for the next.
        for key in keys:
            cache.pop(key, None)
        cache.update(previous)

    return restore


def _split_observed(ranges, parent_id):
    return (
        len(ranges) == 2
        and len({r["id"] for r in ranges}) == 2
        and all(parent_id in r.get("parents", []) for r in ranges)
    )


def _timeout(parent_id, ranges):
    observed = [
        {"id": r.get("id"), "parents": r.get("parents"), "status": r.get("status")}
        for r in ranges
    ]
    return unittest.SkipTest(
        "Physical split did not converge from parent {} to two children; last ranges: {}".format(
            parent_id, observed
        )
    )


def wait_for_split_ranges(container, parent_id, deadline, poll_interval=5):
    """Poll live key-auth range metadata without refreshing the data client's routing cache."""
    while True:
        ranges = list(
            container.client_connection._ReadPartitionKeyRanges(
                container.container_link
            )
        )
        if _split_observed(ranges, parent_id):
            _record(
                "physical_ranges",
                "passed",
                parent_id=parent_id,
                child_ids=[r["id"] for r in ranges],
            )
            return
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise _timeout(parent_id, ranges)
        time.sleep(min(poll_interval, remaining))


async def wait_for_split_ranges_async(container, parent_id, deadline, poll_interval=5):
    """Async counterpart of wait_for_split_ranges."""
    while True:
        ranges = [
            r
            async for r in container.client_connection._ReadPartitionKeyRanges(
                container.container_link
            )
        ]
        if _split_observed(ranges, parent_id):
            _record(
                "physical_ranges",
                "passed",
                parent_id=parent_id,
                child_ids=[r["id"] for r in ranges],
            )
            return
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise _timeout(parent_id, ranges)
        await asyncio.sleep(min(poll_interval, remaining))
