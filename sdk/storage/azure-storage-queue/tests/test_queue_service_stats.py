# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import unittest

import pytest

from azure.storage.queue import QueueServiceClient

from devtools_testutils import recorded_by_proxy
from devtools_testutils.storage import StorageRecordedTestCase
from settings.testcase import QueuePreparer

SERVICE_UNAVAILABLE_RESP_BODY = '<?xml version="1.0" encoding="utf-8"?><StorageServiceStats><GeoReplication><Status' \
                                '>unavailable</Status><LastSyncTime></LastSyncTime></GeoReplication' \
                                '></StorageServiceStats> '

SERVICE_LIVE_RESP_BODY = '<?xml version="1.0" encoding="utf-8"?><StorageServiceStats><GeoReplication><Status' \
                                '>live</Status><LastSyncTime>Wed, 19 Jan 2021 22:28:43 GMT</LastSyncTime></GeoReplication' \
                                '></StorageServiceStats> '

# --Test Class -----------------------------------------------------------------
class TestQueueServiceStats(StorageRecordedTestCase):
    # --Helpers-----------------------------------------------------------------
    def _assert_stats_default(self, stats):
        assert stats is not None
        assert stats['geo_replication'] is not None

        assert stats['geo_replication']['status'] == 'live'
        assert stats['geo_replication']['last_sync_time'] is not None

    def _assert_stats_unavailable(self, stats):
        assert stats is not None
        assert stats['geo_replication'] is not None

        assert stats['geo_replication']['status'] == 'unavailable'
        assert stats['geo_replication']['last_sync_time'] is None

    @staticmethod
    def override_response_body_with_unavailable_status(response):
        response.http_response.text = lambda encoding=None: SERVICE_UNAVAILABLE_RESP_BODY

    @staticmethod
    def override_response_body_with_live_status(response):
        response.http_response.text = lambda encoding=None: SERVICE_LIVE_RESP_BODY

    # --Test cases per service ---------------------------------------

    @pytest.mark.live_test_only
    @QueuePreparer()
    @recorded_by_proxy
    def test_queue_service_stats(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        qsc = self.create_storage_client(QueueServiceClient, self.account_url(storage_account_name, "queue"), storage_account_key)

        # Act
        stats = qsc.get_service_stats()
        # Assert
        self._assert_stats_default(stats)

    @pytest.mark.live_test_only
    @QueuePreparer()
    @recorded_by_proxy
    def test_queue_service_stats_when_unavailable(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        qsc = self.create_storage_client(QueueServiceClient, self.account_url(storage_account_name, "queue"), storage_account_key)

        # Act
        stats = qsc.get_service_stats()

        # Assert
        self._assert_stats_unavailable(stats)


# ------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
