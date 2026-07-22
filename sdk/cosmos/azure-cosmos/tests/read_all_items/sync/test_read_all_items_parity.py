# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Parity tests for ``Container.read_all_items``.

These tests run the same customer call once on the core-python backend and once
on the Rust backend, then compare the observable result. The read-all migration
currently uses a Rust fast path for eligible pages and falls back for
unsupported knobs, so both routes need operation-scoped parity coverage.

Unlike the routing unit tests (which use a fake backend that always returns a
canned success), these run against a real account, so they actually exercise the
Rust driver. That is the coverage the unit tests structurally cannot give: a
whole-container read_all_items (no partition key) that was routed to a native
read-feed would be rejected by the driver and error, while core-python returns
normally -- a mismatch these parity tests would catch immediately.
"""
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
    client = CosmosClient(os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"])
    db = client.create_database_if_not_exists("parity_db")
    container_id = "parity_read_all_" + request.node.name + "_" + uuid.uuid4().hex[:6]
    container = db.create_container(id=container_id, partition_key=PartitionKey(path="/pk"))
    yield container
    try:
        db.delete_container(container_id)
    except Exception:  # pylint: disable=broad-except
        pass


def _seed_docs(container, run_id: str) -> list[str]:
    expected_ids = []
    for i in range(3):
        doc_id = "{}-doc-{}".format(run_id, i)
        container.upsert_item({"id": doc_id, "pk": "tenant-{}".format(i % 2), "run_id": run_id, "value": i})
        expected_ids.append(doc_id)
    return sorted(expected_ids)


def _collect_run_ids(items, run_id: str) -> list[str]:
    return sorted(item["id"] for item in items if item.get("run_id") == run_id)


def test_read_all_items_baseline(container_for):
    """Baseline read_all_items returns the same seeded ids."""
    # A plain read_all_items() is whole-container (no partition key), so it
    # is served through the Rust query fast path ("Select * from root r").
    run_id = "run-" + uuid.uuid4().hex

    def _do(client):
        container = client.get_database_client("parity_db").get_container_client(container_for.id)
        expected_ids = _seed_docs(container, run_id)
        observed_ids = run_target_operation(
            client,
            lambda: _collect_run_ids(list(container.read_all_items()), run_id),
        )
        return {"expected_ids": expected_ids, "observed_ids": observed_ids}

    comparison = run_on_both_backends(
        _do,
        description="read_all_items baseline",
    )
    comparison.print_report()
    comparison.assert_functional_parity()


def test_read_all_items_respects_max_item_count_paging(container_for):
    """read_all_items with max_item_count still returns the same seeded ids."""
    # Same Rust query fast path as the baseline test, but max_item_count=1 forces
    # the read across multiple pages so paging/continuation is exercised, not just one page.
    run_id = "run-" + uuid.uuid4().hex

    def _do(client):
        container = client.get_database_client("parity_db").get_container_client(container_for.id)
        expected_ids = _seed_docs(container, run_id)
        observed_ids = run_target_operation(
            client,
            lambda: _collect_run_ids(
                list(container.read_all_items(max_item_count=1)), run_id
            ),
        )
        return {"expected_ids": expected_ids, "observed_ids": observed_ids}

    comparison = run_on_both_backends(
        _do,
        description="read_all_items max_item_count=1",
        request_kwargs={"max_item_count": 1},
    )
    comparison.print_report()
    comparison.assert_functional_parity()


def test_read_all_items_availability_strategy_fallback(container_for):
    """read_all_items with availability_strategy=False stays behaviorally equivalent."""
    # availability_strategy is an unsupported knob for the Rust fast path, so
    # the gate rejects it and this exercises the legacy fallback path on a
    # Rust-backed client -- it must still match core-python.
    run_id = "run-" + uuid.uuid4().hex

    def _do(client):
        container = client.get_database_client("parity_db").get_container_client(container_for.id)
        expected_ids = _seed_docs(container, run_id)
        observed_ids = run_target_operation(
            client,
            lambda: _collect_run_ids(
                list(
                    container.read_all_items(
                        max_item_count=2, availability_strategy=False
                    )
                ),
                run_id,
            ),
            expect_rust=False,
        )
        return {"expected_ids": expected_ids, "observed_ids": observed_ids}

    comparison = run_on_both_backends(
        _do,
        description="read_all_items availability_strategy=False",
        request_kwargs={"max_item_count": 2, "availability_strategy": False},
    )
    comparison.print_report()
    comparison.assert_functional_parity()
