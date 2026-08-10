# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Cross-backend parity tests for upsert_item (sync): run both backends in one
process and diff the result. Skips without an account or the rust binding."""
from __future__ import annotations

import os
import uuid

import pytest

from azure.cosmos import CosmosClient, PartitionKey
from common._parity_helpers import run_on_both_backends, skip_unless_emulator, skip_unless_rust_binding

pytestmark = [skip_unless_emulator(), skip_unless_rust_binding()]


@pytest.fixture
def container_for(request):
    """Provide an isolated container so each test targets only its own items."""
    client = CosmosClient(os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"])
    db = client.create_database_if_not_exists("parity_db")
    cname = "up_" + request.node.name + "_" + uuid.uuid4().hex[:6]
    container = db.create_container(id=cname, partition_key=PartitionKey(path="/pk"))
    yield container
    try:
        db.delete_container(cname)
    except Exception:  # pylint: disable=broad-except
        pass


def test_upsert_insert_then_update(container_for):
    """upsert inserts, then upserts the same id with a new field — parity on both."""
    item_id = uuid.uuid4().hex

    def _do(client):
        c = client.get_database_client("parity_db").get_container_client(container_for.id)
        c.upsert_item({"id": item_id, "pk": "a", "n": 1})
        return c.upsert_item({"id": item_id, "pk": "a", "n": 2})

    cmp = run_on_both_backends(_do, description="upsert insert+update", request_body={"id": item_id, "pk": "a"})
    cmp.print_report()
    cmp.assert_functional_parity()


def test_response_hook_fires_once(container_for):
    """upsert fires response_hook exactly once per backend."""
    fired = {"core-python": 0, "rust": 0}
    order = ["core-python", "rust"]; idx = [0]

    def _do(client):
        b = order[idx[0]]; idx[0] += 1
        c = client.get_database_client("parity_db").get_container_client(container_for.id)
        return c.upsert_item({"id": uuid.uuid4().hex, "pk": "a"}, response_hook=lambda h, x: fired.__setitem__(b, fired[b] + 1))

    cmp = run_on_both_backends(_do, description="upsert response_hook")
    cmp.assert_functional_parity()
    assert fired["core-python"] == 1 and fired["rust"] == 1

