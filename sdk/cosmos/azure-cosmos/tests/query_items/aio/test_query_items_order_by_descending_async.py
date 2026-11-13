# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
# Rust behavior test
"""Async partition-scoped ``ORDER BY ... DESC`` queries on Rust return rows in descending order."""

import os
import uuid

import pytest

from azure.cosmos import CosmosClient, PartitionKey, exceptions
from azure.cosmos.aio import CosmosClient as AsyncCosmosClient
from common._rust_checks import run_on_rust_async

pytestmark = [pytest.mark.cosmosEmulator, pytest.mark.asyncio]


@pytest.fixture(scope="module")
def database_id():
    """Orders for two customers in a throwaway database."""
    name = "rust_query_desc_a_" + uuid.uuid4().hex
    with CosmosClient(os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"], _backend="rust") as client:
        try:
            database = client.create_database(name)
            orders = database.create_container(id="orders", partition_key=PartitionKey(path="/customerId"))
            for item in (
                {"id": "order-1", "customerId": "customer-501", "amount": 40},
                {"id": "order-2", "customerId": "customer-501", "amount": 150},
                {"id": "order-3", "customerId": "customer-502", "amount": 200},
            ):
                orders.create_item(item)
            yield name
        finally:
            try:
                client.delete_database(name)
            except exceptions.CosmosResourceNotFoundError:
                pass


async def test_query_order_by_descending_offset_limit_returns_second_largest_async_rust(database_id):
    """ORDER BY amount DESC with OFFSET 1 LIMIT 1 returns exactly the second-largest row, order-1."""
    async with AsyncCosmosClient(os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"], _backend="rust") as client:
        container = client.get_database_client(database_id).get_container_client("orders")

        async def consume():
            results = container.query_items(
                query=(
                    "SELECT o.id FROM orders o WHERE o.amount >= @minimumAmount "
                    "ORDER BY o.amount DESC OFFSET 1 LIMIT 1"
                ),
                parameters=[{"name": "@minimumAmount", "value": 40}],
                partition_key="customer-501",
            )
            return [row async for row in results]

        rows = await run_on_rust_async(client, consume)

    assert rows == [{"id": "order-1"}]
