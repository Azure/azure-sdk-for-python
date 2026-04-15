# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import pytest
from datetime import datetime, timedelta, timezone

from devtools_testutils import AzureRecordedTestCase
from devtools_testutils.aio import recorded_by_proxy_async

from azure.core.exceptions import HttpResponseError
from azure.data.tables.aio import TableServiceClient

from _shared.asynctestcase import AsyncTableTestCase
from async_preparers import cosmos_decorator_async

# ------------------------------------------------------------------------------


class TestTableUserDelegationKeyCosmosAsync(AzureRecordedTestCase, AsyncTableTestCase):
    @cosmos_decorator_async
    @recorded_by_proxy_async
    async def test_get_user_delegation_key_not_supported_cosmos_async(
        self, tables_cosmos_account_name, tables_primary_cosmos_account_key
    ):
        """Cosmos DB does not support get_user_delegation_key. Verify it raises an error (async)."""
        tsc = TableServiceClient(
            self.account_url(tables_cosmos_account_name, "cosmos"),
            credential=tables_primary_cosmos_account_key,
            api_version="2025-07-05",
        )

        start_time = datetime.now(timezone.utc)
        expiry_time = start_time + timedelta(hours=1)

        with pytest.raises(HttpResponseError):
            await tsc.get_user_delegation_key(
                key_start_time=start_time,
                key_expiry_time=expiry_time,
            )
