# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: blob_samples_common_async.py
DESCRIPTION:
    This sample demonstrates common blob operations including creating snapshots, soft deleteing, undeleting blobs,
    batch deleting blobs and acquiring lease.
USAGE:
    python blob_samples_common_async.py
    Set the environment variables with your own values before running the sample.
    1) AZURE_STORAGE_CONNECTION_STRING - the connection string to your storage account
"""

import os
import sys
import asyncio
from azure.core.exceptions import ResourceExistsError


SOURCE_FILE = './SampleSource.txt'


class CommonBlobSamplesAsync(object):

    connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")

    #--Begin Blob Samples-----------------------------------------------------------------

    async def blob_snapshots_async(self):
        if self.connection_string is None:
            print("Missing required environment variable: AZURE_STORAGE_CONNECTION_STRING." + '\n' +
                  "Test: blob_snapshots_async")
            sys.exit(1)
        # Instantiate a BlobServiceClient using a connection string
        from azure.storage.blob.aio import BlobServiceClient
        blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)

        # Instantiate a ContainerClient
        async with blob_service_client:
            container_client = blob_service_client.get_container_client("containerformyblobsasync")

            # Create new Container
            try:
                await container_client.create_container()
            except ResourceExistsError:
                pass

            # Upload a blob to the container
            with open(SOURCE_FILE, "rb") as data:
                await container_client.upload_blob(name="my_blob", data=data)

            # Get a BlobClient for a specific blob
            blob_client = blob_service_client.get_blob_client(container="containerformyblobsasync", blob="my_blob")

            # [START create_blob_snapshot]
            # Create a read-only snapshot of the blob at this point in time
            snapshot_blob = await blob_client.create_snapshot()

            # Get the snapshot ID
            print(snapshot_blob.get('snapshot'))

            # Delete only the snapshot (blob itself is retained)
            await blob_client.delete_blob(delete_snapshots="only")
            # [END create_blob_snapshot]

            # Delete container
            await blob_service_client.delete_container("containerformyblobsasync")

    async def soft_delete_and_undelete_blob_async(self):
        if self.connection_string is None:
            print("Missing required environment variable: AZURE_STORAGE_CONNECTION_STRING." + '\n' +
                  "Test: soft_delete_and_undelete_blob_async")
            sys.exit(1)
        # Instantiate a BlobServiceClient using a connection string
        from azure.storage.blob.aio import BlobServiceClient
        blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)

        async with blob_service_client:
            # Create a retention policy to retain deleted blobs
            from azure.storage.blob import RetentionPolicy
            delete_retention_policy = RetentionPolicy(enabled=True, days=1)

            # Set the retention policy on the service
            await blob_service_client.set_service_properties(delete_retention_policy=delete_retention_policy)

            # Instantiate a ContainerClient
            container_client = blob_service_client.get_container_client("containerfordeletedblobsasync")

            # Create new Container
            try:
                await container_client.create_container()
            except ResourceExistsError:
                # Container already created
                pass

            # Upload a blob to the container
            with open(SOURCE_FILE, "rb") as data:
                blob_client = await container_client.upload_blob(name="my_blob", data=data)

            # Soft delete blob in the container (blob can be recovered with undelete)
            await blob_client.delete_blob()

            # [START undelete_blob]
            # Undelete the blob before the retention policy expires
            await blob_client.undelete_blob()
            # [END undelete_blob]

            # [START get_blob_properties]
            properties = await blob_client.get_blob_properties()
            # [END get_blob_properties]

            # Delete container
            await blob_service_client.delete_container("containerfordeletedblobsasync")

    async def delete_multiple_blobs_async(self):
        if self.connection_string is None:
            print("Missing required environment variable: AZURE_STORAGE_CONNECTION_STRING." + '\n' +
                  "Test: delete_multiple_blobs_async")
            sys.exit(1)
        # Instantiate a BlobServiceClient using a connection string
        from azure.storage.blob.aio import BlobServiceClient
        blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)

        async with blob_service_client:
            # Instantiate a ContainerClient
            container_client = blob_service_client.get_container_client("containerforbatchblobdeletesasync")

            # Create new Container
            try:
                await container_client.create_container()
            except ResourceExistsError:
                # Container already created
                pass

            # Upload a blob to the container
            upload_data = b"Hello World"
            await container_client.upload_blob(name="my_blob1", data=upload_data)
            await container_client.upload_blob(name="my_blob2", data=upload_data)
            await container_client.upload_blob(name="my_blob3", data=upload_data)

            # [START delete_multiple_blobs]
            # Delete multiple blobs in the container by name
            await container_client.delete_blobs("my_blob1", "my_blob2")

            # Delete multiple blobs by properties iterator
            my_blobs = container_client.list_blobs(name_starts_with="my_blob")
            await container_client.delete_blobs(*[b async for b in my_blobs])  # async for in list comprehension after 3.6 only
            # [END delete_multiple_blobs]

            # Delete container
            await blob_service_client.delete_container("containerforbatchblobdeletesasync")

    async def acquire_lease_on_blob_async(self):
        if self.connection_string is None:
            print("Missing required environment variable: AZURE_STORAGE_CONNECTION_STRING." + '\n' +
                  "Test: acquire_lease_on_blob_async")
            sys.exit(1)
        # Instantiate a BlobServiceClient using a connection string
        from azure.storage.blob.aio import BlobServiceClient
        blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)

        async with blob_service_client:
            # Instantiate a ContainerClient
            container_client = blob_service_client.get_container_client("leasemyblobscontainerasync")

            # Create new Container
            try:
                await container_client.create_container()
            except ResourceExistsError:
                pass

            # Upload a blob to the container
            with open(SOURCE_FILE, "rb") as data:
                await container_client.upload_blob(name="my_blob", data=data)

            # [START acquire_lease_on_blob]
            # Get the blob client
            blob_client = blob_service_client.get_blob_client("leasemyblobscontainerasync", "my_blob")

            # Acquire a lease on the blob
            lease = await blob_client.acquire_lease()

            # Delete blob by passing in the lease
            await blob_client.delete_blob(lease=lease)
            # [END acquire_lease_on_blob]

            # Delete container
            await blob_service_client.delete_container("leasemyblobscontainerasync")

    async def start_copy_blob_from_url_and_abort_copy_async(self):
        if self.connection_string is None:
            print("Missing required environment variable: AZURE_STORAGE_CONNECTION_STRING." + '\n' +
                  "Test: start_copy_blob_from_url_and_abort_copy_async")
            sys.exit(1)
        # Instantiate a BlobServiceClient using a connection string
        from azure.storage.blob.aio import BlobServiceClient
        blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)

        async with blob_service_client:
            # Instantiate a ContainerClient
            container_client = blob_service_client.get_container_client("copyblobcontainerasync")

            # Create new Container
            try:
                await container_client.create_container()
            except ResourceExistsError:
                pass

            try:
                # [START copy_blob_from_url]
                # Get the blob client with the source blob
                source_blob = "https://www.gutenberg.org/files/59466/59466-0.txt"
                copied_blob = blob_service_client.get_blob_client("copyblobcontainerasync", '59466-0.txt')

                # start copy and check copy status
                copy = await copied_blob.start_copy_from_url(source_blob)
                props = await copied_blob.get_blob_properties()
                print(props.copy.status)
                # [END copy_blob_from_url]

                copy_id = props.copy.id
                # [START abort_copy_blob_from_url]
                # Passing in copy id to abort copy operation
                if props.copy.status != "success":
                    if copy_id is not None:
                        await copied_blob.abort_copy(copy_id)
                    else:
                        print("copy_id was unexpectedly None, check if the operation completed successfully.")

                # check copy status
                props = await copied_blob.get_blob_properties()
                print(props.copy.status)
                # [END abort_copy_blob_from_url]

            finally:
                await blob_service_client.delete_container("copyblobcontainerasync")

async def main():
    sample = CommonBlobSamplesAsync()
    await sample.blob_snapshots_async()
    await sample.soft_delete_and_undelete_blob_async()
    await sample.delete_multiple_blobs_async()
    await sample.acquire_lease_on_blob_async()
    await sample.start_copy_blob_from_url_and_abort_copy_async()

if __name__ == '__main__':
    asyncio.run(main())
