# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Keep feed-range values safe to pass between an order scan's workers.

These offline tests cover Python wrapper validation, independent results and
headers, and calls into the Python/Rust binding. Mixed-case, multi-range inputs
check the exact dictionary shape against legacy Python. Fake responses do not
prove live partition splits, cache refresh, or Rust driver behavior.
"""
from __future__ import annotations
from common.typed_requests import legacy_partition_key_from_request

from types import SimpleNamespace
import asyncio
import inspect
import json
import threading
from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
from typing import get_type_hints
from unittest.mock import AsyncMock, Mock

import pytest

from azure.cosmos import ContainerProxy
from azure.cosmos.exceptions import CosmosResourceNotFoundError
from azure.cosmos.aio import ContainerProxy as AsyncContainerProxy
from azure.cosmos._backend.contracts import BackendResponse
from azure.cosmos._backend.cosmos_backend import CosmosBackend
from azure.cosmos._backend.legacy import LEGACY_BACKEND
from azure.cosmos._cosmos_responses import CosmosAsyncItemPaged, CosmosItemPaged
from azure.cosmos.aio._backend.cosmos_backend import AsyncCosmosBackend
from azure.cosmos.aio._backend.legacy import ASYNC_LEGACY_BACKEND
from azure.cosmos._change_feed.feed_range_internal import FeedRangeInternalEpk
from azure.cosmos._backend.operations import OP_FEED_RANGE_FROM_PARTITION_KEY
from azure.cosmos._feed_ranges_rust_routing import (
    build_feed_range_from_partition_key_prepared_request,
    build_read_feed_ranges_prepared_request,
    can_use_rust_backend_for_feed_range_from_partition_key,
    can_use_rust_backend_for_read_feed_ranges,
    parse_feed_range_from_partition_key_payload,
    parse_read_feed_ranges_payload,
)

RUST_BACKEND = SimpleNamespace(name="rust")

from azure.cosmos._routing.routing_range import PartitionKeyRange, Range


def _legacy_feed_ranges(raw_ranges):
    """Reproduce the legacy read_feed_ranges output for the same raw ranges."""
    return [
        FeedRangeInternalEpk(Range.PartitionKeyRangeToRange(partition_key_range)).to_dict()
        for partition_key_range in raw_ranges
    ]


def test_rust_parser_matches_legacy_for_multi_range_mixed_case():
    """Rust payload to feed ranges must be byte-identical to the legacy builder.

    Uses multiple ranges with lowercase hex EPKs so a dropped .upper() (or any
    other divergence) would make the two backends produce different opaque
    feed-range values.
    """
    raw = [
        {"minInclusive": "", "maxExclusive": "3fffffffffffffff"},
        {"minInclusive": "3fffffffffffffff", "maxExclusive": "7fffffffffffffff"},
        {"minInclusive": "7fffffffffffffff", "maxExclusive": "ff"},
    ]

    rust_payload = {
        "PartitionKeyRanges": [
            {
                PartitionKeyRange.MinInclusive: r["minInclusive"],
                PartitionKeyRange.MaxExclusive: r["maxExclusive"],
            }
            for r in raw
        ]
    }

    rust_result = parse_read_feed_ranges_payload(rust_payload)
    legacy_result = _legacy_feed_ranges(raw)

    assert rust_result == legacy_result
    # And the bounds are normalized to upper-case (matching legacy).
    for feed_range in rust_result:
        assert feed_range["Range"]["min"] == feed_range["Range"]["min"].upper()
        assert feed_range["Range"]["max"] == feed_range["Range"]["max"].upper()


def test_rust_parser_matches_legacy_for_full_range():
    """Single full range parity (the shape the emulator suites exercise)."""
    raw = [{"minInclusive": "", "maxExclusive": "FF"}]
    rust_payload = {
        "PartitionKeyRanges": [
            {PartitionKeyRange.MinInclusive: "", PartitionKeyRange.MaxExclusive: "FF"}
        ]
    }
    assert parse_read_feed_ranges_payload(rust_payload) == _legacy_feed_ranges(raw)


def test_rust_parser_rejects_missing_partition_key_ranges():
    """A missing range list raises the expected public parsing error."""
    with pytest.raises(ValueError):
        parse_read_feed_ranges_payload({})


def test_rust_parser_rejects_non_list_partition_key_ranges():
    """A non-list range value raises the expected public parsing error."""
    with pytest.raises(ValueError):
        parse_read_feed_ranges_payload({"PartitionKeyRanges": {"minInclusive": ""}})


def test_rust_parser_rejects_non_object_entry():
    """A non-object range entry raises the expected public parsing error."""
    with pytest.raises(ValueError):
        parse_read_feed_ranges_payload({"PartitionKeyRanges": ["not-an-object"]})


def test_rust_parser_rejects_non_string_bounds():
    """Non-string boundaries raise the expected public parsing error."""
    with pytest.raises(ValueError):
        parse_read_feed_ranges_payload(
            {"PartitionKeyRanges": [{"minInclusive": 0, "maxExclusive": 1}]}
        )


def test_gate_requires_backend():
    """Python handles the call when Rust is unavailable."""
    assert can_use_rust_backend_for_read_feed_ranges(backend=LEGACY_BACKEND, kwargs={}) is False


def test_gate_allows_backend_with_no_kwargs():
    """Rust handles a supported read-feed-ranges call."""
    assert can_use_rust_backend_for_read_feed_ranges(backend=RUST_BACKEND, kwargs={}) is True


def test_gate_rejects_extra_rust_options():
    """The operation policy rejects unsupported options without a legacy call."""
    assert (
        can_use_rust_backend_for_read_feed_ranges(
            backend=RUST_BACKEND, kwargs={"partition_key": "x"}
        )
        is False
    )


def test_feed_range_from_partition_key_gate_requires_backend():
    """Python handles partition-key conversion when Rust is unavailable."""
    assert can_use_rust_backend_for_feed_range_from_partition_key(backend=LEGACY_BACKEND) is False


def test_feed_range_from_partition_key_gate_allows_backend():
    """Rust handles supported partition-key conversion."""
    assert can_use_rust_backend_for_feed_range_from_partition_key(backend=RUST_BACKEND) is True


def test_feed_range_from_partition_key_builds_prepared_request():
    """The request targets the correct container and partition key."""
    prepared = build_feed_range_from_partition_key_prepared_request(
        container_link="/dbs/d/colls/c/",
        partition_key_value="customerA",
    )
    assert prepared.op == OP_FEED_RANGE_FROM_PARTITION_KEY
    assert prepared.container_link == "dbs/d/colls/c"
    assert legacy_partition_key_from_request(prepared) == '["customerA"]'
    assert prepared.body_bytes == b""


def test_feed_range_from_partition_key_payload_round_trips_and_normalizes_case():
    """Rust returns the same normalized public feed range as Python."""
    parsed = parse_feed_range_from_partition_key_payload(
        {"Range": {"min": "3c", "max": "3cff", "isMinInclusive": True, "isMaxInclusive": False}}
    )
    assert parsed == {
        "Range": {"min": "3C", "max": "3CFF", "isMinInclusive": True, "isMaxInclusive": False}
    }


def test_feed_range_from_partition_key_payload_requires_range_object():
    """A missing or invalid range raises the expected public parsing error."""
    with pytest.raises(ValueError):
        parse_feed_range_from_partition_key_payload({})
    with pytest.raises(ValueError):
        parse_feed_range_from_partition_key_payload({"Range": "not-an-object"})


def test_feed_range_from_partition_key_payload_requires_string_bounds():
    """Missing or non-string boundaries raise the expected public parsing error."""
    with pytest.raises(ValueError):
        parse_feed_range_from_partition_key_payload(
            {"Range": {"max": "3cff", "isMinInclusive": True, "isMaxInclusive": False}}
        )
    with pytest.raises(ValueError):
        parse_feed_range_from_partition_key_payload(
            {"Range": {"min": 60, "max": "3cff", "isMinInclusive": True, "isMaxInclusive": False}}
        )


def test_feed_range_from_partition_key_payload_requires_boolean_flags():
    """Missing or non-boolean boundary flags raise the expected public error."""
    with pytest.raises(ValueError):
        parse_feed_range_from_partition_key_payload(
            {"Range": {"min": "3c", "max": "3cff", "isMaxInclusive": False}}
        )
    with pytest.raises(ValueError):
        parse_feed_range_from_partition_key_payload(
            {"Range": {"min": "3c", "max": "3cff", "isMinInclusive": "true", "isMaxInclusive": False}}
        )


class _RecordingBackend(CosmosBackend):
    name = "rust"

    def __init__(self):
        self.requests = []
        self.error = None
        self.response = BackendResponse(
            200, 0,
            {"content-type": "application/json", "x-ms-item-count": "0"},
            b'{"PartitionKeyRanges":[{"minInclusive":"","maxExclusive":"FF"}]}',
        )

    def execute(self, prepared, *, deadline=None):
        self.requests.append(prepared)
        if self.error is not None:
            raise self.error
        return self.response


class _AsyncRecordingBackend(AsyncCosmosBackend):
    name = "rust"

    def __init__(self):
        self.recording = _RecordingBackend()
        self.started = None
        self.release = None

    async def execute(self, prepared, *, deadline=None):
        if self.started is not None:
            self.started.set()
            await self.release.wait()
        return self.recording.execute(prepared, deadline=deadline)


def _container(async_client=False):
    backend = _AsyncRecordingBackend() if async_client else _RecordingBackend()
    connection = SimpleNamespace(
        _backend=backend,
        last_response_headers={"previous": "response"},
        _routing_map_provider=SimpleNamespace(get_overlapping_ranges=Mock()),
        refresh_routing_map_provider=Mock(),
    )
    proxy_type = AsyncContainerProxy if async_client else ContainerProxy
    container = proxy_type.__new__(proxy_type)
    container.client_connection = connection
    container.container_link = "dbs/sales/colls/orders"
    container._get_properties_with_options = AsyncMock() if async_client else Mock()
    return container, backend.recording if async_client else backend


async def _collect_async(values):
    return [value async for value in values]


def _collect(values, async_client):
    return asyncio.run(_collect_async(values)) if async_client else list(values)


@pytest.mark.parametrize("async_client", [False, True])
@pytest.mark.parametrize("value", [None, 0, 1, "false", "true", [], {}, object()])
def test_read_feed_ranges_rejects_non_boolean_refresh_before_execution(async_client, value):
    container, recording = _container(async_client)
    with pytest.raises(TypeError, match="force_refresh.*bool"):
        container.read_feed_ranges(force_refresh=value)
    assert not recording.requests


@pytest.mark.parametrize("value", [None, 0, 1, "false", [], {}])
def test_read_feed_ranges_builder_does_not_coerce_refresh(value):
    with pytest.raises(TypeError, match="force_refresh.*bool"):
        build_read_feed_ranges_prepared_request(container_link="dbs/sales/colls/orders", force_refresh=value)


@pytest.mark.parametrize("async_client", [False, True])
@pytest.mark.parametrize("options", [
    {"response_hook": None}, {"timeout": 5}, {"read_timeout": None},
    {"excluded_locations": ["West US"]}, {"max_item_count": 1},
    {"initial_headers": {"x-customer": "orders"}}, {"request_options": {}},
    {"unknown_option": False},
])
def test_read_feed_ranges_rejects_extra_options_without_legacy_execution(async_client, options):
    container, recording = _container(async_client)
    with pytest.raises(NotImplementedError, match="read_feed_ranges"):
        _collect(container.read_feed_ranges(**options), async_client)
    assert not recording.requests
    container._get_properties_with_options.assert_not_called()
    container.client_connection.refresh_routing_map_provider.assert_not_called()
    container.client_connection._routing_map_provider.get_overlapping_ranges.assert_not_called()


@pytest.mark.parametrize("async_client", [False, True])
@pytest.mark.parametrize("force_refresh", [False, True])
def test_read_feed_ranges_is_lazy_and_returns_an_owned_result(async_client, force_refresh):
    container, recording = _container(async_client)
    results = container.read_feed_ranges(force_refresh=force_refresh)
    assert not recording.requests
    assert results.get_response_headers() == {}
    values = _collect(results, async_client)
    assert values == [{"Range": {"min": "", "max": "FF", "isMinInclusive": True, "isMaxInclusive": False}}]
    assert len(recording.requests) == 1
    assert json.loads(recording.requests[0].body_bytes) == {"forceRefresh": force_refresh}
    assert results.get_response_headers() == {"content-type": "application/json", "x-ms-item-count": "0"}
    values[0]["Range"]["max"] = "changed by the customer"
    if async_client:
        async def repeat():
            pages = results.by_page()
            return await _collect_async(await pages.__anext__())
        again = asyncio.run(repeat())
    else:
        again = list(next(results.by_page()))
    assert again[0]["Range"]["max"] == "FF"
    assert len(recording.requests) == 1
    headers = results.get_response_headers()
    headers["x-ms-item-count"] = "changed"
    container.client_connection.last_response_headers["x-ms-item-count"] = "another call"
    assert results.get_response_headers()["x-ms-item-count"] == "0"
    container._get_properties_with_options.assert_not_called()


@pytest.mark.parametrize("async_client", [False, True])
@pytest.mark.parametrize("token", ["", "not-a-range-token"])
def test_read_feed_ranges_rejects_continuation_instead_of_restarting(async_client, token):
    container, recording = _container(async_client)
    pages = container.read_feed_ranges().by_page(continuation_token=token)
    with pytest.raises(ValueError, match="continuation"):
        if async_client:
            asyncio.run(pages.__anext__())
        else:
            next(pages)
    assert not recording.requests


@pytest.mark.parametrize("payload", [None, [], {"PartitionKeyRanges": []}])
def test_read_feed_ranges_rejects_missing_or_empty_routing_data(payload):
    with pytest.raises(ValueError, match="read_feed_ranges"):
        parse_read_feed_ranges_payload(payload)


@pytest.mark.asyncio
async def test_read_feed_ranges_rejects_overlapping_async_fetches():
    container, recording = _container(True)
    backend = container.client_connection._backend
    backend.started, backend.release = asyncio.Event(), asyncio.Event()
    results = container.read_feed_ranges()
    first = asyncio.create_task(results.by_page().__anext__())
    try:
        await asyncio.wait_for(backend.started.wait(), timeout=2)
        with pytest.raises(RuntimeError, match="concurrent"):
            await asyncio.wait_for(results.by_page().__anext__(), timeout=2)
    finally:
        backend.release.set()
        await first
    assert len(recording.requests) == 1


def test_read_feed_ranges_rejects_overlapping_sync_fetches():
    container, recording = _container()
    started, release = threading.Event(), threading.Event()
    original_execute = recording.execute

    def blocked(prepared, *, deadline=None):
        started.set()
        assert release.wait(timeout=5)
        return original_execute(prepared, deadline=deadline)

    recording.execute = blocked
    results = container.read_feed_ranges()
    with ThreadPoolExecutor(max_workers=1) as executor:
        first = executor.submit(next, results.by_page())
        try:
            assert started.wait(timeout=2)
            with pytest.raises(RuntimeError, match="concurrent"):
                next(results.by_page())
        finally:
            release.set()
            first.result(timeout=5)
    assert len(recording.requests) == 1


@pytest.mark.parametrize("async_client", [False, True])
@pytest.mark.parametrize("body", [
    b"not JSON", b"null", b"[]",
    b'[["PartitionKeyRanges",[{"minInclusive":"","maxExclusive":"FF"}]]]',
    b'{"PartitionKeyRanges":[]}', b'{"unexpected":[]}',
])
def test_read_feed_ranges_invalid_responses_do_not_become_empty_success(async_client, body):
    container, recording = _container(async_client)
    recording.response = replace(recording.response, body=body)
    results = container.read_feed_ranges()
    with pytest.raises(ValueError):
        _collect(results, async_client)
    assert len(recording.requests) == 1
    assert results.get_response_headers() == {}
    container._get_properties_with_options.assert_not_called()


@pytest.mark.parametrize("async_client", [False, True])
def test_read_feed_ranges_preserves_service_errors_and_does_not_replay(async_client):
    container, recording = _container(async_client)
    recording.response = BackendResponse(
        404, 1002, {"x-ms-activity-id": "failed-lookup"},
        b'{"message":"Container missing"}', diagnostics="lookup diagnostics",
    )
    with pytest.raises(CosmosResourceNotFoundError) as caught:
        _collect(container.read_feed_ranges(), async_client)
    assert caught.value.status_code == 404
    assert caught.value.headers["x-ms-activity-id"] == "failed-lookup"
    assert caught.value.headers["x-ms-cosmos-sdk-diagnostics"] == "lookup diagnostics"
    assert len(recording.requests) == 1
    container._get_properties_with_options.assert_not_called()


@pytest.mark.parametrize("async_client", [False, True])
@pytest.mark.parametrize("error", [RuntimeError("binding failed"), NotImplementedError("unsupported driver call")])
def test_read_feed_ranges_binding_failures_never_execute_legacy(async_client, error):
    container, recording = _container(async_client)
    recording.error = error
    with pytest.raises(type(error), match=str(error)):
        _collect(container.read_feed_ranges(), async_client)
    assert len(recording.requests) == 1
    container._get_properties_with_options.assert_not_called()


@pytest.mark.parametrize("async_client", [False, True])
def test_read_feed_ranges_new_iterators_have_independent_results_and_headers(async_client):
    container, recording = _container(async_client)
    first = container.read_feed_ranges()
    first_values = _collect(first, async_client)
    recording.response = replace(
        recording.response, headers={"x-ms-item-count": "0", "new-result": "second"},
        body=b'{"PartitionKeyRanges":[{"minInclusive":"","maxExclusive":"3f"},{"minInclusive":"3f","maxExclusive":"FF"}]}',
    )
    second = container.read_feed_ranges(force_refresh=True)
    assert len(_collect(second, async_client)) == 2
    assert first_values[0]["Range"]["max"] == "FF"
    assert "new-result" not in first.get_response_headers()
    assert second.get_response_headers()["new-result"] == "second"
    assert len(recording.requests) == 2


@pytest.mark.asyncio
async def test_read_feed_ranges_cancellation_releases_the_fetch_guard():
    container, recording = _container(True)
    backend = container.client_connection._backend
    backend.started, backend.release = asyncio.Event(), asyncio.Event()
    results = container.read_feed_ranges()
    attempt = asyncio.create_task(results.by_page().__anext__())
    await asyncio.wait_for(backend.started.wait(), timeout=2)
    attempt.cancel()
    with pytest.raises(asyncio.CancelledError):
        await attempt
    assert results.get_response_headers() == {}
    container._get_properties_with_options.assert_not_called()
    backend.release.set()
    values = await _collect_async(results)
    assert len(values) == 1
    assert len(recording.requests) == 1


@pytest.mark.parametrize("async_client", [False, True])
def test_read_feed_ranges_unsupported_hooks_are_not_copied_or_called(async_client):
    class Hook:
        def __deepcopy__(self, memo):
            raise AssertionError("A customer callback must not be copied.")

        def __call__(self, *args):
            raise AssertionError("An unsupported callback must not be called.")

    container, recording = _container(async_client)
    with pytest.raises(NotImplementedError, match="read_feed_ranges"):
        _collect(container.read_feed_ranges(response_hook=Hook()), async_client)
    assert not recording.requests


@pytest.mark.parametrize("async_client", [False, True])
@pytest.mark.parametrize("force_refresh", [False, True])
def test_read_feed_ranges_preserves_the_private_legacy_comparison_path(async_client, force_refresh):
    container, recording = _container(async_client)
    connection = container.client_connection
    connection._backend = ASYNC_LEGACY_BACKEND if async_client else LEGACY_BACKEND
    mock_type = AsyncMock if async_client else Mock
    connection.refresh_routing_map_provider = mock_type()
    connection._routing_map_provider.get_overlapping_ranges = mock_type(
        return_value=[{"minInclusive": "", "maxExclusive": "ff"}],
    )
    container._get_properties_with_options.return_value = {"_rid": "container-rid"}
    values = _collect(
        container.read_feed_ranges(force_refresh=force_refresh, excluded_locations=["West US"]),
        async_client,
    )
    assert values == [{"Range": {"min": "", "max": "FF", "isMinInclusive": True, "isMaxInclusive": False}}]
    assert not recording.requests
    assert connection.refresh_routing_map_provider.call_count == int(force_refresh)
    assert connection._routing_map_provider.get_overlapping_ranges.call_args.kwargs == {
        "excluded_locations": ["West US"],
    }


@pytest.mark.parametrize("proxy_type, result_type", [
    (ContainerProxy, CosmosItemPaged),
    (AsyncContainerProxy, CosmosAsyncItemPaged),
])
def test_read_feed_ranges_return_type_exposes_response_headers(proxy_type, result_type):
    method = inspect.unwrap(proxy_type.read_feed_ranges)
    assert get_type_hints(method)["return"] is result_type
    assert not inspect.iscoroutinefunction(method)
