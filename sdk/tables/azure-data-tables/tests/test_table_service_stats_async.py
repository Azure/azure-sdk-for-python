# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from devtools_testutils import AzureRecordedTestCase
from devtools_testutils.aio import recorded_by_proxy_async

from azure.data.tables.aio import TableServiceClient

from _shared.asynctestcase import AsyncTableTestCase
from async_preparers import tables_decorator_async

SERVICE_UNAVAILABLE_RESP_BODY = '<?xml version="1.0" encoding="utf-8"?><StorageServiceStats><GeoReplication><Status' \
                                '>unavailable</Status><LastSyncTime></LastSyncTime></GeoReplication' \
                                '></StorageServiceStats> '

SERVICE_LIVE_RESP_BODY = '<?xml version="1.0" encoding="utf-8"?><StorageServiceStats><GeoReplication><Status' \
                         '>live</Status><LastSyncTime>Wed, 19 Jan 2021 22:28:43 GMT</LastSyncTime></GeoReplication' \
                         '></StorageServiceStats> '


class TestTableServiceStatsAsync(AzureRecordedTestCase, AsyncTableTestCase):

    @staticmethod
    def override_response_body_with_unavailable_status(response):
        response.http_response.text = lambda _: SERVICE_UNAVAILABLE_RESP_BODY

    @staticmethod
    def override_response_body_with_live_status(response):
        response.http_response.text = lambda _: SERVICE_LIVE_RESP_BODY

    # --Test cases per service ---------------------------------------
    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_table_service_stats_f(self, tables_storage_account_name, tables_primary_storage_account_key):
        # Arrange
        tsc = TableServiceClient(self.account_url(tables_storage_account_name, "table"), credential=tables_primary_storage_account_key)

        # Act
        stats = await tsc.get_service_stats(raw_response_hook=self.override_response_body_with_live_status)
        # Assert
        self._assert_stats_default(stats)

    @tables_decorator_async
    @recorded_by_proxy_async
    async def test_table_service_stats_when_unavailable(self, tables_storage_account_name, tables_primary_storage_account_key):
        # Arrange
        tsc = TableServiceClient(self.account_url(tables_storage_account_name, "table"), credential=tables_primary_storage_account_key)

        # Act
        stats = await tsc.get_service_stats(raw_response_hook=self.override_response_body_with_unavailable_status)

        # Assert
        self._assert_stats_unavailable(stats)
