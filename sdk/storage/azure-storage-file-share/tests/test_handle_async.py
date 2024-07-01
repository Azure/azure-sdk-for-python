# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import unittest

import pytest
from azure.storage.fileshare.aio import ShareServiceClient

from devtools_testutils.aio import recorded_by_proxy_async
from devtools_testutils.storage.aio import AsyncStorageRecordedTestCase
from settings.testcase import FileSharePreparer

# ------------------------------------------------------------------------------
TEST_SHARE_NAME = 'test-share'
# ------------------------------------------------------------------------------


class TestStorageHandleAsync(AsyncStorageRecordedTestCase):
    def _setup(self, storage_account, storage_account_key):
        file_url = self.account_url(storage_account, "file")
        credentials = storage_account_key
        self.fsc = ShareServiceClient(account_url=file_url, credential=credentials)

    # --Helpers-----------------------------------------------------------------

    def _validate_handles(self, handles):
        # Assert
        assert handles is not None
        assert len(handles) >= 1
        assert handles[0] is not None

        # verify basic fields
        # path may or may not be present
        # last_connect_time_string has been missing in the test
        assert handles[0].id is not None
        assert handles[0].file_id is not None
        assert handles[0].parent_id is not None
        assert handles[0].session_id is not None
        assert handles[0].client_ip is not None
        assert handles[0].open_time is not None

    @pytest.mark.playback_test_only
    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_close_single_handle(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # don't run live, since the test set up was highly manual
        # only run when recording, or playing back in CI

        self._setup(storage_account_name, storage_account_key)
        share = self.fsc.get_share_client(TEST_SHARE_NAME)
        root = share.get_directory_client()
        handles = []
        async for handle in root.list_handles(recursive=True):
            handles.append(handle)
        self._validate_handles(handles)

        # Act
        with pytest.raises(ValueError):
            await root.close_handle('*')

        handles_info = await root.close_handle(handles[0])

        # Assert 1 handle has been closed
        assert 1 == handles_info['closed_handles_count']
        assert handles_info['failed_handles_count'] == 0

    @pytest.mark.playback_test_only
    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_close_all_handle(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # don't run live, since the test set up was highly manual
        # only run when recording, or playing back in CI

        self._setup(storage_account_name, storage_account_key)
        share = self.fsc.get_share_client(TEST_SHARE_NAME)
        root = share.get_directory_client()
        handles = []
        async for handle in root.list_handles(recursive=True):
            handles.append(handle)
        self._validate_handles(handles)

        # Act
        handles_info = await root.close_all_handles(recursive=True)

        # Assert at least 1 handle has been closed
        assert handles_info['closed_handles_count'] > 1
        assert handles_info['failed_handles_count'] == 0

    @pytest.mark.playback_test_only
    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_list_handles_access_rights(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # don't run live, since the test set up was highly manual
        # only run when recording, or playing back in CI

        self._setup(storage_account_name, storage_account_key)
        share = self.fsc.get_share_client('mytestshare')
        root = share.get_directory_client('testdir')
        file_client = root.get_file_client('testfile.txt')

        # Act
        handles = []
        async for handle in file_client.list_handles():
            handles.append(handle)

        # Assert
        self._validate_handles(handles)
        assert handles[0]['access_rights'][0] == 'Write'
        assert handles[0]['client_name'] is not None


# ------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
