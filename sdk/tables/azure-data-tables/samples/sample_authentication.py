# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_authentication.py

DESCRIPTION:
    These samples demonstrate authenticating a client via:
        * connection string
        * shared access key
        * generating a sas token with which the returned signature can be used with
    the credential parameter of any TableServiceClient or TableClient
        * Azure Active Directory(AAD)

USAGE:
    python sample_authentication.py

    Set the environment variables with your own values before running the sample:
    1) TABLES_STORAGE_ENDPOINT_SUFFIX - the Table service account URL suffix
    2) TABLES_STORAGE_ACCOUNT_NAME - the name of the storage account
    3) TABLES_PRIMARY_STORAGE_ACCOUNT_KEY - the storage account access key
    The following environment variables are required for using azure-identity's DefaultAzureCredential.
    For more information, please refer to https://aka.ms/azsdk/python/identity/docs#azure.identity.DefaultAzureCredential
    4) AZURE_TENANT_ID - the tenant ID in Azure Active Directory
    5) AZURE_CLIENT_ID - the application (client) ID registered in the AAD tenant
    6) AZURE_CLIENT_SECRET - the client secret for the registered application
"""

import os
from dotenv import find_dotenv, load_dotenv


class TableAuthSamples(object):
    def __init__(self):
        load_dotenv(find_dotenv())
        self.access_key = os.environ["TABLES_PRIMARY_STORAGE_ACCOUNT_KEY"]
        self.endpoint_suffix = os.environ["TABLES_STORAGE_ENDPOINT_SUFFIX"]
        self.account_name = os.environ["TABLES_STORAGE_ACCOUNT_NAME"]
        self.endpoint = f"{self.account_name}.table.{self.endpoint_suffix}"
        self.connection_string = f"DefaultEndpointsProtocol=https;AccountName={self.account_name};AccountKey={self.access_key};EndpointSuffix={self.endpoint_suffix}"

    def authentication_by_connection_string(self):
        print("Instantiate a TableServiceClient using a connection string")
        # [START auth_from_connection_string]
        from azure.data.tables import TableServiceClient

        with TableServiceClient.from_connection_string(conn_str=self.connection_string) as table_service_client:
            properties = table_service_client.get_service_properties()
            print(f"{properties}")
        # [END auth_from_connection_string]

    def authentication_by_shared_key(self):
        print("Instantiate a TableServiceClient using a shared access key")
        # [START auth_from_shared_key]
        from azure.data.tables import TableServiceClient
        from azure.core.credentials import AzureNamedKeyCredential

        credential = AzureNamedKeyCredential(self.account_name, self.access_key)
        with TableServiceClient(endpoint=self.endpoint, credential=credential) as table_service_client:
            properties = table_service_client.get_service_properties()
            print(f"{properties}")
        # [END auth_from_shared_key]

    def authentication_by_shared_access_signature(self):
        print("Instantiate a TableServiceClient using a shared access signature")
        # [START auth_from_sas]
        from datetime import datetime, timedelta
        from azure.data.tables import TableServiceClient, generate_account_sas, ResourceTypes, AccountSasPermissions
        from azure.core.credentials import AzureNamedKeyCredential, AzureSasCredential

        credential = AzureNamedKeyCredential(self.account_name, self.access_key)
        # Create a SAS token to use for authentication of a client
        sas_token = generate_account_sas(
            credential,
            resource_types=ResourceTypes(service=True),
            permission=AccountSasPermissions(read=True),
            expiry=datetime.utcnow() + timedelta(hours=1),
        )

        with TableServiceClient(
            endpoint=self.endpoint, credential=AzureSasCredential(sas_token)
        ) as table_service_client:
            properties = table_service_client.get_service_properties()
            print(f"{properties}")
        # [END auth_from_sas]

    def authentication_by_AAD(self):
        print("Instantiate a TableServiceClient using a TokenCredential")
        # [START auth_from_aad]
        from azure.data.tables import TableServiceClient
        from azure.identity import DefaultAzureCredential

        with TableServiceClient(endpoint=self.endpoint, credential=DefaultAzureCredential()) as table_service_client:
            properties = table_service_client.get_service_properties()
            print(f"{properties}")
        # [END auth_from_aad]


if __name__ == "__main__":
    sample = TableAuthSamples()
    sample.authentication_by_connection_string()
    sample.authentication_by_shared_key()
    sample.authentication_by_shared_access_signature()
    sample.authentication_by_AAD()
