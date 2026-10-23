# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Public async bookmark recovery after a real, later query-page failure."""

import asyncio
import os
import time
import uuid

import pytest

from azure.core.exceptions import AzureError
from azure.cosmos.aio import CosmosClient
from common._parity_helpers import _binding_operation_count, _rust_fallback_count
from fault_injection._delayed_create import assert_route, emit
from fault_injection._query_resume import (
    PAGE_BUDGET,
    QUERY,
    assert_complete,
    assert_failure,
    capture_query_calls,
    resume_rule,
    set_rule,
)

pytestmark = pytest.mark.cosmosEmulator


@pytest.mark.asyncio
@pytest.mark.timeout(90)
@pytest.mark.parametrize(
    "inject", [True, False], ids=["failure-after-page", "no-injection"]
)
async def test_query_failure_resumes_from_delivered_bookmark_async_rust(
    owned_target, monkeypatch, inject
):
    database_id, observer = owned_target
    partition = uuid.uuid4().hex
    items = [
        {
            "id": f"{partition}-{i}",
            "pk": partition,
            "name": f"order-{i}",
            "state": "confirmed",
        }
        for i in range(4)
    ]
    for item in items:
        await asyncio.to_thread(observer.create_item, item)
    rule_id = "query-resume-" + uuid.uuid4().hex
    async with CosmosClient(
        os.environ["ACCOUNT_HOST"],
        os.environ["ACCOUNT_KEY"],
        _backend="rust",
        consistency_level="Session",
        retry_throttle_total=0,
        _fault_injection_rules=[resume_rule(rule_id, observer.id, inject)],
    ) as client:
        container = client.get_database_client(database_id).get_container_client(
            observer.id
        )
        await container.read(timeout=30)
        await client._adapter.get_container_metadata(
            container.container_link, deadline=time.monotonic() + 30
        )
        calls = capture_query_calls(monkeypatch, asynchronous=True)
        hooks = []
        pager = container.query_items(
            QUERY,
            partition_key=partition,
            max_item_count=1,
            timeout=PAGE_BUDGET,
            response_hook=lambda headers, body: hooks.append(dict(headers)),
        )
        pages = pager.by_page()
        before = (_binding_operation_count(), _rust_fallback_count())
        first = [row async for row in await pages.__anext__()]
        assert len(first) == 1 and first[0]["id"] == items[0]["id"]
        assert_route(
            before, (_binding_operation_count(), _rust_fallback_count()), "rust"
        )
        assert len(calls) == len(hooks) == 1
        handle, cursor = calls[0]
        assert pages.state.cursor is cursor
        bookmark = pages.continuation_token
        assert isinstance(bookmark, str) and bookmark.startswith("q1.")
        assert await client._adapter._debug_fault_injection_rule_hit_count(rule_id) == 0
        set_rule(handle, rule_id, True)
        error, second = None, None
        before = (_binding_operation_count(), _rust_fallback_count())
        start = time.perf_counter()
        try:
            try:
                second = [row async for row in await pages.__anext__()]
            except (AzureError, TimeoutError) as caught:
                error = caught
        finally:
            set_rule(handle, rule_id, False)
        elapsed = time.perf_counter() - start
        after = (_binding_operation_count(), _rust_fallback_count())
        hits = await client._adapter._debug_fault_injection_rule_hit_count(rule_id)
        emit(
            "query_resume_failure",
            surface="async",
            database_id=database_id,
            inject=inject,
            hits=hits,
            elapsed=elapsed,
            error_type=None if error is None else type(error).__name__,
            status=None if error is None else getattr(error, "status_code", None),
            bookmark_preserved=pages.continuation_token == bookmark,
            hook_count=len(hooks),
            binding_delta=after[0] - before[0],
            fallback_delta=after[1] - before[1],
        )
        assert_route(before, after, "rust")
        assert len(calls) == 2 and calls[1][1] is cursor
        if inject:
            assert_failure(error, bookmark, hits, elapsed)
            assert second is None and len(hooks) == 1
            assert pages.state.failed and pages.state.cursor is None
            assert pages.continuation_token == bookmark
            with pytest.raises(RuntimeError, match="Query pager failed"):
                await pages.__anext__()
            assert len(calls) == 2
            assert (_binding_operation_count(), _rust_fallback_count()) == after
            resume_token = error.continuation_token
        else:
            assert error is None and hits == 0 and len(hooks) == 2
            assert len(second) == 1 and second[0]["id"] == items[1]["id"]
            original_remainder = second + [
                row async for page in pages async for row in page
            ]
            assert_complete(first, original_remainder, items)
            resume_token = bookmark
        resumed = container.query_items(
            QUERY,
            partition_key=partition,
            max_item_count=1,
            timeout=PAGE_BUDGET,
        ).by_page(continuation_token=resume_token)
        resume_call_start = len(calls)
        resume_before = (_binding_operation_count(), _rust_fallback_count())
        remainder = [row async for page in resumed async for row in page]
        resume_after = (_binding_operation_count(), _rust_fallback_count())
        assert_complete(first, remainder, items)
        assert calls[resume_call_start][1] is not cursor
        assert all(
            call[1] is calls[resume_call_start][1] for call in calls[resume_call_start:]
        )
        assert resumed.state.cursor is None
        assert resume_after[0] - resume_before[0] == len(calls) - resume_call_start
        assert resume_after[1] == resume_before[1]
        assert (
            await client._adapter._debug_fault_injection_rule_hit_count(rule_id) == hits
        )
        emit(
            "query_resume_complete",
            surface="async",
            database_id=database_id,
            inject=inject,
            first_ids=[row["id"] for row in first],
            resumed_ids=[row["id"] for row in remainder],
            expected_ids=[item["id"] for item in items],
            new_cursor=True,
            hits=hits,
            binding_delta=resume_after[0] - resume_before[0],
            fallback_delta=resume_after[1] - resume_before[1],
        )
        for item in items:
            stored = await asyncio.to_thread(
                observer.read_item, item["id"], partition_key=partition
            )
            assert {field: stored[field] for field in item} == item
        emit(
            "query_resume_stored_state",
            surface="async",
            database_id=database_id,
            fields=items,
        )
