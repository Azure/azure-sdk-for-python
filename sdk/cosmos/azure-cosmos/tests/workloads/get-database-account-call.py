# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
import asyncio
import os
import time
from datetime import datetime

from azure.cosmos.aio import CosmosClient as AsyncClient

from workload_configs import COSMOS_CREDENTIAL, COSMOS_URI, PREFERRED_LOCATIONS
from workload_utils import create_logger


async def run_workload(client_id: str):
    async with AsyncClient(COSMOS_URI, COSMOS_CREDENTIAL, preferred_locations=PREFERRED_LOCATIONS,
                           enable_diagnostics_logging=True, logger=logger,
                           user_agent=client_id + "-" + datetime.now().strftime(
                               "%Y%m%d-%H%M%S")) as client:
        await asyncio.sleep(1)

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
    file_name = os.path.basename(__file__)
    prefix, logger = create_logger(file_name)
    asyncio.run(run_workload(prefix))
