# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------

"""Sample showing how max_concurrency and availability_strategy
interact when configured together on the async Cosmos DB client.

max_concurrency controls parallel cross-partition query fan-out.
availability_strategy controls cross-region request hedging.
When both are enabled, each parallel partition query could also
hedge to secondary regions, so this sample shows how to
configure both for controlled resource usage.

Prerequisites:
    1. An Azure Cosmos account with multiple regions -
       https://azure.microsoft.com/documentation/articles/documentdb-create-account/
    2. Microsoft Azure Cosmos PyPi package -
       https://pypi.python.org/pypi/azure-cosmos/
"""

import asyncio
import os

from azure.cosmos.aio import CosmosClient


async def query_serial_no_hedging(container):
    """Baseline: serial query, no availability strategy (default behavior)."""
    print("\n--- Serial query, no hedging (default) ---")
    items = container.query_items(
        query="SELECT * FROM c ORDER BY c._ts",
    )
    count = 0
    async for _ in items:
        count += 1
    print(f"  Retrieved {count} items")


async def query_parallel_no_hedging(container):
    """Parallel cross-partition query with no availability strategy.

    max_concurrency=4 allows up to 4 partition ranges to be queried
    concurrently. Since availability_strategy is not configured,
    each partition query goes to the primary region only.
    Worst-case concurrent HTTP requests: 4
    """
    print("\n--- Parallel query (degree=4), no hedging ---")
    items = container.query_items(
        query="SELECT * FROM c ORDER BY c._ts",
        max_concurrency=4,
    )
    count = 0
    async for _ in items:
        count += 1
    print(f"  Retrieved {count} items")


async def query_serial_with_hedging(container):
    """Serial query with per-request availability strategy.

    Each page fetch can hedge to secondary regions if the primary
    is slow (threshold_ms=500). Since the query runs serially,
    only 1 partition is queried at a time, but that single request
    may spawn hedged requests to other regions.
    Worst-case concurrent HTTP requests: availability_strategy_max_concurrency (client-level)
    """
    print("\n--- Serial query with per-request hedging ---")
    items = container.query_items(
        query="SELECT * FROM c ORDER BY c._ts",
        availability_strategy={"threshold_ms": 500, "threshold_steps_ms": 100},
    )
    count = 0
    async for _ in items:
        count += 1
    print(f"  Retrieved {count} items")


async def query_parallel_with_hedging(container):
    """Parallel query + availability strategy: both concurrency systems active.

    max_concurrency=4 fans out across partitions concurrently.
    availability_strategy hedges each partition request across regions.
    In the worst case (all regions slow), concurrent requests =
        max_concurrency * availability_strategy_max_concurrency

    With the configuration below: 4 * 2 = 8 max concurrent HTTP requests.
    In the normal (happy) path, hedging doesn't trigger, so it's just 4.
    """
    print("\n--- Parallel query (degree=4) with hedging ---")
    items = container.query_items(
        query="SELECT * FROM c ORDER BY c._ts",
        max_concurrency=4,
        availability_strategy={"threshold_ms": 500, "threshold_steps_ms": 100},
    )
    count = 0
    async for _ in items:
        count += 1
    print(f"  Retrieved {count} items")


async def query_auto_parallel_with_hedging(container):
    """Auto-tuned parallelism + hedging.

    max_concurrency=-1 lets the SDK auto-select concurrency based on
    partition count and CPU cores: min(num_partitions, cpu_count*2, 32).
    Combined with hedging, the worst case is bounded by:
        min(num_partitions, cpu_count*2, 32) * availability_strategy_max_concurrency
    """
    print("\n--- Auto-parallel query (degree=-1) with hedging ---")
    items = container.query_items(
        query="SELECT * FROM c ORDER BY c._ts",
        max_concurrency=-1,
        availability_strategy=True,  # use client defaults
    )
    count = 0
    async for _ in items:
        count += 1
    print(f"  Retrieved {count} items")


async def run_sample():
    url = os.environ["ACCOUNT_URI"]
    key = os.environ["ACCOUNT_KEY"]
    database_id = os.environ.get("DATABASE_ID", "testDatabase")
    container_id = os.environ.get("CONTAINER_ID", "testContainer")

    # Configure client with availability strategy at the client level.
    # availability_strategy_max_concurrency limits hedging concurrency
    # per individual request — this is separate from max_concurrency.
    async with CosmosClient(
        url,
        key,
        availability_strategy={"threshold_ms": 500, "threshold_steps_ms": 100},
        availability_strategy_max_concurrency=2,
    ) as client:
        db = client.get_database_client(database_id)
        container = db.get_container_client(container_id)

        await query_serial_no_hedging(container)
        await query_parallel_no_hedging(container)
        await query_serial_with_hedging(container)
        await query_parallel_with_hedging(container)
        await query_auto_parallel_with_hedging(container)

    print("\nDone.")


if __name__ == "__main__":
    asyncio.run(run_sample())
