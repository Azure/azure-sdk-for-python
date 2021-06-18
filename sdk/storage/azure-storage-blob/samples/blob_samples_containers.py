# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: blob_samples_container.py
DESCRIPTION:
    This sample demonstrates common container operations including list blobs, create a container,
    set metadata etc.
USAGE:
    python blob_samples_container.py
    Set the environment variables with your own values before running the sample:
    1) AZURE_STORAGE_CONNECTION_STRING - the connection string to your storage account
"""

import os
from datetime import datetime, timedelta

from azure.core.exceptions import ResourceExistsError

SOURCE_FILE = 'SampleSource.txt'


class ContainerSamples(object):

    connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")

    #--Begin Blob Samples-----------------------------------------------------------------

    def container_sample(self):

        # [START create_container_client_from_service]
        # Instantiate a BlobServiceClient using a connection string
        from azure.storage.blob import BlobServiceClient
        blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)

        # Instantiate a ContainerClient
        container_client = blob_service_client.get_container_client("mynewcontainer")
        # [END create_container_client_from_service]

        # [START create_container_client_sasurl]
        from azure.storage.blob import ContainerClient

        sas_url = "https://account.blob.core.windows.net/mycontainer?sv=2015-04-05&st=2015-04-29T22%3A18%3A26Z&se=2015-04-30T02%3A23%3A26Z&sr=b&sp=rw&sip=168.1.5.60-168.1.5.70&spr=https&sig=Z%2FRHIX5Xcg0Mq2rqI3OlWTjEg2tYkboXr1P9ZUXDtkk%3D"
        container = ContainerClient.from_container_url(sas_url)
        # [END create_container_client_sasurl]

        try:
            # [START create_container]
            container_client.create_container()
            # [END create_container]

            # [START get_container_properties]
            properties = container_client.get_container_properties()
            # [END get_container_properties]

        finally:
            # [START delete_container]
            container_client.delete_container()
            # [END delete_container]

    def acquire_lease_on_container(self):

        # Instantiate a BlobServiceClient using a connection string
        from azure.storage.blob import BlobServiceClient
        blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)

        # Instantiate a ContainerClient
        container_client = blob_service_client.get_container_client("myleasecontainer")

        # Create new Container
        try:
            container_client.create_container()
        except ResourceExistsError:
            pass

        # [START acquire_lease_on_container]
        # Acquire a lease on the container
        lease = container_client.acquire_lease()

        # Delete container by passing in the lease
        container_client.delete_container(lease=lease)
        # [END acquire_lease_on_container]

    def set_metadata_on_container(self):

        # Instantiate a BlobServiceClient using a connection string
        from azure.storage.blob import BlobServiceClient
        blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)

        # Instantiate a ContainerClient
        container_client = blob_service_client.get_container_client("mymetadatacontainersync")

        try:
            # Create new Container
            container_client.create_container()

            # [START set_container_metadata]
            # Create key, value pairs for metadata
            metadata = {'type': 'test'}

            # Set metadata on the container
            container_client.set_container_metadata(metadata=metadata)
            # [END set_container_metadata]

            # Get container properties
            properties = container_client.get_container_properties().metadata

        finally:
            # Delete container
            container_client.delete_container()

    def container_access_policy(self):
        # Instantiate a BlobServiceClient using a connection string
        from azure.storage.blob import BlobServiceClient
        blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)

        # Instantiate a ContainerClient
        container_client = blob_service_client.get_container_client("myaccesscontainer")

        try:
            # Create new Container
            container_client.create_container()

            # [START set_container_access_policy]
            # Create access policy
            from azure.storage.blob import AccessPolicy, ContainerSasPermissions
            access_policy = AccessPolicy(permission=ContainerSasPermissions(read=True),
                                         expiry=datetime.utcnow() + timedelta(hours=1),
                                         start=datetime.utcnow() - timedelta(minutes=1))

            identifiers = {'test': access_policy}

            # Set the access policy on the container
            container_client.set_container_access_policy(signed_identifiers=identifiers)
            # [END set_container_access_policy]

            # [START get_container_access_policy]
            policy = container_client.get_container_access_policy()
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
            from azure.storage.blob import ContainerClient
            container = ContainerClient.from_container_url(
                container_url="https://account.blob.core.windows.net/mycontainer",
                credential=sas_token
            )
            # [END create_container_client_sastoken]

        finally:
            # Delete container
            container_client.delete_container()

    def list_blobs_in_container(self):

        # Instantiate a BlobServiceClient using a connection string
        from azure.storage.blob import BlobServiceClient
        blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)

        # Instantiate a ContainerClient
        container_client = blob_service_client.get_container_client("myblobscontainer")

        # Create new Container
        container_client.create_container()

        # [START upload_blob_to_container]
        with open(SOURCE_FILE, "rb") as data:
            blob_client = container_client.upload_blob(name="myblob", data=data)
        
        properties = blob_client.get_blob_properties()
        # [END upload_blob_to_container]

        # [START list_blobs_in_container]
        blobs_list = container_client.list_blobs()
        for blob in blobs_list:
            print(blob.name + '\n')
        # [END list_blobs_in_container]

        # Delete container
        container_client.delete_container()

    def get_blob_client_from_container(self):

        # Instantiate a BlobServiceClient using a connection string
        from azure.storage.blob import BlobServiceClient
        blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)

        # Instantiate a ContainerClient
        container_client = blob_service_client.get_container_client("blobcontainer")

        # Create new Container
        try:
            container_client.create_container()
        except ResourceExistsError:
            pass

        # [START get_blob_client]
        # Get the BlobClient from the ContainerClient to interact with a specific blob
        blob_client = container_client.get_blob_client("mynewblob")
        # [END get_blob_client]

        # Delete container
        container_client.delete_container()

    def get_container_client_from_blob_client(self):
        # Instantiate a BlobServiceClient using a connection string
        from azure.storage.blob import BlobServiceClient
        blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)

        # [START get_container_client_from_blob_client]
        container_client1 = blob_service_client.get_container_client("blobcontainer")
        container_client1.create_container()
        print(container_client1.get_container_properties())
        blob_client1 = container_client1.get_blob_client("blob")
        blob_client1.upload_blob("hello")

        container_client2 = blob_client1._get_container_client()
        print(container_client2.get_container_properties())
        container_client2.delete_container()
        # [END get_container_client_from_blob_client]


if __name__ == '__main__':
    sample = ContainerSamples()
    sample.container_sample()
    sample.acquire_lease_on_container()
    sample.set_metadata_on_container()
    sample.container_access_policy()
    sample.list_blobs_in_container()
    sample.get_blob_client_from_container()
    sample.get_container_client_from_blob_client()
