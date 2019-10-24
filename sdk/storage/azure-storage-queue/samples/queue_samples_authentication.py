# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from datetime import datetime, timedelta
import os

class QueueAuthSamples(object):

    connection_string = os.getenv("CONNECTION_STRING")

    account_url = os.getenv("ACCOUNT_URL")
    access_key = os.getenv("ACCESS_KEY")

    active_directory_application_id = os.getenv("ACTIVE_DIRECTORY_APPLICATION_ID")
    active_directory_application_secret = os.getenv("ACTIVE_DIRECTORY_APPLICATION_SECRET")
    active_directory_tenant_id = os.getenv("ACTIVE_DIRECTORY_TENANT_ID")

    def auth_connection_string(self):
        # Instantiate a QueueServiceClient using a connection string
        # [START auth_from_connection_string]
        from azure.storage.queue import QueueServiceClient
        queue_service = QueueServiceClient.from_connection_string(conn_str=self.connection_string)
        # [END auth_from_connection_string]

        # Get information for the Queue Service
        properties = queue_service.get_service_properties()

    def auth_shared_key(self):
        # Instantiate a QueueServiceClient using a shared access key
        # [START create_queue_service_client]
        from azure.storage.queue import QueueServiceClient
        queue_service = QueueServiceClient(account_url=self.account_url, credential=self.access_key)
        # [END create_queue_service_client]

        # Get information for the Queue Service
        properties = queue_service.get_service_properties()

    def auth_active_directory(self):
        # [START create_queue_service_client_token]
        # Get a token credential for authentication
        from azure.identity import ClientSecretCredential
        token_credential = ClientSecretCredential(
            self.active_directory_tenant_id,
            self.active_directory_application_id,
            self.active_directory_application_secret
        )

        # Instantiate a QueueServiceClient using a token credential
        from azure.storage.queue import QueueServiceClient
        queue_service = QueueServiceClient(account_url=self.account_url, credential=token_credential)
        # [END create_queue_service_client_token]

        # Get information for the Queue Service
        properties = queue_service.get_service_properties()

    def auth_shared_access_signature(self):
        # Instantiate a QueueServiceClient using a connection string
        from azure.storage.queue import QueueServiceClient
        queue_service = QueueServiceClient.from_connection_string(conn_str=self.connection_string)

        # Create a SAS token to use for authentication of a client
        from azure.storage.queue import generate_account_sas

        sas_token = generate_account_sas(
            queue_service.account_name,
            queue_service.credential.account_key,
            resource_types="object",
            permission="read",
            expiry=datetime.utcnow() + timedelta(hours=1)
        )

        token_auth_queue_service = QueueServiceClient(account_url=self.account_url, credential=sas_token)

        # Get information for the Queue Service
        properties = token_auth_queue_service.get_service_properties()
