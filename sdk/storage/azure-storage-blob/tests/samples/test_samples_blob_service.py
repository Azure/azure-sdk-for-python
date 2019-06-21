# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

try:
    import tests.settings_real as settings
except ImportError:
    settings = None


class TestBlobServiceSamples(object):

    connection_string = settings.CONNECTION_STRING

    def test_get_storage_account_information(self):

        # Instantiate a BlobServiceClient using a connection string
        from azure.storage.blob import BlobServiceClient
        blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)

        # Get account information for the Blob Service
        account_info = blob_service_client.get_account_information()

        assert account_info is not None

    def test_blob_service_properties(self):

        # Instantiate a BlobServiceClient using a connection string
        from azure.storage.blob import BlobServiceClient
        blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)

        # Get blob service properties
        properties = blob_service_client.get_service_properties()

        assert properties is not None

    def test_blob_service_stats(self):

        # Instantiate a BlobServiceClient using a connection string
        from azure.storage.blob import BlobServiceClient
        blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)

        # Get blob service stats
        stats = blob_service_client.get_service_stats()

        assert stats is not None

    def test_container_operations(self):

        # Instantiate a BlobServiceClient using a connection string
        from azure.storage.blob import BlobServiceClient
        blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)

        try:
            # Create a container in the service
            blob_service_client.create_container("containerfromblobservice")

            # List containers in the service
            list_response = blob_service_client.list_containers()

            assert list_response is not None

        finally:
            # Delete a container
            blob_service_client.delete_container("containerfromblobservice")

    def test_get_blob_and_container_clients(self):

        # Instantiate a BlobServiceClient using a connection string
        from azure.storage.blob import BlobServiceClient
        blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)

        # Create a ContainerClient to interact with a container
        container_client = blob_service_client.get_container_client("containertest")

        try:
            # Create new Container in the service
            container_client.create_container()

            # Create a BlobClient to interact with a specific blob
            blob_client = blob_service_client.get_blob_client(container="containertest", blob="my_blob")

            assert container_client is not None
            assert blob_client is not None

        finally:
            # Delete the container
            blob_service_client.delete_container("containertest")