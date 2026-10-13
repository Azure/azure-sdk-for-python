# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Bite 3's numeric parameter, separate from the existing legacy copy.

Run with --noconftest and COSMOS_BACKEND set to core-python or rust.
Only the queries are measured; core Python prepares the owned fixture.
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
class TestQueryBite3:
    """Change the numeric parameter without changing SQL or partition scope."""

    def test_query_with_changing_minimum_amount(self):
        """Minimums 100 and 150 return order-2; minimum 200 returns no orders."""
        backend = os.environ.get("COSMOS_BACKEND", "rust")
        database_id = "query_bite3_" + uuid.uuid4().hex
        query = "SELECT o.id FROM orders o WHERE o.amount >= @minimumAmount"
        with CosmosClient(
            os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"], _backend="core-python",
        ) as setup_client:
            database = setup_client.create_database(database_id)
            print(f"\nOwned Bite 3 database: {database_id}")
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
                    for minimum_amount, expected in (
                        (100, [{"id": "order-2"}]),
                        (150, [{"id": "order-2"}]),
                        (200, []),
                    ):
                        rows = run_target_operation(
                            client,
                            lambda: list(orders_container.query_items(
                                query=query,
                                parameters=[{"name": "@minimumAmount", "value": minimum_amount}],
                                partition_key="customer-501",
                            )),
                        )
                        assert rows == expected, f"minimum_amount={minimum_amount}"
                        print(f"minimum_amount={minimum_amount}: {rows}")
            finally:
                setup_client.delete_database(database_id)
                print(f"Deleted owned Bite 3 database: {database_id}")
