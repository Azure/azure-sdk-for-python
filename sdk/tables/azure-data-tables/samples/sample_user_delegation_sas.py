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
        * Use the SAS token to access table data

    User delegation SAS tokens are more secure than account key-based SAS tokens
    because they do not require sharing or storing account keys.

USAGE:
    python sample_user_delegation_sas.py

    Set the environment variables with your own values before running the sample:
    1) TABLES_STORAGE_ACCOUNT_NAME - the name of the storage account
    The following environment variables are required for using azure-identity's DefaultAzureCredential.
    For more information, please refer to https://aka.ms/azsdk/python/identity/docs#azure.identity.DefaultAzureCredential
    2) AZURE_TENANT_ID - the tenant ID in Azure Active Directory
    3) AZURE_CLIENT_ID - the client ID of the registered application
    4) AZURE_CLIENT_SECRET - the client secret of the registered application
"""

import os
from datetime import datetime, timedelta, timezone
from azure.data.tables import TableServiceClient, TableClient, generate_table_sas, TableSasPermissions
from azure.identity import DefaultAzureCredential
from azure.core.credentials import AzureSasCredential


def sample_user_delegation_sas():
    account_name = os.environ["TABLES_STORAGE_ACCOUNT_NAME"]
    endpoint = f"https://{account_name}.table.core.windows.net"
    table_name = "userDelegationSasTable"

    # Authenticate with Microsoft Entra ID
    credential = DefaultAzureCredential()

    # [START get_user_delegation_key]
    with TableServiceClient(endpoint=endpoint, credential=credential) as table_service_client:
        # Get a user delegation key valid for 1 hour
        user_delegation_key = table_service_client.get_user_delegation_key(
            key_start_time=datetime.now(timezone.utc),
            key_expiry_time=datetime.now(timezone.utc) + timedelta(hours=1),
        )
        print(f"User delegation key obtained, signed OID: {user_delegation_key.signed_oid}")
    # [END get_user_delegation_key]

    # [START generate_user_delegation_sas]
    # Generate a user delegation SAS token for the table
    sas_token = generate_table_sas(
        table_name=table_name,
        user_delegation_key=user_delegation_key,
        account_name=account_name,
        permission=TableSasPermissions(read=True, query=True, add=True),
        expiry=datetime.now(timezone.utc) + timedelta(hours=1),
    )
    print(f"Generated user delegation SAS token")
    # [END generate_user_delegation_sas]

    # [START use_user_delegation_sas]
    # Use the SAS token to create a client and access table data
    table_client = TableClient(
        endpoint=endpoint,
        table_name=table_name,
        credential=AzureSasCredential(sas_token),
    )

    # Create the table and add an entity using the SAS token
    try:
        table_client.create_table()
        entity = {
            "PartitionKey": "sample",
            "RowKey": "1",
            "Name": "User Delegation SAS Example",
        }
        table_client.create_entity(entity=entity)
        print(f"Created entity with SAS token: {entity['RowKey']}")

        # Query entities using the SAS token
        for entity in table_client.query_entities("PartitionKey eq 'sample'"):
            print(f"Entity: {entity['Name']}")
    finally:
        table_client.delete_table()
        print("Cleaned up table")
    # [END use_user_delegation_sas]


if __name__ == "__main__":
    sample_user_delegation_sas()
