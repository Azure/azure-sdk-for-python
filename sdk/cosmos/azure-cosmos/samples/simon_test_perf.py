"""
Cosmos DB Vector Search – QPS Benchmark (50K) — Python async SDK
Direct translation of the .NET query50k benchmark.
"""

import asyncio
import struct
import time
import random
import os
import sys
from dataclasses import dataclass

import numpy as np
import pyarrow.parquet as pq
import aiohttp
from azure.core.pipeline.transport import AioHttpTransport
from azure.cosmos.aio import CosmosClient
from azure.cosmos import PartitionKey
import azure.cosmos._timing_instrument  # noqa: F401 - installs timing hooks
from azure.cosmos._timing import print_timing_summary

# ── Config ──────────────────────────────────────────────────────────────────
ENDPOINT = os.environ.get("COSMOS_ENDPOINT", "")
KEY = os.environ.get("COSMOS_KEY", "")
if not ENDPOINT or not KEY:
    print("ERROR: Set COSMOS_ENDPOINT and COSMOS_KEY environment variables.", file=sys.stderr)
    sys.exit(1)
DATABASE_NAME = "vectorbench"
CONTAINER_NAME = "cohere1m"

TOP_K = 10
DURATION_PER_LEVEL_SECONDS = 20
CONCURRENCY_LEVELS = [32, 64, 100]
SEARCH_LIST_MULTIPLIERS = [3, 4, 5]
COOLDOWN_SECONDS = 5
CONNECTION_POOL_SIZES = [32, 64, 100, 128, 256]

DATASET_CACHE = os.path.join(os.path.dirname(__file__), "..", "dataset_cache")


@dataclass
class BenchmarkResult:
    concurrency: int
    total_queries: int
    duration_seconds: float
    avg_latency_ms: float
    p50_latency_ms: float
    p95_latency_ms: float
    p99_latency_ms: float
    avg_ru_per_query: float
    recall: float

    @property
    def qps(self) -> float:
        return self.total_queries / self.duration_seconds if self.duration_seconds > 0 else 0


def read_all_binary(path: str) -> tuple[np.ndarray, np.ndarray]:
    """Read test vectors from the custom binary format."""
    with open(path, "rb") as f:
        count, dim = struct.unpack("<ii", f.read(8))
        # Each record: int32 id + float32[dim]
        ids = np.empty(count, dtype=np.int32)
        embeddings = np.empty((count, dim), dtype=np.float32)
        record_bytes = 4 + dim * 4
        for i in range(count):
            buf = f.read(record_bytes)
            if len(buf) < record_bytes:
                raise EOFError(f"Unexpected EOF at vector {i}")
            ids[i] = struct.unpack_from("<i", buf, 0)[0]
            embeddings[i] = np.frombuffer(buf, dtype=np.float32, count=dim, offset=4)
    return ids, embeddings


def read_neighbors(path: str) -> list[np.ndarray]:
    """Read ground truth neighbor IDs from parquet."""
    table = pq.read_table(path)
    neighbors_col = table.column("neighbors_id")
    result = []
    for row in neighbors_col:
        result.append(np.array(row.as_py(), dtype=np.int32))
    return result


def percentile(sorted_data: list[float], p: float) -> float:
    if not sorted_data:
        return 0.0
    idx = max(0, min(int(np.ceil(p * len(sorted_data))) - 1, len(sorted_data) - 1))
    return sorted_data[idx]


async def execute_search(
    container,
    query_vector: np.ndarray,
    top_k: int,
    search_list_multiplier: int | None = None,
) -> tuple[list[int], float]:
    """Execute a single vector search query."""
    vec_list = query_vector.tolist()

    if search_list_multiplier is not None:
        query_text = (
            f"SELECT TOP @topK c.datasetId, "
            f"VectorDistance(c.embedding, @queryVector, false, {{'searchListSizeMultiplier': {search_list_multiplier}}}) AS score "
            f"FROM c "
            f"ORDER BY VectorDistance(c.embedding, @queryVector, false, {{'searchListSizeMultiplier': {search_list_multiplier}}})"
        )
    else:
        query_text = (
            "SELECT TOP @topK c.datasetId, VectorDistance(c.embedding, @queryVector) AS score "
            "FROM c ORDER BY VectorDistance(c.embedding, @queryVector)"
        )

    parameters = [
        {"name": "@topK", "value": top_k},
        {"name": "@queryVector", "value": vec_list},
    ]

    result_ids: list[int] = []

    pager = container.query_items(
        query=query_text,
        parameters=parameters,
        partition_key="vectors",
        max_item_count=top_k,
    )

    async for item in pager:
        result_ids.append(item["datasetId"])

    total_ru = sum(
        float(h.get("x-ms-request-charge", 0))
        for h in pager.get_response_headers()
    )

    return result_ids, total_ru


async def run_at_concurrency(
    container,
    concurrency: int,
    duration_seconds: int,
    query_vectors: np.ndarray,
    ground_truth: list[np.ndarray] | None,
    top_k: int,
    search_list_multiplier: int | None = None,
) -> BenchmarkResult:
    """Run benchmark at a specific concurrency level."""
    gt_sets: list[set[int]] | None = None
    if ground_truth is not None:
        gt_sets = [set(gt[:top_k].tolist()) for gt in ground_truth]

    latencies: list[float] = []
    ru_charges: list[float] = []
    recall_scores: list[float] = []
    query_count = 0
    error_count = 0

    deadline = time.monotonic() + duration_seconds

    async def worker(thread_id: int):
        nonlocal query_count, error_count
        rng = random.Random(thread_id)
        while time.monotonic() < deadline:
            query_idx = rng.randint(0, len(query_vectors) - 1)
            query_vec = query_vectors[query_idx]

            start = time.perf_counter()
            try:
                result_ids, ru = await execute_search(
                    container, query_vec, top_k, search_list_multiplier
                )
                elapsed_ms = (time.perf_counter() - start) * 1000.0

                latencies.append(elapsed_ms)
                ru_charges.append(ru)
                query_count += 1

                if gt_sets is not None and query_idx < len(gt_sets):
                    gt = gt_sets[query_idx]
                    hits = sum(1 for rid in result_ids if rid in gt)
                    recall_scores.append(hits / len(gt) if gt else 0.0)

            except asyncio.CancelledError:
                break
            except Exception as e:
                error_count += 1
                if error_count <= 3:
                    print(f"\n  ❌ Error: {type(e).__name__}: {e}")

    wall_start = time.monotonic()
    tasks = [asyncio.create_task(worker(t)) for t in range(concurrency)]
    await asyncio.gather(*tasks)
    actual_duration = time.monotonic() - wall_start

    sorted_latencies = sorted(latencies)

    if error_count > 0:
        print(f"  ⚠ {error_count} errors at concurrency {concurrency}")

    return BenchmarkResult(
        concurrency=concurrency,
        total_queries=query_count,
        duration_seconds=actual_duration,
        avg_latency_ms=sum(sorted_latencies) / len(sorted_latencies) if sorted_latencies else 0,
        p50_latency_ms=percentile(sorted_latencies, 0.50),
        p95_latency_ms=percentile(sorted_latencies, 0.95),
        p99_latency_ms=percentile(sorted_latencies, 0.99),
        avg_ru_per_query=sum(ru_charges) / len(ru_charges) if ru_charges else 0,
        recall=sum(recall_scores) / len(recall_scores) if recall_scores else 0,
    )


def print_header():
    pass  # No header needed for key=value format


def print_result(result: BenchmarkResult, label: str | None = None):
    tag = f"{label}, " if label else f"Conc={result.concurrency}, "
    print(f"{tag}Queries={result.total_queries}, Duration={result.duration_seconds:.1f}s, "
          f"QPS={result.qps:.1f}, AvgLat={result.avg_latency_ms:.2f}ms, "
          f"P50={result.p50_latency_ms:.2f}ms, P95={result.p95_latency_ms:.2f}ms, "
          f"P99={result.p99_latency_ms:.2f}ms, AvgRU={result.avg_ru_per_query:.1f}, "
          f"Recall={result.recall:.4f}")


async def main():
    # ── Load test vectors ────────────────────────────────────────────────────
    test_bin_path = os.path.join(DATASET_CACHE, "test.bin")
    if not os.path.exists(test_bin_path):
        print(f"Test binary not found: {test_bin_path}", file=sys.stderr)
        print("Run the main project first to download and convert the dataset.", file=sys.stderr)
        return 1

    print("╔══════════════════════════════════════════════════════════════╗")
    print("║   Cosmos DB Vector Search – QPS Benchmark (1M)  [Python]     ║")
    print("║   Container: cohere1m                                        ║")
    print("╚══════════════════════════════════════════════════════════════╝\n")

    print("▸ Loading test vectors...")
    test_ids, test_embeddings = read_all_binary(test_bin_path)
    print(f"  {len(test_ids):,} query vectors ({test_embeddings.shape[1]}d)")

    # ── Load ground truth ────────────────────────────────────────────────────
    neighbors_path = os.path.join(DATASET_CACHE, "neighbors.parquet")
    ground_truth: list[np.ndarray] | None = None
    if os.path.exists(neighbors_path):
        print("▸ Loading ground truth...")
        ground_truth = read_neighbors(neighbors_path)
        print(f"  {len(ground_truth):,} neighbor sets")
    else:
        print("  ⚠ neighbors.parquet not found — recall won't be computed.")

    # ── Create Cosmos client ─────────────────────────────────────────────────
    print(f"\n▸ Connecting to {CONTAINER_NAME}...")
    client = CosmosClient(ENDPOINT, credential=KEY, consistency_level="Eventual")
    database = client.get_database_client(DATABASE_NAME)
    container = database.get_container_client(CONTAINER_NAME)

    # ── Warm up ──────────────────────────────────────────────────────────────
    print("  Warming up connections...")
    warmup_count = min(16, len(test_embeddings))
    warmup_tasks = [
        execute_search(container, test_embeddings[i % len(test_embeddings)], TOP_K)
        for i in range(warmup_count)
    ]
    await asyncio.gather(*warmup_tasks, return_exceptions=True)
    print("  Warm-up complete.")

    # ── Concurrency sweep ────────────────────────────────────────────────────
    print(f"\n▸ Concurrency sweep (duration={DURATION_PER_LEVEL_SECONDS}s per level)")
    print()
    print_header()

    best_result: BenchmarkResult | None = None

    for i, concurrency in enumerate(CONCURRENCY_LEVELS):
        if i > 0:
            await asyncio.sleep(COOLDOWN_SECONDS)
        result = await run_at_concurrency(
            container, concurrency, DURATION_PER_LEVEL_SECONDS,
            test_embeddings, ground_truth, TOP_K
        )
        print_result(result)

        if best_result is None or result.qps > best_result.qps:
            best_result = result

    # ── Summary ──────────────────────────────────────────────────────────────
    print("\n" + "═" * 80)
    print("  RESULTS SUMMARY")
    print("═" * 80)
    if best_result:
        print(f"  🏆 Max QPS:         {best_result.qps:.1f}  (at concurrency {best_result.concurrency})")
        print(f"     Avg latency:     {best_result.avg_latency_ms:.2f} ms")
        print(f"     P50 / P95 / P99: {best_result.p50_latency_ms:.2f} / {best_result.p95_latency_ms:.2f} / {best_result.p99_latency_ms:.2f} ms")
        print(f"     Avg RU/query:    {best_result.avg_ru_per_query:.1f}")
        print(f"     Recall@{TOP_K}:      {best_result.recall:.4f}")
    print("═" * 80)

    # ── Multiplier sweep (all concurrency × all multipliers) ────────────────
    if SEARCH_LIST_MULTIPLIERS:
        print(f"\n▸ Search list multiplier sweep (all concurrency levels × all multipliers)")
        print()

        for concurrency in CONCURRENCY_LEVELS:
            for mult in SEARCH_LIST_MULTIPLIERS:
                await asyncio.sleep(COOLDOWN_SECONDS)
                result = await run_at_concurrency(
                    container, concurrency, DURATION_PER_LEVEL_SECONDS,
                    test_embeddings, ground_truth, TOP_K, mult
                )
                print_result(result, label=f"Mult={mult}, Conc={concurrency}")

        print("═" * 80)

    # ── Connection pool sweep (all pool sizes × all concurrency levels) ────
    if CONNECTION_POOL_SIZES:
        await client.close()
        print(f"\n▸ Connection pool sweep (pool sizes × concurrency levels)")
        print()

        for pool_size in CONNECTION_POOL_SIZES:
            connector = aiohttp.TCPConnector(limit=pool_size, limit_per_host=pool_size)
            session = aiohttp.ClientSession(connector=connector)
            transport = AioHttpTransport(session=session, session_owner=False)
            pool_client = CosmosClient(ENDPOINT, credential=KEY, consistency_level="Eventual",
                                       transport=transport)
            pool_database = pool_client.get_database_client(DATABASE_NAME)
            pool_container = pool_database.get_container_client(CONTAINER_NAME)

            # Brief warmup
            warmup_tasks = [
                execute_search(pool_container, test_embeddings[i % len(test_embeddings)], TOP_K)
                for i in range(min(pool_size, len(test_embeddings)))
            ]
            await asyncio.gather(*warmup_tasks, return_exceptions=True)

            for concurrency in CONCURRENCY_LEVELS:
                await asyncio.sleep(COOLDOWN_SECONDS)
                result = await run_at_concurrency(
                    pool_container, concurrency, DURATION_PER_LEVEL_SECONDS,
                    test_embeddings, ground_truth, TOP_K
                )
                print_result(result, label=f"Pool={pool_size}, Conc={concurrency}")

            await pool_client.close()
            await session.close()

        print("═" * 80)
        client = None  # skip the final close

    if client:
        await client.close()
    print_timing_summary()
    print("\nDone.")
    return 0


if __name__ == "__main__":
    # Use uvloop if available (Linux/macOS) for significantly faster async I/O
    try:
        import uvloop
        print("[PERF] Using uvloop event loop")
        sys.exit(uvloop.run(main()))
    except ImportError:
        print("[PERF] uvloop not available, using default asyncio event loop")
        sys.exit(asyncio.run(main()))