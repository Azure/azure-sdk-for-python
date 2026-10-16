# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Bite 2's exact numeric filter, separate from copied legacy coverage.

Run with --noconftest and COSMOS_BACKEND set to core-python or rust.
Only the query is measured; core Python prepares the owned fixture.
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
class TestQueryAmountFilter:
    """Check partition scope and the numeric condition together."""

    def test_query_one_customers_large_order_ids(self):
        """Return only order-2: amount 150 in customer-501's partition."""
        backend = os.environ.get("COSMOS_BACKEND", "rust")
        database_id = "query_bite2_" + uuid.uuid4().hex
        with CosmosClient(
            os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"], _backend="core-python",
        ) as setup_client:
            database = setup_client.create_database(database_id)
            print(f"\nOwned Bite 2 database: {database_id}")
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
                            query="SELECT o.id FROM orders o WHERE o.amount >= 100",
                            partition_key="customer-501",
                        )),
                    )
                    assert rows == [{"id": "order-2"}]
            finally:
                setup_client.delete_database(database_id)
                print(f"Deleted owned Bite 2 database: {database_id}")
