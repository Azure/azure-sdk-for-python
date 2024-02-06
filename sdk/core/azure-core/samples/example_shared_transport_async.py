# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: example_shared_transport_async.py

DESCRIPTION:
    This sample demonstrates how to share transport connections between multiple async clients.

USAGE:
    python example_shared_transport_async.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_STORAGE_CONNECTION_STRING - the endpoint of your Azure Metrics Advisor service
"""

import os
import asyncio
from azure.core.pipeline.transport import AioHttpTransport
from azure.storage.blob.aio import BlobServiceClient

connection_string = os.environ["AZURE_STORAGE_CONNECTION_STRING"]


async def shared_transport_async():
    # [START shared_transport_async]
    import aiohttp

    session = aiohttp.ClientSession()
    shared_transport = AioHttpTransport(
        session=session, session_owner=False
    )  # here we set session_owner to False to indicate that we don't want to close the session when the client is closed
    async with shared_transport:
        blob_service_client1 = BlobServiceClient.from_connection_string(
            connection_string,
            transport=shared_transport,
        )
        blob_service_client2 = BlobServiceClient.from_connection_string(connection_string, transport=shared_transport)
        containers1 = blob_service_client1.list_containers()
        async for contain in containers1:
            print(contain.name)
        containers2 = blob_service_client2.list_containers()
        async for contain in containers2:
            print(contain.name)
    await session.close()  # we need to close the session manually
    # [END shared_transport_async]


async def shared_transport_async_with_pooling():
    # [START shared_transport_async_with_pooling]
    import aiohttp

    conn = aiohttp.TCPConnector(limit=100)
    session = aiohttp.ClientSession(connector=conn)
    shared_transport = AioHttpTransport(session=session, session_owner=False)
    async with shared_transport:
        blob_service_client1 = BlobServiceClient.from_connection_string(connection_string, transport=shared_transport)
        blob_service_client2 = BlobServiceClient.from_connection_string(connection_string, transport=shared_transport)
        containers1 = blob_service_client1.list_containers()
        async for contain in containers1:
            print(contain.name)
        containers2 = blob_service_client2.list_containers()
        async for contain in containers2:
            print(contain.name)
    await session.close()  # we need to close the session manually
    # [END shared_transport_async_with_pooling]


if __name__ == "__main__":
    asyncio.run(shared_transport_async())
    asyncio.run(shared_transport_async_with_pooling())
