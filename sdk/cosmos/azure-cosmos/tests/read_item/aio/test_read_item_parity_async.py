# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Cross-backend parity tests for read_item (async): run both backends in one
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
    cname = "rda_" + request.node.name + "_" + uuid.uuid4().hex[:6]
    container = db.create_container(id=cname, partition_key=PartitionKey(path="/pk"))
    yield container
    try:
        db.delete_container(cname)
    except Exception:  # pylint: disable=broad-except
        pass


@pytest.mark.asyncio
async def test_L0_async_read(container_for):
    """async read of an existing item — parity on both backends."""
    item_id = uuid.uuid4().hex

    async def _do(client):
        c = client.get_database_client("parity_db").get_container_client(container_for.id)
        await c.upsert_item({"id": item_id, "pk": "a", "n": 1})
        return await c.read_item(item_id, partition_key="a")

    cmp = await run_on_both_backends_async(_do, description="[L0] async read")
    cmp.print_report()
    cmp.assert_functional_parity()


@pytest.mark.asyncio
async def test_L5_async_read_missing_raises(container_for):
    """async read of a missing id raises CosmosResourceNotFoundError on both."""
    async def _do(client):
        c = client.get_database_client("parity_db").get_container_client(container_for.id)
        return await c.read_item("missing-" + uuid.uuid4().hex, partition_key="a")

    cmp = await run_on_both_backends_async(_do, description="[L5] async read missing -> 404")
    cmp.print_report()
    cmp.assert_exception_parity()

