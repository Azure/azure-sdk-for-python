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

USAGE:
    python sample_authentication.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_STORAGE_CONNECTION_STRING - the connection string to your storage account
    2) AZURE_STORAGE_ENDPOINT_SUFFIX - the Table service account URL suffix
    3) AZURE_STORAGE_ACCOUNT_NAME - the name of the storage account
    4) AZURE_STORAGE_ACCESS_KEY - the storage account access key
"""


from datetime import datetime, timedelta
from dotenv import find_dotenv, load_dotenv


class TableAuthSamples(object):
    def __init__(self):
        load_dotenv(find_dotenv())

    def authentication_by_connection_string(self):
        # Instantiate a TableServiceClient using a connection string
        # [START auth_from_connection_string]
        import os
        from azure.data.tables import TableServiceClient

        access_key = os.getenv("TABLES_PRIMARY_STORAGE_ACCOUNT_KEY")
        endpoint_suffix = os.getenv("TABLES_STORAGE_ENDPOINT_SUFFIX")
        account_name = os.getenv("TABLES_STORAGE_ACCOUNT_NAME")
        connection_string = "DefaultEndpointsProtocol=https;AccountName={};AccountKey={};EndpointSuffix={}".format(
            account_name, access_key, endpoint_suffix
        )

        with TableServiceClient.from_connection_string(conn_str=connection_string) as table_service:
            properties = table_service.get_service_properties()
            print("Connection String: {}".format(properties))
        # [END auth_from_connection_string]

    def authentication_by_shared_key(self):
        # Instantiate a TableServiceClient using a shared access key
        # [START auth_from_shared_key]
        import os
        from azure.data.tables import TableServiceClient
        from azure.core.credentials import AzureNamedKeyCredential

        access_key = os.getenv("TABLES_PRIMARY_STORAGE_ACCOUNT_KEY")
        endpoint_suffix = os.getenv("TABLES_STORAGE_ENDPOINT_SUFFIX")
        account_name = os.getenv("TABLES_STORAGE_ACCOUNT_NAME")
        endpoint = "{}.table.{}".format(account_name, endpoint_suffix)

        credential = AzureNamedKeyCredential(account_name, access_key)
        with TableServiceClient(endpoint=endpoint, credential=credential) as table_service:
            properties = table_service.get_service_properties()
            print("Shared Key: {}".format(properties))
        # [END auth_from_shared_key]

    def authentication_by_shared_access_signature(self):
        # Instantiate a TableServiceClient using a connection string

        # [START auth_from_sas]
        import os

        from azure.data.tables import TableServiceClient
        from azure.core.credentials import AzureNamedKeyCredential

        # Create a SAS token to use for authentication of a client
        from azure.data.tables import generate_account_sas, ResourceTypes, AccountSasPermissions

        access_key = os.getenv("TABLES_PRIMARY_STORAGE_ACCOUNT_KEY")
        account_name = os.getenv("TABLES_STORAGE_ACCOUNT_NAME")
        endpoint_suffix = os.getenv("TABLES_STORAGE_ENDPOINT_SUFFIX")
        endpoint = "{}.table.{}".format(account_name, endpoint_suffix)

        print("Account name: {}".format(account_name))
        credential = AzureNamedKeyCredential(account_name, access_key)
        sas_token = generate_account_sas(
            credential,
            resource_types=ResourceTypes(service=True),
            permission=AccountSasPermissions(read=True),
            expiry=datetime.utcnow() + timedelta(hours=1),
        )

        with TableServiceClient(endpoint=endpoint, credential=sas_token) as token_auth_table_service:
            properties = token_auth_table_service.get_service_properties()
            print("Shared Access Signature: {}".format(properties))
        # [END auth_from_sas]


if __name__ == "__main__":
    sample = TableAuthSamples()
    sample.authentication_by_connection_string()
    sample.authentication_by_shared_key()
    sample.authentication_by_shared_access_signature()
