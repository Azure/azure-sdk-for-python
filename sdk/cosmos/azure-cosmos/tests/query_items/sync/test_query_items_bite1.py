# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Bite 1's exact query, run separately on each backend for page capture.

This is a lesson-specific scenario, not a copied original legacy test.
Run with shared conftest provisioning disabled and COSMOS_BACKEND set to
core-python or rust. The fixture owns and deletes its database.
"""

import os
import uuid

import pytest

from azure.cosmos import CosmosClient, PartitionKey
from common._parity_helpers import (
    run_target_operation,
    skip_unless_emulator,
    skip_unless_rust_binding,
)


@pytest.mark.cosmosEmulator
@skip_unless_emulator()
@skip_unless_rust_binding()
class TestQueryBite1:
    """Keep class-based node IDs compatible with the legacy parity reporter."""

    def test_query_one_customers_order_ids(self):
        """Return exactly customer-501's two order IDs, excluding customer-502."""
        backend = os.environ.get("COSMOS_BACKEND", "rust")
        database_id = "query_bite1_" + uuid.uuid4().hex
        with CosmosClient(
            os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"], _backend="core-python",
        ) as setup_client:
            database = setup_client.create_database(database_id)
            print(f"\nOwned Bite 1 database: {database_id}")
            try:
                orders = database.create_container(
                    id="orders", partition_key=PartitionKey(path="/customerId"),
                )
                for item in (
                    {"id": "order-1", "customerId": "customer-501"},
                    {"id": "order-2", "customerId": "customer-501"},
                    {"id": "order-3", "customerId": "customer-502"},
                ):
                    orders.create_item(item)

                with CosmosClient(
                    os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"], _backend=backend,
                ) as client:
                    assert client.client_connection._backend.name == backend
                    orders_container = client.get_database_client(database_id).get_container_client("orders")
                    rows = run_target_operation(
                        client,
                        lambda: list(orders_container.query_items(
                            query="SELECT o.id FROM orders o",
                            partition_key="customer-501",
                        )),
                    )
                    # No ORDER BY: compare complete rows without requiring their order.
                    assert sorted(rows, key=lambda row: row["id"]) == [
                        {"id": "order-1"}, {"id": "order-2"},
                    ]
            finally:
                setup_client.delete_database(database_id)
                print(f"Deleted owned Bite 1 database: {database_id}")
