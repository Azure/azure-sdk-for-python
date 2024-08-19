# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: blob_samples_common.py
DESCRIPTION:
    This sample demonstrates common blob operations including creating snapshots, soft deleteing, undeleting blobs,
    batch deleting blobs and acquiring lease.
USAGE:
    python blob_samples_common.py
    Set the environment variables with your own values before running the sample.
    1) AZURE_STORAGE_CONNECTION_STRING - the connection string to your storage account
"""

import os
import sys

from azure.core.exceptions import HttpResponseError, ResourceExistsError
from azure.storage.blob import BlobServiceClient

SOURCE_FILE = 'SampleSource.txt'


class CommonBlobSamples(object):

    connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")

    #--Begin Blob Samples-----------------------------------------------------------------

    def blob_snapshots(self):
        if self.connection_string is None:
            print("Missing required environment variable: AZURE_STORAGE_CONNECTION_STRING." + '\n' +
                  "Test: blob_snapshots")
            sys.exit(1)

        # Instantiate a BlobServiceClient using a connection string
        from azure.storage.blob import BlobServiceClient
        blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)

        # Instantiate a ContainerClient
        container_client = blob_service_client.get_container_client("containerformyblobs")

        # Create new Container
        try:
            container_client.create_container()
        except ResourceExistsError:
            pass

        # Upload a blob to the container
        with open(SOURCE_FILE, "rb") as data:
            container_client.upload_blob(name="my_blob", data=data)

        # Get a BlobClient for a specific blob
        blob_client = blob_service_client.get_blob_client(container="containerformyblobs", blob="my_blob")

        # [START create_blob_snapshot]
        # Create a read-only snapshot of the blob at this point in time
        snapshot_blob = blob_client.create_snapshot()

        # Get the snapshot ID
        print(snapshot_blob.get('snapshot'))
        # [END create_blob_snapshot]

        # Delete only the snapshot (blob itself is retained)
        blob_client.delete_blob(delete_snapshots="only")

        # Delete container
        blob_service_client.delete_container("containerformyblobs")

    def soft_delete_and_undelete_blob(self):
        if self.connection_string is None:
            print("Missing required environment variable: AZURE_STORAGE_CONNECTION_STRING." + '\n' +
                  "Test: soft_delete_and_undelete_blob")
            sys.exit(1)

        # Instantiate a BlobServiceClient using a connection string
        from azure.storage.blob import BlobServiceClient
        blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)

        # Create a retention policy to retain deleted blobs
        from azure.storage.blob import RetentionPolicy
        delete_retention_policy = RetentionPolicy(enabled=True, days=1)

        # Set the retention policy on the service
        blob_service_client.set_service_properties(delete_retention_policy=delete_retention_policy)

        # Instantiate a ContainerClient
        container_client = blob_service_client.get_container_client("containerfordeletedblobs")

        # Create new Container
        try:
            container_client.create_container()
        except ResourceExistsError:
            # Container already created
            pass

        # Upload a blob to the container
        with open(SOURCE_FILE, "rb") as data:
            blob_client = container_client.upload_blob(name="my_blob", data=data)

        # Soft delete blob in the container (blob can be recovered with undelete)
        blob_client.delete_blob()

        # [START undelete_blob]
        # Undelete the blob before the retention policy expires
        blob_client.undelete_blob()
        # [END undelete_blob]

        # [START get_blob_properties]
        properties = blob_client.get_blob_properties()
        # [END get_blob_properties]

        # Delete container
        blob_service_client.delete_container("containerfordeletedblobs")

    def delete_multiple_blobs(self):
        if self.connection_string is None:
            print("Missing required environment variable: AZURE_STORAGE_CONNECTION_STRING." + '\n' +
                  "Test: delete_multiple_blobs")
            sys.exit(1)
        # Instantiate a BlobServiceClient using a connection string
        from azure.storage.blob import BlobServiceClient
        blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)

        # Instantiate a ContainerClient
        container_client = blob_service_client.get_container_client("containerforbatchblobdelete")

        # Create new Container
        try:
            container_client.create_container()
        except ResourceExistsError:
            # Container already created
            pass

        # Upload a blob to the container
        upload_data = b"Hello World"
        container_client.upload_blob(name="my_blob1", data=upload_data)
        container_client.upload_blob(name="my_blob2", data=upload_data)
        container_client.upload_blob(name="my_blob3", data=upload_data)

        # [START delete_multiple_blobs]
        # Delete multiple blobs in the container by name
        container_client.delete_blobs("my_blob1", "my_blob2")

        # Delete multiple blobs by properties iterator
        my_blobs = container_client.list_blobs(name_starts_with="my_blob")
        container_client.delete_blobs(*my_blobs)
        # [END delete_multiple_blobs]

        # Delete container
        blob_service_client.delete_container("containerforbatchblobdelete")

    def acquire_lease_on_blob(self):
        if self.connection_string is None:
            print("Missing required environment variable: AZURE_STORAGE_CONNECTION_STRING." + '\n' +
                  "Test: acquire_lease_on_blob")
            sys.exit(1)

        # Instantiate a BlobServiceClient using a connection string
        from azure.storage.blob import BlobServiceClient
        blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)

        # Instantiate a ContainerClient
        container_client = blob_service_client.get_container_client("leasemyblobscontainer")

        # Create new Container
        try:
            container_client.create_container()
        except ResourceExistsError:
            pass

        # Upload a blob to the container
        with open(SOURCE_FILE, "rb") as data:
            container_client.upload_blob(name="my_blob", data=data)

        # Get the blob client
        blob_client = blob_service_client.get_blob_client("leasemyblobscontainer", "my_blob")

        # [START acquire_lease_on_blob]
        # Acquire a lease on the blob
        lease = blob_client.acquire_lease()

        # Delete blob by passing in the lease
        blob_client.delete_blob(lease=lease)
        # [END acquire_lease_on_blob]

        # Delete container
        blob_service_client.delete_container("leasemyblobscontainer")

    def start_copy_blob_from_url_and_abort_copy(self):
        if self.connection_string is None:
            print("Missing required environment variable: AZURE_STORAGE_CONNECTION_STRING." + '\n' +
                  "Test: start_copy_blob_from_url_and_abort_copy")
            sys.exit(1)
        # Instantiate a BlobServiceClient using a connection string
        from azure.storage.blob import BlobServiceClient
        blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)

        # Instantiate a ContainerClient
        container_client = blob_service_client.get_container_client("copyblobcontainer")

        # Create new Container
        try:
            container_client.create_container()
        except ResourceExistsError:
            pass

        try:
            # [START copy_blob_from_url]
            # Get the blob client with the source blob
            source_blob = "https://www.gutenberg.org/files/59466/59466-0.txt"
            copied_blob = blob_service_client.get_blob_client("copyblobcontainer", '59466-0.txt')

            # start copy and check copy status
            copy = copied_blob.start_copy_from_url(source_blob)
            props = copied_blob.get_blob_properties()
            print(props.copy.status)
            # [END copy_blob_from_url]

            copy_id = props.copy.id
            # [START abort_copy_blob_from_url]
            # Passing in copy id to abort copy operation
            if props.copy.status != "success":
                if copy_id is not None:
                    copied_blob.abort_copy(copy_id)
                else:
                    print("copy_id was unexpectedly None, check if the operation completed successfully.")

            # check copy status
            props = copied_blob.get_blob_properties()
            print(props.copy.status)
            # [END abort_copy_blob_from_url]

        finally:
            blob_service_client.delete_container("copyblobcontainer")

if __name__ == '__main__':
    sample = CommonBlobSamples()
    sample.blob_snapshots()
    sample.soft_delete_and_undelete_blob()
    sample.acquire_lease_on_blob()
    sample.start_copy_blob_from_url_and_abort_copy()
    sample.delete_multiple_blobs()
