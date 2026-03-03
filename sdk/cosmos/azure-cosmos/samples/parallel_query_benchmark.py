# The MIT License (MIT)
# Copyright (c) 2026 Microsoft Corporation

"""Benchmark script for measuring async query parallelization performance.

This script measures the impact of max_degree_of_parallelism on cross-partition
query execution time, RU consumption, and throughput.

Prerequisites:
    - A Cosmos DB account with a multi-partition container
    - The container should have enough data spread across partitions
    - Set environment variables:
        COSMOS_ENDPOINT: Your Cosmos DB endpoint
        COSMOS_KEY: Your Cosmos DB key
        COSMOS_DATABASE: Database name
        COSMOS_CONTAINER: Container name (must have multiple physical partitions)

Usage:
    python samples/parallel_query_benchmark.py

    # With custom parallelism levels:
    python samples/parallel_query_benchmark.py --degrees 0,1,2,4,8,16,-1

    # With custom number of iterations:
    python samples/parallel_query_benchmark.py --iterations 5
"""

import argparse
import asyncio
import os
import statistics
import time
from azure.cosmos.aio import CosmosClient  # noqa: E402


async def run_query(container, query, max_degree, max_item_count=100):
    """Run a query and return (elapsed_seconds, total_ru, item_count).

    :param container: The container proxy to query.
    :param str query: The SQL query string.
    :param int max_degree: The max_degree_of_parallelism value.
    :param int max_item_count: Page size.
    :returns: Tuple of (elapsed_seconds, total_ru, item_count).
    :rtype: tuple[float, float, int]
    """
    total_ru = 0.0
    item_count = 0

    def response_hook(headers, _body):
        nonlocal total_ru
        ru = headers.get("x-ms-request-charge", "0")
        total_ru += float(ru)

    start = time.perf_counter()
    items = container.query_items(
        query=query,
        max_degree_of_parallelism=max_degree,
        max_item_count=max_item_count,
        response_hook=response_hook,
    )
    async for _item in items:
        item_count += 1
    elapsed = time.perf_counter() - start

    return elapsed, total_ru, item_count


async def populate_container(container, num_items=500):
    """Populate the container with test documents if it's empty.

    :param container: The container proxy.
    :param int num_items: Number of items to create.
    """
    # Check if container already has data
    count = 0
    items = container.query_items(query="SELECT VALUE COUNT(1) FROM c")
    async for result in items:
        count = result
    if count >= num_items:
        print(f"Container already has {count} items, skipping population.")
        return

    import uuid
    print(f"Populating container with {num_items} items...")
    for i in range(num_items):
        doc = {
            "id": str(uuid.uuid4()),
            "partitionKey": f"pk_{i % 50}",  # spread across 50 logical partitions
            "value": i,
            "category": f"cat_{i % 10}",
            "description": f"Test document number {i} for benchmarking parallel query execution",
        }
        await container.create_item(body=doc)
    print(f"Populated {num_items} items.")


async def main():
    parser = argparse.ArgumentParser(description="Benchmark parallel query execution")
    parser.add_argument("--degrees", type=str, default="0,1,2,4,8,-1",
                        help="Comma-separated list of max_degree_of_parallelism values to test")
    parser.add_argument("--iterations", type=int, default=3,
                        help="Number of iterations per configuration")
    parser.add_argument("--populate", action="store_true",
                        help="Populate the container with test data first")
    parser.add_argument("--max-item-count", type=int, default=100,
                        help="Page size for queries")
    args = parser.parse_args()

    endpoint = os.environ.get("COSMOS_ENDPOINT")
    key = os.environ.get("COSMOS_KEY")
    database_name = os.environ.get("COSMOS_DATABASE", "benchmark_db")
    container_name = os.environ.get("COSMOS_CONTAINER", "benchmark_container")

    if not endpoint or not key:
        print("ERROR: Set COSMOS_ENDPOINT and COSMOS_KEY environment variables.")
        sys.exit(1)

    degrees = [int(d.strip()) for d in args.degrees.split(",")]

    queries = [
        ("Cross-partition scan", "SELECT * FROM c"),
        ("Cross-partition ORDER BY", "SELECT * FROM c ORDER BY c.value"),
        ("Cross-partition with filter", "SELECT * FROM c WHERE c.category = 'cat_5'"),
        ("Cross-partition aggregate", "SELECT VALUE COUNT(1) FROM c"),
    ]

    async with CosmosClient(endpoint, key) as client:
        database = client.get_database_client(database_name)
        container = database.get_container_client(container_name)

        if args.populate:
            await populate_container(container)

        print("=" * 90)
        print(f"{'Query Type':<35} {'Degree':<8} {'Time (s)':<12} {'RU':<12} {'Items':<8} {'Items/s':<10}")
        print("=" * 90)

        for query_name, query_str in queries:
            for degree in degrees:
                times = []
                rus = []
                counts = []

                for _ in range(args.iterations):
                    elapsed, total_ru, item_count = await run_query(
                        container, query_str, degree, args.max_item_count
                    )
                    times.append(elapsed)
                    rus.append(total_ru)
                    counts.append(item_count)

                avg_time = statistics.mean(times)
                avg_ru = statistics.mean(rus)
                avg_count = statistics.mean(counts)
                items_per_sec = avg_count / avg_time if avg_time > 0 else 0

                degree_str = "auto" if degree == -1 else str(degree)
                print(f"{query_name:<35} {degree_str:<8} {avg_time:<12.3f} {avg_ru:<12.1f} "
                      f"{int(avg_count):<8} {items_per_sec:<10.1f}")

            print("-" * 90)

        print("\nBenchmark complete.")
        print("\nNotes:")
        print("  - Degree 0 = serial execution (baseline)")
        print("  - Degree -1 = auto (system decides)")
        print("  - Higher degrees consume more RU/s but may reduce wall-clock time")
        print("  - Results vary based on partition count, data distribution, and account throughput")


if __name__ == "__main__":
    asyncio.run(main())
