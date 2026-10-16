# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Bite 5: a total TOP limit is not a per-page max_item_count limit."""

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
class TestQueryTopAndPageSize:
    def test_top_limit_and_page_size(self):
        backend = os.environ.get("COSMOS_BACKEND", "rust")
        database_id = "query_bite5_" + uuid.uuid4().hex
        with CosmosClient(
            os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"], _backend="core-python",
        ) as setup_client:
            database = setup_client.create_database(database_id)
            print(f"\nOwned Bite 5 database: {database_id}")
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
                    suffix = "o.id FROM orders o WHERE o.amount >= @minimumAmount ORDER BY o.amount DESC"
                    cases = (
                        ("SELECT TOP 1 " + suffix, {}, [{"id": "order-2"}]),
                        ("SELECT TOP 1 " + suffix, {"max_item_count": 1}, [{"id": "order-2"}]),
                        ("SELECT " + suffix, {"max_item_count": 1}, [{"id": "order-2"}, {"id": "order-1"}]),
                    )
                    for query, options, expected in cases:
                        def consume_pages():
                            results = orders_container.query_items(
                                query=query,
                                parameters=[{"name": "@minimumAmount", "value": 40}],
                                partition_key="customer-501",
                                **options,
                            )
                            return [list(page) for page in results.by_page()]

                        pages = run_target_operation(client, consume_pages)
                        assert [row for page in pages for row in page] == expected
                        if "max_item_count" in options:
                            assert all(len(page) <= 1 for page in pages)
                        print(f"{query}; options={options}; pages={pages}")
            finally:
                setup_client.delete_database(database_id)
                print(f"Deleted owned Bite 5 database: {database_id}")
