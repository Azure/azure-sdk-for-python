# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Real read routing, downstream faults, forwarding progress, and recovery."""

import asyncio
import hashlib
import os
import time
import uuid

import pytest

from azure.core.exceptions import ServiceRequestError, ServiceResponseError
from azure.cosmos import (
    ConnectionPoolOptions,
    CosmosClient,
    CosmosRuntime,
    _rust,
    exceptions,
)
from azure.cosmos.aio import CosmosClient as AsyncCosmosClient
from common._parity_helpers import _binding_operation_count, _rust_fallback_count
from fault_injection._delayed_create import assert_route, emit
from fault_injection._regional_routing import (
    capture_native,
    emulator_endpoints,
    load_account,
)
from fault_injection._toxiproxy import (
    OwnedProxy,
    CUTOFF_BYTES,
    READ_TIMEOUT,
    REGION,
    account_rule,
    assert_bandwidth_outcome,
    assert_latency_outcome,
    assert_read_outcome,
    assert_stall_outcome,
    assert_warmed_connections,
    proxy_account,
)
from fault_injection._tcp_observer import (
    assert_cutoff_connection,
    assert_reset_connection,
    assert_response_exchange,
    exchange_events,
    forwarding_progress,
    warmed_connection,
)

pytestmark = [
    pytest.mark.cosmosEmulator,
    pytest.mark.skipif(
        not os.environ.get("TOXIPROXY_SERVER"),
        reason="Opt-in network test: set TOXIPROXY_SERVER to the pinned Windows x64 executable",
    ),
]
DRIVER_COMMIT = "84e2bb66c9911fa730dc9756c8fc3f9612456344"


@pytest.fixture
def proxy_route(tmp_path, request):
    endpoint = os.environ.get("ACCOUNT_HOST", "")
    emulator_endpoints(endpoint)
    assert (
        _rust.__rust_driver_commit__ == DRIVER_COMMIT
    ), "Use the verified pinned driver build"
    assert (
        os.environ.get("AZURE_COSMOS_E2E_BACKGROUND_ACCOUNT_REFRESH_INTERVAL_MS")
        == "100"
    ), "Run this selection in its own process with account refresh interval 100ms"
    server = os.environ.get("TOXIPROXY_SERVER", "")
    proxy = OwnedProxy(
        server,
        endpoint,
        "cosmos-route-" + uuid.uuid4().hex,
        tmp_path,
        observe=request.node.originalname
        in (
            "test_read_response_stall",
            "test_read_connection_reset",
            "test_read_response_latency",
            "test_read_response_bandwidth",
            "test_read_response_cutoff",
        ),
    )
    request.addfinalizer(proxy.close)
    proxy.start()
    if request.node.originalname == "test_read_connection_reset":
        proxy.prepare_reset()
    if request.node.originalname in (
        "test_read_response_bandwidth",
        "test_read_response_cutoff",
    ):
        proxy.observe_sdk_side()
    return proxy


@pytest.fixture
def proxy_target(proxy_route, owned_target):
    return owned_target


async def invoke(asynchronous, function, *args, **kwargs):
    if asynchronous:
        return await function(*args, **kwargs)
    return function(*args, **kwargs)


async def wait_account(client, asynchronous, rule_id):
    handle = await invoke(asynchronous, client._adapter._ensure_driver_handle)
    deadline = time.monotonic() + 30
    while True:
        regions = _rust._debug_cached_account_regions(handle)
        hits = _rust._debug_fault_injection_rule_hit_count(handle, rule_id)
        if regions == (["westus"], ["westus"]) and hits > 0:
            emit(
                "proxy_account_ready",
                rule_id=rule_id,
                hits=hits,
                simulated_metadata=True,
            )
            return
        assert (
            time.monotonic() < deadline
        ), f"Proxy topology not observed: {regions}; hits={hits}"
        await asyncio.sleep(0.05)


@pytest.mark.asyncio
@pytest.mark.timeout(120)
@pytest.mark.parametrize("asynchronous", [False, True], ids=["sync", "async"])
@pytest.mark.parametrize("disable_route", [True, False], ids=["unavailable", "control"])
async def test_read_depends_on_proxy(
    proxy_route, proxy_target, monkeypatch, asynchronous, disable_route
):
    await exercise_read(
        proxy_route,
        proxy_target,
        monkeypatch,
        asynchronous,
        "unavailable",
        disable_route,
    )


@pytest.mark.asyncio
@pytest.mark.timeout(120)
@pytest.mark.parametrize("asynchronous", [False, True], ids=["sync", "async"])
@pytest.mark.parametrize("stall_response", [True, False], ids=["stalled", "control"])
async def test_read_response_stall(
    proxy_route, proxy_target, monkeypatch, asynchronous, stall_response
):
    await exercise_read(
        proxy_route, proxy_target, monkeypatch, asynchronous, "stall", stall_response
    )


@pytest.mark.asyncio
@pytest.mark.timeout(120)
@pytest.mark.parametrize("asynchronous", [False, True], ids=["sync", "async"])
@pytest.mark.parametrize("reset_connection", [True, False], ids=["reset", "control"])
async def test_read_connection_reset(
    proxy_route, proxy_target, monkeypatch, asynchronous, reset_connection
):
    await exercise_read(
        proxy_route, proxy_target, monkeypatch, asynchronous, "reset", reset_connection
    )


@pytest.mark.asyncio
@pytest.mark.timeout(120)
@pytest.mark.parametrize("asynchronous", [False, True], ids=["sync", "async"])
@pytest.mark.parametrize("delay_ms", [0, 500, 5000], ids=["control", "slow", "late"])
async def test_read_response_latency(
    proxy_route, proxy_target, monkeypatch, asynchronous, delay_ms
):
    await exercise_read(
        proxy_route,
        proxy_target,
        monkeypatch,
        asynchronous,
        "latency",
        delay_ms > 0,
        delay_ms=delay_ms,
    )


@pytest.mark.asyncio
@pytest.mark.timeout(120)
@pytest.mark.parametrize("asynchronous", [False, True], ids=["sync", "async"])
@pytest.mark.parametrize("rate_kbps", [0, 64, 16], ids=["control", "moderate", "slow"])
async def test_read_response_bandwidth(
    proxy_route, proxy_target, monkeypatch, asynchronous, rate_kbps
):
    await exercise_read(
        proxy_route,
        proxy_target,
        monkeypatch,
        asynchronous,
        "bandwidth",
        rate_kbps > 0,
        rate_kbps=rate_kbps,
    )


@pytest.mark.asyncio
@pytest.mark.timeout(120)
@pytest.mark.parametrize("asynchronous", [False, True], ids=["sync", "async"])
@pytest.mark.parametrize("cut_response", [True, False], ids=["cutoff", "control"])
async def test_read_response_cutoff(
    proxy_route, proxy_target, monkeypatch, asynchronous, cut_response
):
    await exercise_read(
        proxy_route, proxy_target, monkeypatch, asynchronous, "cutoff", cut_response
    )


async def exercise_cutoff(
    read,
    proxy,
    identity,
    sdk_identity,
    baseline_bytes,
    inject_fault,
    asynchronous,
    records,
):
    assert baseline_bytes >= 64000
    before, sdk_before = proxy.observer.snapshot(), proxy.sdk_observer.snapshot()
    state = None
    if inject_fault:
        with proxy.single_cutoff(sdk_identity) as state:
            _, _, started, finished = await read("cutoff", transport_retry=True)
    else:
        _, _, started, finished = await read("control")
        assert len(records) == 1
    after, sdk_after = proxy.observer.snapshot(), proxy.sdk_observer.snapshot()
    source = assert_response_exchange(before, after, identity, started, finished)
    if inject_fault:
        progress = assert_cutoff_connection(
            sdk_before,
            sdk_after,
            sdk_identity,
            started,
            finished,
            CUTOFF_BYTES,
            baseline_bytes,
        )
        closed = [
            key
            for key, value in sdk_after.items()
            if value["closed_at"] is not None and value["closed_at"] >= started
        ]
        assert closed == [
            sdk_identity
        ], "More than one SDK-facing connection was interrupted"
        replacements = [
            value for key, value in sdk_after.items() if key not in sdk_before
        ]
        assert (
            replacements
        ), "The interrupted read did not open a replacement connection"
        assert all(
            value["forwarding_started_at"] is not None
            and value["forwarding_started_at"] >= state["removed_at"]
            for value in replacements
        ), "Replacement traffic passed before cutoff removal"
        assert started <= state["cutoff_at"] <= state["removed_at"] < finished
        assert source["response_bytes"] > CUTOFF_BYTES
    else:
        progress = assert_response_exchange(
            sdk_before, sdk_after, sdk_identity, started, finished
        )
        assert set(before) == set(after) and set(sdk_before) == set(sdk_after)
        assert sdk_after[sdk_identity]["closed_at"] is None
        assert (
            baseline_bytes * 0.95 <= progress["response_bytes"] <= baseline_bytes * 1.05
        )
    assert source["request_bytes"] == progress["request_bytes"]
    assert (
        source["first_response_after_start"] <= progress["first_response_after_start"]
    )
    proxy.assert_enabled()
    emit(
        "proxy_cutoff_evidence",
        name=proxy.name,
        asynchronous=asynchronous,
        inject_fault=inject_fault,
        cutoff_bytes=CUTOFF_BYTES,
        baseline_bytes=baseline_bytes,
        started=started,
        finished=finished,
        before=before,
        after=after,
        sdk_before=sdk_before,
        sdk_after=sdk_after,
        source=source,
        progress=progress,
        cutoff_state=state,
    )


async def exercise_bandwidth(
    read,
    proxy,
    identity,
    sdk_identity,
    baseline_bytes,
    rate_kbps,
    asynchronous,
    records,
):
    with proxy.response_bandwidth(rate_kbps):
        before = proxy.observer.snapshot()
        sdk_before = proxy.sdk_observer.snapshot()
        error, elapsed, started, finished = await read(
            "bandwidth" if rate_kbps else "control", must_fail=rate_kbps == 16
        )
        after = proxy.observer.snapshot()
        sdk_after = proxy.sdk_observer.snapshot()
        source = assert_response_exchange(before, after, identity, started, finished)
        progress = forwarding_progress(
            sdk_before, sdk_after, sdk_identity, started, finished
        )
        assert source["first_response_after_start"] < 0.5
        assert (
            source["first_response_after_start"]
            <= progress["first_response_after_start"]
        )
        assert source["request_bytes"] == progress["request_bytes"]
        assert source["response_bytes"] >= progress["response_bytes"]
        observed_rate = assert_bandwidth_outcome(
            error, elapsed, progress, baseline_bytes, rate_kbps, records
        )
        if rate_kbps != 16:
            assert sdk_after[sdk_identity]["closed_at"] is None
        proxy.assert_enabled()
        emit(
            "proxy_bandwidth_evidence",
            name=proxy.name,
            asynchronous=asynchronous,
            rate_kbps=rate_kbps,
            started=started,
            finished=finished,
            baseline_bytes=baseline_bytes,
            before=before,
            after=after,
            sdk_before=sdk_before,
            sdk_after=sdk_after,
            source=source,
            progress=progress,
            observed_bytes_per_second=observed_rate,
        )


async def exercise_latency(read, proxy, identity, delay_ms, asynchronous, records):
    with proxy.response_latency(delay_ms):
        before = proxy.observer.snapshot()
        error, elapsed, started, finished = await read(
            "latency" if delay_ms else "control",
            must_fail=delay_ms > READ_TIMEOUT * 1000,
        )
        after = proxy.observer.snapshot()
        exchange = assert_response_exchange(before, after, identity, started, finished)
        if delay_ms <= READ_TIMEOUT * 1000:
            assert set(after) == set(
                before
            ), "Successful delay case opened another connection"
            assert (
                after[identity]["closed_at"] is None
            ), "Successful read connection closed"
        elapsed_after_response = assert_latency_outcome(
            error, elapsed, exchange["first_response_after_start"], delay_ms, records
        )
        proxy.assert_enabled()
        emit(
            "proxy_latency_evidence",
            name=proxy.name,
            asynchronous=asynchronous,
            delay_ms=delay_ms,
            started=started,
            finished=finished,
            before=before,
            after=after,
            exchange=exchange,
            elapsed_after_response=elapsed_after_response,
        )


async def exercise_reset(read, proxy, identity, inject_fault, asynchronous):
    before = proxy.observer.snapshot()
    if inject_fault:
        with proxy.single_reset(identity) as state:
            _, _, started, finished = await read("reset", transport_retry=True)
        after = proxy.observer.snapshot()
        exchange = assert_reset_connection(before, after, identity, started, finished)
        resets = [
            key
            for key, connection in after.items()
            if connection["end_reason"] == "ConnectionResetError"
            and connection["end_direction"] == "upstream"
            and connection["closed_at"] >= started
        ]
        assert resets == [
            identity
        ], "The fault reset more than the selected read connection"
        replacements = [
            connection
            for key, connection in after.items()
            if key not in before and connection["forwarding_started_at"] is not None
        ]
        assert replacements, "Read did not open a replacement connection"
        assert all(
            connection["forwarding_started_at"] >= state["removed_at"]
            for connection in replacements
        )
        assert state["reset_at"] <= state["removed_at"] < finished
        emit(
            "proxy_reset_evidence",
            name=proxy.name,
            asynchronous=asynchronous,
            started=started,
            finished=finished,
            before=before,
            after=after,
            exchange=exchange,
            reset_state=state,
        )
    else:
        _, _, started, finished = await read("control")
        after = proxy.observer.snapshot()
        assert set(after) == set(
            before
        ), "No-fault control unexpectedly opened another connection"
        assert all(
            connection["closed_at"] is None or connection["closed_at"] < started
            for connection in after.values()
        ), "No-fault control unexpectedly closed a connection"
        assert_response_exchange(before, after, identity, started, finished)


async def exercise_read(
    proxy_route,
    proxy_target,
    monkeypatch,
    asynchronous,
    scenario,
    inject_fault,
    delay_ms=0,
    rate_kbps=0,
):
    database_id, observer = proxy_target
    item_id = uuid.uuid4().hex
    item = {"id": item_id, "pk": item_id, "name": "order-42", "state": "confirmed"}
    if scenario in ("bandwidth", "cutoff"):
        item["receipt"] = "".join(
            hashlib.sha256(index.to_bytes(4, "big")).hexdigest()
            for index in range(1000)
        )
    observer.create_item(item)
    endpoint, key = os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"]
    read_endpoint = proxy_route.sdk_endpoint
    account = proxy_account(load_account(endpoint, key), read_endpoint)
    rule_id = proxy_route.name + "-account"
    records = []
    capture_native(monkeypatch, records, asynchronous=asynchronous)
    options = ConnectionPoolOptions(
        proxy_allowed=False,
        connection_timeout=0.5,
        data_http_request_timeout=1 if scenario == "unavailable" else 10,
        metadata_http_request_timeout=3 if scenario == "unavailable" else 10,
    )
    runtime = await CosmosRuntime.create_async(connection_pool=options)
    client_type = AsyncCosmosClient if asynchronous else CosmosClient
    client = client_type(
        read_endpoint,
        key,
        _backend="rust",
        runtime=runtime,
        consistency_level="Session",
        preferred_locations=[REGION],
        retry_throttle_total=0,
        _fault_injection_rules=[account_rule(rule_id, account)],
    )
    try:
        await invoke(
            asynchronous, client.__aenter__ if asynchronous else client.__enter__
        )
        await wait_account(client, asynchronous, rule_id)
        container = client.get_database_client(database_id).get_container_client(
            observer.id
        )
        await invoke(asynchronous, container.read, timeout=30)
        await invoke(
            asynchronous,
            container.read_item,
            item_id,
            partition_key=item_id,
            timeout=30,
        )

        async def read(phase, must_fail=False, transport_retry=False):
            records.clear()
            before = (_binding_operation_count(), _rust_fallback_count())
            started = time.monotonic()
            returned, error = None, None
            try:
                returned = await invoke(
                    asynchronous,
                    container.read_item,
                    item_id,
                    partition_key=item_id,
                    timeout=READ_TIMEOUT,
                )
            except (
                ServiceRequestError,
                ServiceResponseError,
                exceptions.CosmosHttpResponseError,
                exceptions.CosmosClientTimeoutError,
            ) as caught:
                error = caught
            finished = time.monotonic()
            elapsed = finished - started
            after = (_binding_operation_count(), _rust_fallback_count())
            emit(
                "proxy_read",
                phase=phase,
                asynchronous=asynchronous,
                disable_route=scenario == "unavailable" and inject_fault,
                scenario=scenario,
                inject_fault=inject_fault,
                delay_ms=delay_ms if scenario == "latency" else None,
                rate_kbps=rate_kbps if scenario == "bandwidth" else None,
                elapsed=elapsed,
                attempts=records,
                endpoint=read_endpoint,
                error_type=None if error is None else type(error).__name__,
                binding_delta=after[0] - before[0],
                fallback_delta=after[1] - before[1],
            )
            assert_route(before, after, "rust")
            assert_read_outcome(
                returned,
                error,
                elapsed,
                records,
                read_endpoint,
                item,
                must_fail,
                transport_retry=transport_retry,
            )
            return error, elapsed, started, finished

        traffic_observer = proxy_route.observer
        warm_before = (
            traffic_observer.snapshot() if traffic_observer is not None else None
        )
        sdk_warm_before = (
            proxy_route.sdk_observer.snapshot()
            if scenario in ("bandwidth", "cutoff")
            else None
        )
        await read("before")
        warm_after = (
            traffic_observer.snapshot() if traffic_observer is not None else None
        )
        connection = (
            warmed_connection(warm_before, warm_after)
            if traffic_observer is not None
            else None
        )
        if scenario in ("bandwidth", "cutoff"):
            sdk_warm_after = proxy_route.sdk_observer.snapshot()
            sdk_connection = warmed_connection(sdk_warm_before, sdk_warm_after)
            baseline_bytes = sum(
                event["bytes"]
                for event in exchange_events(
                    sdk_warm_before, sdk_warm_after, sdk_connection
                )
                if event["direction"] == "downstream"
            )
            emit(
                "proxy_" + scenario + "_warm",
                name=proxy_route.name,
                sdk_before=sdk_warm_before,
                sdk_after=sdk_warm_after,
                sdk_connection=sdk_connection,
                emulator_connection=connection,
                baseline_bytes=baseline_bytes,
                receipt_bytes=len(item["receipt"]),
            )
        connections_before = (
            proxy_route.connection_state() if scenario == "stall" else None
        )
        try:
            if scenario == "reset":
                await exercise_reset(
                    read, proxy_route, connection, inject_fault, asynchronous
                )
            elif inject_fault:
                if scenario == "unavailable":
                    proxy_route.set_enabled(False)
                elif scenario == "stall":
                    proxy_route.add_response_stall()
            observed_before = (
                traffic_observer.snapshot() if traffic_observer is not None else None
            )
            if scenario == "cutoff":
                await exercise_cutoff(
                    read,
                    proxy_route,
                    connection,
                    sdk_connection,
                    baseline_bytes,
                    inject_fault,
                    asynchronous,
                    records,
                )
            elif scenario == "bandwidth":
                await exercise_bandwidth(
                    read,
                    proxy_route,
                    connection,
                    sdk_connection,
                    baseline_bytes,
                    rate_kbps,
                    asynchronous,
                    records,
                )
            elif scenario == "latency":
                await exercise_latency(
                    read, proxy_route, connection, delay_ms, asynchronous, records
                )
            elif scenario != "reset":
                error, elapsed, started, finished = await read(
                    scenario if inject_fault else "control", must_fail=inject_fault
                )
            if scenario == "stall":
                proxy_route.assert_enabled()
                connections_after = proxy_route.connection_state()
                emit(
                    "proxy_warmed_connections",
                    name=proxy_route.name,
                    inject_fault=inject_fault,
                    before=connections_before,
                    after=connections_after,
                )
                observed_after = traffic_observer.snapshot()
                evidence = assert_response_exchange(
                    observed_before,
                    observed_after,
                    connection,
                    started,
                    finished,
                )
                emit(
                    "proxy_connection_evidence",
                    name=proxy_route.name,
                    inject_fault=inject_fault,
                    asynchronous=asynchronous,
                    started=started,
                    finished=finished,
                    warm_before=warm_before,
                    warm_after=warm_after,
                    before=observed_before,
                    after=observed_after,
                    exchange=evidence,
                )
                if inject_fault:
                    assert (
                        evidence["first_response_after_start"] < READ_TIMEOUT / 2
                    ), "Returning response traffic was not observed before the timeout approached"
                else:
                    assert_warmed_connections(connections_before, connections_after)
        finally:
            if inject_fault and scenario in ("unavailable", "stall"):
                if scenario == "unavailable":
                    proxy_route.set_enabled(True)
                else:
                    proxy_route.remove_response_stall()
        if scenario == "stall" and inject_fault:
            transfers = proxy_route.completed_transfers()
            assert_stall_outcome(error, elapsed, transfers)
        await read("recovered")
        stored = observer.read_item(item_id, partition_key=item_id)
        assert {field: stored[field] for field in item} == item
        if scenario in ("bandwidth", "cutoff"):
            emit(
                "proxy_stored_state",
                database_id=database_id,
                expected_fields={
                    field: value for field, value in item.items() if field != "receipt"
                },
                receipt_bytes=len(item["receipt"]),
                receipt_sha256=hashlib.sha256(
                    stored["receipt"].encode("ascii")
                ).hexdigest(),
            )
        else:
            emit("proxy_stored_state", database_id=database_id, expected_fields=item)
    finally:
        await invoke(asynchronous, client.close)
