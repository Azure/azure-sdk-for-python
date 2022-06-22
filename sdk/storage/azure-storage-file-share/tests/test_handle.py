# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import unittest
import pytest

from azure.storage.fileshare import (
    ShareServiceClient,
    ShareDirectoryClient,
    ShareFileClient,
    ShareClient
)
from devtools_testutils.storage import StorageTestCase
from settings.testcase import FileSharePreparer
# ------------------------------------------------------------------------------
TEST_SHARE_NAME = 'test'
TEST_SHARE_PREFIX = 'share'


# ------------------------------------------------------------------------------

class StorageHandleTest(StorageTestCase):
    def _setup(self, storage_account_name, storage_account_key):
        file_url = self.account_url(storage_account_name, "file")
        credentials = storage_account_key
        self.fsc = ShareServiceClient(account_url=file_url, credential=credentials)
        self.test_shares = []

    # --Helpers-----------------------------------------------------------------
    def _get_share_reference(self, prefix=TEST_SHARE_PREFIX):
        share_name = self.get_resource_name(prefix)
        share = self.fsc.get_share_client(share_name)
        self.test_shares.append(share)
        return share

    def _create_share(self, prefix=TEST_SHARE_PREFIX):
        share_client = self._get_share_reference(prefix)
        share = share_client.create_share()
        return share_client

    def _validate_handles(self, handles):
        # Assert
        self.assertIsNotNone(handles)
        self.assertGreaterEqual(len(handles), 1)
        self.assertIsNotNone(handles[0])

        # verify basic fields
        # path may or may not be present
        # last_connect_time_string has been missing in the test
        self.assertIsNotNone(handles[0].id)
        self.assertIsNotNone(handles[0].file_id)
        self.assertIsNotNone(handles[0].parent_id)
        self.assertIsNotNone(handles[0].session_id)
        self.assertIsNotNone(handles[0].client_ip)
        self.assertIsNotNone(handles[0].open_time)

    @pytest.mark.playback_test_only
    @FileSharePreparer()
    def test_list_handles_on_share(self, storage_account_name, storage_account_key):
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
    def test_list_handles_on_share_snapshot(self, storage_account_name, storage_account_key):
        # don't run live, since the test set up was highly manual
        # only run when recording, or playing back in CI

        self._setup(storage_account_name, storage_account_key)
        share = self.fsc.get_share_client(TEST_SHARE_NAME, snapshot="2019-05-08T23:27:24.0000000Z")
        root = share.get_directory_client()

        # Act
        handles = list(root.list_handles(recursive=True))

        # Assert
        self._validate_handles(handles)

    @pytest.mark.playback_test_only
    @FileSharePreparer()
    def test_list_handles_with_marker(self, storage_account_name, storage_account_key):
        # don't run live, since the test set up was highly manual
        # only run when recording, or playing back in CI

        self._setup(storage_account_name, storage_account_key)
        share = self.fsc.get_share_client(TEST_SHARE_NAME)
        root = share.get_directory_client()

        # Act
        handle_generator = root.list_handles(recursive=True, results_per_page=1).by_page()
        handles = list(next(handle_generator))

        # Assert
        self.assertIsNotNone(handle_generator.continuation_token)
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
        self.assertTrue(old_handle_not_present)

    @pytest.mark.playback_test_only
    @FileSharePreparer()
    def test_list_handles_on_directory(self, storage_account_name, storage_account_key):
        # don't run live, since the test set up was highly manual
        # only run when recording, or playing back in CI

        self._setup(storage_account_name, storage_account_key)
        share = self.fsc.get_share_client(TEST_SHARE_NAME)
        dir = share.get_directory_client('wut')

        # Act
        handles = list(dir.list_handles(recursive=True))

        # Assert
        self._validate_handles(handles)

        # Act
        handles = list(dir.list_handles(recursive=False))

        # Assert recursive option is functioning when disabled
        self.assertTrue(len(handles) == 0)

    @pytest.mark.playback_test_only
    @FileSharePreparer()
    def test_list_handles_on_file(self, storage_account_name, storage_account_key):
        # don't run live, since the test set up was highly manual
        # only run when recording, or playing back in CI

        self._setup(storage_account_name, storage_account_key)
        share = self.fsc.get_share_client(TEST_SHARE_NAME)
        client = share.get_file_client('wut/bla.txt')

        # Act
        handles = list(client.list_handles())

        # Assert
        self._validate_handles(handles)

    @pytest.mark.playback_test_only
    @FileSharePreparer()
    def test_close_single_handle(self, storage_account_name, storage_account_key):
        # don't run live, since the test set up was highly manual
        # only run when recording, or playing back in CI

        self._setup(storage_account_name, storage_account_key)
        share = self.fsc.get_share_client(TEST_SHARE_NAME)
        root = share.get_directory_client()
        handles = list(root.list_handles(recursive=True))
        self._validate_handles(handles)

        # Act
        with self.assertRaises(ValueError):
            root.close_handle('*')

        handles_info = root.close_handle(handles[0])

        # Assert 1 handle has been closed
        self.assertEqual(1, handles_info['closed_handles_count'])
        self.assertEqual(handles_info['failed_handles_count'], 0)

    @pytest.mark.playback_test_only
    @FileSharePreparer()
    def test_close_all_handle(self, storage_account_name, storage_account_key):
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
        self.assertTrue(handles_info['closed_handles_count'] > 1)
        self.assertEqual(handles_info['failed_handles_count'], 0)


# ------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
