# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Parity tests for ``Container.query_items``: run the same query once on the existing
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
    run_on_both_backends,
    run_target_operation,
    skip_unless_emulator,
    skip_unless_rust_binding,
)

pytestmark = [skip_unless_emulator(), skip_unless_rust_binding()]


@pytest.fixture
def container_for(request):
    # Fresh throwaway container per test, deleted afterward, so tests don't share data.
    client = CosmosClient(os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"])
    db = client.create_database_if_not_exists("parity_db")
    container_id = "parity_query_" + request.node.name + "_" + uuid.uuid4().hex[:6]
    container = db.create_container(id=container_id, partition_key=PartitionKey(path="/pk"))
    yield container
    try:
        db.delete_container(container_id)
    except Exception:  # pylint: disable=broad-except
        pass


def test_L0_partition_query_baseline(container_for):
    """Baseline: partition-scoped query returns the same item ids."""
    # Without this, a basic partition query returning different items or a different order
    # on rust would go unnoticed.

    def _do(client):
        container = client.get_database_client("parity_db").get_container_client(container_for.id)
        pk_value = "pk-" + uuid.uuid4().hex[:8]
        for i in range(3):
            container.create_item({"id": uuid.uuid4().hex, "pk": pk_value, "value": i})
        return run_target_operation(
            client,
            lambda: [
                doc["value"]
                for doc in container.query_items(
                    query="SELECT * FROM c WHERE c.pk = @pk ORDER BY c['value']",
                    parameters=[{"name": "@pk", "value": pk_value}],
                    partition_key=pk_value,
                )
            ],
        )

    comparison = run_on_both_backends(
        _do,
        description="[L0] partition query baseline",
    )
    comparison.print_report()
    comparison.assert_functional_parity()


def test_L1_partition_query_continuation_replay(container_for):
    """Partition query continuation token resumes on the same page."""
    # Without this, broken paging on rust (a wrong or non-resumable continuation token)
    # would slip through and break customers who page through large results.
    run_suffix = uuid.uuid4().hex

    def _do(client):
        container = client.get_database_client("parity_db").get_container_client(container_for.id)
        pk_value = "pk-" + run_suffix[:8]
        first_id = "id-a-" + run_suffix
        second_id = "id-b-" + run_suffix
        container.upsert_item({"id": first_id, "pk": pk_value, "value": 1})
        container.upsert_item({"id": second_id, "pk": pk_value, "value": 2})

        def _target():
            query_iterable = container.query_items(
                query="SELECT * FROM c WHERE c.pk = @pk ORDER BY c.id",
                parameters=[{"name": "@pk", "value": pk_value}],
                partition_key=pk_value,
                max_item_count=1,
            )
            pager = query_iterable.by_page()
            list(pager.next())
            continuation_token = pager.continuation_token
            second_page = list(pager.next())
            replay_page = list(query_iterable.by_page(continuation_token).next())
            return {
                "token_present": continuation_token is not None,
                "second_page_id": second_page[0]["id"],
                "replay_page_id": replay_page[0]["id"],
            }

        return run_target_operation(client, _target)

    comparison = run_on_both_backends(
        _do,
        description="[L1] partition query continuation replay",
    )
    comparison.print_report()
    comparison.assert_functional_parity()


def test_L2_cross_partition_query_fallback(container_for):
    """Cross-partition query (no partition key) stays behaviorally equivalent."""
    # Without this, the rust cross-partition path could drop or duplicate items unnoticed.

    def _do(client):
        container = client.get_database_client("parity_db").get_container_client(container_for.id)
        run_id = "run-" + uuid.uuid4().hex
        container.create_item({"id": uuid.uuid4().hex, "pk": "a", "run_id": run_id})
        container.create_item({"id": uuid.uuid4().hex, "pk": "b", "run_id": run_id})
        return run_target_operation(
            client,
            lambda: sorted(
                item["pk"]
                for item in container.query_items(
                    query="SELECT * FROM c WHERE c.run_id = @run_id",
                    parameters=[{"name": "@run_id", "value": run_id}],
                    enable_cross_partition_query=True,
                )
            ),
        )

    comparison = run_on_both_backends(
        _do,
        description="[L2] cross-partition query fallback",
    )
    comparison.print_report()
    comparison.assert_functional_parity()


def test_L3_invalid_query_raises_same_type(container_for):
    """Invalid SQL text raises the same typed exception on both backends."""
    # Without this, rust raising a different exception type on bad SQL would break
    # customers' error handling.

    def _do(client):
        container = client.get_database_client("parity_db").get_container_client(container_for.id)
        pk_value = "pk-" + uuid.uuid4().hex[:8]
        return run_target_operation(
            client,
            lambda: list(
                container.query_items(
                    query="SELECT FROM c",
                    partition_key=pk_value,
                )
            ),
        )

    comparison = run_on_both_backends(
        _do,
        description="[L3] invalid query syntax",
    )
    comparison.print_report()
    comparison.assert_exception_parity()
