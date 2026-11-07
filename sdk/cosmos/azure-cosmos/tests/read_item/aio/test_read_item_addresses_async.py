# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
# Rust behavior test
"""Live async ``read_item`` by name and by saved resource address on the Rust backend."""

from copy import deepcopy
import os
import uuid

import pytest

from azure.cosmos import CosmosClient as SyncCosmosClient, PartitionKey
from azure.cosmos.aio import CosmosClient
from common._rust_checks import run_on_rust_async


@pytest.fixture(scope="module")
def saved_order():
    """Own a database holding the target order and a decoy order with the same partition key."""
    with SyncCosmosClient(os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"], _backend="rust") as client:
        database = client.create_database("read_address_aio_" + uuid.uuid4().hex)
        try:
            container = database.create_container("orders", partition_key=PartitionKey(path="/customerId"))
            order = container.create_item({
                "id": "order-42", "customerId": "customer-17", "status": "paid",
                "lines": [{"sku": "book", "quantity": 2}], "total": 25.5,
            })
            container.create_item({"id": "other-order", "customerId": "customer-17", "status": "wrong-target"})
            yield database.id, dict(order)
        finally:
            client.delete_database(database.id)


def _target(expected, kind):
    return {
        "id": expected["id"],
        "document": dict(expected),
        "self_only": {"_self": expected["_self"]},
        "different_id": {"_self": expected["_self"], "id": "other-order"},
        "non_string_id": {"_self": expected["_self"], "id": 42},
    }[kind]


@pytest.mark.asyncio
@pytest.mark.parametrize("warm", [False, True], ids=["cold", "warm"])
@pytest.mark.parametrize("target_kind", ["id", "document", "self_only", "different_id", "non_string_id"])
async def test_read_by_name_or_saved_address_returns_stored_item_async_rust(saved_order, warm, target_kind):
    """Async read_item returns the full stored body and etag whether given an id, a document or a saved _self.

    A target carrying _self is read from that address even when its id names another item or is not a
    string, on a cold client and on one whose metadata cache is already warm, and the target dict is
    never mutated.
    """
    database_id, expected = saved_order
    target = _target(expected, target_kind)
    original = deepcopy(target)
    async with CosmosClient(os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"], _backend="rust") as client:
        container = client.get_database_client(database_id).get_container_client("orders")
        if warm:
            await container.read_item("order-42", partition_key="customer-17")
        result = await run_on_rust_async(client, lambda: container.read_item(target, partition_key="customer-17"))

    assert dict(result) == expected
    assert result.get_response_headers().get("etag") == expected["_etag"]
    assert target == original
