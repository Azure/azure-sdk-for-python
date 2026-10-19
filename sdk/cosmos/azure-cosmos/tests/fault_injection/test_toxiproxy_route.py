# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Real read routing, downstream faults, forwarding progress, and recovery."""

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
    exceptions,
)
from azure.cosmos.aio import CosmosClient as AsyncCosmosClient
from common._parity_helpers import _binding_operation_count, _rust_fallback_count
from fault_injection._delayed_create import assert_route, emit
from fault_injection._regional_routing import (
    capture_native,
    load_account,
)
from fault_injection._toxiproxy import (
    CUTOFF_BYTES,
    READ_TIMEOUT,
    REGION,
    account_rule,
    assert_bandwidth_outcome,
    assert_latency_outcome,
    assert_persistent_cutoff_outcome,
    assert_read_outcome,
    assert_stall_outcome,
    assert_warmed_connections,
    invoke,
    large_receipt,
    proxy_account,
    wait_account,
)
from fault_injection._tcp_observer import (
    assert_cutoff_connection,
    assert_persistent_cutoffs,
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


@pytest.mark.asyncio
@pytest.mark.timeout(120)
@pytest.mark.parametrize("asynchronous", [False, True], ids=["sync", "async"])
@pytest.mark.parametrize("disable_route", [True, False], ids=["unavailable", "control"])
async def test_read_depends_on_proxy(proxy_route, proxy_target, monkeypatch, asynchronous, disable_route):
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
@pytest.mark.parametrize("proxy_route", ["observed"], indirect=True)
async def test_read_response_stall(proxy_route, proxy_target, monkeypatch, asynchronous, stall_response):
    await exercise_read(proxy_route, proxy_target, monkeypatch, asynchronous, "stall", stall_response)


@pytest.mark.asyncio
@pytest.mark.timeout(120)
@pytest.mark.parametrize("asynchronous", [False, True], ids=["sync", "async"])
@pytest.mark.parametrize("reset_connection", [True, False], ids=["reset", "control"])
@pytest.mark.parametrize("proxy_route", ["reset"], indirect=True)
async def test_read_connection_reset(proxy_route, proxy_target, monkeypatch, asynchronous, reset_connection):
    await exercise_read(proxy_route, proxy_target, monkeypatch, asynchronous, "reset", reset_connection)


@pytest.mark.asyncio
@pytest.mark.timeout(120)
@pytest.mark.parametrize("asynchronous", [False, True], ids=["sync", "async"])
@pytest.mark.parametrize("delay_ms", [0, 500, 5000], ids=["control", "slow", "late"])
@pytest.mark.parametrize("proxy_route", ["observed"], indirect=True)
async def test_read_response_latency(proxy_route, proxy_target, monkeypatch, asynchronous, delay_ms):
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
@pytest.mark.parametrize("proxy_route", ["sdk-observed"], indirect=True)
async def test_read_response_bandwidth(proxy_route, proxy_target, monkeypatch, asynchronous, rate_kbps):
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
@pytest.mark.parametrize("proxy_route", ["sdk-observed"], indirect=True)
async def test_read_response_cutoff(proxy_route, proxy_target, monkeypatch, asynchronous, cut_response):
    await exercise_read(proxy_route, proxy_target, monkeypatch, asynchronous, "cutoff", cut_response)


@pytest.mark.asyncio
@pytest.mark.timeout(120)
@pytest.mark.parametrize("asynchronous", [False, True], ids=["sync", "async"])
@pytest.mark.parametrize("cut_response", [True, False], ids=["persistent", "control"])
@pytest.mark.parametrize("proxy_route", ["sdk-observed"], indirect=True)
async def test_read_persistent_cutoff(proxy_route, proxy_target, monkeypatch, asynchronous, cut_response):
    await exercise_read(
        proxy_route,
        proxy_target,
        monkeypatch,
        asynchronous,
        "persistent_cutoff",
        cut_response,
    )


async def exercise_persistent_cutoff(
    read,
    proxy,
    identity,
    sdk_identity,
    baseline_bytes,
    inject_fault,
    asynchronous,
    records,
):
    before, sdk_before = proxy.observer.snapshot(), proxy.sdk_observer.snapshot()
    with proxy.persistent_cutoff(inject_fault):
        armed_at = time.monotonic()
        try:
            error, elapsed, started, finished = await read(
                "persistent_cutoff" if inject_fault else "control",
                must_fail=inject_fault,
            )
        finally:
            after, sdk_after = proxy.observer.snapshot(), proxy.sdk_observer.snapshot()
            configuration = proxy.request("/proxies/" + proxy.name + "/toxics")
            checked_at = time.monotonic()
            emit(
                "proxy_persistent_cutoff_observation",
                name=proxy.name,
                asynchronous=asynchronous,
                inject_fault=inject_fault,
                armed_at=armed_at,
                checked_at=checked_at,
                configuration=configuration,
                before=before,
                after=after,
                sdk_before=sdk_before,
                sdk_after=sdk_after,
                sdk_gate_open=proxy.sdk_observer.new_connections.is_set(),
                upstream_gate_open=proxy.observer.new_connections.is_set(),
            )
        assert proxy.sdk_observer.new_connections.is_set()
        assert proxy.observer.new_connections.is_set()
        assert armed_at <= started < finished <= checked_at
        source = assert_response_exchange(before, after, identity, started, finished)
        if inject_fault:
            assert len(configuration) == 1
            assert all(
                configuration[0][key] == value
                for key, value in {
                    "name": "response-limit_data",
                    "type": "limit_data",
                    "stream": "downstream",
                    "toxicity": 1.0,
                    "attributes": {"bytes": CUTOFF_BYTES},
                }.items()
            ), "Persistent fault was changed or removed before the call ended"
            progress = assert_persistent_cutoffs(
                sdk_before,
                sdk_after,
                sdk_identity,
                started,
                finished,
                CUTOFF_BYTES,
                baseline_bytes,
            )
            outcome = assert_persistent_cutoff_outcome(error, elapsed, records)
            assert source["response_bytes"] > CUTOFF_BYTES
            first = progress["first"]
        else:
            assert configuration == []
            first = assert_response_exchange(sdk_before, sdk_after, sdk_identity, started, finished)
            assert set(sdk_before) == set(sdk_after) and set(before) == set(after)
            assert sdk_after[sdk_identity]["closed_at"] is None
            assert baseline_bytes * 0.95 <= first["response_bytes"] <= baseline_bytes * 1.05
            assert len(records) == 1
            progress, outcome = {"first": first, "replacement_cutoffs": []}, "success"
        assert source["request_bytes"] == first["request_bytes"]
        assert source["first_response_after_start"] <= first["first_response_after_start"]
    emit(
        "proxy_persistent_cutoff_evidence",
        name=proxy.name,
        asynchronous=asynchronous,
        inject_fault=inject_fault,
        outcome=outcome,
        elapsed=elapsed,
        started=started,
        finished=finished,
        armed_at=armed_at,
        fault_checked_at=checked_at,
        removed_at=time.monotonic(),
        baseline_bytes=baseline_bytes,
        cutoff_bytes=CUTOFF_BYTES,
        source=source,
        progress=progress,
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
            key for key, value in sdk_after.items() if value["closed_at"] is not None and value["closed_at"] >= started
        ]
        assert closed == [sdk_identity], "More than one SDK-facing connection was interrupted"
        replacements = [value for key, value in sdk_after.items() if key not in sdk_before]
        assert replacements, "The interrupted read did not open a replacement connection"
        assert all(
            value["forwarding_started_at"] is not None and value["forwarding_started_at"] >= state["removed_at"]
            for value in replacements
        ), "Replacement traffic passed before cutoff removal"
        assert started <= state["cutoff_at"] <= state["removed_at"] < finished
        assert source["response_bytes"] > CUTOFF_BYTES
    else:
        progress = assert_response_exchange(sdk_before, sdk_after, sdk_identity, started, finished)
        assert set(before) == set(after) and set(sdk_before) == set(sdk_after)
        assert sdk_after[sdk_identity]["closed_at"] is None
        assert baseline_bytes * 0.95 <= progress["response_bytes"] <= baseline_bytes * 1.05
    assert source["request_bytes"] == progress["request_bytes"]
    assert source["first_response_after_start"] <= progress["first_response_after_start"]
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
        progress = forwarding_progress(sdk_before, sdk_after, sdk_identity, started, finished)
        assert source["first_response_after_start"] < 0.5
        assert source["first_response_after_start"] <= progress["first_response_after_start"]
        assert source["request_bytes"] == progress["request_bytes"]
        assert source["response_bytes"] >= progress["response_bytes"]
        observed_rate = assert_bandwidth_outcome(error, elapsed, progress, baseline_bytes, rate_kbps, records)
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
            assert set(after) == set(before), "Successful delay case opened another connection"
            assert after[identity]["closed_at"] is None, "Successful read connection closed"
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
        assert resets == [identity], "The fault reset more than the selected read connection"
        replacements = [
            connection
            for key, connection in after.items()
            if key not in before and connection["forwarding_started_at"] is not None
        ]
        assert replacements, "Read did not open a replacement connection"
        assert all(connection["forwarding_started_at"] >= state["removed_at"] for connection in replacements)
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
        assert set(after) == set(before), "No-fault control unexpectedly opened another connection"
        assert all(
            connection["closed_at"] is None or connection["closed_at"] < started for connection in after.values()
        ), "No-fault control unexpectedly closed a connection"
        assert_response_exchange(before, after, identity, started, finished)


async def exercise_stall(read, proxy, connection, inject_fault, asynchronous, warm_before, warm_after):
    connections_before = proxy.connection_state()
    try:
        if inject_fault:
            proxy.add_response_stall()
        observed_before = proxy.observer.snapshot()
        error, elapsed, started, finished = await read("stall" if inject_fault else "control", must_fail=inject_fault)
        proxy.assert_enabled()
        connections_after = proxy.connection_state()
        emit(
            "proxy_warmed_connections",
            name=proxy.name,
            inject_fault=inject_fault,
            before=connections_before,
            after=connections_after,
        )
        observed_after = proxy.observer.snapshot()
        evidence = assert_response_exchange(observed_before, observed_after, connection, started, finished)
        emit(
            "proxy_connection_evidence",
            name=proxy.name,
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
        if inject_fault:
            proxy.remove_response_stall()
    if inject_fault:
        assert_stall_outcome(error, elapsed, proxy.completed_transfers())


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
    if scenario in ("bandwidth", "cutoff", "persistent_cutoff"):
        item["receipt"] = large_receipt()
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
        await invoke(asynchronous, client.__aenter__ if asynchronous else client.__enter__)
        await wait_account(client, asynchronous, rule_id)
        container = client.get_database_client(database_id).get_container_client(observer.id)
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
        warm_before = traffic_observer.snapshot() if traffic_observer is not None else None
        sdk_warm_before = (
            proxy_route.sdk_observer.snapshot() if scenario in ("bandwidth", "cutoff", "persistent_cutoff") else None
        )
        await read("before")
        warm_after = traffic_observer.snapshot() if traffic_observer is not None else None
        connection = warmed_connection(warm_before, warm_after) if traffic_observer is not None else None
        if scenario in ("bandwidth", "cutoff", "persistent_cutoff"):
            sdk_warm_after = proxy_route.sdk_observer.snapshot()
            sdk_connection = warmed_connection(sdk_warm_before, sdk_warm_after)
            baseline_bytes = sum(
                event["bytes"]
                for event in exchange_events(sdk_warm_before, sdk_warm_after, sdk_connection)
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
        try:
            if scenario == "persistent_cutoff":
                await exercise_persistent_cutoff(
                    read,
                    proxy_route,
                    connection,
                    sdk_connection,
                    baseline_bytes,
                    inject_fault,
                    asynchronous,
                    records,
                )
            elif scenario == "cutoff":
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
                await exercise_latency(read, proxy_route, connection, delay_ms, asynchronous, records)
            elif scenario == "reset":
                await exercise_reset(read, proxy_route, connection, inject_fault, asynchronous)
            elif scenario == "stall":
                await exercise_stall(read, proxy_route, connection, inject_fault, asynchronous, warm_before, warm_after)
            elif scenario == "unavailable":
                if inject_fault:
                    proxy_route.set_enabled(False)
                await read("unavailable" if inject_fault else "control", must_fail=inject_fault)
            else:
                raise ValueError(f"Unknown network scenario: {scenario}")
        finally:
            if inject_fault and scenario == "unavailable":
                proxy_route.set_enabled(True)
        await read("recovered")
        stored = observer.read_item(item_id, partition_key=item_id)
        assert {field: stored[field] for field in item} == item
        if scenario in ("bandwidth", "cutoff", "persistent_cutoff"):
            emit(
                "proxy_stored_state",
                database_id=database_id,
                expected_fields={field: value for field, value in item.items() if field != "receipt"},
                receipt_bytes=len(item["receipt"]),
                receipt_sha256=hashlib.sha256(stored["receipt"].encode("ascii")).hexdigest(),
            )
        else:
            emit("proxy_stored_state", database_id=database_id, expected_fields=item)
    finally:
        await invoke(asynchronous, client.close)
