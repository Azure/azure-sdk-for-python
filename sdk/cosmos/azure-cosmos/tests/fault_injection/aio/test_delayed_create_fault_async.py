# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Adapted from test_fault_injection_transport_async.test_throws_injected_error_async.

Keep the original delay/status expectations through the async public API.
"""
import asyncio
import os
import time
import uuid

import pytest

from azure.cosmos import exceptions
from azure.cosmos.aio import CosmosClient
from common._parity_helpers import _binding_operation_count, _rust_fallback_count
from fault_injection._delayed_create import (
    OPERATION_TIMEOUT, assert_control, assert_failure, assert_route, create_rule, emit,
)

pytestmark = pytest.mark.cosmosEmulator


@pytest.mark.asyncio
@pytest.mark.timeout(180)
@pytest.mark.parametrize("inject", [True, False], ids=["delayed-502-rust", "no-injection-rust"])
async def test_throws_injected_error_async_rust(owned_target, inject):
    database_id, owned_container = owned_target
    item_id = uuid.uuid4().hex
    item = {"id": item_id, "pk": item_id, "name": "sample document", "key": "value"}
    rule_id = "create-502-" + uuid.uuid4().hex
    async with CosmosClient(
        os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"],
        _backend="rust", consistency_level="Session",
        _fault_injection_rules=[create_rule(rule_id, owned_container.id, inject)],
    ) as client:
        container = client.get_database_client(database_id).get_container_client(owned_container.id)
        await container.read()
        assert await client._adapter._debug_fault_injection_rule_hit_count(rule_id) == 0
        before = (_binding_operation_count(), _rust_fallback_count())
        start = time.perf_counter()
        error = None
        returned = None
        try:
            returned = await asyncio.wait_for(
                container.create_item(body=item, timeout=OPERATION_TIMEOUT), OPERATION_TIMEOUT + 5
            )
        except exceptions.CosmosHttpResponseError as caught:
            error = caught
        elapsed = time.perf_counter() - start
        after = (_binding_operation_count(), _rust_fallback_count())
        hits = await client._adapter._debug_fault_injection_rule_hit_count(rule_id)
        emit("operation", surface="async", backend="rust", inject=inject, rule_id=rule_id,
             database_id=database_id, item=item,
             elapsed=elapsed, hits=hits, status=None if error is None else error.status_code,
             binding_delta=after[0] - before[0], fallback_delta=after[1] - before[1])
        assert_route(before, after, "rust")
        if inject:
            assert_failure(error, elapsed, hits)
            with pytest.raises(exceptions.CosmosResourceNotFoundError) as absent:
                await asyncio.to_thread(owned_container.read_item, item_id, partition_key=item_id)
            assert absent.value.status_code == 404
            emit("stored_state", surface="async", backend="rust", inject=True, item_id=item_id, status=404)
        else:
            assert error is None, "The no-injection create failed"
            stored = await asyncio.to_thread(owned_container.read_item, item_id, partition_key=item_id)
            assert_control(returned, stored, item, hits)
            with pytest.raises(AssertionError, match="Expected a Cosmos HTTP failure"):
                assert_failure(error, elapsed, hits)
            emit("stored_state", surface="async", backend="rust", inject=False,
                 item_id=item_id, fields={field: stored[field] for field in item})
