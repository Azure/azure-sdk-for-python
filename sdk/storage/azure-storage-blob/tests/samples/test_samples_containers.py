# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from datetime import datetime, timedelta

try:
    import tests.settings_real as settings
except ImportError:
    import tests.settings_fake as settings


class TestContainerSamples(object):

    connection_string = settings.CONNECTION_STRING

    def test_container_sample(self):

        # Instantiate a BlobServiceClient using a connection string
        from azure.storage.blob import BlobServiceClient
        blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)

        # Instantiate a ContainerClient
        container_client = blob_service_client.get_container_client("mynewcontainer")

        try:
            # Create new Container
            container_client.create_container()

            # Get container properties
            properties = container_client.get_container_properties()

            assert properties is not None

        finally:
            # Delete the container
            container_client.delete_container()

    def test_acquire_lease_on_container(self):

        # Instantiate a BlobServiceClient using a connection string
        from azure.storage.blob import BlobServiceClient
        blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)

        # Instantiate a ContainerClient
        container_client = blob_service_client.get_container_client("myleasecontainer")

        try:
            # Create new Container
            container_client.create_container()

            # Acquire a lease on the container
            lease = container_client.acquire_lease()

        finally:
            # Delete container by passing in the lease
            container_client.delete_container(lease=lease)

    def test_set_metadata_on_container(self):

        # Instantiate a BlobServiceClient using a connection string
        from azure.storage.blob import BlobServiceClient
        blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)

        # Instantiate a ContainerClient
        container_client = blob_service_client.get_container_client("mymetadatacontainer")

        try:
            # Create new Container
            container_client.create_container()

            # Create key, value pairs for metadata
            metadata = {'type': 'test'}

            # Set metadata on the container
            container_client.set_container_metadata(metadata=metadata)

            # Get container properties
            properties = container_client.get_container_properties().metadata

            assert properties == metadata

        finally:
            # Delete container
            container_client.delete_container()

    def test_container_access_policy(self):

        # Instantiate a BlobServiceClient using a connection string
        from azure.storage.blob import BlobServiceClient
        blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)

        # Instantiate a ContainerClient
        container_client = blob_service_client.get_container_client("myaccesscontainer")

        try:
            # Create new Container
            container_client.create_container()

            # Create access policy
            from azure.storage.blob import AccessPolicy, ContainerPermissions
            access_policy = AccessPolicy(permission=ContainerPermissions(read=True),
                                         expiry=datetime.utcnow() + timedelta(hours=1),
                                         start=datetime.utcnow() - timedelta(minutes=1))

            identifiers = {'test': access_policy}

            # Set the access policy on the container
            container_client.set_container_access_policy(signed_identifiers=identifiers)

            # Get the access policy on the container
            policy = container_client.get_container_access_policy()

            assert policy is not None

        finally:
            # Delete container
            container_client.delete_container()

    def test_list_blobs_in_container(self):

        # Instantiate a BlobServiceClient using a connection string
        from azure.storage.blob import BlobServiceClient
        blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)

        # Instantiate a ContainerClient
        container_client = blob_service_client.get_container_client("myblobscontainer")

        # Create new Container
        container_client.create_container()

        # Upload a blob to the container
        with open("./SampleSource.txt", "rb") as data:
            container_client.upload_blob(name="bloby", data=data)

        # List blobs in the container
        blobs_list = container_client.list_blobs()
        for blob in blobs_list:
            print(blob.name + '\n')

        assert blobs_list is not None

    def test_get_blob_client_from_container(self):

        # Instantiate a BlobServiceClient using a connection string
        from azure.storage.blob import BlobServiceClient
        blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)

        # Instantiate a ContainerClient
        container_client = blob_service_client.get_container_client("myblobscontainer")

        # Get the BlobClient from the ContainerClient to interact with a specific blob
        blob_client = container_client.get_blob_client("bloby")

        # Delete blob
        blob_client.delete_blob()

        # Delete container
        container_client.delete_container()