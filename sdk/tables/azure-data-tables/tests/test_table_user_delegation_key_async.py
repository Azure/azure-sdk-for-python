# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import pytest
from datetime import datetime, timedelta, timezone

from devtools_testutils import AzureRecordedTestCase, set_custom_default_matcher
from devtools_testutils.aio import recorded_by_proxy_async

from azure.core.credentials import AzureSasCredential
from azure.core.exceptions import HttpResponseError
from azure.data.tables import (
    TableSasPermissions,
    generate_table_sas,
    UserDelegationKey,
)
from azure.data.tables.aio import TableServiceClient, TableClient

from _shared.testcase import TableTestCase
from async_preparers import tables_decorator_async


class TestTableUserDelegationKeyAsync(AzureRecordedTestCase, TableTestCase):

    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_get_user_delegation_key_async(self, tables_storage_account_name):
        """Test getting a user delegation key with valid start/expiry times (async)."""
        set_custom_default_matcher(compare_bodies=False)
        account_url = self.account_url(tables_storage_account_name, "table")
        tsc = TableServiceClient(
            credential=self.get_token_credential(), endpoint=account_url
        )

        start_time = datetime.now(timezone.utc)
        expiry_time = datetime.now(timezone.utc) + timedelta(hours=1)

        user_delegation_key = await tsc.get_user_delegation_key(
            key_start_time=start_time,
            key_expiry_time=expiry_time,
        )

        # Verify all attributes exist on the returned key
        assert user_delegation_key is not None
        assert user_delegation_key.signed_oid is not None
        assert user_delegation_key.signed_tid is not None
        assert user_delegation_key.signed_start is not None
        assert user_delegation_key.signed_expiry is not None
        assert user_delegation_key.signed_service is not None
        assert user_delegation_key.signed_version is not None
        assert user_delegation_key.value is not None

        await tsc.close()

    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_user_delegation_sas_table_operations_async(self, tables_storage_account_name):
        """Test end-to-end: get delegation key, generate SAS, use SAS to access table (async)."""
        set_custom_default_matcher(
            compare_bodies=False,
            ignored_query_parameters="skt,ske",
        )
        account_url = self.account_url(tables_storage_account_name, "table")
        tsc = TableServiceClient(
            credential=self.get_token_credential(), endpoint=account_url
        )

        start_time = datetime.now(timezone.utc) - timedelta(minutes=5)
        expiry_time = datetime.now(timezone.utc) + timedelta(hours=1)

        # Step 1: Get user delegation key
        user_delegation_key = await tsc.get_user_delegation_key(
            key_start_time=start_time,
            key_expiry_time=expiry_time,
        )

        # Step 2: Create a table for testing
        table_name = self._get_table_reference()
        await tsc.create_table(table_name)

        try:
            # Step 3: Generate user delegation SAS
            sas_token = generate_table_sas(
                table_name=table_name,
                user_delegation_key=user_delegation_key,
                account_name=tables_storage_account_name,
                permission=TableSasPermissions(read=True, add=True, update=True, delete=True),
                expiry=expiry_time,
                start=start_time,
            )

            assert sas_token is not None
            assert "sig=" in sas_token
            assert "skoid=" in sas_token

            # Step 4: Use SAS to access the table
            sas_client = TableClient(
                endpoint=account_url,
                table_name=table_name,
                credential=AzureSasCredential(sas_token),
            )

            # Insert an entity using SAS
            entity = {
                "PartitionKey": "pk",
                "RowKey": "rk1",
                "Value": "test_value_async",
            }
            await sas_client.create_entity(entity)

            # Query the entity using SAS
            retrieved = await sas_client.get_entity("pk", "rk1")
            assert retrieved["Value"] == "test_value_async"

            await sas_client.close()

        finally:
            await tsc.delete_table(table_name)
            await tsc.close()
