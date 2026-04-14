# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import pytest
from datetime import datetime, timedelta, timezone
from urllib.parse import parse_qs

from devtools_testutils import AzureRecordedTestCase
from devtools_testutils.aio import recorded_by_proxy_async

from azure.core.credentials import AzureNamedKeyCredential, AzureSasCredential
from azure.core.exceptions import HttpResponseError
from azure.data.tables import (
    TableSasPermissions,
    generate_table_sas,
    UserDelegationKey,
)
from azure.data.tables.aio import TableServiceClient, TableClient

from _shared.asynctestcase import AsyncTableTestCase
from async_preparers import tables_decorator_async

# ------------------------------------------------------------------------------


class TestTableUserDelegationKeyAsync(AzureRecordedTestCase, AsyncTableTestCase):

    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_get_user_delegation_key(self, tables_storage_account_name):
        """Test getting a user delegation key with valid start/expiry times."""
        account_url = self.account_url(tables_storage_account_name, "table")
        tsc = TableServiceClient(credential=self.get_token_credential(), endpoint=account_url)

        start_time = datetime.now(timezone.utc)
        expiry_time = start_time + timedelta(hours=1)

        user_delegation_key = await tsc.get_user_delegation_key(
            key_start_time=start_time,
            key_expiry_time=expiry_time,
        )

        assert user_delegation_key is not None
        assert user_delegation_key.signed_oid is not None
        assert user_delegation_key.signed_tid is not None
        assert user_delegation_key.signed_start is not None
        assert user_delegation_key.signed_expiry is not None
        assert user_delegation_key.signed_service is not None
        assert user_delegation_key.signed_version is not None
        assert user_delegation_key.value is not None

    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_get_user_delegation_key_past_expiry(self, tables_storage_account_name):
        """Test that getting a user delegation key with an expiry in the past raises an error."""
        account_url = self.account_url(tables_storage_account_name, "table")
        tsc = TableServiceClient(credential=self.get_token_credential(), endpoint=account_url)

        start_time = datetime.now(timezone.utc) - timedelta(hours=2)
        expiry_time = datetime.now(timezone.utc) - timedelta(hours=1)

        with pytest.raises(HttpResponseError):
            await tsc.get_user_delegation_key(
                key_start_time=start_time,
                key_expiry_time=expiry_time,
            )

    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_get_user_delegation_key_shared_key_auth(
        self, tables_storage_account_name, tables_primary_storage_account_key
    ):
        """Test that getting a user delegation key with SharedKey credential fails."""
        account_url = self.account_url(tables_storage_account_name, "table")
        tsc = TableServiceClient(account_url, credential=tables_primary_storage_account_key)

        start_time = datetime.now(timezone.utc)
        expiry_time = start_time + timedelta(hours=1)

        with pytest.raises(HttpResponseError):
            await tsc.get_user_delegation_key(
                key_start_time=start_time,
                key_expiry_time=expiry_time,
            )

    @pytest.mark.skip(reason="User delegation SAS for Tables requires service-side support for sv=2025-07-05 string-to-sign format")
    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_user_delegation_sas_access_table(self, tables_storage_account_name):
        """End-to-end test: get key → generate SAS → use SAS to access table."""
        account_url = self.account_url(tables_storage_account_name, "table")
        tsc = TableServiceClient(credential=self.get_token_credential(), endpoint=account_url)

        # Create a test table
        table_name = self._get_table_reference()
        try:
            await tsc.create_table(table_name)

            # Get user delegation key
            start_time = datetime.now(timezone.utc)
            expiry_time = start_time + timedelta(hours=1)
            user_delegation_key = await tsc.get_user_delegation_key(
                key_start_time=start_time,
                key_expiry_time=expiry_time,
            )

            # Generate SAS token using user delegation key
            sas_token = generate_table_sas(
                credential=AzureNamedKeyCredential(
                    name=tables_storage_account_name, key="unused"
                ),
                table_name=table_name,
                user_delegation_key=user_delegation_key,
                account_name=tables_storage_account_name,
                permission=TableSasPermissions(read=True, add=True, update=True, delete=True),
                expiry=expiry_time,
                start=start_time,
            )

            # Use SAS token to access the table
            sas_client = TableClient(
                endpoint=account_url,
                table_name=table_name,
                credential=AzureSasCredential(sas_token),
            )

            # Insert an entity to verify the SAS token works
            entity = {
                "PartitionKey": "pk",
                "RowKey": "rk1",
                "Value": "test_value",
            }
            await sas_client.upsert_entity(entity)

            # Query to verify
            queried = await sas_client.get_entity("pk", "rk1")
            assert queried["Value"] == "test_value"

        finally:
            await tsc.delete_table(table_name)
