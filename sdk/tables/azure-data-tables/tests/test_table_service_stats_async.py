# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import unittest
import pytest

# from azure.data.tabless import TableServiceClient
from azure.data.tables.aio import TableServiceClient
from devtools_testutils import CachedResourceGroupPreparer, CachedStorageAccountPreparer
from _shared.testcase import TableTestCase

SERVICE_UNAVAILABLE_RESP_BODY = '<?xml version="1.0" encoding="utf-8"?><StorageServiceStats><GeoReplication><Status' \
                                '>unavailable</Status><LastSyncTime></LastSyncTime></GeoReplication' \
                                '></StorageServiceStats> '

SERVICE_LIVE_RESP_BODY = '<?xml version="1.0" encoding="utf-8"?><StorageServiceStats><GeoReplication><Status' \
                         '>live</Status><LastSyncTime>Wed, 19 Jan 2021 22:28:43 GMT</LastSyncTime></GeoReplication' \
                         '></StorageServiceStats> '


# --Test Class -----------------------------------------------------------------
class TableServiceStatsTest(TableTestCase):
    # --Helpers-----------------------------------------------------------------
    def _assert_stats_default(self, stats):
        self.assertIsNotNone(stats)
        self.assertIsNotNone(stats['geo_replication'])

        self.assertEqual(stats['geo_replication']['status'], 'live')
        self.assertIsNotNone(stats['geo_replication']['last_sync_time'])

    def _assert_stats_unavailable(self, stats):
        self.assertIsNotNone(stats)
        self.assertIsNotNone(stats['geo_replication'])

        self.assertEqual(stats['geo_replication']['status'], 'unavailable')
        self.assertIsNone(stats['geo_replication']['last_sync_time'])

    @staticmethod
    def override_response_body_with_unavailable_status(response):
        response.http_response.text = lambda _: SERVICE_UNAVAILABLE_RESP_BODY

    @staticmethod
    def override_response_body_with_live_status(response):
        response.http_response.text = lambda _: SERVICE_LIVE_RESP_BODY
        #  response.http_response.text = lambda _: SERVICE_LIVE_RESP_BODY

    # --Test cases per service ---------------------------------------

    @CachedResourceGroupPreparer(name_prefix="tablestest")
    @CachedStorageAccountPreparer(name_prefix="tablestest", sku='Standard_RAGRS')
    async def test_table_service_stats_f(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        tsc = TableServiceClient(self.account_url(storage_account, "table"), storage_account_key)

        # Act
        stats = await tsc.get_service_stats(raw_response_hook=self.override_response_body_with_live_status)
        # Assert
        self._assert_stats_default(stats)


    @CachedResourceGroupPreparer(name_prefix="tablestest")
    @CachedStorageAccountPreparer(name_prefix="tablestest", sku='Standard_RAGRS')
    async def test_table_service_stats_when_unavailable(self, resource_group, location, storage_account, storage_account_key):
        # Arrange
        tsc = TableServiceClient(self.account_url(storage_account, "table"), storage_account_key)

        # Act
        stats = await tsc.get_service_stats(
            raw_response_hook=self.override_response_body_with_unavailable_status)

        # Assert
        self._assert_stats_unavailable(stats)


# ------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
