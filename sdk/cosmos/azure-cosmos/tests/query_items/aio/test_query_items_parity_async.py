# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Async parity tests for ``Container.query_items``: run the same query once on the existing
core-python engine and once on the rust engine, then compare the results. During the
migration the rust path must behave exactly like the existing one; without these tests it
could return items in a different order, break continuation-token paging, or raise a
different error on bad SQL, and a customer moving to rust would silently get wrong results.
They run only when a real account and the compiled rust binding are both present."""
from __future__ import annotations

import os
import uuid

import pytest

from azure.cosmos import CosmosClient, PartitionKey
from common._parity_helpers import (
    run_on_both_backends_async,
    run_target_operation_async,
    skip_unless_emulator,
    skip_unless_rust_binding,
)

pytestmark = [skip_unless_emulator(), skip_unless_rust_binding()]


@pytest.fixture
def container_for(request):
    # Fresh throwaway container per test, deleted afterward, so tests don't share data.
    client = CosmosClient(os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"])
    db = client.create_database_if_not_exists("parity_db")
    container_id = "parity_query_async_" + request.node.name + "_" + uuid.uuid4().hex[:6]
    container = db.create_container(id=container_id, partition_key=PartitionKey(path="/pk"))
    yield container
    try:
        db.delete_container(container_id)
    except Exception:  # pylint: disable=broad-except
        pass


@pytest.mark.asyncio
async def test_partition_query_baseline_async(container_for):
    """Baseline async partition query returns the same item ids."""
    # Without this, a basic partition query returning different items or a different order
    # on rust would go unnoticed.

    async def _do(client):
        container = client.get_database_client("parity_db").get_container_client(container_for.id)
        pk_value = "pk-" + uuid.uuid4().hex[:8]
        for i in range(3):
            await container.create_item({"id": uuid.uuid4().hex, "pk": pk_value, "value": i})
        async def _target():
            return [
                item["value"]
                async for item in container.query_items(
                    query="SELECT * FROM c WHERE c.pk = @pk ORDER BY c['value']",
                    parameters=[{"name": "@pk", "value": pk_value}],
                    partition_key=pk_value,
                )
            ]

        return await run_target_operation_async(client, _target)

    comparison = await run_on_both_backends_async(
        _do,
        description="async partition query baseline",
    )
    comparison.print_report()
    comparison.assert_functional_parity()


@pytest.mark.asyncio
async def test_partition_query_continuation_replay_async(container_for):
    """Async partition query continuation token resumes on the same page."""
    # Without this, broken paging on rust (a wrong or non-resumable continuation token)
    # would slip through and break customers who page through large results.
    run_suffix = uuid.uuid4().hex

    async def _do(client):
        container = client.get_database_client("parity_db").get_container_client(container_for.id)
        pk_value = "pk-" + run_suffix[:8]
        first_id = "id-a-" + run_suffix
        second_id = "id-b-" + run_suffix
        await container.upsert_item({"id": first_id, "pk": pk_value, "value": 1})
        await container.upsert_item({"id": second_id, "pk": pk_value, "value": 2})

        async def _target():
            query_iterable = container.query_items(
                query="SELECT * FROM c WHERE c.pk = @pk ORDER BY c.id",
                parameters=[{"name": "@pk", "value": pk_value}],
                partition_key=pk_value,
                max_item_count=1,
            )
            pager = query_iterable.by_page()
            await pager.__anext__()
            continuation_token = pager.continuation_token
            second_page = [item async for item in await pager.__anext__()]
            replay_page = [
                item
                async for item in await query_iterable.by_page(
                    continuation_token
                ).__anext__()
            ]
            return {
                "token_present": continuation_token is not None,
                "second_page_id": second_page[0]["id"],
                "replay_page_id": replay_page[0]["id"],
            }

        return await run_target_operation_async(client, _target)

    comparison = await run_on_both_backends_async(
        _do,
        description="async partition query continuation replay",
    )
    comparison.print_report()
    comparison.assert_functional_parity()


@pytest.mark.asyncio
async def test_cross_partition_query_fallback_async(container_for):
    """Async cross-partition query (no partition key) stays equivalent."""
    # Without this, the rust cross-partition path could drop or duplicate items unnoticed.

    async def _do(client):
        container = client.get_database_client("parity_db").get_container_client(container_for.id)
        run_id = "run-" + uuid.uuid4().hex
        await container.create_item({"id": uuid.uuid4().hex, "pk": "a", "run_id": run_id})
        await container.create_item({"id": uuid.uuid4().hex, "pk": "b", "run_id": run_id})
        async def _target():
            return sorted([
                item["pk"]
                async for item in container.query_items(
                    query="SELECT * FROM c WHERE c.run_id = @run_id",
                    parameters=[{"name": "@run_id", "value": run_id}],
                    enable_cross_partition_query=True,
                )
            ])

        return await run_target_operation_async(client, _target)

    comparison = await run_on_both_backends_async(
        _do,
        description="async cross-partition query fallback",
    )
    comparison.print_report()
    comparison.assert_functional_parity()


@pytest.mark.asyncio
async def test_invalid_query_raises_same_type_async(container_for):
    """Invalid SQL text raises the same typed exception on both backends (async)."""
    # Without this, rust raising a different exception type on bad SQL would break
    # customers' error handling.

    async def _do(client):
        container = client.get_database_client("parity_db").get_container_client(container_for.id)
        pk_value = "pk-" + uuid.uuid4().hex[:8]
        async def _target():
            return [
                item
                async for item in container.query_items(
                    "SELECT FROM c", partition_key=pk_value
                )
            ]

        return await run_target_operation_async(client, _target)

    comparison = await run_on_both_backends_async(
        _do,
        description="async invalid query syntax",
    )
    comparison.print_report()
    comparison.assert_exception_parity()


@pytest.mark.asyncio
async def test_populate_index_metrics_parity_async(container_for):
    """A supported metrics option uses Rust and returns the same public value."""

    async def _do(client):
        """Run the index-metrics query against one backend and return the metrics keys."""
        container = client.get_database_client("parity_db").get_container_client(container_for.id)
        pk_value = "pk-" + uuid.uuid4().hex[:8]
        await container.create_item({"id": uuid.uuid4().hex, "pk": pk_value, "value": 1})
        captured = {}

        def _capture(headers, *_args):
            """Collect response headers for later assertion."""
            captured.update(headers)

        async def _target():
            """Execute the query and return the parsed index-metrics keys."""
            _ = [
                item
                async for item in container.query_items(
                    query="SELECT * FROM c WHERE c.pk = @pk",
                    parameters=[{"name": "@pk", "value": pk_value}],
                    partition_key=pk_value,
                    populate_index_metrics=True,
                    response_hook=_capture,
                )
            ]
            metrics = captured.get("x-ms-cosmos-index-utilization")
            return sorted(metrics.keys()) if isinstance(metrics, dict) else metrics

        return await run_target_operation_async(client, _target)

    comparison = await run_on_both_backends_async(
        _do,
        description="async populate index metrics",
    )
    comparison.print_report()
    comparison.assert_functional_parity()
    assert comparison.rust.return_value, (
        "rust backend must return parsed index metrics, not an empty dict"
    )
