# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import pytest

from devtools_testutils import AzureRecordedTestCase
from devtools_testutils.aio import recorded_by_proxy_async

from azure.data.tables.aio import TableServiceClient

from _shared.asynctestcase import AsyncTableTestCase
from _shared.testcase import SLEEP_DELAY
from async_preparers import cosmos_decorator_async

SERVICE_UNAVAILABLE_RESP_BODY = '<?xml version="1.0" encoding="utf-8"?><StorageServiceStats><GeoReplication><Status' \
                                '>unavailable</Status><LastSyncTime></LastSyncTime></GeoReplication' \
                                '></StorageServiceStats> '

SERVICE_LIVE_RESP_BODY = '<?xml version="1.0" encoding="utf-8"?><StorageServiceStats><GeoReplication><Status' \
                         '>live</Status><LastSyncTime>Wed, 19 Jan 2021 22:28:43 GMT</LastSyncTime></GeoReplication' \
                         '></StorageServiceStats> '

class TestTableServiceStatsCosmosAsync(AzureRecordedTestCase, AsyncTableTestCase):

    @staticmethod
    def override_response_body_with_unavailable_status(response):
        response.http_response.text = lambda _: SERVICE_UNAVAILABLE_RESP_BODY

    @staticmethod
    def override_response_body_with_live_status(response):
        response.http_response.text = lambda _: SERVICE_LIVE_RESP_BODY

    # --Test cases per service ---------------------------------------
    @pytest.mark.skip("JSON is invalid for cosmos")
    @cosmos_decorator_async
    @recorded_by_proxy_async
    async def test_table_service_stats_f(self, **kwargs):
        tables_cosmos_account_name = kwargs.pop("tables_cosmos_account_name")
        tables_primary_cosmos_account_key = kwargs.pop("tables_primary_cosmos_account_key")
        tsc = TableServiceClient(self.account_url(tables_cosmos_account_name, "cosmos"), credential=tables_primary_cosmos_account_key)
        stats = await tsc.get_service_stats(raw_response_hook=self.override_response_body_with_live_status)
        self._assert_stats_default(stats)

    @pytest.mark.skip("JSON is invalid for cosmos")
    @cosmos_decorator_async
    @recorded_by_proxy_async
    async def test_table_service_stats_when_unavailable(self, **kwargs):
        tables_cosmos_account_name = kwargs.pop("tables_cosmos_account_name")
        tables_primary_cosmos_account_key = kwargs.pop("tables_primary_cosmos_account_key")
        tsc = TableServiceClient(self.account_url(tables_cosmos_account_name, "cosmos"), credential=tables_primary_cosmos_account_key)
        stats = await tsc.get_service_stats(raw_response_hook=self.override_response_body_with_unavailable_status)
        self._assert_stats_unavailable(stats)
