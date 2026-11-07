# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Offline observer guards; these do not establish live regional parity."""

from copy import deepcopy
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, Mock

import pytest

from create_item._routing import (
    CREATE_ITEM_TEST_DATA,
    DEFAULT_LOCATION,
    READ_LOCATION,
    WRITE_LOCATION,
    CreateRoutingCapture,
    expected_write_region,
    normalize_region,
)


def payload():
    return {
        "activity_id": "native-operation",
        "request_count": 1,
        "retained_request_count": 1,
        "result_status": 201,
        "requests": [
            {
                "pipeline": "data_plane",
                "endpoint": "https://account-westus.documents.azure.com/",
                "region": "westus",
                "status": 201,
            }
        ],
    }


def capture_with_payload(monkeypatch, evidence):
    capture = CreateRoutingCapture(monkeypatch)
    capture.calls.append(("dbs/db/colls/orders", "order", evidence))
    return capture


@pytest.mark.parametrize("asynchronous", [False, True])
@pytest.mark.asyncio
async def test_capture_calls_selected_native_once_and_preserves_response_rust(monkeypatch, asynchronous):
    if asynchronous:
        from azure.cosmos.aio._backend import binding_adapter as module
    else:
        from azure.cosmos._backend import binding_adapter as module
    response = (201, 0, {}, b'{"id":"order"}', "diagnostics")
    native = (AsyncMock if asynchronous else Mock)(return_value=(response, payload()))
    other = Mock()
    monkeypatch.setattr(module, "_binding_function_for_op", lambda op: native if op == "create_item" else other)
    capture = CreateRoutingCapture(monkeypatch, asynchronous=asynchronous)
    prepared = SimpleNamespace(container_link="dbs/db/colls/orders", item_id="order")
    function = module._binding_function_for_op("create_item")
    result = function("handle", prepared, timeout_seconds=4.5)
    if asynchronous:
        result = await result
        native.assert_awaited_once()
    assert result is response
    native.assert_called_once_with("handle", prepared, timeout_seconds=4.5, include_fault_diagnostics=True)
    assert module._binding_function_for_op("read_item") is other
    capture.assert_destination(prepared.container_link, prepared.item_id, "West US")


@pytest.mark.parametrize("asynchronous", [False, True])
@pytest.mark.asyncio
async def test_native_failure_is_not_replayed_or_recorded_as_success_rust(monkeypatch, asynchronous):
    if asynchronous:
        from azure.cosmos.aio._backend import binding_adapter as module
    else:
        from azure.cosmos._backend import binding_adapter as module
    failure = RuntimeError("native failure")
    native = (AsyncMock if asynchronous else Mock)(side_effect=failure)
    monkeypatch.setattr(module, "_binding_function_for_op", lambda op: native)
    capture = CreateRoutingCapture(monkeypatch, asynchronous=asynchronous)
    with pytest.raises(RuntimeError) as raised:
        result = module._binding_function_for_op("create_item")("handle", object())
        if asynchronous:
            await result
    assert raised.value is failure
    assert not capture.calls
    native.assert_called_once()


@pytest.mark.parametrize(
    "change",
    [
        {"activity_id": None},
        {"request_count": 2},
        {"retained_request_count": 0},
        {"requests": []},
        {"result_status": 409},
        {"requests": [{"pipeline": "metadata"}]},
    ],
)
def test_missing_or_incomplete_create_evidence_fails_rust(monkeypatch, change):
    capture = capture_with_payload(monkeypatch, {**payload(), **change})
    with pytest.raises(AssertionError):
        capture.assert_destination("dbs/db/colls/orders", "order", "West US")


@pytest.mark.parametrize(
    "change",
    [
        {"region": "East US"},
        {"region": None},
        {"endpoint": ""},
        {"endpoint": "https:///"},
        {"status": 429},
    ],
)
def test_wrong_or_missing_attempt_destination_fails_rust(monkeypatch, change):
    evidence = payload()
    evidence["requests"][0].update(change)
    capture = capture_with_payload(monkeypatch, evidence)
    with pytest.raises(AssertionError):
        capture.assert_destination("dbs/db/colls/orders", "order", "West US")


def test_metadata_cannot_mask_wrong_create_route_rust(monkeypatch):
    evidence = payload()
    evidence["requests"].insert(0, {**evidence["requests"][0], "pipeline": "metadata"})
    evidence["requests"][1]["region"] = "eastus"
    evidence["request_count"] = evidence["retained_request_count"] = 2
    capture = capture_with_payload(monkeypatch, evidence)
    with pytest.raises(AssertionError, match="Create attempted"):
        capture.assert_destination("dbs/db/colls/orders", "order", "West US")


def test_success_does_not_hide_wrong_region_on_an_earlier_attempt_rust(monkeypatch):
    evidence = payload()
    evidence["requests"].insert(0, {**evidence["requests"][0], "region": "eastus", "status": 429})
    evidence["request_count"] = evidence["retained_request_count"] = 2
    capture = capture_with_payload(monkeypatch, evidence)
    with pytest.raises(AssertionError, match="Create attempted"):
        capture.assert_destination("dbs/db/colls/orders", "order", "West US")


@pytest.mark.parametrize("container,item", [("dbs/other/colls/orders", "order"), ("dbs/db/colls/orders", "stale")])
def test_other_operation_evidence_fails_rust(monkeypatch, container, item):
    capture = capture_with_payload(monkeypatch, payload())
    with pytest.raises(AssertionError, match="another create"):
        capture.assert_destination(container, item, "West US")


@pytest.mark.parametrize("count", [0, 2])
def test_missing_or_extra_native_calls_fail_rust(monkeypatch, count):
    capture = CreateRoutingCapture(monkeypatch)
    capture.calls = [("dbs/db/colls/orders", "order", payload())] * count
    with pytest.raises(AssertionError, match="exactly one"):
        capture.assert_destination("dbs/db/colls/orders", "order", "West US")


@pytest.mark.parametrize("multi_write", [False, True])
@pytest.mark.parametrize("test_data", CREATE_ITEM_TEST_DATA)
def test_expected_destination_uses_account_write_capability_rust(test_data, multi_write):
    writes = [WRITE_LOCATION, READ_LOCATION] if multi_write else [WRITE_LOCATION]
    topology = (writes, [WRITE_LOCATION, READ_LOCATION])
    before = deepcopy(topology)
    expected = test_data[-1]
    actual = expected_write_region(topology, expected)
    assert actual == normalize_region(WRITE_LOCATION if not multi_write or expected == DEFAULT_LOCATION else expected)
    assert topology == before


@pytest.mark.parametrize("topology", [None, ([], [WRITE_LOCATION, READ_LOCATION]), ([WRITE_LOCATION], [])])
def test_missing_account_topology_is_not_assumed_multi_write_rust(topology):
    with pytest.raises(AssertionError):
        expected_write_region(topology, READ_LOCATION)


@pytest.mark.parametrize("asynchronous", [False, True])
@pytest.mark.parametrize("multi_write", [False, True])
@pytest.mark.parametrize("test_data", CREATE_ITEM_TEST_DATA)
@pytest.mark.asyncio
async def test_live_matrix_keeps_overrides_native_capture_and_cleanup_rust(
    monkeypatch, test_data, multi_write, asynchronous
):
    if asynchronous:
        from azure.cosmos.aio._backend import binding_adapter as binding
        from create_item.aio import test_excluded_locations as live

        scenario = live.TestExcludedLocationsAsync()
    else:
        from azure.cosmos._backend import binding_adapter as binding
        from create_item.sync import test_excluded_locations as live

        scenario = live.TestExcludedLocations()

    topology = ([WRITE_LOCATION, READ_LOCATION] if multi_write else [WRITE_LOCATION], [WRITE_LOCATION, READ_LOCATION])
    evidence = payload()
    evidence["requests"][0]["region"] = expected_write_region(topology, test_data[-1])
    response = (201, 0, {}, b"{}", "diagnostics")
    native = (AsyncMock if asynchronous else Mock)(return_value=(response, evidence))
    monkeypatch.setattr(binding, "_binding_function_for_op", lambda op: native)
    monkeypatch.setattr(live._rust, "_debug_cached_account_regions", lambda handle: topology)
    options_seen = []

    def create(body, **options):
        options_seen.append(options)
        prepared = SimpleNamespace(
            container_link=f"dbs/{live.DATABASE_ID}/colls/{live.CONTAINER_ID}", item_id=body["id"]
        )
        return binding._binding_function_for_op("create_item")("handle", prepared)

    async def create_async(body, **options):
        await create(body, **options)
        return dict(body)

    def create_sync(body, **options):
        create(body, **options)
        return dict(body)

    container = SimpleNamespace(create_item=create_async if asynchronous else create_sync)
    client = MagicMock()
    client.__enter__.return_value = client
    client.__aenter__.return_value = client
    client.get_database_client.return_value.get_container_client.return_value = container
    client._adapter._ensure_driver_handle = (AsyncMock if asynchronous else Mock)(return_value="handle")
    factory = Mock(return_value=client)
    factory_name = "create_data_client_async" if asynchronous else "create_data_client"
    monkeypatch.setattr(live.clients, factory_name, factory)
    before = deepcopy(test_data)

    result = scenario.test_create_item_rust(test_data, monkeypatch)
    if asynchronous:
        await result
        client.__aexit__.assert_awaited_once()
    else:
        client.__exit__.assert_called_once()

    expected_options = {"tracing_enable": False}
    if test_data[1] is not None:
        expected_options["excluded_locations"] = test_data[1]
    assert options_seen == [expected_options]
    factory.assert_called_once_with(preferred_locations=live.PREFERRED_LOCATIONS, excluded_locations=test_data[0])
    native.assert_called_once()
    assert test_data == before
