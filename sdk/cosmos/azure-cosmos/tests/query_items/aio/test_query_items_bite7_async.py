# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Async Bite 7: return each selected status once within one partition."""

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
class TestQueryBite7Async:
    async def test_query_each_status_once_async(self):
        backend = os.environ.get("COSMOS_BACKEND", "rust")
        database_id = "query_bite7_async_" + uuid.uuid4().hex
        async with CosmosClient(
            os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"], _backend="core-python",
        ) as setup_client:
            database = await setup_client.create_database(database_id)
            print(f"\nOwned async Bite 7 database: {database_id}")
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
                            query="SELECT DISTINCT o.status FROM orders o",
                            partition_key="customer-501",
                        )
                        return [row async for row in results]

                    rows = await run_target_operation_async(client, consume)
                    assert rows == [{"status": "pending"}]
                    print(f"Distinct statuses: {rows}")
            finally:
                await setup_client.delete_database(database_id)
                print(f"Deleted owned async Bite 7 database: {database_id}")
