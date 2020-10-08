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
    2) AZURE_STORAGE_ACCOUNT_URL - the Table service account URL
    3) AZURE_STORAGE_ACCOUNT_NAME - the name of the storage account
    4) AZURE_STORAGE_ACCESS_KEY - the storage account access key
"""


from datetime import datetime, timedelta
import os


class TableAuthSamples(object):
    connection_string = os.getenv("AZURE_TABLES_CONNECTION_STRING")
    access_key = os.getenv("AZURE_TABLES_KEY")
    account_url = os.getenv("AZURE_TABLES_ACCOUNT_URL")
    account_name = os.getenv("AZURE_TABLES_ACCOUNT_NAME")

    def authentication_by_connection_string(self):
        # Instantiate a TableServiceClient using a connection string
        # [START auth_from_connection_string]
        from azure.data.tables import TableServiceClient
        table_service = TableServiceClient.from_connection_string(conn_str=self.connection_string)
        properties = table_service.get_service_properties()
        print("Connection String: {}".format(properties))
        # [END auth_from_connection_string]

    def authentication_by_shared_key(self):
        # Instantiate a TableServiceClient using a shared access key
        # [START auth_from_shared_key]
        from azure.data.tables import TableServiceClient
        table_service = TableServiceClient(account_url=self.account_url, credential=self.access_key)
        properties = table_service.get_service_properties()
        print("Shared Key: {}".format(properties))
        # [END auth_from_shared_key]

    def authentication_by_shared_access_signature(self):
        # Instantiate a TableServiceClient using a connection string
        from azure.data.tables import TableServiceClient

        # [START auth_from_sas]
        # Create a SAS token to use for authentication of a client
        from azure.data.tables import generate_account_sas, ResourceTypes, AccountSasPermissions
        print(self.account_name)
        sas_token = generate_account_sas(
            self.account_name,
            self.access_key,
            resource_types=ResourceTypes(service=True),
            permission=AccountSasPermissions(read=True),
            expiry=datetime.utcnow() + timedelta(hours=1)
        )

        token_auth_table_service = TableServiceClient(account_url=self.account_url, credential=sas_token)

        properties = token_auth_table_service.get_service_properties()
        print("Shared Access Signature: {}".format(properties))
        # [END auth_from_sas]

if __name__ == '__main__':
    sample = TableAuthSamples()
    sample.authentication_by_connection_string()
    sample.authentication_by_shared_key()
    sample.authentication_by_shared_access_signature()
