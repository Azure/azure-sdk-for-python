# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
# Rust behavior test
"""Live async ``patch_item(no_response=True)`` behavior on the Rust backend."""

import os
import uuid

import pytest
import pytest_asyncio

from azure.cosmos import PartitionKey
from azure.cosmos.aio import CosmosClient
from common._rust_checks import run_on_rust_async


@pytest_asyncio.fixture
async def container():
    """Yield an async Rust client and a ``/pk`` container in an owned database deleted afterwards."""
    async with CosmosClient(os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"], _backend="rust") as client:
        database = await client.create_database("patch_no_response_aio_" + uuid.uuid4().hex)
        try:
            yield client, await database.create_container("orders", partition_key=PartitionKey(path="/pk"))
        finally:
            await client.delete_database(database.id)


@pytest.mark.asyncio
async def test_patch_with_no_response_returns_empty_dict_and_applies_patch_async_rust(container):
    """Async patch_item(no_response=True) returns an empty dict while the patch is still applied on the service."""
    client, orders = container
    item_id = uuid.uuid4().hex
    await orders.create_item({"id": item_id, "pk": "customerA", "n": 1, "label": "before"})

    result = await run_on_rust_async(client, lambda: orders.patch_item(
        item=item_id, partition_key="customerA",
        patch_operations=[{"op": "set", "path": "/n", "value": 2}],
        no_response=True,
    ))

    assert dict(result) == {}
    stored = await orders.read_item(item_id, partition_key="customerA")
    assert stored["n"] == 2
    assert stored["label"] == "before"
