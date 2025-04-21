import os
import random
import sys

from azure.cosmos import documents
from workload_utils import create_logger, read_item_concurrently, query_items_concurrently
from workload_configs import (COSMOS_URI, COSMOS_KEY, PREFERRED_LOCATIONS, USE_MULTIPLE_WRITABLE_LOCATIONS,
                              CONCURRENT_REQUESTS, COSMOS_CONTAINER, COSMOS_DATABASE)

sys.path.append(r"./")

from azure.cosmos.aio import CosmosClient as AsyncClient
import asyncio

import time
from datetime import datetime

async def run_workload(client_id, client_logger):

    connectionPolicy = documents.ConnectionPolicy()
    connectionPolicy.UseMultipleWriteLocations = USE_MULTIPLE_WRITABLE_LOCATIONS
    async with AsyncClient(COSMOS_URI, COSMOS_KEY,
                           enable_diagnostics_logging=True, logger=client_logger,
                           user_agent=str(client_id) + "-" + datetime.now().strftime(
                               "%Y%m%d-%H%M%S"), preferred_locations=PREFERRED_LOCATIONS,
                           connection_policy=connectionPolicy) as client:
        db = client.get_database_client(COSMOS_DATABASE)
        cont = db.get_container_client(COSMOS_CONTAINER)
        await asyncio.sleep(1)

        while True:
            try:
                await read_item_concurrently(cont, CONCURRENT_REQUESTS)
                await query_items_concurrently(cont, 2)
            except Exception as e:
                client_logger.info("Exception in application layer")
                client_logger.error(e)


if __name__ == "__main__":
    file_name = os.path.basename(__file__)
    first_name, logger = create_logger(file_name)
    asyncio.run(run_workload(first_name, logger))
