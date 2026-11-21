# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""Bounded create/delete/idle phases; no CLI, provisioning, or automatic live run."""

import asyncio
from dataclasses import asdict, dataclass
import math
import re
import time

from azure.core import MatchConditions
import psutil


@dataclass(frozen=True)
class CycleConfig:
    namespace: str
    partition_key: str
    pool_size: int
    cycles: int
    concurrency: int
    idle_seconds: float
    sample_seconds: float
    max_seconds: float
    max_rss_bytes: int
    operation_timeout: float

    def __post_init__(self):
        if not re.fullmatch(r"[0-9a-f]{32}", self.namespace):
            raise ValueError("A fresh 32-character hexadecimal namespace is required")
        if self.partition_key not in ("/id", "/customerId"):
            raise ValueError("Only /id and /customerId are supported")
        for name, lower, upper in (
            ("pool_size", 1, 10000), ("cycles", 1, 10000),
            ("concurrency", 1, 64), ("max_rss_bytes", 1, 16 * 1024**3),
        ):
            value = getattr(self, name)
            if type(value) is not int or not lower <= value <= upper:
                raise ValueError(f"{name} must be an integer in [{lower}, {upper}]")
        for name in ("idle_seconds", "sample_seconds", "max_seconds", "operation_timeout"):
            value = getattr(self, name)
            if not math.isfinite(value) or value <= 0:
                raise ValueError(f"{name} must be finite and positive")
        if self.concurrency > self.pool_size or self.sample_seconds < 0.1:
            raise ValueError("Concurrency must fit the pool; sample interval must be >= 0.1s")
        if self.cycles * self.idle_seconds >= self.max_seconds:
            raise ValueError("Time budget must leave room for create/delete phases")

    @property
    def prefix(self):
        return f"memory-{self.namespace}-"

    def item(self, slot):
        suffix = f"{self.namespace}-{slot}"
        return {
            "id": f"memory-{suffix}", "customerId": f"customer-{suffix}",
            "countryCode": "US", "quantity": 2, "status": "Pending",
            "memoryRun": self.namespace,
        }

    def key(self, slot):
        return self.item(slot)[self.partition_key[1:]]


async def _workers(count, concurrency, operation):
    remaining = iter(range(count))
    failed = False

    async def worker():
        nonlocal failed
        try:
            while not failed:
                slot = next(remaining, None)
                if slot is None:
                    return
                await operation(slot)
        except BaseException:
            failed = True
            raise

    tasks = [asyncio.create_task(worker()) for _ in range(concurrency)]
    try:
        await asyncio.gather(*tasks)
    finally:
        for task in tasks:
            if not task.done():
                task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)


async def run_memory_cycles(client, database, container_name, config, emit):
    """Own one client lifetime; stream records through a synchronous bounded sink.

    The caller must persist the initial run record before writes and arrange
    explicit live-target approval. This function never selects a default target.
    A completed run is bookkeeping evidence, not a leak or allocator verdict.
    """
    if not database or not container_name:
        raise ValueError("Explicit database and container names are required")
    process = psutil.Process()
    started = time.monotonic()
    phase = "preflight"
    cycle = 0
    progress = {"completed": 0, "request_charge": 0.0, "errors": 0, "throttled_429": 0}

    def record(kind, **values):
        cpu = process.cpu_times()
        rss = process.memory_info().rss
        elapsed = time.monotonic() - started
        emit({
            "record_type": kind, "pid": process.pid, "elapsed_seconds": elapsed,
            "phase": phase, "cycle": cycle, "cpu_seconds": cpu.user + cpu.system,
            "rss_bytes": rss, "threads": process.num_threads(), **progress, **values,
        })
        if kind not in ("failure", "cleanup") and (
            rss >= config.max_rss_bytes or elapsed >= config.max_seconds
        ):
            raise RuntimeError("Memory-cycle resource budget exceeded")

    async def inventory(container):
        rows = []
        query = container.query_items(
            "SELECT * FROM c WHERE STARTSWITH(c.id, @prefix)",
            parameters=[{"name": "@prefix", "value": config.prefix}],
            enable_cross_partition_query=True,
        )
        async for item in query:
            rows.append(item)
            if len(rows) > config.pool_size:
                raise RuntimeError("Owned inventory exceeds the bounded pool")
        return rows

    async def cleanup(container):
        rows = await inventory(container)
        expected = {config.item(slot)["id"]: config.item(slot) for slot in range(config.pool_size)}
        seen = set()
        for item in rows:
            body = {key: value for key, value in item.items() if not key.startswith("_")}
            if (body != expected.get(item.get("id")) or not item.get("_etag")
                    or item["id"] in seen):
                raise RuntimeError("Cleanup ownership/body check failed; no cleanup deletes issued")
            seen.add(item["id"])
        for item in rows:
            await container.delete_item(
                item["id"], partition_key=item[config.partition_key[1:]],
                etag=item["_etag"], match_condition=MatchConditions.IfNotModified,
            )
        if await inventory(container):
            raise RuntimeError("Owned items remain after cleanup")
        record("cleanup", removed=len(rows), observed_empty=True)

    async with client:
        container = client.get_database_client(database).get_container_client(container_name)
        record("run", config=asdict(config), database=database, container=container_name)
        properties = await asyncio.wait_for(container.read(), config.operation_timeout)
        if (properties.get("partitionKey", {}).get("paths") != [config.partition_key]
                or properties.get("defaultTtl") is not None):
            raise ValueError("Actual partition key or TTL differs from the explicit workload contract")
        if await asyncio.wait_for(inventory(container), config.operation_timeout):
            raise ValueError("Namespace is occupied; explicit recovery required")
        async def sample():
            while True:
                await asyncio.sleep(config.sample_seconds)
                record("sample")

        async def cycles():
            nonlocal phase, cycle
            for cycle in range(1, config.cycles + 1):
                for phase in ("create", "delete"):
                    progress.update(completed=0, request_charge=0.0, errors=0, throttled_429=0)
                    record("phase_start")

                    async def operation(slot):
                        request_charge = None

                        def response_hook(headers, _):
                            nonlocal request_charge
                            request_charge = float(headers["x-ms-request-charge"])
                            if not math.isfinite(request_charge) or request_charge < 0:
                                raise ValueError("Invalid request charge")

                        if phase == "create":
                            call = container.create_item(config.item(slot), response_hook=response_hook)
                        else:
                            call = container.delete_item(
                                config.item(slot)["id"], partition_key=config.key(slot),
                                response_hook=response_hook,
                            )
                        try:
                            await asyncio.wait_for(call, config.operation_timeout)
                            if request_charge is None:
                                raise RuntimeError("Successful operation did not expose a request charge")
                        except BaseException as error:
                            progress["errors"] += 1
                            progress["throttled_429"] += getattr(error, "status_code", None) == 429
                            raise
                        progress["completed"] += 1
                        progress["request_charge"] += request_charge

                    await _workers(config.pool_size, config.concurrency, operation)
                    record("phase_end")
                phase = "idle"
                progress.update(completed=0, request_charge=0.0, errors=0, throttled_429=0)
                record("phase_start")
                await asyncio.sleep(config.idle_seconds)
                record("phase_end", completed=0, request_charge=0.0)

        monitor = asyncio.create_task(sample())
        workload = asyncio.create_task(cycles())
        try:
            done, _ = await asyncio.wait(
                (monitor, workload), timeout=config.max_seconds - (time.monotonic() - started),
                return_when=asyncio.FIRST_COMPLETED,
            )
            if not done:
                raise TimeoutError("Memory-cycle elapsed-time budget exceeded")
            if monitor in done:
                await monitor
            await workload
        except BaseException as error:
            # Cancellation/timeout can leave an ambiguous service outcome; never
            # turn an empty cleanup inventory into a successful workload verdict.
            for task in (monitor, workload):
                task.cancel()
            await asyncio.gather(monitor, workload, return_exceptions=True)
            try:
                try:
                    record("failure", error_type=type(error).__name__, outcome="incomplete")
                finally:
                    phase = "cleanup"
                    await asyncio.wait_for(cleanup(container), config.operation_timeout)
            except BaseException as cleanup_error:
                raise RuntimeError(
                    f"Run failed ({type(error).__name__}); cleanup also failed "
                    f"({type(cleanup_error).__name__}); explicit recovery required"
                ) from error
            raise
        else:
            monitor.cancel()
            await asyncio.gather(monitor, return_exceptions=True)
            phase = "cleanup"
            await asyncio.wait_for(cleanup(container), config.operation_timeout)
    phase = "complete"
    record("completion", completed_cycles=config.cycles, memory_verdict="not_evaluated")
