import os
import sys

sys.path.append(r"./")

from azure.cosmos.aio import CosmosClient as AsyncClient
import asyncio

import time
from datetime import datetime

import logging

# Replace with your Cosmos DB details
preferred_locations = []
COSMOS_URI = ""
COSMOS_KEY = ""


async def run_workload(client_id: str):
    async with AsyncClient(COSMOS_URI, COSMOS_KEY, preferred_locations=preferred_locations,
                           enable_diagnostics_logging=True, logger=logger,
                           user_agent=client_id + "-" + datetime.now().strftime(
                               "%Y%m%d-%H%M%S")) as client:
        time.sleep(1)

        while True:
            try:
                database_account = await client._get_database_account()
                logger.info("%s - Database account - writable locations: %s",
                            datetime.now().strftime("%Y%m%d-%H%M%S"),
                            database_account.WritableLocations)
                logger.info("%s - Database account - readable locations: %s",
                            datetime.now().strftime("%Y%m%d-%H%M%S"),
                            database_account.ReadableLocations)
                time.sleep(1)
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
