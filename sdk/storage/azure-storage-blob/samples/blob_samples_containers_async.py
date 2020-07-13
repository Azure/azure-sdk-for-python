# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: blob_samples_container_async.py
DESCRIPTION:
    This sample demonstrates common container operations including list blobs, create a container,
    set metadata etc.
USAGE:
    python blob_samples_container_async.py
    Set the environment variables with your own values before running the sample:
    1) AZURE_STORAGE_CONNECTION_STRING - the connection string to your storage account
"""

import os
import asyncio
from datetime import datetime, timedelta

SOURCE_FILE = 'SampleSource.txt'

class ContainerSamplesAsync(object):
    connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")

    # --Begin Blob Samples-----------------------------------------------------------------

    async def container_sample_async(self):

        # [START create_container_client_from_service]
        # Instantiate a BlobServiceClient using a connection string
        from azure.storage.blob.aio import BlobServiceClient
        blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)

        # Instantiate a ContainerClient
        container_client = blob_service_client.get_container_client("mynewcontainerasync")
        # [END create_container_client_from_service]

        async with blob_service_client:
            # [START create_container_client_sasurl]
            from azure.storage.blob.aio import ContainerClient

            sas_url = sas_url = "https://account.blob.core.windows.net/mycontainer?sv=2015-04-05&st=2015-04-29T22%3A18%3A26Z&se=2015-04-30T02%3A23%3A26Z&sr=b&sp=rw&sip=168.1.5.60-168.1.5.70&spr=https&sig=Z%2FRHIX5Xcg0Mq2rqI3OlWTjEg2tYkboXr1P9ZUXDtkk%3D"
            container = ContainerClient.from_container_url(sas_url)
            # [END create_container_client_sasurl]

            try:
                # [START create_container]
                await container_client.create_container()
                # [END create_container]

                # [START get_container_properties]
                properties = await container_client.get_container_properties()
                # [END get_container_properties]

            finally:
                # [START delete_container]
                await container_client.delete_container()
                # [END delete_container]

    async def acquire_lease_on_container_async(self):

        # Instantiate a BlobServiceClient using a connection string
        from azure.storage.blob.aio import BlobServiceClient
        blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)

        async with blob_service_client:
            # Instantiate a ContainerClient
            container_client = blob_service_client.get_container_client("myleasecontainerasync")

            # Create new Container
            await container_client.create_container()

            # [START acquire_lease_on_container]
            # Acquire a lease on the container
            lease = await container_client.acquire_lease()

            # Delete container by passing in the lease
            await container_client.delete_container(lease=lease)
            # [END acquire_lease_on_container]

    async def set_metadata_on_container_async(self):

        # Instantiate a BlobServiceClient using a connection string
        from azure.storage.blob.aio import BlobServiceClient
        blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)

        async with blob_service_client:
            # Instantiate a ContainerClient
            container_client = blob_service_client.get_container_client("mymetadatacontainerasync")

            try:
                # Create new Container
                await container_client.create_container()

                # [START set_container_metadata]
                # Create key, value pairs for metadata
                metadata = {'type': 'test'}

                # Set metadata on the container
                await container_client.set_container_metadata(metadata=metadata)
                # [END set_container_metadata]

                # Get container properties
                properties = (await container_client.get_container_properties()).metadata

            finally:
                # Delete container
                await container_client.delete_container()

    async def container_access_policy_async(self):
        # Instantiate a BlobServiceClient using a connection string
        from azure.storage.blob.aio import BlobServiceClient
        blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)

        async with blob_service_client:
            # Instantiate a ContainerClient
            container_client = blob_service_client.get_container_client("myaccesscontainerasync")

            try:
                # Create new Container
                await container_client.create_container()

                # [START set_container_access_policy]
                # Create access policy
                from azure.storage.blob import AccessPolicy, ContainerSasPermissions
                access_policy = AccessPolicy(permission=ContainerSasPermissions(read=True),
                                            expiry=datetime.utcnow() + timedelta(hours=1),
                                            start=datetime.utcnow() - timedelta(minutes=1))

                identifiers = {'my-access-policy-id': access_policy}

                # Set the access policy on the container
                await container_client.set_container_access_policy(signed_identifiers=identifiers)
                # [END set_container_access_policy]

                # [START get_container_access_policy]
                policy = await container_client.get_container_access_policy()
                # [END get_container_access_policy]

                # [START generate_sas_token]
                # Use access policy to generate a sas token
                from azure.storage.blob import generate_container_sas
                
                sas_token = generate_container_sas(
                    container_client.account_name,
                    container_client.container_name,
                    account_key=container_client.credential.account_key,
                    policy_id='my-access-policy-id'
                )
                # [END generate_sas_token]

                # Use the sas token to authenticate a new client
                # [START create_container_client_sastoken]
                from azure.storage.blob.aio import ContainerClient
                container = ContainerClient.from_container_url(
                    container_url="https://account.blob.core.windows.net/mycontainerasync",
                    credential=sas_token,
                )
                # [END create_container_client_sastoken]

            finally:
                # Delete container
                await container_client.delete_container()

    async def list_blobs_in_container_async(self):

        # Instantiate a BlobServiceClient using a connection string
        from azure.storage.blob.aio import BlobServiceClient
        blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)

        async with blob_service_client:
            # Instantiate a ContainerClient
            container_client = blob_service_client.get_container_client("myblobscontainerasync")

            # Create new Container
            await container_client.create_container()

            # [START upload_blob_to_container]
            with open(SOURCE_FILE, "rb") as data:
                blob_client = await container_client.upload_blob(name="myblob", data=data)

            properties = await blob_client.get_blob_properties()
            # [END upload_blob_to_container]

            # [START list_blobs_in_container]
            blobs_list = []
            async for blob in container_client.list_blobs():
                blobs_list.append(blob)
            # [END list_blobs_in_container]

            # Delete container
            await container_client.delete_container()

    async def get_blob_client_from_container_async(self):

        # Instantiate a BlobServiceClient using a connection string
        from azure.storage.blob.aio import BlobServiceClient
        blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)

        async with blob_service_client:
            # Instantiate a ContainerClient
            container_client = blob_service_client.get_container_client("blobcontainerasync")

            # Create new Container
            await container_client.create_container()

            # [START get_blob_client]
            # Get the BlobClient from the ContainerClient to interact with a specific blob
            blob_client = container_client.get_blob_client("mynewblob")
            # [END get_blob_client]

            # Delete container
            await container_client.delete_container()

async def main():
    sample = ContainerSamplesAsync()
    await sample.container_sample_async()
    await sample.acquire_lease_on_container_async()
    await sample.set_metadata_on_container_async()
    await sample.container_access_policy_async()
    await sample.list_blobs_in_container_async()
    await sample.get_blob_client_from_container_async()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
