# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_user_delegation_key.py

DESCRIPTION:
    This sample demonstrates how to obtain a user delegation key and use it
    to generate a user delegation SAS token for Azure Tables. User delegation
    SAS tokens are signed using Microsoft Entra ID (OAuth) credentials instead
    of account keys, providing a more secure way to delegate access.

USAGE:
    python sample_user_delegation_key.py

    Set the environment variables with your own values before running the sample:
    1) TABLES_STORAGE_ENDPOINT_SUFFIX - the Table service account URL suffix
    2) TABLES_STORAGE_ACCOUNT_NAME - the name of the storage account
    The following environment variables are required for using azure-identity's DefaultAzureCredential.
    For more information, please refer to https://aka.ms/azsdk/python/identity/docs#azure.identity.DefaultAzureCredential
    3) AZURE_TENANT_ID - the tenant ID in Azure Active Directory
    4) AZURE_CLIENT_ID - the application (client) ID registered in the AAD tenant
    5) AZURE_CLIENT_SECRET - the client secret for the registered application
"""

import os
from datetime import datetime, timedelta, timezone
from dotenv import find_dotenv, load_dotenv


class UserDelegationKeySamples(object):
    def __init__(self):
        load_dotenv(find_dotenv())
        self.access_key = os.environ.get("TABLES_PRIMARY_STORAGE_ACCOUNT_KEY", "")
        self.endpoint_suffix = os.environ.get("TABLES_STORAGE_ENDPOINT_SUFFIX", "core.windows.net")
        self.account_name = os.environ.get("TABLES_STORAGE_ACCOUNT_NAME", "")
        self.endpoint = f"https://{self.account_name}.table.{self.endpoint_suffix}"
        self.table_name = "sampleUserDelegationKey"

    def get_user_delegation_key(self):
        # [START get_user_delegation_key]
        from azure.data.tables import TableServiceClient
        from azure.identity import DefaultAzureCredential

        credential = DefaultAzureCredential()
        table_service_client = TableServiceClient(
            endpoint=self.endpoint, credential=credential
        )

        # Request a user delegation key valid for 1 hour
        user_delegation_key = table_service_client.get_user_delegation_key(
            key_start_time=datetime.now(timezone.utc),
            key_expiry_time=datetime.now(timezone.utc) + timedelta(hours=1),
        )

        print(f"User delegation key signed OID: {user_delegation_key.signed_oid}")
        print(f"Key valid from: {user_delegation_key.signed_start}")
        print(f"Key valid until: {user_delegation_key.signed_expiry}")
        # [END get_user_delegation_key]

    def generate_user_delegation_sas(self):
        # [START generate_user_delegation_sas]
        from azure.data.tables import (
            TableServiceClient,
            TableSasPermissions,
            generate_table_sas,
        )
        from azure.identity import DefaultAzureCredential

        credential = DefaultAzureCredential()
        table_service_client = TableServiceClient(
            endpoint=self.endpoint, credential=credential
        )

        # Step 1: Get a user delegation key
        user_delegation_key = table_service_client.get_user_delegation_key(
            key_start_time=datetime.now(timezone.utc),
            key_expiry_time=datetime.now(timezone.utc) + timedelta(hours=1),
        )

        # Step 2: Generate a user delegation SAS token for a table
        sas_token = generate_table_sas(
            credential=user_delegation_key,
            table_name=self.table_name,
            account_name=self.account_name,
            user_delegation_key=user_delegation_key,
            permission=TableSasPermissions(read=True, query=True),
            expiry=datetime.now(timezone.utc) + timedelta(hours=1),
        )
        print(f"Generated user delegation SAS token: {sas_token[:50]}...")
        # [END generate_user_delegation_sas]


if __name__ == "__main__":
    sample = UserDelegationKeySamples()
    sample.get_user_delegation_key()
    sample.generate_user_delegation_sas()
