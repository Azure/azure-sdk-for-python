# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Customize and share a Rust runtime, without changing the default singleton.

Set ACCOUNT_URI and ACCOUNT_KEY. Database sales and container orders must
already contain order-42 with partition key customer-17. This sample only reads.
For this migration checkout, also set COSMOS_BACKEND=rust.
Run `python runtime_configuration.py` (sync) or add `--async`.
"""

import argparse
import asyncio
import os

from azure.cosmos import ConnectionPoolOptions, CosmosClient, CosmosRuntime
from azure.cosmos.aio import CosmosClient as AsyncCosmosClient


OPTIONS = ConnectionPoolOptions(
    connection_timeout=2,
    data_http_request_timeout=6,
    metadata_http_request_timeout=20,
    idle_connection_timeout=300,
    max_idle_connections_per_endpoint=100,
)


def run_sync(endpoint: str, key: str) -> None:
    """Share one custom runtime between clients with different overall defaults."""
    runtime = CosmosRuntime.create(connection_pool=OPTIONS)
    with CosmosClient(endpoint, key, runtime=runtime, timeout=30) as first:
        with CosmosClient(endpoint, key, runtime=runtime, timeout=10) as second:
            orders = second.get_database_client("sales").get_container_client("orders")
            print(orders.read_item("order-42", partition_key="customer-17", timeout=2)["id"])
        # Closing second does not invalidate first's runtime reference.
        orders = first.get_database_client("sales").get_container_client("orders")
        print(orders.read_item("order-42", partition_key="customer-17")["id"])


async def run_async(endpoint: str, key: str) -> None:
    """Initialize without blocking the event loop, then share the runtime."""
    runtime = await CosmosRuntime.create_async(connection_pool=OPTIONS)
    async with AsyncCosmosClient(endpoint, key, runtime=runtime, timeout=30) as first:
        async with AsyncCosmosClient(endpoint, key, runtime=runtime, timeout=10) as second:
            orders = second.get_database_client("sales").get_container_client("orders")
            order = await orders.read_item("order-42", partition_key="customer-17", timeout=2)
            print(order["id"])
        orders = first.get_database_client("sales").get_container_client("orders")
        order = await orders.read_item("order-42", partition_key="customer-17")
        print(order["id"])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--async", dest="asynchronous", action="store_true")
    args = parser.parse_args()
    if args.asynchronous:
        asyncio.run(run_async(os.environ["ACCOUNT_URI"], os.environ["ACCOUNT_KEY"]))
    else:
        run_sync(os.environ["ACCOUNT_URI"], os.environ["ACCOUNT_KEY"])
