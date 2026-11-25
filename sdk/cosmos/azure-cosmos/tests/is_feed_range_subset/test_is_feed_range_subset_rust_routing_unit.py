# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Backend-agnostic unit tests for the ``is_feed_range_subset`` Rust-routing helpers
(input validation / prepared-request builder / payload parser).

These tests do not need the emulator. The native boundary regression uses the
compiled binding when available; other cases use fakes. They lock in the request
shape, parsed answer, and malformed-input handling without network requests.
Without them, a regression in the request shape or the payload parser would surface
only in a slow emulator run.
"""

from __future__ import annotations
from common.typed_requests import legacy_partition_key_from_request

import asyncio
import json
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import pytest
from azure.core.utils import CaseInsensitiveDict

from azure.cosmos._backend.contracts import BackendResponse
from azure.cosmos._backend.cosmos_backend import CosmosBackend
from azure.cosmos._backend.legacy import LEGACY_BACKEND
from azure.cosmos.aio._backend.legacy import ASYNC_LEGACY_BACKEND
from azure.cosmos._backend.operations import OP_IS_FEED_RANGE_SUBSET
from azure.cosmos.aio._backend.cosmos_backend import AsyncCosmosBackend
from azure.cosmos._change_feed.feed_range_internal import FeedRangeInternalEpk
from azure.cosmos._routing.routing_range import Range
from azure.cosmos._feed_ranges_rust_routing import (
    build_feed_range_subset_request,
    parse_is_feed_range_subset_payload,
)

def _feed_range(range_min, range_max, is_min_inclusive=True, is_max_inclusive=False):
    """Build a public feed range from explicit boundaries."""
    return FeedRangeInternalEpk(
        Range(range_min, range_max, is_min_inclusive, is_max_inclusive)
    ).to_dict()


# ---------------------------------------------------------------------------
# Input validation
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("async_mode", [False, True])
def test_legacy_comparison_keeps_its_original_validation(async_mode, monkeypatch):
    from azure.cosmos._helpers import _feed_range_operations as operations

    monkeypatch.setattr(
        operations, "build_feed_range_subset_request",
        Mock(side_effect=AssertionError("Legacy must not build a Rust request")),
    )
    connection = SimpleNamespace(_backend=ASYNC_LEGACY_BACKEND if async_mode else LEGACY_BACKEND)
    result = (operations.is_feed_range_subset_async if async_mode else operations.is_feed_range_subset)(
        client_connection=connection,
        parent_feed_range=_feed_range("7F", "3F"),
        child_feed_range=_feed_range("3F", "7F"),
    )
    if async_mode:
        result = asyncio.run(result)
    assert result is False


@pytest.mark.parametrize(
    "parent",
    [
        {},
        {"Range": {}},
        {"Range": {"min": ""}},
        {"Range": None},
        None,
        [],
        _feed_range("FF", "00"),
        _feed_range("80", "7F", True, True),
        _feed_range("not-hex", "zz"),
        _feed_range("0", "F"),
        _feed_range("00", "FF", 1, 0),
        {**_feed_range("", "FF"), "ignored": float("nan")},
    ],
)
@pytest.mark.parametrize("async_mode", [False, True])
@pytest.mark.parametrize("invalid_side", ["parent", "child"])
def test_unsupported_ranges_are_rejected_without_fallback_rust(parent, async_mode, invalid_side, monkeypatch):
    """Invalid customer inputs are not missing Rust capabilities."""
    from azure.cosmos.container import ContainerProxy
    from azure.cosmos.aio._container import ContainerProxy as AsyncContainerProxy

    class Sync(CosmosBackend):
        name = "rust"

        def execute(self, prepared, *, deadline=None):
            pytest.fail("An unsupported shape must not be dispatched to Rust")

    class Async(AsyncCosmosBackend):
        name = "rust"

        async def execute(self, prepared, *, deadline=None):
            pytest.fail("An unsupported shape must not be dispatched to Rust")

    child = _feed_range("20", "40")
    if invalid_side == "child":
        parent, child = child, parent
    monkeypatch.setattr(
        FeedRangeInternalEpk, "from_json",
        lambda *_: pytest.fail("Unsupported inputs must not execute legacy comparison"),
    )
    connection = SimpleNamespace(_backend=Async() if async_mode else Sync())
    container_type = AsyncContainerProxy if async_mode else ContainerProxy
    container = container_type(connection, "dbs/db", "orders")
    with pytest.raises(ValueError, match=f"{invalid_side}_feed_range"):
        result = container.is_feed_range_subset(
            parent_feed_range=parent,
            child_feed_range=child,
        )
        if async_mode:
            asyncio.run(result)


# ---------------------------------------------------------------------------
# Prepared-request builder
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("parent,child", [
    (_feed_range("", "FF"), _feed_range("3F", "7F")),
    (_feed_range("80", "FF", True, True), _feed_range("80", "90")),
    (_feed_range("00", "FF", False, True), _feed_range("80", "90")),
    (_feed_range("8000", "80", True, True), _feed_range("80", "8000", True, True)),
])
def test_builds_prepared_request_with_both_feed_ranges_in_body_rust(parent, child):
    """The Rust request contains the correct parent and child feed ranges."""
    prepared = build_feed_range_subset_request(
        parent_feed_range=parent, child_feed_range=child
    )
    assert prepared.op == OP_IS_FEED_RANGE_SUBSET
    # No container to target for a pure client-side check.
    assert prepared.container_link == ""
    assert legacy_partition_key_from_request(prepared) == "[]"
    # Both feed ranges ride verbatim in the body under "parent" / "child".
    body = json.loads(prepared.body_bytes)
    assert body == {"parent": parent, "child": child}


# ---------------------------------------------------------------------------
# Payload parser
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("value", [True, False])
def test_parses_boolean_answer_rust(value):
    """Rust Boolean results preserve the Python public result."""
    assert parse_is_feed_range_subset_payload({"IsSubset": value}) is value


def test_parser_rejects_missing_is_subset_rust():
    """A missing result raises the expected public parsing error."""
    with pytest.raises(ValueError):
        parse_is_feed_range_subset_payload({})


def test_parser_rejects_non_boolean_is_subset_rust():
    """A non-Boolean result raises the expected public parsing error."""
    with pytest.raises(ValueError):
        parse_is_feed_range_subset_payload({"IsSubset": "true"})


@pytest.mark.parametrize("parent,child,expected", [
    (_feed_range("80", "FF", True, True), _feed_range("80", "FF", True, True), True),
    (_feed_range("80", "FF", True, True), _feed_range("80", "90"), True),
    (_feed_range("00", "FF", False, True), _feed_range("80", "90"), True),
    (_feed_range("80", "FF", False, True), _feed_range("80", "90"), False),
    (_feed_range("80", "FF"), _feed_range("FF", "FF", True, True), False),
    (_feed_range("8000", "80", True, True), _feed_range("80", "8000", True, True), True),
    (_feed_range("40", "80", True, True), _feed_range("80", "8001"), False),
])
def test_native_subset_preserves_endpoint_meaning_rust(parent, child, expected):
    binding = pytest.importorskip("azure.cosmos._rust")
    prepared = build_feed_range_subset_request(
        parent_feed_range=parent, child_feed_range=child,
    )
    status, _, _, body, _ = binding.is_feed_range_subset(None, prepared)
    assert status == 200
    assert json.loads(body) == {"IsSubset": expected}


@pytest.mark.parametrize("async_mode", [False, True])
@pytest.mark.parametrize("is_subset", [False, True])
@pytest.mark.parametrize("parent", [
    _feed_range("", "FF"),
    _feed_range("80", "FF", True, True),
])
def test_subset_comparison_preserves_previous_response_headers_rust(async_mode, is_subset, parent, monkeypatch):
    from azure.cosmos.container import ContainerProxy
    from azure.cosmos.aio._container import ContainerProxy as AsyncContainerProxy

    response = BackendResponse(
        status_code=200,
        headers=CaseInsensitiveDict({"x-ms-activity-id": "comparison"}),
        body=json.dumps({"IsSubset": is_subset}).encode(),
    )
    execute = (AsyncMock if async_mode else Mock)(return_value=response)

    class Sync(CosmosBackend):
        name = "rust"

        def execute(self, prepared, *, deadline=None):
            return execute(prepared, deadline=deadline)

    class Async(AsyncCosmosBackend):
        name = "rust"

        async def execute(self, prepared, *, deadline=None):
            return await execute(prepared, deadline=deadline)

    monkeypatch.setattr(
        FeedRangeInternalEpk, "from_json", Mock(side_effect=AssertionError("Unexpected legacy comparison"))
    )
    previous = CaseInsensitiveDict({"x-ms-activity-id": "previous-read", "x-ms-request-charge": "2"})
    connection = SimpleNamespace(_backend=Async() if async_mode else Sync(), last_response_headers=previous.copy())
    container_type = AsyncContainerProxy if async_mode else ContainerProxy
    container = container_type(connection, "dbs/db", "orders")
    arguments = {
        "parent_feed_range": parent,
        "child_feed_range": _feed_range("3F", "7F"),
    }

    result = container.is_feed_range_subset(**arguments)
    if async_mode:
        result = asyncio.run(result)

    assert result is is_subset
    execute.assert_called_once()
    assert execute.call_args.args[0].op == OP_IS_FEED_RANGE_SUBSET
    assert connection.last_response_headers == previous
