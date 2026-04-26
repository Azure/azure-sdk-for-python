# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
import sys

from azure.cosmos import documents
from datetime import datetime, timezone
import time
from workload_utils import _get_upsert_item
from workload_utils import *
from workload_configs import *
sys.path.append(r"/")

from azure.cosmos.aio import CosmosClient as AsyncClient
import asyncio

async def log_request_counts(counter):
    while True:
        await asyncio.sleep(300)  # 5 minutes
        count = counter["count"]
        duration = counter["upsert_time"] + counter["read_time"]
        print("Current UTC time:", datetime.now(timezone.utc))
        print(f"Executed {count} requests in the last 5 minutes")
        print(f"Errors in the last 5 minutes: {counter['error_count']}")
        print(f"Per-request latency: {duration / count if count > 0 else 0} ms")
        print(f"Upsert latency: {counter['upsert_time'] / (count / 2) if count > 0 else 0} ms")
        print(f"Read latency: {counter['read_time'] / (count / 2) if count > 0 else 0} ms")
        print("-------------------------------")
        counter["count"] = 0  # reset for next interval
        counter["upsert_time"] = 0
        counter["read_time"] = 0
        counter["error_count"] = 0

async def run_workload(client_id, client_logger):
    counter = {"count": 0, "upsert_time": 0, "read_time": 0, "error_count": 0}
    # Start background task
    asyncio.create_task(log_request_counts(counter))
    connectionPolicy = documents.ConnectionPolicy()
    connectionPolicy.UseMultipleWriteLocations = USE_MULTIPLE_WRITABLE_LOCATIONS
    async with AsyncClient(COSMOS_URI, COSMOS_CREDENTIAL, connection_policy=connectionPolicy,
                           preferred_locations=PREFERRED_LOCATIONS, excluded_locations=CLIENT_EXCLUDED_LOCATIONS,
                           enable_diagnostics_logging=True, logger=client_logger,
                           user_agent=get_user_agent(client_id)) as client:
        db = client.get_database_client(COSMOS_DATABASE)
        cont = db.get_container_client(COSMOS_CONTAINER)
        await asyncio.sleep(1)

        while True:
            try:
                upsert_start = time.perf_counter()
                up_item = _get_upsert_item()
                await cont.upsert_item(up_item)
                elapsed = time.perf_counter() - upsert_start
                counter["count"] += 1
                counter["upsert_time"] += elapsed

                read_start = time.perf_counter()
                item = get_existing_random_item()
                await cont.read_item(item["id"], item[PARTITION_KEY])
                elapsed = time.perf_counter() - read_start
                counter["count"] += 1
                counter["read_time"] += elapsed

                # await upsert_item_concurrently(cont, REQUEST_EXCLUDED_LOCATIONS, CONCURRENT_REQUESTS)
                # await read_item_concurrently(cont, REQUEST_EXCLUDED_LOCATIONS, CONCURRENT_REQUESTS)
                # await query_items_concurrently(cont, REQUEST_EXCLUDED_LOCATIONS, CONCURRENT_QUERIES)
            except Exception as e:
                counter["error_count"] += 1
                client_logger.info("Exception in application layer")


if __name__ == "__main__":
    file_name = os.path.basename(__file__)
    prefix, logger = create_logger(file_name)
    create_inner_logger()
    utc_now = datetime.now(timezone.utc)
    print("Current UTC time:", utc_now)
    asyncio.run(run_workload(prefix, logger))
