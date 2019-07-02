# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import unittest
import pytest

from azure.storage.queue import QueueServiceClient

from queuetestcase import (
    QueueTestCase,
    record,
)

SERVICE_UNAVAILABLE_RESP_BODY = '<?xml version="1.0" encoding="utf-8"?><StorageServiceStats><GeoReplication><Status' \
                                '>unavailable</Status><LastSyncTime></LastSyncTime></GeoReplication' \
                                '></StorageServiceStats> '


# --Test Class -----------------------------------------------------------------
class QueueServiceStatsTest(QueueTestCase):
    # --Helpers-----------------------------------------------------------------
    def _assert_stats_default(self, stats):
        self.assertIsNotNone(stats)
        self.assertIsNotNone(stats.geo_replication)

        self.assertEqual(stats.geo_replication.status, 'live')
        self.assertIsNotNone(stats.geo_replication.last_sync_time)

    def _assert_stats_unavailable(self, stats):
        self.assertIsNotNone(stats)
        self.assertIsNotNone(stats.geo_replication)

        self.assertEqual(stats.geo_replication.status, 'unavailable')
        self.assertIsNone(stats.geo_replication.last_sync_time)

    @staticmethod
    def override_response_body_with_unavailable_status(response):
        response.http_response.text = lambda: SERVICE_UNAVAILABLE_RESP_BODY

    # --Test cases per service ---------------------------------------

    @record
    def test_queue_service_stats_f(self):
        # Arrange
        url = self._get_queue_url()
        credential = self._get_shared_key_credential()
        qsc = QueueServiceClient(url, credential=credential)

        # Act
        stats = qsc.get_service_stats()

        # Assert
        self._assert_stats_default(stats)

    @record
    def test_queue_service_stats_when_unavailable(self):
        # Arrange
        url = self._get_queue_url()
        credential = self._get_shared_key_credential()
        qsc = QueueServiceClient(url, credential=credential)

        # Act
        stats = qsc.get_service_stats(
            raw_response_hook=self.override_response_body_with_unavailable_status)

        # Assert
        self._assert_stats_unavailable(stats)


# ------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
