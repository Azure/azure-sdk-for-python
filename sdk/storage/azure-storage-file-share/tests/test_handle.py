# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import unittest

import pytest
from azure.storage.fileshare import ShareServiceClient

from devtools_testutils import recorded_by_proxy
from devtools_testutils.storage import StorageRecordedTestCase
from settings.testcase import FileSharePreparer

# ------------------------------------------------------------------------------
TEST_SHARE_NAME = 'test-share'
# ------------------------------------------------------------------------------


class TestStorageHandle(StorageRecordedTestCase):
    def _setup(self, storage_account_name, storage_account_key):
        file_url = self.account_url(storage_account_name, "file")
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
    @recorded_by_proxy
    def test_list_handles_on_share(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # don't run live, since the test set up was highly manual
        # only run when recording, or playing back in CI
    
        self._setup(storage_account_name, storage_account_key)
        share = self.fsc.get_share_client(TEST_SHARE_NAME)
        root = share.get_directory_client()

        # Act
        handles = list(root.list_handles(recursive=True))

        # Assert
        self._validate_handles(handles)

    @pytest.mark.playback_test_only
    @FileSharePreparer()
    @recorded_by_proxy
    def test_list_handles_on_share_snapshot(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # don't run live, since the test set up was highly manual
        # only run when recording, or playing back in CI

        self._setup(storage_account_name, storage_account_key)
        share = self.fsc.get_share_client(TEST_SHARE_NAME, snapshot="2022-11-21T22:38:55.0000000Z")
        root = share.get_directory_client()

        # Act
        handles = list(root.list_handles(recursive=True))

        # Assert
        self._validate_handles(handles)

    @pytest.mark.playback_test_only
    @FileSharePreparer()
    @recorded_by_proxy
    def test_list_handles_with_marker(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # don't run live, since the test set up was highly manual
        # only run when recording, or playing back in CI

        self._setup(storage_account_name, storage_account_key)
        share = self.fsc.get_share_client(TEST_SHARE_NAME)
        root = share.get_directory_client()

        # Act
        handle_generator = root.list_handles(recursive=True, results_per_page=1).by_page()
        handles = list(next(handle_generator))

        # Assert
        assert handle_generator.continuation_token is not None
        self._validate_handles(handles)

        # Note down a handle that we saw
        old_handle = handles[0]

        # Continue listing
        remaining_handles = list(next(
            root.list_handles(recursive=True).by_page(
                continuation_token=handle_generator.continuation_token)
        ))
        self._validate_handles(handles)

        # Make sure the old handle did not appear
        # In other words, the marker worked
        old_handle_not_present = all([old_handle.id != handle.id for handle in remaining_handles])
        assert old_handle_not_present

    @pytest.mark.playback_test_only
    @FileSharePreparer()
    @recorded_by_proxy
    def test_list_handles_on_directory(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # don't run live, since the test set up was highly manual
        # only run when recording, or playing back in CI

        self._setup(storage_account_name, storage_account_key)
        share = self.fsc.get_share_client(TEST_SHARE_NAME)
        dir = share.get_directory_client('testdir')

        # Act
        handles = list(dir.list_handles(recursive=True))

        # Assert
        self._validate_handles(handles)

        # Act
        handles = list(dir.list_handles(recursive=False))

        # Assert recursive option is functioning when disabled
        assert len(handles) == 0

    @pytest.mark.playback_test_only
    @FileSharePreparer()
    @recorded_by_proxy
    def test_list_handles_on_file(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # don't run live, since the test set up was highly manual
        # only run when recording, or playing back in CI

        self._setup(storage_account_name, storage_account_key)
        share = self.fsc.get_share_client(TEST_SHARE_NAME)
        client = share.get_file_client('testdir/test.txt')

        # Act
        handles = list(client.list_handles())

        # Assert
        self._validate_handles(handles)

    @pytest.mark.playback_test_only
    @FileSharePreparer()
    @recorded_by_proxy
    def test_close_single_handle(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # don't run live, since the test set up was highly manual
        # only run when recording, or playing back in CI

        self._setup(storage_account_name, storage_account_key)
        share = self.fsc.get_share_client(TEST_SHARE_NAME)
        root = share.get_directory_client()
        handles = list(root.list_handles(recursive=True))
        self._validate_handles(handles)

        # Act
        with pytest.raises(ValueError):
            root.close_handle('*')

        handles_info = root.close_handle(handles[0])

        # Assert 1 handle has been closed
        assert 1 == handles_info['closed_handles_count']
        assert handles_info['failed_handles_count'] == 0

    @pytest.mark.playback_test_only
    @FileSharePreparer()
    @recorded_by_proxy
    def test_close_all_handle(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # don't run live, since the test set up was highly manual
        # only run when recording, or playing back in CI

        self._setup(storage_account_name, storage_account_key)
        share = self.fsc.get_share_client(TEST_SHARE_NAME)
        root = share.get_directory_client()
        handles = list(root.list_handles(recursive=True))
        self._validate_handles(handles)

        # Act
        handles_info = root.close_all_handles(recursive=True)

        # Assert at least 1 handle has been closed
        assert handles_info['closed_handles_count'] > 1
        assert handles_info['failed_handles_count'] == 0

    @pytest.mark.playback_test_only
    @FileSharePreparer()
    @recorded_by_proxy
    def test_list_handles_access_rights(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # don't run live, since the test set up was highly manual
        # only run when recording, or playing back in CI

        self._setup(storage_account_name, storage_account_key)
        share = self.fsc.get_share_client('testshare')
        root = share.get_directory_client('testdir')
        file_client = root.get_file_client('testfile.txt')

        # Act
        handles = list(file_client.list_handles())

        # Assert
        self._validate_handles(handles)
        handles[0]['access_rights'][0] == 'Write'


# ------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
