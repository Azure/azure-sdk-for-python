# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Async Bite 8: return one status string rather than a status object."""

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
class TestQueryBite8Async:
    async def test_query_distinct_status_values_async(self):
        backend = os.environ.get("COSMOS_BACKEND", "rust")
        database_id = "query_bite8_async_" + uuid.uuid4().hex
        async with CosmosClient(
            os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"], _backend="core-python",
        ) as setup_client:
            database = await setup_client.create_database(database_id)
            print(f"\nOwned async Bite 8 database: {database_id}")
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
                            query="SELECT DISTINCT VALUE o.status FROM orders o",
                            partition_key="customer-501",
                        )
                        return [status async for status in results]

                    statuses = await run_target_operation_async(client, consume)
                    assert statuses == ["pending"]
                    print(f"Distinct status values: {statuses}")
            finally:
                await setup_client.delete_database(database_id)
                print(f"Deleted owned async Bite 8 database: {database_id}")
