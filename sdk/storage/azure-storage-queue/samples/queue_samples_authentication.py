# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: queue_samples_authentication.py

DESCRIPTION:
    These samples demonstrate authenticating a client via a connection string,
    shared access key, token credential from Azure Active Directory, or by
    generating a sas token with which the returned signature can be used with
    the credential parameter of any QueueServiceClient or QueueClient.

USAGE:
    python queue_samples_authentication.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_STORAGE_CONNECTION_STRING - the connection string to your storage account
    2) AZURE_STORAGE_ACCOUNT_URL - the queue service account URL
    3) AZURE_STORAGE_ACCOUNT_NAME - the name of the storage account
    4) AZURE_STORAGE_ACCESS_KEY - the storage account access key
"""


from datetime import datetime, timedelta
import os
import sys


class QueueAuthSamples(object):

    connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")

    account_url = os.getenv("AZURE_STORAGE_ACCOUNT_URL")
    account_name = os.getenv("AZURE_STORAGE_ACCOUNT_NAME")
    access_key = os.getenv("AZURE_STORAGE_ACCESS_KEY")

    def authentication_by_connection_string(self):
        if self.connection_string is None:
            print("Missing required environment variable(s). Please see specific test for more details." + '\n' +
                  "Test: authentication_by_connection_string")
            sys.exit(1)

        # Instantiate a QueueServiceClient using a connection string
        # [START auth_from_connection_string]
        from azure.storage.queue import QueueServiceClient
        queue_service = QueueServiceClient.from_connection_string(conn_str=self.connection_string)
        # [END auth_from_connection_string]

        # Get information for the Queue Service
        properties = queue_service.get_service_properties()

    def authentication_by_shared_key(self):
        if self.account_url is None or self.access_key is None:
            print("Missing required environment variable(s). Please see specific test for more details." + '\n' +
                  "Test: authentication_by_shared_key")
            sys.exit(1)

        # Instantiate a QueueServiceClient using a shared access key
        # [START create_queue_service_client]
        from azure.storage.queue import QueueServiceClient
        queue_service = QueueServiceClient(account_url=self.account_url, credential=self.access_key)
        # [END create_queue_service_client]

        # Get information for the Queue Service
        properties = queue_service.get_service_properties()

    def authentication_by_oauth(self):
        if self.account_url is None:
            print("Missing required environment variable(s). Please see specific test for more details." + '\n' +
                  "Test: authentication_by_oauth")
            sys.exit(1)

        # [START create_queue_service_client_oauth]
        # Get a token credential for authentication
        from azure.identity import DefaultAzureCredential
        token_credential = DefaultAzureCredential()

        # Instantiate a QueueServiceClient using a token credential
        from azure.storage.queue import QueueServiceClient
        queue_service = QueueServiceClient(account_url=self.account_url, credential=token_credential)
        # [END create_queue_service_client_oauth]

        # Get information for the Queue Service
        properties = queue_service.get_service_properties()

    def authentication_by_shared_access_signature(self):
        if (self.connection_string is None or
            self.account_name is None or
            self.access_key is None or
            self.account_url is None
        ):
            print("Missing required environment variable(s). Please see specific test for more details." + '\n' +
                  "Test: authentication_by_shared_access_signature")
            sys.exit(1)

        # Instantiate a QueueServiceClient using a connection string
        from azure.storage.queue import QueueServiceClient
        queue_service = QueueServiceClient.from_connection_string(conn_str=self.connection_string)

        # Create a SAS token to use for authentication of a client
        from azure.storage.queue import generate_account_sas, ResourceTypes, AccountSasPermissions

        sas_token = generate_account_sas(
            self.account_name,
            self.access_key,
            resource_types=ResourceTypes(service=True),
            permission=AccountSasPermissions(read=True),
            expiry=datetime.utcnow() + timedelta(hours=1)
        )

        token_auth_queue_service = QueueServiceClient(account_url=self.account_url, credential=sas_token)

        # Get information for the Queue Service
        properties = token_auth_queue_service.get_service_properties()


if __name__ == '__main__':
    sample = QueueAuthSamples()
    sample.authentication_by_connection_string()
    sample.authentication_by_shared_key()
    sample.authentication_by_oauth()
    sample.authentication_by_shared_access_signature()
