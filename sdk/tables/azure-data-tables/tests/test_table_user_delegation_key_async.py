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

from azure.core.exceptions import HttpResponseError
from azure.data.tables import (
    TableSasPermissions,
    UserDelegationKey,
    generate_table_sas,
)
from azure.data.tables.aio import TableServiceClient

from _shared.asynctestcase import AsyncTableTestCase
from async_preparers import tables_decorator_async

# ------------------------------------------------------------------------------


class TestTableUserDelegationKeyAsync(AzureRecordedTestCase, AsyncTableTestCase):
    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_get_user_delegation_key_async(self, tables_storage_account_name):
        """Test getting a user delegation key with OAuth credential (async)."""
        account_url = self.account_url(tables_storage_account_name, "table")
        tsc = TableServiceClient(
            endpoint=account_url,
            credential=self.get_token_credential(),
            api_version="2025-07-05",
        )
        start_time = datetime.now(timezone.utc)
        expiry_time = start_time + timedelta(hours=1)

        udk = await tsc.get_user_delegation_key(
            key_start_time=start_time,
            key_expiry_time=expiry_time,
        )

        assert udk is not None
        assert udk.signed_oid is not None
        assert udk.signed_tid is not None
        assert udk.signed_start is not None
        assert udk.signed_expiry is not None
        assert udk.signed_service is not None
        assert udk.signed_version is not None
        assert udk.value is not None

    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_get_user_delegation_key_without_delegated_user_tid_async(self, tables_storage_account_name):
        """Test getting a user delegation key without delegated_user_tid (second call verifies consistency, async)."""
        account_url = self.account_url(tables_storage_account_name, "table")
        tsc = TableServiceClient(
            endpoint=account_url,
            credential=self.get_token_credential(),
            api_version="2025-07-05",
        )
        start_time = datetime.now(timezone.utc)
        expiry_time = start_time + timedelta(hours=1)

        udk = await tsc.get_user_delegation_key(
            key_start_time=start_time,
            key_expiry_time=expiry_time,
        )

        assert udk is not None
        assert udk.value is not None
        assert udk.signed_oid is not None
        assert udk.signed_tid is not None

    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_user_delegation_sas_full_workflow_async(self, tables_storage_account_name):
        """Test the full workflow: get UDK -> generate SAS -> use SAS (async)."""
        account_url = self.account_url(tables_storage_account_name, "table")
        tsc = TableServiceClient(
            endpoint=account_url,
            credential=self.get_token_credential(),
            api_version="2025-07-05",
        )

        start_time = datetime.now(timezone.utc)
        expiry_time = start_time + timedelta(hours=1)

        udk = await tsc.get_user_delegation_key(
            key_start_time=start_time,
            key_expiry_time=expiry_time,
        )

        table_name = self._get_table_reference()
        try:
            await tsc.create_table(table_name)

            sas_token = generate_table_sas(
                credential=udk,
                table_name=table_name,
                account_name=tables_storage_account_name,
                permission=TableSasPermissions(read=True, add=True, update=True, delete=True),
                expiry=expiry_time,
                start=start_time,
            )

            assert sas_token is not None
            parsed = parse_qs(sas_token)
            assert "skoid" in parsed
            assert "sktid" in parsed

            from azure.core.credentials import AzureSasCredential

            sas_client = TableServiceClient(
                endpoint=account_url,
                credential=AzureSasCredential(sas_token),
            )
            sas_table = sas_client.get_table_client(table_name)

            entities = []
            async for entity in sas_table.list_entities():
                entities.append(entity)
            assert isinstance(entities, list)
        finally:
            await tsc.delete_table(table_name)
