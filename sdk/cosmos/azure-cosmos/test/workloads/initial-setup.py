import os
import sys

from azure.cosmos import PartitionKey
from test.workloads.workload_configs import COSMOS_URI, COSMOS_KEY, PREFERRED_LOCATIONS

sys.path.append(r"./")

from azure.cosmos.aio import CosmosClient as AsyncClient
import asyncio

import time
from datetime import datetime

import logging

async def write_item_concurrently_initial(container, num_upserts):
    tasks = []
    for i in range(num_upserts):
        tasks.append(container.upsert_item({"id": "Simon-" + str(i), "pk": "pk-" + str(i)}))
    await asyncio.gather(*tasks)


async def run_workload(client_id: str):
    async with AsyncClient(COSMOS_URI, COSMOS_KEY, preferred_locations=PREFERRED_LOCATIONS,
                           enable_diagnostics_logging=True, logger=logger,
                           user_agent=str(client_id) + "-" + datetime.now().strftime("%Y%m%d-%H%M%S")) as client:
        db = await client.create_database_if_not_exists("SimonDB")
        cont = await db.create_container_if_not_exists("SimonContainer", PartitionKey("/pk"))
        time.sleep(1)

        try:
            await write_item_concurrently_initial(cont, 10001)  # Number of concurrent upserts
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
