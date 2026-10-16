# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Async Bite 13: find the customer's smallest order amount."""

import os
import uuid

import pytest

from azure.cosmos import PartitionKey
from azure.cosmos.aio import CosmosClient
from common._parity_helpers import run_target_operation_async, skip_unless_emulator, skip_unless_rust_binding


@pytest.mark.cosmosEmulator
@pytest.mark.asyncio
@skip_unless_emulator()
@skip_unless_rust_binding()
class TestQueryCustomerOrderMinimumAsync:
    async def test_query_minimum_customer_order_amount_async(self):
        backend = os.environ.get("COSMOS_BACKEND", "rust")
        database_id = "query_bite13_async_" + uuid.uuid4().hex
        async with CosmosClient(
            os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"], _backend="core-python",
        ) as setup_client:
            database = await setup_client.create_database(database_id)
            print(f"\nOwned async Bite 13 database: {database_id}")
            try:
                orders = await database.create_container(
                    id="orders", partition_key=PartitionKey(path="/customerId"),
                )
                for item in (
                    {"id": "order-1", "customerId": "customer-501", "amount": 40, "status": "pending"},
                    {"id": "order-2", "customerId": "customer-501", "amount": 150, "status": "pending"},
                    {"id": "order-3", "customerId": "customer-502", "amount": 200, "status": "shipped"},
                ):
                    await orders.create_item(item)

                async with CosmosClient(
                    os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"], _backend=backend,
                ) as client:
                    assert client.client_connection._backend.name == backend
                    orders_container = client.get_database_client(database_id).get_container_client("orders")

                    async def consume():
                        results = orders_container.query_items(
                            query="SELECT VALUE MIN(o.amount) FROM orders o",
                            partition_key="customer-501",
                        )
                        return [minimum async for minimum in results]

                    minimums = await run_target_operation_async(client, consume)
                    assert minimums == [40]
                    print(f"Customer minimum order amount: {minimums}")
            finally:
                await setup_client.delete_database(database_id)
                print(f"Deleted owned async Bite 13 database: {database_id}")
