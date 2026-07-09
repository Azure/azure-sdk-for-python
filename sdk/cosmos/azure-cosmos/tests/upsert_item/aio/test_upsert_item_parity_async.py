# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Cross-backend parity tests for upsert_item (async): run both backends in one
process and diff the result. Skips without an account or the rust binding."""
from __future__ import annotations

import os
import uuid

import pytest

from azure.cosmos import CosmosClient, PartitionKey
from common._parity_helpers import run_on_both_backends_async, skip_unless_emulator, skip_unless_rust_binding

pytestmark = [skip_unless_emulator(), skip_unless_rust_binding()]


@pytest.fixture
def container_for(request):
    client = CosmosClient(os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"])
    db = client.create_database_if_not_exists("parity_db")
    cname = "upa_" + request.node.name + "_" + uuid.uuid4().hex[:6]
    container = db.create_container(id=cname, partition_key=PartitionKey(path="/pk"))
    yield container
    try:
        db.delete_container(cname)
    except Exception:  # pylint: disable=broad-except
        pass


@pytest.mark.asyncio
async def test_L0_async_upsert_insert_then_update(container_for):
    """async upsert insert then update — parity on both backends."""
    item_id = uuid.uuid4().hex

    async def _do(client):
        c = client.get_database_client("parity_db").get_container_client(container_for.id)
        await c.upsert_item({"id": item_id, "pk": "a", "n": 1})
        return await c.upsert_item({"id": item_id, "pk": "a", "n": 2})

    cmp = await run_on_both_backends_async(_do, description="[L0] async upsert")
    cmp.print_report()
    cmp.assert_functional_parity()


@pytest.mark.asyncio
async def test_L4_async_upsert_response_hook_fires_once(container_for):
    """async upsert fires response_hook exactly once per backend."""
    fired = {"core-python": 0, "rust": 0}
    order = ["core-python", "rust"]
    idx = [0]

    async def _do(client):
        backend = order[idx[0]]
        idx[0] += 1
        c = client.get_database_client("parity_db").get_container_client(container_for.id)
        return await c.upsert_item(
            {"id": uuid.uuid4().hex, "pk": "a"},
            response_hook=lambda h, x: fired.__setitem__(backend, fired[backend] + 1),
        )

    cmp = await run_on_both_backends_async(_do, description="[L4] async upsert response_hook")
    cmp.assert_functional_parity()
    assert fired["core-python"] == 1 and fired["rust"] == 1
