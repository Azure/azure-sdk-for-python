# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""F07 throttle retry counts, alias precedence, and waiting budgets through asynchronous reads."""
import asyncio
import os
import time
import uuid

import pytest

from azure.core.exceptions import ServiceRequestError, ServiceResponseError
from azure.cosmos import exceptions
from azure.cosmos.aio import CosmosClient
from config.diagnostics import _binding_operation_count, fault_rule_hit_count_async
from fault_injection._delayed_create import assert_control, assert_route, emit
from fault_injection._query_resume import set_rule
from fault_injection._throttle_retry import (
    OPERATION_TIMEOUT,
    THROTTLE_RETRY_CASES,
    assert_throttle_failure,
    assert_throttle_wait_failure,
    throttle_rule,
    DATABASE_READ_THROTTLE_CASES,
    database_read_throttle_rule,
    assert_database_retry_metadata,
)

pytestmark = [pytest.mark.cosmosEmulator, pytest.mark.cosmosSdkFaultInjection]


@pytest.mark.asyncio
@pytest.mark.timeout(90)
@pytest.mark.parametrize("retry_settings,retry_limit", THROTTLE_RETRY_CASES)
@pytest.mark.parametrize("inject", [True, False], ids=["persistent-429", "no-injection"])
async def test_point_read_throttle_retry_limit_async_rust(owned_target, retry_settings, retry_limit, inject):
    database_id, observer = owned_target
    item_id = uuid.uuid4().hex
    item = {"id": item_id, "pk": item_id, "name": "order-17", "state": "confirmed"}
    await asyncio.to_thread(observer.create_item, item)
    rule_id = "throttle-read-" + uuid.uuid4().hex
    wait_budget = "throttle_retry_wait_threshold_seconds" in retry_settings
    rule = throttle_rule(rule_id, observer.id, inject, wait_budget=wait_budget)
    async with CosmosClient(
        os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"],
        _backend="rust", consistency_level="Session",
        _fault_injection_rules=[rule],
        **retry_settings,  # Pass omitted, zero, and None settings unchanged to the public API.
    ) as client:
        container = client.get_database_client(database_id).get_container_client(observer.id)
        await container.read(timeout=30)
        await client._adapter.get_container_metadata(container.container_link, deadline=time.monotonic() + 30)
        assert await fault_rule_hit_count_async(client._adapter, rule_id) == 0
        before = _binding_operation_count()
        error, returned = None, None
        start = time.perf_counter()
        try:
            returned = await container.read_item(item_id, partition_key=item_id, timeout=OPERATION_TIMEOUT)
        except (exceptions.CosmosClientTimeoutError, exceptions.CosmosHttpResponseError,
                ServiceRequestError, ServiceResponseError, TimeoutError) as caught:
            error = caught
        elapsed = time.perf_counter() - start
        after = _binding_operation_count()
        hits = await fault_rule_hit_count_async(client._adapter, rule_id)
        emit("throttle_retry", surface="async", backend="rust", inject=inject, database_id=database_id,
             rule_id=rule_id, retry_settings=retry_settings, retry_limit=retry_limit, elapsed=elapsed, hits=hits,
             response_headers=rule.get("response_headers", {}),
             error_type=None if error is None else type(error).__name__,
             status=error.status_code if isinstance(error, exceptions.CosmosHttpResponseError) else None,
             error_message=None if error is None else str(error),
             binding_delta=after - before)
        assert_route(before, after, "rust")
        stored = await asyncio.to_thread(observer.read_item, item_id, partition_key=item_id)
        assert {field: stored[field] for field in item} == item, "Stored customer fields changed"
        emit("stored_state", surface="async", inject=inject, retry_limit=retry_limit, item_id=item_id,
             fields={field: stored[field] for field in item})
        if inject:
            assert returned is None
            if wait_budget:
                assert_throttle_wait_failure(
                    error, elapsed, hits, retry_limit, max_retries=retry_settings["retry_throttle_total"],
                )
            else:
                assert_throttle_failure(error, elapsed, hits, retry_limit)
        else:
            assert error is None, "The no-injection read failed"
            assert_control(returned, stored, item, hits)


@pytest.mark.asyncio
@pytest.mark.timeout(90)
@pytest.mark.parametrize("retry_limit,hit_limit,inject", DATABASE_READ_THROTTLE_CASES)
async def test_database_read_throttle_retry_async_rust(
    owned_target, retry_limit, hit_limit, inject
):
    await _run_database_read_throttle(owned_target, retry_limit, hit_limit, inject)


@pytest.mark.asyncio
@pytest.mark.skip(
    reason="driver-gap: gap 29 - complete throttle retry totals are not exposed in Python "
    "response metadata (Azure/azure-sdk-for-rust#5521, item 11)"
)
@pytest.mark.timeout(90)
@pytest.mark.parametrize(
    "hit_limit,expected_retries",
    [(1, 1), (None, 2)],
    ids=["recovered-response", "terminal-error"],
)
async def test_database_read_retry_metadata_async_rust(
    owned_target, hit_limit, expected_retries
):
    channels = await _run_database_read_throttle(owned_target, 2, hit_limit, True)
    assert_database_retry_metadata(channels, expected_retries)


async def _run_database_read_throttle(owned_target, retry_limit, hit_limit, inject):
    database_id, _ = owned_target
    rule_id = "throttle-database-read-" + uuid.uuid4().hex
    async with CosmosClient(
        os.environ["ACCOUNT_HOST"],
        os.environ["ACCOUNT_KEY"],
        _backend="rust",
        retry_throttle_total=retry_limit,
        _fault_injection_rules=[
            database_read_throttle_rule(rule_id, inject, hit_limit)
        ],
    ) as client:
        database = client.get_database_client(database_id)
        expected = await database.read(timeout=OPERATION_TIMEOUT)
        handle = await client._adapter._ensure_driver_handle()
        assert await fault_rule_hit_count_async(client._adapter, rule_id) == 0
        hooks = []
        before = _binding_operation_count()
        error, returned = None, None
        set_rule(handle, rule_id, True)
        start = time.perf_counter()
        try:
            try:
                returned = await database.read(
                    timeout=OPERATION_TIMEOUT,
                    response_hook=lambda headers, body: hooks.append(
                        (dict(headers), body)
                    ),
                )
            except exceptions.CosmosHttpResponseError as caught:
                error = caught
        finally:
            set_rule(handle, rule_id, False)
        elapsed = time.perf_counter() - start
        hits = await fault_rule_hit_count_async(client._adapter, rule_id)
        after = _binding_operation_count()
        emit(
            "database_read_throttle_retry",
            surface="async",
            database_id=database_id,
            retry_limit=retry_limit,
            hit_limit=hit_limit,
            inject=inject,
            hits=hits,
            elapsed=elapsed,
            status=None if error is None else error.status_code,
        )
        assert_route(before, after, "rust")
        if inject and hit_limit is None:
            assert_throttle_failure(error, elapsed, hits, retry_limit)
            assert returned is None and not hooks
        else:
            assert error is None, "The database read did not recover"
            assert hits == (hit_limit if inject else 0)
            assert returned == expected
            assert len(hooks) == 1 and hooks[0][1] == expected
        channels = {
            "error" if error is not None else "response": dict(
                error.headers if error is not None else returned.get_response_headers()
            ),
            "last_response": dict(client.client_connection.last_response_headers),
        }
        if hooks:
            channels["response_hook"] = hooks[0][0]
        assert await database.read(timeout=OPERATION_TIMEOUT) == expected
        assert (
            await fault_rule_hit_count_async(client._adapter, rule_id) == hits
        )
        return channels
