# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Regional outage contracts using simulated topology and real emulator storage."""

import asyncio
import copy
import os
import time
import uuid

import pytest
from azure.core.exceptions import ServiceRequestError, ServiceResponseError
from azure.cosmos import CosmosClient, _rust, exceptions
from azure.cosmos.aio import CosmosClient as AsyncCosmosClient
from config.diagnostics import _binding_operation_count
from fault_injection._delayed_create import assert_route, emit
from fault_injection._regional_routing import (
    READ_REGION,
    WRITE_REGION,
    READ_SECONDS,
    TIMEOUT,
    assert_destination,
    assert_fields,
    capture_native,
    emulator_endpoints,
    mock_account,
    rules,
    topology,
    wait_topology,
    wait_topology_async,
)

CASES = ("read-down", "read-envoy", "mwr-down", "all-reads-down", "all-down")


def outage_rules(case, prefix, container_id, write_endpoint, read_endpoint, inject):
    if case not in CASES:
        raise ValueError(f"Unknown regional outage case: {case}")
    multi_write = case in ("mwr-down", "all-down")
    account = topology(mock_account(), write_endpoint, read_endpoint, False)
    if multi_write:
        account["writableLocations"] = copy.deepcopy(account["readableLocations"])
        account["enableMultipleWriteLocations"] = True
    configured = rules(prefix, container_id, account)
    if multi_write:
        configured = configured[:1]
    else:
        configured.append({**configured[1], "id": prefix + "-upsert-guard", "operation_type": "UpsertItem"})
    regions = (
        (WRITE_REGION, READ_REGION)
        if case in ("all-reads-down", "all-down")
        else (WRITE_REGION,) if multi_write else (READ_REGION,)
    )
    operations = ("UpsertItem", "ReadItem") if multi_write else ("ReadItem",)
    for region in regions:
        for operation in operations:
            outcome = (
                {"status_code": 502, "delay_ms": 500}
                if case == "read-envoy"
                else {
                    "error_type": "ConnectionError",
                }
            )
            configured.append(
                {
                    "id": f"{prefix}-outage-{region}-{operation}",
                    "operation_type": operation,
                    "region": region,
                    "container_id": container_id,
                    "probability": 1.0 if inject else 0.0,
                    "hit_limit": None,
                    **outcome,
                }
            )
    return configured


def assert_fault_evidence(configured, counts, attempts, inject):
    outages = [rule for rule in configured if "-outage-" in rule["id"]]
    for rule in configured[1:]:
        rule_id = rule["id"]
        applied = sum(
            evaluation["rule_id"] == rule_id and evaluation["applied"]
            for attempt in attempts
            for evaluation in attempt["evaluations"]
        )
        assert counts[rule_id] == applied, f"Missing attempt evidence for {rule_id}"
        if "-outage-" not in rule_id or not inject:
            assert applied == 0, f"Unexpected fault application: {rule_id}"
    if inject:
        for region in {rule["region"] for rule in outages}:
            assert (
                sum(counts[rule["id"]] for rule in outages if rule["region"] == region) > 0
            ), f"The outage in {region} was not exercised"


async def exercise(request, regional_target, monkeypatch, case, inject, *, asynchronous, _backend):
    from fault_injection._regional_routing import isolate

    assert _backend == "rust"
    if isolate(request, regional_target):
        return
    database_id, observer = regional_target
    write_endpoint, read_endpoint = emulator_endpoints(os.environ["ACCOUNT_HOST"])
    prefix = "region-down-" + uuid.uuid4().hex
    configured = outage_rules(case, prefix, observer.id, write_endpoint, read_endpoint, inject)
    multi_write = case in ("mwr-down", "all-down")
    client_type = AsyncCosmosClient if asynchronous else CosmosClient
    client = client_type(
        write_endpoint,
        os.environ["ACCOUNT_KEY"],
        _backend=_backend,
        consistency_level="Session",
        preferred_locations=[WRITE_REGION, READ_REGION] if multi_write else [READ_REGION, WRITE_REGION],
        timeout=TIMEOUT,
        _fault_injection_rules=configured,
    )

    async def invoke(function, *args, **kwargs):
        return await function(*args, **kwargs) if asynchronous else function(*args, **kwargs)

    item_id = uuid.uuid4().hex
    item = {"id": item_id, "pk": item_id, "name": "sample document", "key": "value"}
    records, attempts = [], []
    try:
        if asynchronous:
            await client.__aenter__()
            await wait_topology_async(client, prefix, False, multi_write=multi_write)
        else:
            client.__enter__()
            wait_topology(client, prefix, False, multi_write=multi_write)
        handle = await invoke(client._adapter._ensure_driver_handle)
        capture_native(monkeypatch, records, asynchronous, driver_handle=handle)
        container = client.get_database_client(database_id).get_container_client(observer.id)
        await invoke(container.read, timeout=TIMEOUT)
        assert all(_rust._debug_fault_injection_rule_hit_count(handle, rule["id"]) == 0 for rule in configured[1:])

        async def measured(operation, *args, **kwargs):
            records.clear()
            before = _binding_operation_count()
            started = time.monotonic()
            error, returned = None, None
            try:
                returned = await invoke(getattr(container, operation), *args, timeout=TIMEOUT, **kwargs)
            except (ServiceRequestError, ServiceResponseError, exceptions.CosmosHttpResponseError) as caught:
                error = caught
            elapsed = time.monotonic() - started
            assert_route(before, _binding_operation_count(), "rust")
            assert records, "No native attempt diagnostics"
            attempts.extend(records)
            emit(
                "regional_outage_operation",
                case=case,
                inject=inject,
                asynchronous=asynchronous,
                operation=operation,
                elapsed=elapsed,
                error_type=None if error is None else type(error).__name__,
                error=str(error),
                attempts=records,
            )
            return returned, error, elapsed

        def success(returned, error, destination):
            assert error is None, f"Expected failover success, got {error!r}"
            assert_fields(returned, item)
            successful = [record for record in records if record["status"] in (200, 201)]
            assert successful, "No successful service attempt"
            for record in successful:
                assert_destination([record], destination, record["status"])

        if case in ("read-down", "read-envoy"):
            returned, error, _ = await measured("create_item", item)
            success(returned, error, write_endpoint)
        elif case == "all-reads-down":
            returned, error, _ = await measured("upsert_item", item)
            success(returned, error, write_endpoint)

        if inject and case in ("all-down", "all-reads-down"):
            operation = "upsert_item" if multi_write else "read_item"
            args = (item,) if multi_write else (item_id,)
            kwargs = {} if multi_write else {"partition_key": item_id}
            returned, error, elapsed = await measured(operation, *args, **kwargs)
            assert returned is None
            # Characterize the existing Rust mapping; legacy expects ServiceRequestError.
            assert isinstance(error, ServiceResponseError), f"Expected terminal transport failure, got {error!r}"
            assert isinstance(error.__cause__, _rust._DriverTransportError), "Native transport cause was lost"
            assert elapsed < TIMEOUT, "An operation deadline must not stand in for exhausted regions"
        else:
            start, reads = time.monotonic(), 0
            while time.monotonic() - start < READ_SECONDS:
                if multi_write:
                    returned, error, _ = await measured("upsert_item", item)
                    success(returned, error, read_endpoint if inject else write_endpoint)
                returned, error, _ = await measured("read_item", item_id, partition_key=item_id)
                destination = (
                    (read_endpoint if inject else write_endpoint)
                    if multi_write
                    else (write_endpoint if inject else read_endpoint)
                )
                success(returned, error, destination)
                reads += 1
                await asyncio.sleep(0.02)
            assert reads > 0
            emit("regional_outage_read_window", reads=reads, elapsed=time.monotonic() - start)

        counts = {
            rule["id"]: _rust._debug_fault_injection_rule_hit_count(handle, rule["id"]) for rule in configured[1:]
        }
        assert_fault_evidence(configured, counts, attempts, inject)
        if inject and case == "all-down":
            with pytest.raises(exceptions.CosmosResourceNotFoundError) as absent:
                observer.read_item(item_id, partition_key=item_id)
            assert absent.value.status_code == 404
        else:
            assert_fields(observer.read_item(item_id, partition_key=item_id), item)
        emit("regional_outage_result", case=case, inject=inject, asynchronous=asynchronous, hits=counts)
    finally:
        await invoke(client.close)
