# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Async Bite 6: return only the second-largest qualifying order."""

import os
import uuid

import pytest

from azure.cosmos import PartitionKey
from azure.cosmos.aio import CosmosClient
from common._parity_helpers import (
    run_target_operation_async,
    skip_unless_emulator,
    skip_unless_rust_binding,
)


@pytest.mark.cosmosEmulator
@pytest.mark.asyncio
@skip_unless_emulator()
@skip_unless_rust_binding()
class TestQueryBite6Async:
    async def test_query_second_largest_order_async(self):
        backend = os.environ.get("COSMOS_BACKEND", "rust")
        database_id = "query_bite6_async_" + uuid.uuid4().hex
        async with CosmosClient(
            os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"], _backend="core-python",
        ) as setup_client:
            database = await setup_client.create_database(database_id)
            print(f"\nOwned async Bite 6 database: {database_id}")
            try:
                orders = await database.create_container(
                    id="orders", partition_key=PartitionKey(path="/customerId"),
                )
                for item in (
                    {"id": "order-1", "customerId": "customer-501", "amount": 40},
                    {"id": "order-2", "customerId": "customer-501", "amount": 150},
                    {"id": "order-3", "customerId": "customer-502", "amount": 200},
                ):
                    await orders.create_item(item)

                async with CosmosClient(
                    os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"], _backend=backend,
                ) as client:
                    assert client.client_connection._backend.name == backend
                    orders_container = client.get_database_client(database_id).get_container_client("orders")

                    async def consume():
                        results = orders_container.query_items(
                            query=(
                                "SELECT o.id FROM orders o "
                                "WHERE o.amount >= @minimumAmount "
                                "ORDER BY o.amount DESC "
                                "OFFSET 1 LIMIT 1"
                            ),
                            parameters=[{"name": "@minimumAmount", "value": 40}],
                            partition_key="customer-501",
                        )
                        return [row async for row in results]

                    rows = await run_target_operation_async(client, consume)
                    assert rows == [{"id": "order-1"}]
                    print(f"Second-largest order: {rows}")
            finally:
                await setup_client.delete_database(database_id)
                print(f"Deleted owned async Bite 6 database: {database_id}")
