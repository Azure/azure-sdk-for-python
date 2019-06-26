# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

try:
    import tests.settings_real as settings
except ImportError:
    import tests.settings_fake as settings

from tests.testcase import (
    StorageTestCase,
    TestMode,
    record
)


class TestCommonBlobSamples(StorageTestCase):

    connection_string = settings.CONNECTION_STRING

    @record
    def test_blob_snapshots(self):

        # Instantiate a BlobServiceClient using a connection string
        from azure.storage.blob import BlobServiceClient
        blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)

        # Instantiate a ContainerClient
        container_client = blob_service_client.get_container_client("containerformyblobs")

        # Create new Container
        container_client.create_container()

        # Upload a blob to the container
        with open("./SampleSource.txt", "rb") as data:
            container_client.upload_blob(name="my_blob", data=data)

        # Get a BlobClient for a specific blob
        blob_client = blob_service_client.get_blob_client(container="containerformyblobs", blob="my_blob")

        # Create a read-only snapshot of the blob at this point in time
        snapshot_blob = blob_client.create_snapshot()

        # Get the snapshot ID
        print(snapshot_blob.get('snapshot'))

        # Delete only the snapshot (blob itself is retained)
        blob_client.delete_blob(delete_snapshots="only")

        # Delete container
        blob_service_client.delete_container("containerformyblobs")

    @record
    def test_soft_delete_and_undelete_blob(self):

        # Instantiate a BlobServiceClient using a connection string
        from azure.storage.blob import BlobServiceClient
        blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)

        # Create a retention policy to retain deleted blobs
        from azure.storage.blob import RetentionPolicy
        delete_retention_policy = RetentionPolicy(enabled=True, days=1)

        # Set the retention policy on the service
        blob_service_client.set_service_properties(delete_retention_policy=delete_retention_policy)

        # Instantiate a ContainerClient
        container_client = blob_service_client.get_container_client("containerforblobs")

        # Create new Container
        container_client.create_container()

        # Upload a blob to the container
        with open("./SampleSource.txt", "rb") as data:
            container_client.upload_blob(name="my_blob", data=data)

        # Get the blob client
        blob_client = blob_service_client.get_blob_client("containerforblobs", "my_blob")

        # Soft delete blob in the container (blob can be recovered with undelete)
        blob_client.delete_blob()

        # Undelete the blob before the retention policy expires
        blob_client.undelete_blob()

        # Get blob properties
        properties = blob_client.get_blob_properties()

        assert properties is not None

        # Delete container
        blob_service_client.delete_container("containerforblobs")

    @record
    def test_acquire_lease_on_blob(self):

        # Instantiate a BlobServiceClient using a connection string
        from azure.storage.blob import BlobServiceClient
        blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)

        # Instantiate a ContainerClient
        container_client = blob_service_client.get_container_client("leasemyblobscontainer")

        # Create new Container
        container_client.create_container()

        # Upload a blob to the container
        with open("./SampleSource.txt", "rb") as data:
            container_client.upload_blob(name="my_blob", data=data)

        # Get the blob client
        blob_client = blob_service_client.get_blob_client("leasemyblobscontainer", "my_blob")

        # Acquire a lease on the blob
        lease = blob_client.acquire_lease()

        # Delete blob by passing in the lease
        blob_client.delete_blob(lease=lease)

        # Delete container
        blob_service_client.delete_container("leasemyblobscontainer")