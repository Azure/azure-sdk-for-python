# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
# Rust behavior test
"""Partition-scoped ``ORDER BY ... DESC`` queries on Rust return rows in descending order."""

import os
import uuid

import pytest

from azure.cosmos import CosmosClient, PartitionKey, exceptions
from common._rust_checks import run_on_rust

pytestmark = [pytest.mark.cosmosEmulator]


def _rust_client():
    return CosmosClient(os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"], _backend="rust")


@pytest.fixture(scope="module")
def database_id():
    """Orders for two customers in a throwaway database."""
    name = "rust_query_desc_" + uuid.uuid4().hex
    with _rust_client() as client:
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


def _query(database_id, query):
    with _rust_client() as client:
        container = client.get_database_client(database_id).get_container_client("orders")
        return run_on_rust(client, lambda: list(container.query_items(
            query=query,
            parameters=[{"name": "@minimumAmount", "value": 40}],
            partition_key="customer-501",
        )))


def test_query_order_by_descending_returns_partition_rows_largest_first_rust(database_id):
    """A parameterized ORDER BY amount DESC returns order-2 before order-1 and excludes other partitions."""
    rows = _query(
        database_id,
        "SELECT o.id FROM orders o WHERE o.amount >= @minimumAmount ORDER BY o.amount DESC",
    )
    assert rows == [{"id": "order-2"}, {"id": "order-1"}]


def test_query_order_by_descending_offset_limit_returns_second_largest_rust(database_id):
    """ORDER BY amount DESC with OFFSET 1 LIMIT 1 returns exactly the second-largest row, order-1."""
    rows = _query(
        database_id,
        "SELECT o.id FROM orders o WHERE o.amount >= @minimumAmount ORDER BY o.amount DESC OFFSET 1 LIMIT 1",
    )
    assert rows == [{"id": "order-1"}]
