# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import pytest
from azure.storage.blob import BlobServiceClient

from devtools_testutils import recorded_by_proxy
from devtools_testutils.storage import StorageRecordedTestCase
from settings.testcase import BlobPreparer


# --Test Class -----------------------------------------------------------------
class TestServiceStats(StorageRecordedTestCase):
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
    @recorded_by_proxy
    def test_blob_service_stats(self, **kwargs):
        # The accounts created in the Live test pipeline do not have time to finish
        # setting up GRS by the time this test runs so this test will return a different
        # response. Therefore can only run in playback.
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        bs = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=storage_account_key)

        # Act
        stats = bs.get_service_stats()

        # Assert
        self._assert_stats_default(stats)

    @pytest.mark.playback_test_only
    @BlobPreparer()
    @recorded_by_proxy
    def test_blob_service_stats_when_unavailable(self, **kwargs):
        # It's difficult to get an unavailable response from the service, so this test
        # was recorded and the recording was manually modified to have the unavailable
        # response. Therefore, can only run in playback mode.
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        bs = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=storage_account_key)

        # Act
        stats = bs.get_service_stats()

        # Assert
        self._assert_stats_unavailable(stats)

# ------------------------------------------------------------------------------
