# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
import os
import sys

from azure.cosmos import PartitionKey, ThroughputProperties
from workload_utils import create_logger
from workload_configs import COSMOS_URI, COSMOS_KEY, PREFERRED_LOCATIONS, COSMOS_CONTAINER, COSMOS_DATABASE, \
    NUMBER_OF_LOGICAL_PARTITIONS, PARTITION_KEY, THROUGHPUT

sys.path.append(r"./")

from azure.cosmos.aio import CosmosClient as AsyncClient
import asyncio

from datetime import datetime

async def write_item_concurrently_initial(container, num_upserts):
    tasks = []
    for i in range(num_upserts):
        tasks.append(container.upsert_item({"id": "test-" + str(i), "pk": "pk-" + str(i)}))
    await asyncio.gather(*tasks)


async def run_workload(client_id: str):
    async with AsyncClient(COSMOS_URI, COSMOS_KEY, preferred_locations=PREFERRED_LOCATIONS,
                           enable_diagnostics_logging=True, logger=logger,
                           user_agent=str(client_id) + "-" + datetime.now().strftime("%Y%m%d-%H%M%S")) as client:
        db = await client.create_database_if_not_exists(COSMOS_DATABASE)
        cont = await db.create_container_if_not_exists(COSMOS_CONTAINER, PartitionKey("/" + PARTITION_KEY),
                                                       offer_throughput=ThroughputProperties(THROUGHPUT))
        await asyncio.sleep(1)

        try:
            await write_item_concurrently_initial(cont, NUMBER_OF_LOGICAL_PARTITIONS + 1)  # Number of concurrent upserts
        except Exception as e:
            logger.error(e)
            raise e


if __name__ == "__main__":
    file_name = os.path.basename(__file__)
    prefix, logger = create_logger(file_name)
    asyncio.run(run_workload(prefix))
