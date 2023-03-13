# --------------------------------------------------------------------------
#
# Copyright (c) Microsoft Corporation. All rights reserved.
#
# The MIT License (MIT)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the ""Software""), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED *AS IS*, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
# --------------------------------------------------------------------------
import os
import asyncio
from azure.core.pipeline.transport import AioHttpTransport
from azure.storage.blob.aio import BlobServiceClient

connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")

async def shared_transport_async():
    # [START shared_transport_async]
    shared_transport = AioHttpTransport()
    async with shared_transport:
        blob_service_client1 = BlobServiceClient.from_connection_string(
            connection_string,
            transport=shared_transport,
            session_owner=False)
        blob_service_client2 = BlobServiceClient.from_connection_string(
            connection_string,
            transport=shared_transport,
            session_owner=False)
        containers1 = blob_service_client1.list_containers()
        async for contain in containers1:
            print(contain.name)
        containers2 = blob_service_client2.list_containers()
        async for contain in containers2:
            print(contain.name)
    # [END shared_transport_async]


async def shared_transport_async_with_pooling():
    # [START shared_transport_async_with_pooling]
    import aiohttp
    conn = aiohttp.TCPConnector(limit=100)
    session = aiohttp.ClientSession(connector=conn)
    shared_transport = AioHttpTransport(session=session)
    async with shared_transport:
        blob_service_client1 = BlobServiceClient.from_connection_string(
            connection_string,
            transport=shared_transport,
            session_owner=False)
        blob_service_client2 = BlobServiceClient.from_connection_string(
            connection_string,
            transport=shared_transport,
            session_owner=False)
        containers1 = blob_service_client1.list_containers()
        async for contain in containers1:
            print(contain.name)
        containers2 = blob_service_client2.list_containers()
        async for contain in containers2:
            print(contain.name)
    # [END shared_transport_async_with_pooling]


if __name__ == '__main__':
    asyncio.run(shared_transport_async())
    asyncio.run(shared_transport_async_with_pooling())
