import os
import random
import sys

import aiohttp

from azure.cosmos import documents
from workload_configs import COSMOS_URI, COSMOS_KEY, PREFERRED_LOCATIONS, USE_MULTIPLE_WRITABLE_LOCATIONS, CONCURRENT_REQUESTS

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
    random_int = random.randint(1, 10000000000000000)
    return {"id": "Simon-" + str(random_int), "pk": "pk-" + str(random_int)}


async def upsert_item_concurrently(container, num_upserts):
    tasks = []
    for _ in range(num_upserts):
        tasks.append(container.upsert_item(get_random_item()))
    await asyncio.gather(*tasks)


async def run_workload(client_id, client_logger):
    async with aiohttp.ClientSession(trust_env=True) as proxied_aio_http_session:

        connectionPolicy = documents.ConnectionPolicy()
        connectionPolicy.UseMultipleWriteLocations = USE_MULTIPLE_WRITABLE_LOCATIONS
        transport = AioHttpTransport(session=proxied_aio_http_session, session_owner=False)
        async with AsyncClient(COSMOS_URI, COSMOS_KEY, preferred_locations=PREFERRED_LOCATIONS,
                               enable_diagnostics_logging=True, logger=client_logger, transport=transport,
                               user_agent=str(client_id) + "-" + datetime.now().strftime(
                                   "%Y%m%d-%H%M%S"), connection_policy=connectionPolicy) as client:
            db = client.get_database_client("SimonDB")
            cont = db.get_container_client("SimonContainer")
            time.sleep(1)

            while True:
                try:
                    await upsert_item_concurrently(cont, CONCURRENT_REQUESTS)
                except Exception as e:
                    client_logger.info("Exception in application layer")
                    client_logger.error(e)


if __name__ == "__main__":
    logger = logging.getLogger('azure.cosmos')
    file_name = os.path.basename(__file__)
    first_name = file_name.split(".")[0]
    file_handler = logging.FileHandler("log-" + first_name + "-" + datetime.now().strftime("%Y%m%d-%H%M%S") + '.log')
    logger.setLevel(logging.DEBUG)
    logger.addHandler(file_handler)
    asyncio.run(run_workload(first_name, logger))
