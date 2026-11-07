# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
# Rust behavior test
"""Live async ``read_item`` not-found behavior on the Rust backend."""

import os
import uuid

import pytest
import pytest_asyncio

from azure.cosmos import PartitionKey
from azure.cosmos.aio import CosmosClient
from azure.cosmos.exceptions import CosmosResourceNotFoundError
from common._rust_checks import run_on_rust_async


@pytest_asyncio.fixture
async def container():
    """Yield an async Rust client and a ``/pk`` container in an owned database deleted afterwards."""
    async with CosmosClient(os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"], _backend="rust") as client:
        database = await client.create_database("read_errors_aio_" + uuid.uuid4().hex)
        try:
            yield client, await database.create_container("orders", partition_key=PartitionKey(path="/pk"))
        finally:
            await client.delete_database(database.id)


@pytest.mark.asyncio
async def test_read_existing_id_with_wrong_partition_key_raises_not_found_async_rust(container):
    """Async read of an existing id with the wrong partition key raises CosmosResourceNotFoundError (404)."""
    client, orders = container
    item_id = uuid.uuid4().hex
    await orders.create_item({"id": item_id, "pk": "a", "value": 1})

    with pytest.raises(CosmosResourceNotFoundError) as caught:
        await run_on_rust_async(client, lambda: orders.read_item(item_id, partition_key="b"))
    assert caught.value.status_code == 404
