# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_user_delegation_sas.py

DESCRIPTION:
    This sample demonstrates how to:
        * Obtain a user delegation key using Microsoft Entra ID credentials
        * Generate a user delegation SAS token for a table
        * Use the SAS token to authenticate a TableClient

    User delegation SAS tokens are more secure than account-key-based SAS tokens
    because they do not require storing or distributing the account key. They
    are only supported for Azure Storage accounts (not Cosmos DB).

USAGE:
    python sample_user_delegation_sas.py

    Set the environment variables with your own values before running the sample:
    1) TABLES_STORAGE_ACCOUNT_NAME - the name of the storage account

    The following environment variables are required for using azure-identity's
    DefaultAzureCredential. For more information, please refer to
    https://aka.ms/azsdk/python/identity/docs#azure.identity.DefaultAzureCredential
    2) AZURE_TENANT_ID - the tenant ID in Microsoft Entra ID
    3) AZURE_CLIENT_ID - the client ID of the application
    4) AZURE_CLIENT_SECRET - the client secret of the application
"""

import os
from datetime import datetime, timedelta, timezone
from azure.data.tables import TableServiceClient, generate_table_sas, TableSasPermissions
from azure.core.credentials import AzureSasCredential
from azure.identity import DefaultAzureCredential


class UserDelegationSasSample(object):
    account_name = os.environ.get("TABLES_STORAGE_ACCOUNT_NAME", "")
    endpoint = f"https://{account_name}.table.core.windows.net"
    table_name = "SampleUserDelegationSAS"

    def user_delegation_sas(self):
        print("--- User Delegation SAS ---")
        credential = DefaultAzureCredential()

        with TableServiceClient(endpoint=self.endpoint, credential=credential) as service_client:
            # Create a table to use for this sample
            service_client.create_table_if_not_exists(self.table_name)

            # Step 1: Get a user delegation key valid for 1 hour
            start_time = datetime.now(tz=timezone.utc)
            expiry_time = start_time + timedelta(hours=1)

            user_delegation_key = service_client.get_user_delegation_key(
                key_start_time=start_time,
                key_expiry_time=expiry_time,
            )
            print(f"Obtained user delegation key, signed OID: {user_delegation_key.signed_oid}")

            # Step 2: Generate a user delegation SAS token for the table
            sas_token = generate_table_sas(
                credential=user_delegation_key,
                table_name=self.table_name,
                account_name=self.account_name,
                permission=TableSasPermissions(read=True, add=True, update=True, delete=True),
                expiry=expiry_time,
                start=start_time,
            )
            print(f"Generated user delegation SAS token: {sas_token[:50]}...")

            # Step 3: Use the SAS token to create a TableClient
            sas_client = TableServiceClient(
                endpoint=self.endpoint,
                credential=AzureSasCredential(sas_token),
            )
            table_client = sas_client.get_table_client(self.table_name)

            # Step 4: Perform operations with the SAS-authenticated client
            entity = {
                "PartitionKey": "sample",
                "RowKey": "udk-test",
                "Description": "Created with user delegation SAS",
            }
            table_client.upsert_entity(entity)
            print("Successfully created entity using user delegation SAS")

            # Read back the entity
            retrieved = table_client.get_entity("sample", "udk-test")
            print(f"Retrieved entity: {retrieved['Description']}")

            # Clean up
            table_client.delete_entity("sample", "udk-test")
            service_client.delete_table(self.table_name)
            print("Cleaned up sample resources")


if __name__ == "__main__":
    sample = UserDelegationSasSample()
    sample.user_delegation_sas()
