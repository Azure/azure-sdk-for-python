#!/usr/bin/env python3
# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""Unified Cosmos DB workload — operations, proxy, and sync/async controlled by env vars.

Environment variables:
  WORKLOAD_OPERATIONS  comma-separated list of operations (default: read,write,query)
  WORKLOAD_USE_PROXY   route through Envoy proxy (default: false)
  WORKLOAD_USE_SYNC    use sync client instead of async (default: false)
"""

import logging
import os
import asyncio
import gc
import time

from azure.cosmos.aio import CosmosClient as AsyncClient
from azure.cosmos import CosmosClient as SyncClient, documents
from azure.core.pipeline.transport import AioHttpTransport

from workload_utils import *
# `import *` skips underscore-prefixed names, so import the loop-lag monitor explicitly.
from workload_utils import _loop_lag_monitor
from workload_configs import *


_gc_frozen = False


def _maybe_freeze_gc(client_logger):
    """Optionally freeze the GC once per process, after warmup.

    gc.freeze() moves every object that already exists into a permanent
    generation that the collector never rescans, so steady-state GC work (and the
    pauses it adds to the latency tail) shrinks. We only do this when explicitly
    asked (WORKLOAD_GC_FREEZE=true) because the default run should measure the SDK
    as it really behaves, GC included. Idempotent: the module flag ensures we
    freeze a single, consistent snapshot even when many clients share the process.
    """
    global _gc_frozen
    if WORKLOAD_GC_FREEZE and not _gc_frozen:
        _gc_frozen = True
        gc.freeze()
        client_logger.info("GC frozen after warmup (WORKLOAD_GC_FREEZE=true)")


async def run_workload_async(client_id, client_logger, stats=None, reporter=None):
    """Async workload loop — default mode."""
    ops = WORKLOAD_OPERATIONS
    use_proxy = WORKLOAD_USE_PROXY

    owns_reporter = False
    if stats is None:
        try:
            from perf_config import get_perf_config

            perf_config = get_perf_config()
            if perf_config["enabled"] and perf_config["results_endpoint"]:
                from perf_stats import Stats
                from perf_reporter import PerfReporter

                stats = Stats()
                reporter = PerfReporter(stats, perf_config)
                reporter.start()
                owns_reporter = True
        except ImportError as e:
            logging.getLogger(__name__).info("Perf reporting disabled: %s", e)

    session = None
    transport = None
    try:
        if use_proxy:
            session = create_custom_session()
            transport = AioHttpTransport(session=session, session_owner=False)

        client_kwargs = dict(
            preferred_locations=PREFERRED_LOCATIONS,
            excluded_locations=CLIENT_EXCLUDED_LOCATIONS,
            enable_diagnostics_logging=ENABLE_DIAGNOSTICS_LOGGING,
            logger=client_logger,
            user_agent=get_user_agent(client_id),
        )
        if use_proxy and transport:
            client_kwargs["transport"] = transport
        if USE_MULTIPLE_WRITABLE_LOCATIONS:
            client_kwargs["multiple_write_locations"] = True

        client = AsyncClient(COSMOS_URI, COSMOS_CREDENTIAL, **client_kwargs)
        if not WORKLOAD_SKIP_CLOSE:
            await client.__aenter__()

        try:
            db = client.get_database_client(COSMOS_DATABASE)
            cont = db.get_container_client(COSMOS_CONTAINER)
            await asyncio.sleep(1)
            _maybe_freeze_gc(client_logger)

            # One event-loop lag monitor per process. Only the single-client direct
            # path (owns_reporter) starts it here; in multi-client mode it is
            # started once in run_multi_client_async so N clients do not spawn N
            # monitors all writing the same gauge.
            monitor_task = None
            if owns_reporter and WORKLOAD_LOOP_LAG_MONITOR and stats is not None:
                monitor_task = asyncio.create_task(_loop_lag_monitor(stats))

            try:
                if WORKLOAD_ARRIVAL_RATE > 0:
                    # Open-loop, constant-arrival load (WORKLOAD_ARRIVAL_RATE ops/sec
                    # PER CLIENT). Unlike the closed-loop driver below it does not
                    # wait between waves and times each op from its intended arrival,
                    # so the tail reflects coordinated omission. See
                    # docs/RUST_PYTHON_PERFORMANCE.md, "Measurement caveats".
                    await run_open_loop(
                        cont, REQUEST_EXCLUDED_LOCATIONS, stats, ops,
                        WORKLOAD_ARRIVAL_RATE, WORKLOAD_MAX_INFLIGHT,
                    )
                else:
                    # Closed-loop, batched-wave load: each op below launches
                    # CONCURRENT_REQUESTS calls and waits for the WHOLE wave (an
                    # asyncio.gather barrier inside each *_concurrently) before the
                    # next op runs. Two consequences for throughput: (1) a wave does
                    # not refill as calls finish — it is gated by its SLOWEST call
                    # (the tail, not the mean), so in-flight decays from N toward 0
                    # each wave; and (2) the enabled ops run in SEQUENTIAL phases, so
                    # with all six each is in flight only ~1/6 of the time. Real
                    # req/s is therefore well below the open-loop (concurrency /
                    # per_op) formula — read achieved req/s from the rows as
                    # count / window_seconds, not from the formula. See
                    # docs/RUST_PYTHON_PERFORMANCE.md, "Concurrency is not throughput".
                    while True:
                        try:
                            if "create" in ops:
                                await create_item_concurrently(
                                    cont, REQUEST_EXCLUDED_LOCATIONS, CONCURRENT_REQUESTS, stats
                                )
                            if "upsert" in ops:
                                await upsert_item_concurrently(
                                    cont, REQUEST_EXCLUDED_LOCATIONS, CONCURRENT_REQUESTS, stats
                                )
                            if "replace" in ops:
                                await replace_item_concurrently(
                                    cont, REQUEST_EXCLUDED_LOCATIONS, CONCURRENT_REQUESTS, stats
                                )
                            if "read" in ops:
                                await read_item_concurrently(
                                    cont, REQUEST_EXCLUDED_LOCATIONS, CONCURRENT_REQUESTS, stats
                                )
                            if "patch" in ops:
                                await patch_item_concurrently(
                                    cont, REQUEST_EXCLUDED_LOCATIONS, CONCURRENT_REQUESTS, stats
                                )
                            if "delete" in ops:
                                await delete_item_concurrently(
                                    cont, REQUEST_EXCLUDED_LOCATIONS, CONCURRENT_REQUESTS, stats
                                )
                            if "query" in ops:
                                await query_items_concurrently(
                                    cont, REQUEST_EXCLUDED_LOCATIONS, CONCURRENT_QUERIES, stats
                                )
                        except Exception as e:
                            client_logger.info("Exception in application layer")
                            client_logger.error(e)
            finally:
                if monitor_task is not None:
                    monitor_task.cancel()
                    try:
                        await monitor_task
                    except Exception:
                        pass
        finally:
            if not WORKLOAD_SKIP_CLOSE:
                await client.__aexit__(None, None, None)
    finally:
        if reporter and owns_reporter:
            try:
                reporter.stop()
            except Exception:
                pass
        if session:
            await session.close()


def run_workload_sync(client_id, client_logger):
    """Sync workload loop — used when WORKLOAD_USE_SYNC=true."""
    if WORKLOAD_USE_PROXY:
        raise RuntimeError("Proxy mode is not supported with sync client. "
                           "Set WORKLOAD_USE_SYNC=false or WORKLOAD_USE_PROXY=false.")
    ops = WORKLOAD_OPERATIONS

    stats = None
    perf_config = None
    reporter = None

    try:
        from perf_config import get_perf_config

        perf_config = get_perf_config()
        if perf_config["enabled"] and perf_config["results_endpoint"]:
            from perf_stats import Stats
            from perf_reporter import PerfReporter

            stats = Stats()
            reporter = PerfReporter(stats, perf_config)
            reporter.start()
    except ImportError as e:
        logging.getLogger(__name__).info("Perf reporting disabled: %s", e)

    try:
        connection_policy = documents.ConnectionPolicy()
        connection_policy.UseMultipleWriteLocations = USE_MULTIPLE_WRITABLE_LOCATIONS

        with SyncClient(
            COSMOS_URI,
            COSMOS_CREDENTIAL,
            connection_policy=connection_policy,
            preferred_locations=PREFERRED_LOCATIONS,
            excluded_locations=CLIENT_EXCLUDED_LOCATIONS,
            enable_diagnostics_logging=ENABLE_DIAGNOSTICS_LOGGING,
            logger=client_logger,
            user_agent=get_user_agent(client_id),
        ) as client:
            db = client.get_database_client(COSMOS_DATABASE)
            cont = db.get_container_client(COSMOS_CONTAINER)
            time.sleep(1)

            # Sync mode is FULLY SERIAL: each op below runs its CONCURRENT_REQUESTS
            # calls in a plain for-loop, one at a time, so real concurrency is 1
            # regardless of CONCURRENT_REQUESTS and throughput is ~ 1 / mean_op
            # latency. Use async mode to drive real concurrency. See
            # docs/RUST_PYTHON_PERFORMANCE.md, "Concurrency is not throughput".
            while True:
                try:
                    if "create" in ops:
                        create_item(
                            cont, REQUEST_EXCLUDED_LOCATIONS, CONCURRENT_REQUESTS, stats
                        )
                    if "upsert" in ops:
                        upsert_item(
                            cont, REQUEST_EXCLUDED_LOCATIONS, CONCURRENT_REQUESTS, stats
                        )
                    if "replace" in ops:
                        replace_item(
                            cont, REQUEST_EXCLUDED_LOCATIONS, CONCURRENT_REQUESTS, stats
                        )
                    if "read" in ops:
                        read_item(
                            cont, REQUEST_EXCLUDED_LOCATIONS, CONCURRENT_REQUESTS, stats
                        )
                    if "patch" in ops:
                        patch_item(
                            cont, REQUEST_EXCLUDED_LOCATIONS, CONCURRENT_REQUESTS, stats
                        )
                    if "delete" in ops:
                        delete_item(
                            cont, REQUEST_EXCLUDED_LOCATIONS, CONCURRENT_REQUESTS, stats
                        )
                    if "query" in ops:
                        query_items(
                            cont, REQUEST_EXCLUDED_LOCATIONS, CONCURRENT_QUERIES, stats
                        )
                except Exception as e:
                    client_logger.info("Exception in application layer")
                    client_logger.error(e)
    finally:
        if reporter:
            try:
                reporter.stop()
            except Exception:
                pass


async def run_multi_client_async(prefix, client_logger):
    """Spawn multiple async clients in a single process with shared metrics."""
    stats = None
    reporter = None
    try:
        from perf_config import get_perf_config
        perf_config = get_perf_config()
        if perf_config["enabled"] and perf_config["results_endpoint"]:
            from perf_stats import Stats
            from perf_reporter import PerfReporter
            stats = Stats()
            reporter = PerfReporter(stats, perf_config)
            reporter.start()
    except ImportError as e:
        logging.getLogger(__name__).info("Perf reporting disabled: %s", e)

    try:
        tasks = []
        for i in range(WORKLOAD_NUM_CLIENTS):
            client_id = f"{prefix}-c{i}"
            tasks.append(run_workload_async(client_id, client_logger, stats=stats, reporter=reporter))
        # One process-wide event-loop lag monitor for all clients sharing this loop
        # (the per-client path skips it because owns_reporter is False here).
        monitor_task = None
        if WORKLOAD_LOOP_LAG_MONITOR and stats is not None:
            monitor_task = asyncio.create_task(_loop_lag_monitor(stats))
        try:
            # return_exceptions=True so one client failing (for example, while it
            # is being built) does not stop the others sharing this process.
            await asyncio.gather(*tasks, return_exceptions=True)
        finally:
            if monitor_task is not None:
                monitor_task.cancel()
                try:
                    await monitor_task
                except Exception:
                    pass
    finally:
        if reporter:
            try:
                reporter.stop()
            except Exception:
                pass


if __name__ == "__main__":
    file_name = os.path.basename(__file__)
    prefix, logger = create_logger(file_name)
    if WORKLOAD_USE_SYNC:
        run_workload_sync(prefix, logger)
    elif WORKLOAD_NUM_CLIENTS > 1:
        asyncio.run(run_multi_client_async(prefix, logger))
    else:
        asyncio.run(run_workload_async(prefix, logger))
