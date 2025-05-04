# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
import os
import sys

import aiohttp

from azure.cosmos import documents
from workload_utils import *
from workload_configs import *
sys.path.append(r"/")

from azure.cosmos.aio import CosmosClient as AsyncClient
from azure.core.pipeline.transport import AioHttpTransport
import asyncio

async def run_workload(client_id, client_logger):
    async with aiohttp.ClientSession(trust_env=True) as proxied_aio_http_session:
        connectionPolicy = documents.ConnectionPolicy()
        connectionPolicy.UseMultipleWriteLocations = USE_MULTIPLE_WRITABLE_LOCATIONS
        connectionPolicy.ProxyConfiguration = documents.ProxyConfiguration()
        transport = AioHttpTransport(session=proxied_aio_http_session, session_owner=False)
        async with AsyncClient(COSMOS_PROXY_URI, COSMOS_KEY, connection_policy=connectionPolicy,
                               preferred_locations=PREFERRED_LOCATIONS, excluded_locations=CLIENT_EXCLUDED_LOCATIONS,
                               enable_diagnostics_logging=True, logger=client_logger, transport=transport,
                               user_agent=get_user_agent(client_id)) as client:
            db = client.get_database_client(COSMOS_DATABASE)
            cont = db.get_container_client(COSMOS_CONTAINER)
            await asyncio.sleep(1)

            while True:
                try:
                    await upsert_item_concurrently(cont, REQUEST_EXCLUDED_LOCATIONS, CONCURRENT_REQUESTS)
                except Exception as e:
                    client_logger.info("Exception in application layer")
                    client_logger.error(e)


if __name__ == "__main__":
    file_name = os.path.basename(__file__)
    prefix, logger = create_logger(file_name)
    asyncio.run(run_workload(prefix, logger))
