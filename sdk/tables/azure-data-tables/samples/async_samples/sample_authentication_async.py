# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_authentication_async.py

DESCRIPTION:
    These samples demonstrate authenticating a client via:
        * connection string
        * shared access key
        * generating a sas token with which the returned signature can be used with
    the credential parameter of any TableServiceClient or TableClient

USAGE:
    python sample_authentication_async.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_STORAGE_CONNECTION_STRING - the connection string to your storage account
    2) AZURE_STORAGE_ACCOUNT_URL - the Table service account URL
    3) AZURE_STORAGE_ACCOUNT_NAME - the name of the storage account
    4) AZURE_STORAGE_ACCESS_KEY - the storage account access key
"""


from datetime import datetime, timedelta
import os
import asyncio

class TableAuthSamples(object):
    connection_string = os.getenv("AZURE_TABLES_CONNECTION_STRING")
    access_key = os.getenv("AZURE_TABLES_KEY")
    account_url = os.getenv("AZURE_TABLES_ACCOUNT_URL")
    account_name = os.getenv("AZURE_TABLES_ACCOUNT_NAME")

    async def authentication_by_connection_string(self):
        # Instantiate a TableServiceClient using a connection string
        # [START auth_from_connection_string]
        from azure.data.tables.aio import TableServiceClient
        async with TableServiceClient.from_connection_string(conn_str=self.connection_string) as table_service:
            properties = await table_service.get_service_properties()
            print("Connection String: {}".format(properties))
        # [END auth_from_connection_string]

    async def authentication_by_shared_key(self):
        # Instantiate a TableServiceClient using a shared access key
        # [START auth_from_shared_key]
        from azure.data.tables.aio import TableServiceClient
        async with TableServiceClient.from_connection_string(conn_str=self.connection_string) as table_service:
            properties = await table_service.get_service_properties()
            print("Shared Key: {}".format(properties))
        # [END auth_from_shared_key]

    async def authentication_by_shared_access_signature(self):
        # Instantiate a TableServiceClient using a connection string
        # [START auth_by_sas]
        from azure.data.tables.aio import TableServiceClient

        # Create a SAS token to use for authentication of a client
        from azure.data.tables import generate_account_sas, ResourceTypes, AccountSasPermissions
        sas_token = generate_account_sas(
            self.account_name,
            self.access_key,
            resource_types=ResourceTypes(service=True),
            permission=AccountSasPermissions(read=True),
            expiry=datetime.utcnow() + timedelta(hours=1)
        )

        async with TableServiceClient(account_url=self.account_url, credential=sas_token) as token_auth_table_service:
            properties = await token_auth_table_service.get_service_properties()
            print("Shared Access Signature: {}".format(properties))
        # [END auth_by_sas]


async def main():
    sample = TableAuthSamples()
    await sample.authentication_by_connection_string()
    await sample.authentication_by_shared_key()
    await sample.authentication_by_shared_access_signature()


if __name__ == '__main__':
    asyncio.run(main())
