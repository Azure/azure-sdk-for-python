# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Owned diagnostics and controls for explicitly approved real-split tests.

Stage/range helpers were copied from tests/_split_test_utils.py; throughput
polling was copied from tests/test_config.py. Neither module is imported.
"""

import asyncio
import json
import os
import time
import traceback
import unittest
import warnings
from contextlib import contextmanager

from azure.cosmos import _base
from azure.cosmos.http_constants import HttpHeaders


SPLIT_TIMEOUT = 60 * 10
SLEEP_TIME = 30
REAL_SPLIT_ENV = "COSMOS_SESSION_TOKEN_REAL_SPLIT"
_CONTEXT_FIELDS = (
    "expected_count",
    "actual_count",
    "missing_count",
    "unexpected_count",
    "ids_match",
    "token_matches",
    "lsn_not_regressed",
    "expected_range_present",
)


def require_real_split():
    """Fail closed before constructing any client or increasing throughput."""
    if os.environ.get(REAL_SPLIT_ENV) != "1":
        raise unittest.SkipTest(
            "environment-gap: real split requires explicit approval; set "
            "COSMOS_SESSION_TOKEN_REAL_SPLIT=1 to authorize 11000 RU/s"
        )
    if not all(os.environ.get(name) for name in ("ACCOUNT_HOST", "ACCOUNT_KEY")):
        raise unittest.SkipTest("environment-gap: real split requires ACCOUNT_HOST and ACCOUNT_KEY")


def _record(stage, outcome, **details):
    print(
        json.dumps(
            {"event": "split_test_stage", "stage": stage, "outcome": outcome, **details}
        ),
        flush=True,
    )


def _failure_details(error, context):
    headers = getattr(error, "headers", None) or {}
    return {
        "error_type": type(error).__name__,
        "status_code": getattr(error, "status_code", None),
        "sub_status": getattr(error, "sub_status", None),
        "activity_id": headers.get(HttpHeaders.ActivityId),
        "locations": [
            {
                "file": os.path.basename(frame.f_code.co_filename),
                "function": frame.f_code.co_name,
                "line": line,
            }
            for frame, line in traceback.walk_tb(error.__traceback__)
        ],
        "context": {
            key: context[key]
            for key in _CONTEXT_FIELDS
            if type(context.get(key)) in (int, bool)
        },
    }


@contextmanager
def split_stage(name, failures=None):
    """Report a stage, yielding optional count/boolean diagnostics for failures."""
    start = time.monotonic()
    context = {}
    _record(name, "started")
    try:
        yield context
    except unittest.SkipTest:
        _record(name, "skipped", elapsed_seconds=round(time.monotonic() - start, 1))
        raise
    except Exception as error:
        details = _failure_details(error, context)
        _record(
            name,
            "failed",
            elapsed_seconds=round(time.monotonic() - start, 1),
            **details,
        )
        if failures is None:
            raise
        failures.append({"stage": name, **details})
    else:
        _record(name, "passed", elapsed_seconds=round(time.monotonic() - start, 1))


def assert_no_stage_failures(failures):
    if failures:
        summaries = []
        for failure in failures:
            locations = " -> ".join(
                "{file}:{line} ({function})".format(**location)
                for location in failure["locations"]
            )
            metadata = {
                key: failure[key]
                for key in ("status_code", "sub_status", "activity_id", "context")
                if failure[key] is not None and failure[key] != {}
            }
            summaries.append(
                "{} ({}) [{}] {}".format(
                    failure["stage"],
                    failure["error_type"],
                    locations,
                    json.dumps(metadata, sort_keys=True),
                )
            )
        raise AssertionError("Post-split checks failed: " + ", ".join(summaries)) from None


def snapshot_split_routing_map(container, collection_rid, *, legacy_routing_cache=True):
    """Preserve the legacy reset only for a legacy data client.

    Rust routing is driver-owned. The explicit False branch disables only the
    Python cache injection, not any before/after customer assertion. Successful
    live requests in that mode do not prove independent stale-cache recovery.
    """
    if not legacy_routing_cache:
        warnings.warn(
            "internals-only: Python routing-cache snapshot/reset is disabled for Rust; "
            "customer split assertions do not establish Rust stale-routing recovery",
            UserWarning,
            stacklevel=2,
        )
        return lambda: None
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
        "environment-gap: Physical split did not converge from parent {} to two children; last ranges: {}".format(
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


def trigger_split(container, throughput):
    require_real_split()
    print("Triggering a split in session token helpers")
    # Use a single control-plane attempt to avoid masking contention failures.
    container.replace_throughput(throughput)
    print(f"changed offer to {throughput}")
    print("--------------------------------")
    print("Waiting for split to complete")
    start_time = time.time()

    while True:
        offer = container.get_throughput()
        if offer.properties['content'].get('isOfferReplacePending', False):
            if time.time() - start_time > SPLIT_TIMEOUT:
                raise unittest.SkipTest("environment-gap: Partition split didn't complete in time")
            else:
                print("Waiting for split to complete")
                time.sleep(SLEEP_TIME)
        else:
            break
    print("Split in session token helpers has completed")


async def trigger_split_async(container, throughput):
    require_real_split()
    print("Triggering a split in session token helpers")
    # Use a single control-plane attempt to avoid masking contention failures.
    await container.replace_throughput(throughput)
    print(f"changed offer to {throughput}")
    print("--------------------------------")
    print("Waiting for split to complete")
    start_time = time.time()

    while True:
        offer = await container.get_throughput()
        if offer.properties['content'].get('isOfferReplacePending', False):
            if time.time() - start_time > SPLIT_TIMEOUT:
                raise unittest.SkipTest("environment-gap: Partition split didn't complete in time")
            else:
                print("Waiting for split to complete")
                await asyncio.sleep(SLEEP_TIME)
        else:
            break
    print("Split in session token helpers has completed")
