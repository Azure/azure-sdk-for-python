# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: blob_samples_hello_world_async.py
DESCRIPTION:
    This sample demos basic blob operations like getting a blob client from container, uploading and downloading
    a blob using the blob_client.
USAGE: python blob_samples_hello_world_async.py
    Set the environment variables with your own values before running the sample:
    1) AZURE_STORAGE_CONNECTION_STRING - the connection string to your storage account
"""

import os
import sys
import asyncio

# set up
DEST_FILE = 'BlockDestination.txt'
SOURCE_FILE = 'SampleSource.txt'


class BlobSamplesAsync(object):

    connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")

    #--Begin Blob Samples-----------------------------------------------------------------

    async def create_container_sample_async(self):
        if self.connection_string is None:
            print("Missing required environment variable: AZURE_STORAGE_CONNECTION_STRING." + '\n' +
                  "Test: create_container_sample_async")
            sys.exit(1)

        # Instantiate a new BlobServiceClient using a connection string
        from azure.storage.blob.aio import BlobServiceClient
        blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)

        async with blob_service_client:
            # Instantiate a new ContainerClient
            container_client = blob_service_client.get_container_client("mycontainerasync")

            try:
                # Create new container in the service
                await container_client.create_container()

                # List containers in the storage account
                my_containers = []
                async for container in blob_service_client.list_containers():
                    my_containers.append(container)

            finally:
                # Delete the container
                await container_client.delete_container()

    async def block_blob_sample_async(self):
        if self.connection_string is None:
            print("Missing required environment variable: AZURE_STORAGE_CONNECTION_STRING." + '\n' +
                  "Test: block_blob_sample_async")
            sys.exit(1)

        # Instantiate a new BlobServiceClient using a connection string
        from azure.storage.blob.aio import BlobServiceClient
        blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)

        async with blob_service_client:
            # Instantiate a new ContainerClient
            container_client = blob_service_client.get_container_client("myblockcontainerasync")

            try:
                # Create new Container in the service
                await container_client.create_container()

                # Instantiate a new BlobClient
                blob_client = container_client.get_blob_client("myblockblob")

                # [START upload_a_blob]
                # Upload content to block blob
                with open(SOURCE_FILE, "rb") as source:
                    await blob_client.upload_blob(source, blob_type="BlockBlob")
                # [END upload_a_blob]

                # [START download_a_blob]
                with open(DEST_FILE, "wb") as my_blob:
                    stream = await blob_client.download_blob()
                    data = await stream.readall()
                    my_blob.write(data)
                # [END download_a_blob]

                # [START delete_blob]
                await blob_client.delete_blob()
                # [END delete_blob]

            finally:
                # Delete the container
                await container_client.delete_container()

    async def stream_block_blob(self):
        if self.connection_string is None:
            print("Missing required environment variable: AZURE_STORAGE_CONNECTION_STRING." + '\n' +
                  "Test: stream_block_blob_async")
            sys.exit(1)

        import uuid
        # Instantiate a new BlobServiceClient using a connection string - set chunk size to 1MB
        from azure.storage.blob import BlobBlock
        from azure.storage.blob.aio import BlobServiceClient
        blob_service_client = BlobServiceClient.from_connection_string(self.connection_string,
                                                                       max_single_get_size=1024*1024,
                                                                       max_chunk_get_size=1024*1024)

        async with blob_service_client:
            # Instantiate a new ContainerClient
            container_client = blob_service_client.get_container_client("containerasync")
            # Generate 4MB of data
            data = b'a'*4*1024*1024

            try:
                # Create new Container in the service
                await container_client.create_container()

                # Instantiate a new source blob client
                source_blob_client = container_client.get_blob_client("source_blob")
                # Upload content to block blob
                await source_blob_client.upload_blob(data, blob_type="BlockBlob")

                destination_blob_client = container_client.get_blob_client("destination_blob")

                # [START download_a_blob_in_chunk]
                # This returns a StorageStreamDownloader.
                stream = await source_blob_client.download_blob()
                block_list = []

                # Read data in chunks to avoid loading all into memory at once
                async for chunk in stream.chunks():
                    # process your data (anything can be done here really. `chunk` is a byte array).
                    block_id = str(uuid.uuid4())
                    await destination_blob_client.stage_block(block_id=block_id, data=chunk)
                    block_list.append(BlobBlock(block_id=block_id))
                # [END download_a_blob_in_chunk]

                # Upload the whole chunk to azure storage and make up one blob
                await destination_blob_client.commit_block_list(block_list)

            finally:
                # Delete container
                await container_client.delete_container()

    async def page_blob_sample_async(self):
        if self.connection_string is None:
            print("Missing required environment variable: AZURE_STORAGE_CONNECTION_STRING." + '\n' +
                  "Test: page_blob_sample_async")
            sys.exit(1)

        # Instantiate a new BlobServiceClient using a connection string
        from azure.storage.blob.aio import BlobServiceClient
        blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)

        async with blob_service_client:
            # Instantiate a new ContainerClient
            container_client = blob_service_client.get_container_client("mypagecontainerasync")

            try:
                # Create new Container in the Service
                await container_client.create_container()

                # Instantiate a new BlobClient
                blob_client = container_client.get_blob_client("mypageblob")

                # Upload content to the Page Blob
                data = b'abcd'*128
                await blob_client.upload_blob(data, blob_type="PageBlob")

                # Download Page Blob
                with open(DEST_FILE, "wb") as my_blob:
                    stream = await blob_client.download_blob()
                    data = await stream.readall()
                    my_blob.write(data)

                # Delete Page Blob
                await blob_client.delete_blob()

            finally:
                # Delete container
                await container_client.delete_container()

    async def append_blob_sample_async(self):
        if self.connection_string is None:
            print("Missing required environment variable: AZURE_STORAGE_CONNECTION_STRING." + '\n' +
                  "Test: append_blob_sample_async")
            sys.exit(1)

        # Instantiate a new BlobServiceClient using a connection string
        from azure.storage.blob.aio import BlobServiceClient
        blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)

        async with blob_service_client:
            # Instantiate a new ContainerClient
            container_client = blob_service_client.get_container_client("myappendcontainerasync")

            try:
                # Create new Container in the Service
                await container_client.create_container()

                # Get the BlobClient
                blob_client = container_client.get_blob_client("myappendblob")

                # Upload content to the append blob
                with open(SOURCE_FILE, "rb") as source:
                    await blob_client.upload_blob(source, blob_type="AppendBlob")

                # Download append blob
                with open(DEST_FILE, "wb") as my_blob:
                    stream = await blob_client.download_blob()
                    data = await stream.readall()
                    my_blob.write(data)

                # Delete append blob
                await blob_client.delete_blob()

            finally:
                # Delete container
                await container_client.delete_container()


async def main():
    sample = BlobSamplesAsync()
    await sample.create_container_sample_async()
    await sample.block_blob_sample_async()
    await sample.append_blob_sample_async()
    await sample.page_blob_sample_async()
    await sample.stream_block_blob()

if __name__ == '__main__':
    asyncio.run(main())
