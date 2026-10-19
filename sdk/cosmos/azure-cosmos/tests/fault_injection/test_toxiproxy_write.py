# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Compare the customer write outcome with independently observed stored state."""

import hashlib
import os
import time
import uuid
import threading
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager, nullcontext

import pytest
from azure.core.exceptions import ServiceRequestError, ServiceResponseError
from azure.cosmos import ConnectionPoolOptions, CosmosClient, CosmosRuntime, exceptions
from azure.cosmos.aio import CosmosClient as AsyncCosmosClient
from common._parity_helpers import _binding_operation_count, _rust_fallback_count
from fault_injection._delayed_create import assert_route, emit
from fault_injection._regional_routing import (
    assert_fields,
    capture_native,
    load_account,
)
from fault_injection._tcp_observer import (
    assert_cutoff_connection,
    assert_response_exchange,
    exchange_events,
    warmed_connection,
)
from fault_injection._toxiproxy import (
    CUTOFF_BYTES,
    READ_TIMEOUT,
    REGION,
    account_rule,
    invoke,
    large_receipt,
    proxy_account,
    wait_account,
)

pytestmark = [
    pytest.mark.cosmosEmulator,
    pytest.mark.skipif(
        not os.environ.get("TOXIPROXY_SERVER"),
        reason="Opt-in pinned Toxiproxy network test",
    ),
]
PATCH = [{"op": "incr", "path": "/refund_attempts", "value": 1}]


@contextmanager
def cutoff_after_commit(proxy, observer, target, expected, identity, source_identity):
    """Hold the committed response on its forwarding thread until the controller arms the cutoff.

    Preliminary reads pass unchanged. Release the callback before joining it on teardown.
    """
    committed, armed, done = threading.Event(), threading.Event(), threading.Event()
    state = {}

    def before_forward(connection, direction):
        if connection != source_identity or direction != "downstream" or committed.is_set():
            return
        stored = observer.read_item(target, partition_key=target)
        if stored["refund_attempts"] == 0:
            return
        assert_fields(stored, expected)
        state.update(
            committed_at=time.monotonic(),
            committed_counter=stored["refund_attempts"],
            before=proxy.sdk_observer.snapshot(),
        )
        committed.set()
        assert armed.wait(READ_TIMEOUT), "Committed response was not released after arming"

    def arm():
        deadline = time.monotonic() + READ_TIMEOUT
        while not committed.wait(0.005):
            assert (
                not done.is_set() and time.monotonic() < deadline
            ), "No committed write observed before returning traffic"
        with proxy.single_cutoff(identity) as cutoff:
            state["cutoff"] = cutoff
            armed.set()
            assert done.wait(READ_TIMEOUT + 1), "Write did not finish after committed-response cutoff"

    with proxy.observer.forwarding_callback(before_forward):
        with ThreadPoolExecutor(max_workers=1, thread_name_prefix="cosmos-commit-cutoff") as executor:
            worker = executor.submit(arm)
            try:
                yield state
            finally:
                done.set()
                try:
                    worker.result(timeout=READ_TIMEOUT + 2)
                finally:
                    armed.set()


@pytest.mark.asyncio
@pytest.mark.parametrize("operation", ["create", "patch"])
@pytest.mark.parametrize("asynchronous", [False, True], ids=["sync", "async"])
@pytest.mark.parametrize("inject_fault", [True, False], ids=["cutoff", "control"])
@pytest.mark.parametrize("proxy_route", ["sdk-observed"], indirect=True)
async def test_lost_write_response(proxy_route, proxy_target, monkeypatch, operation, asynchronous, inject_fault):
    database_id, observer = proxy_target
    target = uuid.uuid4().hex
    item = {
        "id": target,
        "pk": target,
        "name": "order-42",
        "refund_attempts": 0,
        "receipt": large_receipt(),
    }
    expected = dict(item, refund_attempts=1) if operation == "patch" else item.copy()
    # Execute the no-fault legacy baseline, then restore the same starting state.
    legacy = observer.create_item(item)
    if operation == "patch":
        legacy = observer.patch_item(target, partition_key=target, patch_operations=PATCH)
    assert_fields(legacy, expected)
    assert_fields(observer.read_item(target, partition_key=target), expected)
    observer.delete_item(target, partition_key=target)
    with pytest.raises(exceptions.CosmosResourceNotFoundError):
        observer.read_item(target, partition_key=target)
    if operation == "patch":
        observer.create_item(item)
        assert_fields(observer.read_item(target, partition_key=target), item)
    emit(
        "proxy_write_legacy_baseline",
        operation=operation,
        name=proxy_route.name,
        same_inputs=True,
        fault_injected=False,
    )
    warm = dict(item, id=uuid.uuid4().hex)
    observer.create_item(warm)
    records = []
    capture_native(
        monkeypatch,
        records,
        asynchronous,
    )
    endpoint = proxy_route.sdk_endpoint
    key = os.environ["ACCOUNT_KEY"]
    account = proxy_account(load_account(os.environ["ACCOUNT_HOST"], key), endpoint)
    rule_id = proxy_route.name + "-account"
    runtime = await CosmosRuntime.create_async(
        connection_pool=ConnectionPoolOptions(
            proxy_allowed=False,
            connection_timeout=0.5,
            data_http_request_timeout=10,
            metadata_http_request_timeout=10,
        )
    )
    client = (AsyncCosmosClient if asynchronous else CosmosClient)(
        endpoint,
        key,
        _backend="rust",
        runtime=runtime,
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
            warm["id"],
            partition_key=target,
            timeout=30,
        )
        before_warm = proxy_route.sdk_observer.snapshot()
        source_before_warm = proxy_route.observer.snapshot()
        await invoke(
            asynchronous,
            container.read_item,
            warm["id"],
            partition_key=target,
            timeout=READ_TIMEOUT,
        )
        after_warm = proxy_route.sdk_observer.snapshot()
        identity = warmed_connection(before_warm, after_warm)
        source_identity = warmed_connection(source_before_warm, proxy_route.observer.snapshot())
        baseline = sum(
            e["bytes"]
            for e in after_warm[identity]["events"][len(before_warm[identity]["events"]) :]
            if e["direction"] == "downstream"
        )
        before = proxy_route.sdk_observer.snapshot()
        records.clear()
        counters = (_binding_operation_count(), _rust_fallback_count())
        returned, error, state = None, None, None

        async def write():
            if operation == "create":
                return await invoke(asynchronous, container.create_item, item, timeout=READ_TIMEOUT)
            return await invoke(
                asynchronous,
                container.patch_item,
                target,
                partition_key=target,
                patch_operations=PATCH,
                timeout=READ_TIMEOUT,
            )

        fault = nullcontext()
        if inject_fault:
            fault = (
                cutoff_after_commit(proxy_route, observer, target, expected, identity, source_identity)
                if operation == "patch"
                else proxy_route.single_cutoff(identity)
            )
        with fault as state:
            started = time.monotonic()
            try:
                returned = await write()
            except (
                ServiceRequestError,
                ServiceResponseError,
                exceptions.CosmosHttpResponseError,
            ) as caught:
                error = caught
            finished = time.monotonic()
        after = proxy_route.sdk_observer.snapshot()
        after_counters = (_binding_operation_count(), _rust_fallback_count())
        emit(
            "proxy_write_result",
            name=proxy_route.name,
            operation=operation,
            asynchronous=asynchronous,
            inject_fault=inject_fault,
            elapsed=finished - started,
            error_type=None if error is None else type(error).__name__,
            error_status=getattr(error, "status_code", None),
            attempts=records if operation == "create" else None,
            binding_delta=after_counters[0] - counters[0],
            fallback_delta=after_counters[1] - counters[1],
            before=before,
            after=after,
            connection=identity,
            started=started,
            finished=finished,
            baseline_bytes=baseline,
            cutoff_state=state,
            write_attempt_diagnostics_available=operation == "create",
        )
        assert_route(counters, after_counters, "rust")
        assert 0 < finished - started < READ_TIMEOUT + 0.5
        if operation == "create":
            assert records, "No create-attempt diagnostics"
        else:
            assert records == [], "PATCH attempt diagnostics are not exposed by this snapshot"
        assert all(r["endpoint"] == endpoint and not any(e["applied"] for e in r["evaluations"]) for r in records)
        if inject_fault:
            if operation == "create":
                assert_cutoff_connection(before, after, identity, started, finished, CUTOFF_BYTES, baseline)
                assert records[0]["status"] == 503 and records[0]["sub_status"] == 20003
                assert returned is None and isinstance(error, exceptions.CosmosResourceExistsError)
                assert [(r["status"], r["sub_status"]) for r in records] == [
                    (503, 20003),
                    (409, 0),
                ]
            else:
                events = exchange_events(state["before"], after, identity)
                assert events and all(e["direction"] == "downstream" for e in events)
                assert sum(e["bytes"] for e in events) == CUTOFF_BYTES
                closed = after[identity]
                assert (
                    closed["end_reason"],
                    closed["end_direction"],
                    closed["end_operation"],
                ) == ("downstream_eof", "downstream", "recv")
                assert state["committed_counter"] == 1
                assert (
                    started <= state["committed_at"] <= state["cutoff"]["armed_at"] <= closed["closed_at"] <= finished
                )
                assert all(state["cutoff"]["armed_at"] <= e["at"] <= closed["closed_at"] for e in events)
                assert error is None, f"Tracked increment did not recover: {error}"
                assert_fields(returned, expected)
        else:
            assert error is None
            assert_fields(returned, expected)
            if operation == "create":
                assert len(records) == 1 and records[0]["status"] == 201
            exchange = assert_response_exchange(before, after, identity, started, finished)
            assert exchange["response_bytes"] >= len(expected["receipt"])
        stored = observer.read_item(target, partition_key=target)
        assert_fields(stored, expected)
        recovered = await invoke(
            asynchronous,
            container.read_item,
            target,
            partition_key=target,
            timeout=READ_TIMEOUT,
        )
        assert_fields(recovered, expected)
        emit(
            "proxy_write_stored_state",
            name=proxy_route.name,
            operation=operation,
            asynchronous=asynchronous,
            inject_fault=inject_fault,
            refund_attempts=stored["refund_attempts"],
            receipt_bytes=len(stored["receipt"]),
            receipt_sha256=hashlib.sha256(stored["receipt"].encode()).hexdigest(),
            same_client_read_passed=True,
            independent_read_passed=True,
        )
    finally:
        await invoke(asynchronous, client.close)
