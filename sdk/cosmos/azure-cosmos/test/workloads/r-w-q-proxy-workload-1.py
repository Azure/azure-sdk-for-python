import os
import random
import sys

import aiohttp

from azure.cosmos import documents
from workload_configs import COSMOS_URI, COSMOS_KEY, PREFERRED_LOCATIONS, USE_MULTIPLE_WRITABLE_LOCATIONS

sys.path.append(r"./")

from azure.cosmos.aio import CosmosClient as AsyncClient
from azure.core.pipeline.transport import AioHttpTransport
import asyncio

import time
from datetime import datetime

import logging

# Replace with your Cosmos DB details
os.environ["HTTP_PROXY"] = "http://0.0.0.0:5100"

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
        tasks.append(container.read_item(item["id"], item["pk"]))
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
                                    partition_key=random_item["pk"])
    items = [item async for item in results]


async def run_workload(client_id):

    connectionPolicy = documents.ConnectionPolicy()
    connectionPolicy.UseMultipleWriteLocations = USE_MULTIPLE_WRITABLE_LOCATIONS
    async with aiohttp.ClientSession(trust_env=True) as proxied_aio_http_session:

        transport = AioHttpTransport(session=proxied_aio_http_session, session_owner=False)
        async with AsyncClient(COSMOS_URI, COSMOS_KEY, preferred_locations=PREFERRED_LOCATIONS,
                               enable_diagnostics_logging=True, logger=logger, transport=transport,
                               user_agent=str(client_id) + "-" + datetime.now().strftime(
                                   "%Y%m%d-%H%M%S"), connectionPolicy=connectionPolicy) as client:
            db = client.get_database_client("SimonDB")
            cont = db.get_container_client("SimonContainer")
            time.sleep(1)

            while True:
                try:
                    await upsert_item_concurrently(cont, 5)
                    time.sleep(1)
                    await read_item_concurrently(cont, 5)
                    time.sleep(1)
                    await query_items_concurrently(cont, 2)
                except Exception as e:
                    logger.error(e)
                    raise e


if __name__ == "__main__":
    logger = logging.getLogger('azure.cosmos')
    file_name = os.path.basename(__file__)
    first_name = file_name.split(".")[0]
    file_handler = logging.FileHandler("log-" + first_name + "-" + datetime.now().strftime("%Y%m%d-%H%M%S") + '.log')
    logger.setLevel(logging.DEBUG)
    logger.addHandler(file_handler)
    asyncio.run(run_workload(first_name))
