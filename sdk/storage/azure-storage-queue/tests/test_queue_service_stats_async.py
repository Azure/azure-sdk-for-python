# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import unittest

import pytest
from azure.storage.queue.aio import QueueServiceClient

from devtools_testutils.aio import recorded_by_proxy_async
from devtools_testutils.storage.aio import AsyncStorageRecordedTestCase
from settings.testcase import QueuePreparer

# --Test Class -----------------------------------------------------------------
class TestAsyncQueueServiceStats(AsyncStorageRecordedTestCase):

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

    # --Test cases per service ---------------------------------------
    @pytest.mark.playback_test_only
    @QueuePreparer()
    @recorded_by_proxy_async
    async def test_queue_service_stats(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        qsc = QueueServiceClient(self.account_url(storage_account_name, "queue"), storage_account_key)
        # Act
        stats = await qsc.get_service_stats()

        # Assert
        self._assert_stats_default(stats)

    @pytest.mark.playback_test_only
    @QueuePreparer()
    @recorded_by_proxy_async
    async def test_queue_service_stats_when_unavailable(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        qsc = QueueServiceClient(self.account_url(storage_account_name, "queue"), storage_account_key)

        # Act
        stats = await qsc.get_service_stats()

        # Assert
        self._assert_stats_unavailable(stats)

# ------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
