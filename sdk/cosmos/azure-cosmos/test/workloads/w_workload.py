import os
import random
import sys

from azure.cosmos import documents
from MockExecuteAsync import mock_execute_func
from workload_configs import PREFERRED_LOCATIONS, COSMOS_URI, COSMOS_KEY, USE_MULTIPLE_WRITABLE_LOCATIONS

sys.path.append(r"./")

from azure.cosmos.aio import CosmosClient as AsyncClient
import asyncio

import time
from datetime import datetime

import logging


def get_random_item():
    random_int = random.randint(1, 100000000000000000000)
    return {"id": "Simon-" + str(random_int), "pk": "pk-" + str(random_int)}


async def upsert_item_concurrently(container, num_upserts):
    tasks = []
    for _ in range(num_upserts):
        tasks.append(container.upsert_item(get_random_item()))
    await asyncio.gather(*tasks)


async def run_workload(client_id, client_logger):
    mock_execute_func()
    connectionPolicy = documents.ConnectionPolicy()
    connectionPolicy.UseMultipleWriteLocations = USE_MULTIPLE_WRITABLE_LOCATIONS
    async with AsyncClient(COSMOS_URI, COSMOS_KEY,
                           enable_diagnostics_logging=True, logger=client_logger,
                           user_agent=str(client_id) + "-" + datetime.now().strftime(
                               "%Y%m%d-%H%M%S"), preferred_locations=PREFERRED_LOCATIONS, connection_policy=connectionPolicy) as client:
        db = client.get_database_client("SimonDB")
        cont = db.get_container_client("SimonContainer")
        time.sleep(1)

        while True:
            try:
                await upsert_item_concurrently(cont, 5)
                time.sleep(1)
            except Exception as e:
                logger.info("Exception in application layer")
                client_logger.error(e)


if __name__ == "__main__":
    logger = logging.getLogger('azure.cosmos')
    file_name = os.path.basename(__file__)
    first_name = file_name.split(".")[0]
    file_handler = logging.FileHandler("log-" + first_name + "-" + datetime.now().strftime("%Y%m%d-%H%M%S") + '.log')
    logger.setLevel(logging.DEBUG)
    logger.addHandler(file_handler)
    asyncio.run(run_workload(first_name, logger))
