# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Parity tests for ``Container.read_items``.

Each test runs the same batched read once on core-python and once on rust against
one shared, pre-seeded container, then compares the returned documents. Because
``read_items`` fans a batch out into point reads and per-partition queries, these
cover the shapes that exercise both kinds of leaf: a single item (a point read),
several items in one partition (a query), and items spread across partitions (a
fan-out), plus the customer-visible rules -- missing ids omitted and an empty
result -- so rust returns the same set of documents core-python does.

The call under test returns a small projection (each document's id and data)
rather than the raw documents, so the comparison ignores the server-stamped
fields (``_rid`` / ``_ts`` / ``_etag`` / ...) that legitimately differ per write.
"""
from __future__ import annotations

import os
import uuid

import pytest

from azure.cosmos import CosmosClient, PartitionKey
from common._parity_helpers import (
    run_on_both_backends,
    skip_unless_emulator,
    skip_unless_rust_binding,
)

pytestmark = [skip_unless_emulator(), skip_unless_rust_binding()]


@pytest.fixture(scope="module")
def seeded():
    """Create one /pk container, seed a known set of items across three partition
    keys, and hand tests the container id, the seeded (id, pk) pairs, and a couple
    of ids that were never created."""
    client = CosmosClient(os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"])
    db = client.create_database_if_not_exists("parity_db")
    container_id = "parity_read_items_" + uuid.uuid4().hex[:8]
    container = db.create_container(id=container_id, partition_key=PartitionKey(path="/pk"))

    seeded_pairs = []
    # pk-a: 2 items, pk-b: 2 items, pk-c: 1 item -> spans three logical partitions.
    layout = [("pk-a", 2), ("pk-b", 2), ("pk-c", 1)]
    for pk_value, n in layout:
        for i in range(n):
            doc_id = f"{pk_value}-item-{i}"
            container.upsert_item({"id": doc_id, "pk": pk_value, "data": f"{pk_value}:{i}"})
            seeded_pairs.append((doc_id, pk_value))

    missing = [("ghost-1", "pk-a"), ("ghost-2", "pk-z")]
    try:
        yield {"container_id": container_id, "seeded": seeded_pairs, "missing": missing}
    finally:
        try:
            db.delete_container(container_id)
        except Exception:  # pylint: disable=broad-except
            pass


def _run(container_id, items, description, request_kwargs):
    def _do(client):
        container = client.get_database_client("parity_db").get_container_client(container_id)
        result = container.read_items(items=items)
        # Project to (id, data) and sort, so the compare is stable and ignores
        # server-stamped fields and any per-backend ordering.
        return sorted((doc["id"], doc.get("data")) for doc in result)

    comparison = run_on_both_backends(_do, description=description, request_kwargs=request_kwargs)
    comparison.print_report()
    comparison.assert_functional_parity()


def test_L0_read_items_single_item(seeded):
    """One item -> read as a point read; same document on both backends."""
    items = [seeded["seeded"][-1]]  # the lone pk-c item
    _run(seeded["container_id"], items,
         description="[L0] read_items single item (point-read leaf)",
         request_kwargs={"count": 1})


def test_L1_read_items_same_partition(seeded):
    """Several items in one partition -> read as one query; same set on both backends."""
    items = [pair for pair in seeded["seeded"] if pair[1] == "pk-a"]
    _run(seeded["container_id"], items,
         description="[L1] read_items multiple items in one partition (query leaf)",
         request_kwargs={"count": len(items)})


def test_L2_read_items_across_partitions(seeded):
    """Items spread across partitions -> fan-out; same merged set on both backends."""
    items = list(seeded["seeded"])
    _run(seeded["container_id"], items,
         description="[L2] read_items across partitions (fan-out)",
         request_kwargs={"count": len(items)})


def test_L3_read_items_missing_omitted(seeded):
    """A mix of real and non-existent ids -> only the real ones come back, on both."""
    items = list(seeded["seeded"]) + seeded["missing"]
    _run(seeded["container_id"], items,
         description="[L3] read_items with missing ids omitted",
         request_kwargs={"requested": len(items), "existing": len(seeded["seeded"])})


def test_L4_read_items_all_missing(seeded):
    """Only non-existent ids -> an empty result on both backends."""
    _run(seeded["container_id"], list(seeded["missing"]),
         description="[L4] read_items all-missing returns empty",
         request_kwargs={"requested": len(seeded["missing"]), "existing": 0})


def _run_with_options(container_id, items, description, read_items_kwargs):
    """Same as ``_run`` but forwards extra kwargs to ``read_items`` -- used to
    check that per-request options (availability strategy, custom headers, read
    timeout) leave the returned documents identical on both backends."""
    def _do(client):
        container = client.get_database_client("parity_db").get_container_client(container_id)
        result = container.read_items(items=items, **read_items_kwargs)
        return sorted((doc["id"], doc.get("data")) for doc in result)

    comparison = run_on_both_backends(_do, description=description, request_kwargs=read_items_kwargs)
    comparison.print_report()
    comparison.assert_functional_parity()


def test_L5_read_items_availability_strategy_disabled(seeded):
    """availability_strategy=False (hedging off) is honored on the rust point
    leg and returns the same documents as legacy."""
    items = [seeded["seeded"][-1]]  # single item -> point read
    _run_with_options(seeded["container_id"], items,
                      description="[L5] read_items availability_strategy=False",
                      read_items_kwargs={"availability_strategy": False})


def test_L6_read_items_custom_initial_headers(seeded):
    """A non-x-ms customer header on read_items is forwarded on both backends and
    does not change the returned documents."""
    items = [seeded["seeded"][-1]]
    _run_with_options(seeded["container_id"], items,
                      description="[L6] read_items initial_headers (custom)",
                      read_items_kwargs={"initial_headers": {"x-trace-id": "read-items-parity"}})


def test_L7_read_items_read_timeout_falls_back_to_legacy(seeded):
    """read_timeout keeps the point leg on legacy (rust has no per-request read
    timeout); the returned documents still match legacy."""
    items = [seeded["seeded"][-1]]
    _run_with_options(seeded["container_id"], items,
                      description="[L7] read_items read_timeout (legacy fallback)",
                      read_items_kwargs={"read_timeout": 30})
