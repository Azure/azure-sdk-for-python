#!/usr/bin/env python3
# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""Unified Cosmos DB workload — operations and sync/async controlled by env vars.

Environment variables:
  WORKLOAD_OPERATIONS  comma-separated operations (default: read,create,upsert,replace,delete,patch)
  WORKLOAD_USE_PROXY   route through Envoy proxy (default: false)
  WORKLOAD_USE_SYNC    use the sync client instead of async (default: false)
"""

import asyncio
import gc
import logging
import os
import signal
import threading
import time

from azure.cosmos.aio import CosmosClient as AsyncClient
from azure.cosmos import CosmosClient as SyncClient, documents
from azure.core.pipeline.transport import AioHttpTransport

import perf_backend_counters as backend_counters
from workload_configs import (
    CLIENT_EXCLUDED_LOCATIONS,
    CONCURRENT_QUERIES,
    CONCURRENT_REQUESTS,
    COSMOS_CONTAINER,
    COSMOS_CREDENTIAL,
    COSMOS_DATABASE,
    COSMOS_URI,
    ENABLE_DIAGNOSTICS_LOGGING,
    PREFERRED_LOCATIONS,
    REQUEST_EXCLUDED_LOCATIONS,
    USE_MULTIPLE_WRITABLE_LOCATIONS,
    WORKLOAD_ARRIVAL_RATE,
    WORKLOAD_GC_FREEZE,
    WORKLOAD_LOOP_LAG_MONITOR,
    WORKLOAD_MAX_INFLIGHT,
    WORKLOAD_MIX,
    WORKLOAD_NUM_CLIENTS,
    WORKLOAD_OPERATIONS,
    WORKLOAD_SKIP_CLOSE,
    WORKLOAD_USE_PROXY,
    WORKLOAD_USE_SYNC,
)
from workload_utils import (
    _loop_lag_monitor,
    create_custom_session,
    create_item,
    create_item_concurrently,
    create_logger,
    delete_item,
    delete_item_concurrently,
    get_user_agent,
    mixed_wave_concurrently,
    patch_item,
    patch_item_concurrently,
    query_items,
    query_items_concurrently,
    read_item,
    read_item_concurrently,
    replace_item,
    replace_item_concurrently,
    run_open_loop,
    upsert_item,
    upsert_item_concurrently,
)

# Perf reporting is optional: it needs hdrhistogram and psutil. If they are not
# installed the import fails and the workload still runs, just without reporting.
try:
    from perf_config import get_perf_config
    from perf_stats import Stats
    from perf_reporter import PerfReporter
    _PERF_IMPORT_ERROR = None
except ImportError as exc:
    get_perf_config = Stats = PerfReporter = None
    _PERF_IMPORT_ERROR = exc


_gc_frozen = False


def _start_reporter():
    """Return a started (Stats, PerfReporter) pair, or (None, None).

    Returns (None, None) when the optional perf dependencies are missing or when
    reporting is disabled or has no results endpoint configured.
    """
    if get_perf_config is None:
        logging.getLogger(__name__).info("Perf reporting disabled: %s", _PERF_IMPORT_ERROR)
        return None, None
    perf_config = get_perf_config()
    if perf_config["enabled"] and perf_config["results_endpoint"]:
        stats = Stats()
        reporter = PerfReporter(stats, perf_config)
        reporter.start()
        return stats, reporter
    return None, None


def _wrap_backend_for_counting(client, is_async, client_logger):
    """Record which backend the client actually built, instead of trusting COSMOS_BACKEND.

    A row tagged "rust" that actually ran core-python would mislabel every number,
    so derive the truth from the live client:

      1. Read the concrete backend object the client built. Fail loudly if it
         does not match the COSMOS_BACKEND
         label, and record its class name as ``runtime_backend`` on every row.
      2. Wrap its ``execute`` to count how many operations the Rust driver actually
         handled (returned a non-None response). The item helpers fall back to
         core-python when ``execute`` returns None, so this count is per-row proof
         the Rust path did the work. The temporary legacy backend is not wrapped,
         so its count stays 0.
    """

    backend = client._backend
    runtime_name = type(backend).__name__
    backend_counters.set_runtime_backend(runtime_name)

    labeled = os.environ.get("COSMOS_BACKEND", "core-python").strip().lower()
    if labeled in ("", "core_python", "core-python", "python"):
        labeled = "core-python"
    actual = backend.name
    if labeled != actual:
        raise RuntimeError(
            "backend mismatch: COSMOS_BACKEND="
            f"{labeled!r} but the client actually built {actual!r} "
            f"({runtime_name}). Refusing to run -- the results would be "
            "mislabeled. Check the _rust extension is built/importable on this "
            "host and COSMOS_BACKEND is set correctly."
        )
    client_logger.info(
        "backend check: label=%s runtime_backend=%s", labeled, runtime_name
    )
    if actual == "core-python":
        return

    orig_execute = backend.execute
    if is_async:
        async def _counting_execute(prepared):
            response = await orig_execute(prepared)
            if response is not None:
                backend_counters.record_execute()
            return response
    else:
        def _counting_execute(prepared):
            response = orig_execute(prepared)
            if response is not None:
                backend_counters.record_execute()
            return response
    backend.execute = _counting_execute


def _maybe_freeze_gc(client_logger):
    """Freeze the GC once per process, after warmup, when WORKLOAD_GC_FREEZE is set.

    gc.freeze() stops existing objects from being rescanned, which keeps GC pauses
    out of the latency tail. Off by default so a normal run measures the SDK with
    GC included. The module flag makes this run only once when clients share a process.
    """
    global _gc_frozen
    if WORKLOAD_GC_FREEZE and not _gc_frozen:
        _gc_frozen = True
        gc.freeze()
        client_logger.info("GC frozen after warmup (WORKLOAD_GC_FREEZE=true)")


def _install_async_stop(stop_event):
    """Handle SIGINT/SIGTERM by setting stop_event for a graceful stop.

    The load loops never finish on their own; the run is bounded externally by
    ``timeout --signal=INT``. Without a handler that signal raises KeyboardInterrupt
    at a random await, which can abandon the client's async close half-done and
    leave the Rust runtime threads alive so the process never exits. The handler
    just sets the event; the loops poll it between waves and exit normally, so the
    finally blocks close the client cleanly.

    add_signal_handler works only on the POSIX main thread. Elsewhere it is
    unavailable, so we return False and the caller keeps the KeyboardInterrupt fallback.
    """
    loop = asyncio.get_running_loop()
    installed = False
    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, stop_event.set)
            installed = True
        except (NotImplementedError, RuntimeError, ValueError):
            # Not the main thread of a POSIX process (e.g. Windows Proactor loop).
            pass
    return installed


async def run_workload_async(client_id, client_logger, stats=None, reporter=None,
                             stop_event=None):
    """Async workload loop — default mode."""
    ops = WORKLOAD_OPERATIONS
    use_proxy = WORKLOAD_USE_PROXY

    owns_reporter = False
    if stats is None:
        stats, reporter = _start_reporter()
        owns_reporter = stats is not None

    # A None stop_event means the single-client path, so install the handler here.
    # Multi-client mode passes in one shared event with the handler already set, so
    # one signal stops every client (a per-client handler would overwrite the others).
    if stop_event is None:
        stop_event = asyncio.Event()
        _install_async_stop(stop_event)

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
            _wrap_backend_for_counting(client, is_async=True, client_logger=client_logger)
            _maybe_freeze_gc(client_logger)

            # One loop-lag monitor per process. Only the single-client path starts
            # it here; multi-client mode starts one in run_multi_client_async.
            monitor_task = None
            if owns_reporter and WORKLOAD_LOOP_LAG_MONITOR and stats is not None:
                monitor_task = asyncio.create_task(_loop_lag_monitor(stats))

            try:
                if WORKLOAD_ARRIVAL_RATE > 0:
                    # Open-loop load at WORKLOAD_ARRIVAL_RATE ops/sec per client. It
                    # does not wait between waves and times each op from its intended
                    # start, so the tail includes time spent waiting to be issued.
                    await run_open_loop(
                        cont, REQUEST_EXCLUDED_LOCATIONS, stats, ops,
                        WORKLOAD_ARRIVAL_RATE, WORKLOAD_MAX_INFLIGHT, stop_event,
                    )
                else:
                    # Closed-loop load: each op launches CONCURRENT_REQUESTS calls and
                    # waits for the whole wave before the next op runs. A wave does not
                    # refill as calls finish, so in-flight decays from N toward 0, and
                    # the enabled ops run one phase at a time. Read achieved req/s from
                    # the rows as count / window_seconds, not from concurrency / latency.
                    #
                    # The loop runs until stop_event is set between waves, so the run
                    # ends by falling out of the loop. KeyboardInterrupt is only the
                    # fallback when the signal handler could not be installed; we catch
                    # it and break so the finally blocks close the client cleanly.
                    try:
                        while not stop_event.is_set():
                            try:
                                if WORKLOAD_MIX:
                                    # Blended wave: one process issues a weighted mix
                                    # of ops all in flight together (realistic app
                                    # traffic), instead of one op type per phase.
                                    await mixed_wave_concurrently(
                                        cont, REQUEST_EXCLUDED_LOCATIONS,
                                        CONCURRENT_REQUESTS, WORKLOAD_MIX, stats,
                                    )
                                else:
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
                    except KeyboardInterrupt:
                        client_logger.info("Stop signal received; shutting down cleanly.")
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

    # Blended traffic is an async, concurrent concept; sync mode is fully serial
    # (real concurrency 1), so a "blend" here would just be per-op phases mislabeled.
    # Fail fast rather than silently ignore the mix and publish misleading numbers.
    if WORKLOAD_MIX:
        raise RuntimeError(
            "WORKLOAD_MIX (blended traffic) is not supported in sync mode "
            "(WORKLOAD_USE_SYNC=true); sync mode is fully serial. Run blended "
            "workloads in async mode (WORKLOAD_USE_SYNC=false)."
        )

    # The sync loop has no event loop, so a signal handler sets a threading flag the
    # loop polls between waves. It does not raise, so a signal cannot interrupt the
    # client close; the loop falls through and the context manager closes cleanly.
    stop_flag = threading.Event()

    def _on_signal(signum, frame):
        stop_flag.set()

    try:
        signal.signal(signal.SIGINT, _on_signal)
        signal.signal(signal.SIGTERM, _on_signal)
    except (ValueError, OSError):
        # Not the main thread: fall back to default KeyboardInterrupt handling.
        pass

    stats, reporter = _start_reporter()

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
            _wrap_backend_for_counting(client, is_async=False, client_logger=client_logger)

            # Sync mode is fully serial: each op runs its CONCURRENT_REQUESTS calls
            # one at a time, so real concurrency is 1 and throughput is about
            # 1 / mean latency. Use async mode to drive real concurrency.
            while not stop_flag.is_set():
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
    stats, reporter = _start_reporter()

    try:
        # One shared stop_event for every client: install the handler once and pass
        # the event to each client, so one signal stops them all.
        stop_event = asyncio.Event()
        _install_async_stop(stop_event)

        tasks = []
        client_ids = []
        for i in range(WORKLOAD_NUM_CLIENTS):
            client_id = f"{prefix}-c{i}"
            client_ids.append(client_id)
            tasks.append(run_workload_async(
                client_id, client_logger, stats=stats, reporter=reporter,
                stop_event=stop_event,
            ))
        # One loop-lag monitor for all clients sharing this loop (the per-client
        # path skips it because owns_reporter is False here).
        monitor_task = None
        if WORKLOAD_LOOP_LAG_MONITOR and stats is not None:
            monitor_task = asyncio.create_task(_loop_lag_monitor(stats))
        try:
            # return_exceptions=True so one client failing does not stop the others
            # in this process. We then inspect the results: a client that dies early
            # would otherwise hide behind the aggregate numbers. Surface every
            # per-client failure and fail the process so a partially dead run is not
            # read as a clean one. (Cancellation on graceful stop is expected.)
            results = await asyncio.gather(*tasks, return_exceptions=True)
            failures = [
                (cid, r)
                for cid, r in zip(client_ids, results)
                if isinstance(r, BaseException)
                and not isinstance(r, asyncio.CancelledError)
            ]
            for cid, r in failures:
                client_logger.error("client %s failed: %r", cid, r)
            if failures:
                raise RuntimeError(
                    f"{len(failures)}/{WORKLOAD_NUM_CLIENTS} client(s) failed: "
                    + ", ".join(cid for cid, _ in failures)
                )
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
