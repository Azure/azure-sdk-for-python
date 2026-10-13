# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Bite 4's descending order within one complete logical partition.

Run with --noconftest and COSMOS_BACKEND set to core-python or rust.
The separate legacy copy verifies ascending order across page boundaries.
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
class TestQueryBite4:
    """Require the returned sequence, not merely the same set of order IDs."""

    def test_query_order_ids_by_amount_descending(self):
        """Return order-2 before order-1; exclude the other customer's order-3."""
        backend = os.environ.get("COSMOS_BACKEND", "rust")
        database_id = "query_bite4_" + uuid.uuid4().hex
        with CosmosClient(
            os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"], _backend="core-python",
        ) as setup_client:
            database = setup_client.create_database(database_id)
            print(f"\nOwned Bite 4 database: {database_id}")
            try:
                orders = database.create_container(
                    id="orders", partition_key=PartitionKey(path="/customerId"),
                )
                for item in (
                    {"id": "order-1", "customerId": "customer-501", "amount": 40},
                    {"id": "order-2", "customerId": "customer-501", "amount": 150},
                    {"id": "order-3", "customerId": "customer-502", "amount": 200},
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
                            query=(
                                "SELECT o.id FROM orders o "
                                "WHERE o.amount >= @minimumAmount "
                                "ORDER BY o.amount DESC"
                            ),
                            parameters=[{"name": "@minimumAmount", "value": 40}],
                            partition_key="customer-501",
                        )),
                    )
                    assert rows == [{"id": "order-2"}, {"id": "order-1"}]
                    print(f"Ordered rows: {rows}")
            finally:
                setup_client.delete_database(database_id)
                print(f"Deleted owned Bite 4 database: {database_id}")
