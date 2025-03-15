import os
import random
import sys

from azure.cosmos import documents
from workload_configs import COSMOS_URI, COSMOS_KEY, PREFERRED_LOCATIONS, USE_MULTIPLE_WRITABLE_LOCATIONS, CONCURRENT_REQUESTS
sys.path.append(r"./")

from azure.cosmos.aio import CosmosClient as AsyncClient
import asyncio

import time
from datetime import datetime

import logging
from logging.handlers import RotatingFileHandler

# Replace with your Cosmos DB details

def get_random_item():
    random_int = random.randint(1, 10000)
    return {"id": "Simon-" + str(random_int), "pk": "pk-" + str(random_int)}


async def upsert_item_concurrently(container, num_upserts):
    tasks = []
    for _ in range(num_upserts):
        tasks.append(container.upsert_item(get_random_item()))
    await asyncio.gather(*tasks)


async def read_item_concurrently(container, num_upserts):
    tasks = []
    for _ in range(num_upserts):
        item = get_random_item()
        tasks.append(container.read_item(item["id"], item["id"]))
    await asyncio.gather(*tasks)


async def query_items_concurrently(container, num_queries):
    tasks = []
    for _ in range(num_queries):
        tasks.append(perform_query(container))
    await asyncio.gather(*tasks)


async def perform_query(container):
    random_item = get_random_item()
    results = container.query_items(query="SELECT * FROM c where c.id=@id and c.pk=@pk",
                                    parameters=[{"name": "@id", "value": random_item["id"]},
                                                {"name": "@pk", "value": random_item["pk"]}],
                                    partition_key=random_item["id"])
    items = [item async for item in results]


async def run_workload(client_id, client_logger):
    connectionPolicy = documents.ConnectionPolicy()
    connectionPolicy.UseMultipleWriteLocations = USE_MULTIPLE_WRITABLE_LOCATIONS
    async with AsyncClient(COSMOS_URI, COSMOS_KEY,
                           enable_diagnostics_logging=True, logger=client_logger,
                           user_agent=str(client_id) + "-" + datetime.now().strftime(
                               "%Y%m%d-%H%M%S"), preferred_locations=PREFERRED_LOCATIONS,
                           connection_policy=connectionPolicy) as client:
        db = client.get_database_client("ycsb")
        cont = db.get_container_client("usertable")
        time.sleep(1)

        while True:
            try:
                await upsert_item_concurrently(cont, CONCURRENT_REQUESTS)
                await read_item_concurrently(cont, CONCURRENT_REQUESTS)
                await query_items_concurrently(cont, 2)
            except Exception as e:
                client_logger.info("Exception in application layer")
                client_logger.error(e)


if __name__ == "__main__":
    logger = logging.getLogger('azure.cosmos')
    file_name = os.path.basename(__file__)
    first_name = file_name.split(".")[0]
    # Create a rotating file handler
    handler = RotatingFileHandler(
        "log-" + first_name + "-" + datetime.now().strftime("%Y%m%d-%H%M%S") + '.log',
        maxBytes=1024 * 1024 * 1024 * 1024,  # 100 MB
        backupCount=3
    )
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    asyncio.run(run_workload(first_name, logger))
