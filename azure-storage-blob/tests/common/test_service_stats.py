# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import unittest

from azure.storage.blob import (
    BlobServiceClient,
    ContainerClient,
    BlobClient,
)
#from azure.storage.common.retry import (
#    LinearRetry
#)
#from azure.storage.queue import QueueService
from tests.testcase import (
    StorageTestCase,
    record,
)

SERVICE_UNAVAILABLE_RESP_BODY = '<?xml version="1.0" encoding="utf-8"?><StorageServiceStats><GeoReplication><Status' \
                                '>unavailable</Status><LastSyncTime></LastSyncTime></GeoReplication' \
                                '></StorageServiceStats> '


# --Test Class -----------------------------------------------------------------
class ServiceStatsTest(StorageTestCase):
    # --Helpers-----------------------------------------------------------------
    def _assert_stats_default(self, stats):
        self.assertIsNotNone(stats)
        self.assertIsNotNone(stats.geo_replication)

        if not self.settings.IS_EMULATED:
            self.assertEqual(stats.geo_replication.status, 'live')
            self.assertIsNotNone(stats.geo_replication.last_sync_time)

    def _assert_stats_unavailable(self, stats):
        self.assertIsNotNone(stats)
        self.assertIsNotNone(stats.geo_replication)

        self.assertEqual(stats.geo_replication.status, 'unavailable')
        self.assertIsNone(stats.geo_replication.last_sync_time)

    @staticmethod
    def override_response_body_with_unavailable_status(response):
        response.body = SERVICE_UNAVAILABLE_RESP_BODY

    # --Test cases per service ---------------------------------------

    @record
    def test_blob_service_stats(self):
        # Arrange
        bs = self._create_storage_service(BlockBlobService, self.settings)

        # Act
        stats = bs.get_blob_service_stats()

        # Assert
        self._assert_stats_default(stats)

    @record
    def test_blob_service_stats_when_unavailable(self):
        # Arrange
        bs = self._create_storage_service(BlockBlobService, self.settings)
        bs.response_callback = self.override_response_body_with_unavailable_status
        bs.retry = LinearRetry(backoff=1).retry

        # Act
        stats = bs.get_blob_service_stats()

        # Assert
        self._assert_stats_unavailable(stats)

    @record
    def test_queue_service_stats(self):
        # Arrange
        qs = self._create_storage_service(QueueService, self.settings)

        # Act
        stats = qs.get_queue_service_stats()

        # Assert
        self._assert_stats_default(stats)

    @record
    def test_queue_service_stats_when_unavailable(self):
        # Arrange
        qs = self._create_storage_service(QueueService, self.settings)
        qs.response_callback = self.override_response_body_with_unavailable_status
        qs.retry = LinearRetry(backoff=1).retry

        # Act
        stats = qs.get_queue_service_stats()

        # Assert
        self._assert_stats_unavailable(stats)


# ------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
