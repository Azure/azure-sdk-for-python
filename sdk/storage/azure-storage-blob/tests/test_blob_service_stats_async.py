# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import pytest
from azure.storage.blob.aio import BlobServiceClient

from devtools_testutils.aio import recorded_by_proxy_async
from devtools_testutils.storage.aio import AsyncStorageRecordedTestCase
from settings.testcase import BlobPreparer


# --Test Class -----------------------------------------------------------------
class TestServiceStatsAsync(AsyncStorageRecordedTestCase):
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
    # --------------------------------------------------------------------------

    @pytest.mark.playback_test_only
    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_blob_service_stats(self, **kwargs):
        # The accounts created in the Live test pipeline do not have time to finish
        # setting up GRS by the time this test runs so this test will return a different
        # response. Therefore can only run in playback.
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        bs = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=storage_account_key)

        # Act
        stats = await bs.get_service_stats()

        # Assert
        self._assert_stats_default(stats)

    @pytest.mark.playback_test_only
    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_blob_service_stats_when_unavailable(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        bs = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=storage_account_key)

        # Act
        stats = await bs.get_service_stats()

        # Assert
        self._assert_stats_unavailable(stats)

# ------------------------------------------------------------------------------
