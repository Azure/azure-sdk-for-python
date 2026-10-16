# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Compare name and saved-address reads of the same item, including every body field."""

import asyncio
from copy import deepcopy
import os
import uuid

import pytest

from azure.cosmos import CosmosClient, PartitionKey
from common._parity_helpers import (
    run_on_both_backends, run_on_both_backends_async,
    run_target_operation, run_target_operation_async,
    skip_unless_emulator, skip_unless_rust_binding,
)


pytestmark = [skip_unless_emulator(), skip_unless_rust_binding()]


@pytest.fixture(scope="module")
def saved_order():
    with CosmosClient(os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"], _backend="core-python") as client:
        database = client.create_database("read_address_parity_" + uuid.uuid4().hex)
        print(f"Owned read-test database: {database.id}")
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


@pytest.mark.parametrize("asynchronous", [False, True], ids=["sync", "async"])
@pytest.mark.parametrize("warm", [False, True], ids=["cold", "warm"])
@pytest.mark.parametrize("target_kind", ["id", "document", "self_only", "different_id", "non_string_id"])
def test_same_item_name_and_saved_address(saved_order, asynchronous, warm, target_kind):
    database_id, expected = saved_order
    target = {
        "id": expected["id"],
        "document": dict(expected),
        "self_only": {"_self": expected["_self"]},
        "different_id": {"_self": expected["_self"], "id": "other-order"},
        "non_string_id": {"_self": expected["_self"], "id": 42},
    }[target_kind]
    original = deepcopy(target)

    def sync_call(client):
        container = client.get_database_client(database_id).get_container_client("orders")
        if warm:
            container.read_item("order-42", partition_key="customer-17")
        return run_target_operation(client, lambda: container.read_item(target, partition_key="customer-17"))

    async def async_call(client):
        container = client.get_database_client(database_id).get_container_client("orders")
        if warm:
            await container.read_item("order-42", partition_key="customer-17")
        return await run_target_operation_async(
            client, lambda: container.read_item(target, partition_key="customer-17"),
        )

    description = f"read target={target_kind}, warm={warm}"
    comparison = (
        asyncio.run(run_on_both_backends_async(async_call, description=description))
        if asynchronous else run_on_both_backends(sync_call, description=description)
    )
    comparison.print_report()
    for outcome in (comparison.core_python, comparison.rust):
        assert outcome.succeeded, f"{outcome.backend}: {outcome.raised!r}"
        assert dict(outcome.return_value) == expected
        assert outcome.return_value.get_response_headers().get("etag") == expected["_etag"]
    assert target == original
    comparison.assert_functional_parity()
