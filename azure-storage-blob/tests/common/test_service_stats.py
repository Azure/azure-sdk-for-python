# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import unittest
import pytest

from azure.storage.blob import BlobServiceClient, SharedKeyCredentials
#from azure.storage.common.retry import (
#    LinearRetry
#)

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
        url = self._get_account_url()
        credentials = SharedKeyCredentials(*self._get_shared_key_credentials())
        bs = BlobServiceClient(url, credentials=credentials)
        # Act
        stats = bs.get_service_stats()

        # Assert
        self._assert_stats_default(stats)

    @record
    def test_blob_service_stats_when_unavailable(self):
        pytest.fail("Waiting on Linear retry and custom response hook.")
        # Arrange
        url = self._get_account_url()
        config = BlobServiceClient.create_configuration()
        #config.response_callback = self.override_response_body_with_unavailable_status
        #config.retry_policy = LinearRetry(backoff=1).retry

        credentials = SharedKeyCredentials(*self._get_shared_key_credentials())
        bs = BlobServiceClient(url, credentials=credentials, configuration=config)

        # Act
        stats = bs.get_service_stats()

        # Assert
        self._assert_stats_unavailable(stats)


# ------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
