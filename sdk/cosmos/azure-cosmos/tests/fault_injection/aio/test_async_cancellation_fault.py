# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Real task cancellation across Python, PyO3, and a delayed Rust read."""
import asyncio
import os
import time
import uuid

import pytest

from azure.cosmos.aio import CosmosClient
from common._parity_helpers import _binding_operation_count, _rust_fallback_count
from fault_injection._async_cancellation import (
    CANCELLATION_ALLOWANCE, OPERATION_TIMEOUT, assert_cancelled, cancellation_rule,
    capture_read_lifecycle, wait_for_evidence,
)
from fault_injection._delayed_create import assert_route, emit

pytestmark = pytest.mark.cosmosEmulator


@pytest.mark.asyncio
@pytest.mark.timeout(90)
@pytest.mark.parametrize("inject", [True, False], ids=["cancel-delayed-read", "no-injection"])
async def test_cancelled_read_drops_native_future_and_client_recovers_rust(owned_target, monkeypatch, inject):
    database_id, observer = owned_target
    item_id = uuid.uuid4().hex
    item = {"id": item_id, "pk": item_id, "name": "order-17", "state": "confirmed"}
    await asyncio.to_thread(observer.create_item, item)
    rule_id = "cancel-read-" + uuid.uuid4().hex
    async with CosmosClient(
        os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"],
        _backend="rust", consistency_level="Session",
        _fault_injection_rules=[cancellation_rule(rule_id, observer.id, inject)],
    ) as client:
        container = client.get_database_client(database_id).get_container_client(observer.id)
        await container.read(timeout=30)
        await client._adapter.get_container_metadata(container.container_link, deadline=time.monotonic() + 30)
        assert await client._adapter._debug_fault_injection_rule_hit_count(rule_id) == 0
        probes = capture_read_lifecycle(monkeypatch)
        before = (_binding_operation_count(), _rust_fallback_count())
        pending = asyncio.create_task(container.read_item(item_id, partition_key=item_id, timeout=OPERATION_TIMEOUT))
        error, returned, started_status = None, None, None
        try:
            if inject:
                async def fault_started():
                    return await client._adapter._debug_fault_injection_rule_hit_count(rule_id) == 1

                await wait_for_evidence(fault_started, 2.0, "The delayed native read never started")
                assert len(probes) == 1
                started_status = probes[0].status
                assert started_status == "running" and not pending.done()
                start = time.perf_counter()
                assert pending.cancel()
                done, _ = await asyncio.wait({pending}, timeout=CANCELLATION_ALLOWANCE)
                assert pending in done, "The Python caller remained blocked after cancellation"
                try:
                    returned = await pending
                except asyncio.CancelledError as caught:
                    error = caught

                async def native_stopped():
                    return probes[0].status == "dropped"

                await wait_for_evidence(native_stopped, CANCELLATION_ALLOWANCE, "Native read survived cancellation")
                elapsed = time.perf_counter() - start
                assert_cancelled(error, probes[0].status, elapsed)
                assert returned is None
            else:
                start = time.perf_counter()
                done, _ = await asyncio.wait({pending}, timeout=2.0)
                assert pending in done, "The no-injection control did not complete"
                returned = await pending
                elapsed = time.perf_counter() - start
                assert len(probes) == 1 and probes[0].status == "completed"
                assert {field: returned[field] for field in item} == item

            after = (_binding_operation_count(), _rust_fallback_count())
            hits = await client._adapter._debug_fault_injection_rule_hit_count(rule_id)
            emit("async_cancellation", surface="async", database_id=database_id, inject=inject,
                 hits=hits, elapsed=elapsed, started_status=started_status, native_status=probes[0].status,
                 error_type=None if error is None else type(error).__name__,
                 binding_delta=after[0] - before[0], fallback_delta=after[1] - before[1])
            assert_route(before, after, "rust")
            assert hits == (1 if inject else 0)

            recovery_before = (_binding_operation_count(), _rust_fallback_count())
            recovered = await container.read_item(item_id, partition_key=item_id, timeout=OPERATION_TIMEOUT)
            recovery_after = (_binding_operation_count(), _rust_fallback_count())
            assert_route(recovery_before, recovery_after, "rust")
            assert len(probes) == 2 and probes[1].status == "completed"
            assert probes[0].status == ("dropped" if inject else "completed")
            assert {field: recovered[field] for field in item} == item
            assert await client._adapter._debug_fault_injection_rule_hit_count(rule_id) == hits
            emit("same_client_recovery", database_id=database_id, inject=inject,
                 first_native_status=probes[0].status, recovery_native_status=probes[1].status,
                 fields={field: recovered[field] for field in item},
                 binding_delta=recovery_after[0] - recovery_before[0],
                 fallback_delta=recovery_after[1] - recovery_before[1])
            stored = await asyncio.to_thread(observer.read_item, item_id, partition_key=item_id)
            assert {field: stored[field] for field in item} == item
            emit("stored_state", database_id=database_id, inject=inject, item_id=item_id,
                 fields={field: stored[field] for field in item})
        finally:
            if not pending.done():
                pending.cancel()
            done, _ = await asyncio.wait({pending}, timeout=2.0)
            assert pending in done, "Owned Python read task did not terminate"
            # Retrieve cancellation/failure even when an earlier assertion failed.
            await asyncio.gather(pending, return_exceptions=True)
