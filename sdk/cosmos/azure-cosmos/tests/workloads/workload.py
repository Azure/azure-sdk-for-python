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
import time

from azure.cosmos.aio import CosmosClient as AsyncClient
from azure.cosmos import CosmosClient as SyncClient, documents
from azure.core.pipeline.transport import AioHttpTransport

from workload_utils import *
from workload_configs import *


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
            enable_diagnostics_logging=True,
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

            while True:
                try:
                    if "write" in ops:
                        await upsert_item_concurrently(
                            cont, REQUEST_EXCLUDED_LOCATIONS, CONCURRENT_REQUESTS, stats
                        )
                    if "read" in ops:
                        await read_item_concurrently(
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
            enable_diagnostics_logging=True,
            logger=client_logger,
            user_agent=get_user_agent(client_id),
        ) as client:
            db = client.get_database_client(COSMOS_DATABASE)
            cont = db.get_container_client(COSMOS_CONTAINER)
            time.sleep(1)

            while True:
                try:
                    if "write" in ops:
                        upsert_item(
                            cont, REQUEST_EXCLUDED_LOCATIONS, CONCURRENT_REQUESTS, stats
                        )
                    if "read" in ops:
                        read_item(
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
        await asyncio.gather(*tasks)
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
