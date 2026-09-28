# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Compare identical observations through explicitly selected real clients."""

import asyncio
from copy import deepcopy
import json
import os

import pytest

from azure.cosmos import CosmosClient
from azure.cosmos.aio import CosmosClient as AsyncCosmosClient
from azure.cosmos._change_feed.feed_range_internal import FeedRangeInternalEpk
from azure.cosmos._routing.routing_range import Range
from common._parity_helpers import (
    _assert_expected_backend, _binding_operation_count, _rust_fallback_count,
    skip_unless_emulator, skip_unless_rust_binding,
)


pytestmark = [skip_unless_emulator(), skip_unless_rust_binding()]


def _range(minimum="", maximum="FF"):
    return FeedRangeInternalEpk(Range(minimum, maximum, True, False)).to_dict()


CASES = [
    ("simple", [(_range(), "0:54"), (_range(), "0:60")], "0:60"),
    ("leading-zero", [(_range(), "0:0054")], "0:0054"),
    ("u64-max", [(_range(), "0:18446744073709551615")], "0:18446744073709551615"),
    ("vector", [(_range(), "0:1#54#3=50"), (_range(), "0:1#51#3=52")], "0:1#54#3=52"),
    ("mixed", [(_range(), "0:1000"), (_range(), "0:1#5#3=2")], "0:1#5#3=2"),
    ("compound", [(_range(), "0:1000,1:30"), (_range(), "0:1#5#3=2,1:40")], "0:1#5#3=2,1:40"),
]
for vector in (False, True):
    prefix = "1#" if vector else ""
    parent, left, right = (f"{partition}:{prefix}{lsn}" for partition, lsn in [(0, 55), (3, 60), (2, 70)])
    for left_max, retain_parent in [("40", True), ("80", False), ("90", False)]:
        CASES.append((
            f"children-{vector}-{left_max}",
            [(_range(), parent), (_range("", left_max), left), (_range("80", "FF"), right)],
            ",".join([parent, left, right] if retain_parent else [left, right]),
        ))


def _before(client, backend, pairs, target):
    _assert_expected_backend(client, backend)
    return (
        _binding_operation_count(), _rust_fallback_count(),
        deepcopy(client.client_connection.last_response_headers),
        deepcopy(pairs), deepcopy(target),
    )


def _check(client, before, pairs, target, result, expected):
    assert _binding_operation_count() == before[0]
    assert _rust_fallback_count() == before[1]
    assert client.client_connection.last_response_headers == before[2]
    assert pairs == before[3]
    assert target == before[4]
    assert sorted(result.split(",")) == sorted(expected.split(","))


@pytest.mark.parametrize("asynchronous", [False, True], ids=["sync", "async"])
@pytest.mark.parametrize("name,pairs,expected", CASES, ids=[case[0] for case in CASES])
def test_same_observations_on_both_backends(asynchronous, name, pairs, expected):
    target = _range()
    results = {}

    async def run_async():
        for backend in ("core-python", "rust"):
            async with AsyncCosmosClient(
                os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"], _backend=backend,
            ) as client:
                container = client.get_database_client("unused").get_container_client("orders")
                before = _before(client, backend, pairs, target)
                result = await container.get_latest_session_token(pairs, target)
                _check(client, before, pairs, target, result, expected)
                results[backend] = result

    if asynchronous:
        asyncio.run(run_async())
    else:
        for backend in ("core-python", "rust"):
            with CosmosClient(os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"], _backend=backend) as client:
                container = client.get_database_client("unused").get_container_client("orders")
                before = _before(client, backend, pairs, target)
                result = container.get_latest_session_token(pairs, target)
                _check(client, before, pairs, target, result, expected)
                results[backend] = result
    assert results["core-python"] == results["rust"]
    print("\nTOKEN-PARITY " + json.dumps({
        "case": name, "surface": "aio" if asynchronous else "sync",
        "observations": pairs, "target": target, "results": results,
        "native_operation_delta": 0, "compatibility_fallback_delta": 0,
        "inputs_and_response_state_unchanged": True,
    }))
