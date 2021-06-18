# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import pytest

from devtools_testutils import AzureTestCase

from azure.data.tables import TableAnalyticsLogging, TableMetrics, TableRetentionPolicy, TableCorsRule
from azure.data.tables.aio import TableServiceClient
from azure.core.exceptions import HttpResponseError

from _shared.testcase import SLEEP_DELAY
from _shared.asynctestcase import AsyncTableTestCase
from async_preparers import cosmos_decorator_async
# ------------------------------------------------------------------------------

class TableServicePropertiesTest(AzureTestCase, AsyncTableTestCase):
    @cosmos_decorator_async
    async def test_too_many_cors_rules_async(self, tables_cosmos_account_name, tables_primary_cosmos_account_key):
        # Arrange
        tsc = TableServiceClient(self.account_url(tables_cosmos_account_name, "cosmos"), credential=tables_primary_cosmos_account_key)
        cors = []
        for i in range(0, 6):
            cors.append(TableCorsRule(['www.xyz.com'], ['GET']))

        # Assert
        with pytest.raises(HttpResponseError):
            await tsc.set_service_properties(cors=cors)

    @cosmos_decorator_async
    async def test_retention_too_long_async(self, tables_cosmos_account_name, tables_primary_cosmos_account_key):
        # Arrange
        tsc = TableServiceClient(self.account_url(tables_cosmos_account_name, "cosmos"), credential=tables_primary_cosmos_account_key)
        minute_metrics = TableMetrics(enabled=True, include_apis=True,
                                 retention_policy=TableRetentionPolicy(enabled=True, days=366))

        # Assert
        with pytest.raises(HttpResponseError):
            await tsc.set_service_properties(minute_metrics=minute_metrics)


class TestTableUnitTest(AsyncTableTestCase):

    @pytest.mark.asyncio
    async def test_retention_no_days_async(self):
        # Assert
        pytest.raises(ValueError, TableRetentionPolicy, enabled=True)
