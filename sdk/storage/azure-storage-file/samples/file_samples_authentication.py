# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import os
import sys
from datetime import datetime, timedelta

try:
    CONNECTION_STRING = os.environ['AZURE_STORAGE_CONNECTION_STRING']
    SHARED_ACCESS_KEY = os.environ['AZURE_STORAGE_SHARED_ACCESS_KEY']
except KeyError:
    print("AZURE_STORAGE_CONNECTION_STRING must be set.")
    print("AZURE_STORAGE_SHARED_ACCESS_KEY must be set.")
    sys.exit(1)


class FileAuthSamples(object):

    def auth_connection_string(self):
        # Instantiate the FileServiceClient from a connection string
        # [START create_file_service_client_from_conn_string]
        from azure.storage.file import FileServiceClient
        file_service = FileServiceClient.from_connection_string(CONNECTION_STRING)
        # [END create_file_service_client_from_conn_string]

    def auth_shared_key(self):
        # Instantiate a FileServiceClient using a shared access key
        # [START create_file_service_client]
        from azure.storage.file import FileServiceClient
        file_service_client = FileServiceClient(
            account_url="https://storageaccountname.file.core.windows.net",
            credential=SHARED_ACCESS_KEY
        )
        # [END create_file_service_client]

    def auth_shared_access_signature(self):
        # Instantiate a FileServiceClient using a connection string
        # [START generate_sas_token]
        from azure.storage.file import FileServiceClient
        file_service_client = FileServiceClient.from_connection_string(CONNECTION_STRING)

        # Create a SAS token to use to authenticate a new client
        from azure.storage.file import generate_account_sas

        sas_token = generate_account_sas(
            file_service_client.account_name,
            file_service_client.credential.account_key,
            resource_types="object",
            permission="read",
            expiry=datetime.utcnow() + timedelta(hours=1)
        )
        # [END generate_sas_token]

