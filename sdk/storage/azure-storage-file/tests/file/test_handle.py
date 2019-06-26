# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import unittest
import pytest

from azure.core.exceptions import (
    HttpResponseError,
    ResourceNotFoundError,
    ResourceExistsError)

from azure.storage.file.file_service_client import FileServiceClient
from azure.storage.file.directory_client import DirectoryClient
from azure.storage.file.file_client import FileClient
from azure.storage.file.share_client import ShareClient
from tests.testcase import (
    StorageTestCase,
    record,
    TestMode,
)

# ------------------------------------------------------------------------------
TEST_SHARE_NAME = 'test'


# ------------------------------------------------------------------------------

class StorageHandleTest(StorageTestCase):
    def setUp(self):
        super(StorageHandleTest, self).setUp()
        file_url = self.get_file_url()
        credentials = self.get_shared_key_credential()
        self.fsc = FileServiceClient(account_url=file_url, credential=credentials)

    def tearDown(self):
        return super(StorageHandleTest, self).tearDown()

    def _validate_handles(self, handles):
        # Assert
        self.assertIsNotNone(handles)
        self.assertGreaterEqual(len(handles), 1)
        self.assertIsNotNone(handles[0])

        # verify basic fields
        # path may or may not be present
        # last_connect_time_string has been missing in the test
        self.assertIsNotNone(handles[0].handle_id)
        self.assertIsNotNone(handles[0].file_id)
        self.assertIsNotNone(handles[0].parent_id)
        self.assertIsNotNone(handles[0].session_id)
        self.assertIsNotNone(handles[0].client_ip)
        self.assertIsNotNone(handles[0].open_time)

    @record
    def test_list_handles_on_share(self):
        pytest.skip("")
        # don't run live, since the test set up was highly manual
        # only run when recording, or playing back in CI
        if not TestMode.need_recording_file(self.test_mode):
            return
        share = self.fsc.get_share_client(TEST_SHARE_NAME)
        root = share.get_directory_client()

        # Act
        handles = list(root.list_handles(recursive=True))

        # Assert
        self._validate_handles(handles)

#
    @record
    def test_list_handles_on_share_snapshot(self):
        pytest.skip("")
        # don't run live, since the test set up was highly manual
        # only run when recording, or playing back in CI
        if not TestMode.need_recording_file(self.test_mode):
            return
        share = self.fsc.get_share_client(TEST_SHARE_NAME, snapshot="2019-05-08T23:27:24.0000000Z")
        root = share.get_directory_client()

        # Act
        handles = list(root.list_handles(recursive=True))

        # Assert
        self._validate_handles(handles)

    @record
    def test_list_handles_with_marker(self):
        pytest.skip("")
        # don't run live, since the test set up was highly manual
        # only run when recording, or playing back in CI
        if not TestMode.need_recording_file(self.test_mode):
            return
        share = self.fsc.get_share_client(TEST_SHARE_NAME)
        root = share.get_directory_client()

        # Act
        handle_generator = root.list_handles(recursive=True, results_per_page=1)
        next(handle_generator)

        # Assert
        self.assertIsNotNone(handle_generator.next_marker)
        handles = handle_generator.current_page
        self._validate_handles(handles)

        # Note down a handle that we saw
        old_handle = handles[0]

        # Continue listing
        remaining_handles = list(
            root.list_handles(recursive=True, marker=handle_generator.next_marker))
        self._validate_handles(handles)

        # Make sure the old handle did not appear
        # In other words, the marker worked
        old_handle_not_present = all([old_handle.handle_id != handle.handle_id for handle in remaining_handles])
        self.assertTrue(old_handle_not_present)

    @record
    def test_list_handles_on_directory(self):
        pytest.skip("")
        # don't run live, since the test set up was highly manual
        # only run when recording, or playing back in CI
        if not TestMode.need_recording_file(self.test_mode):
            return
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

    @record
    def test_list_handles_on_file(self):
        pytest.skip("")
        # don't run live, since the test set up was highly manual
        # only run when recording, or playing back in CI
        if not TestMode.need_recording_file(self.test_mode):
            return
        share = self.fsc.get_share_client(TEST_SHARE_NAME)
        client = share.get_file_client('wut/bla.txt')

        # Act
        handles = list(client.list_handles())

        # Assert
        self._validate_handles(handles)

    @record
    def test_close_single_handle(self):
        pytest.skip("")
        # don't run live, since the test set up was highly manual
        # only run when recording, or playing back in CI
        if not TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        share = self.fsc.get_share_client(TEST_SHARE_NAME)
        root = share.get_directory_client()
        handles = list(root.list_handles(TEST_SHARE_NAME, recursive=True))
        self._validate_handles(handles)
        handle_id = handles[0].handle_id

        # Act
        num_closed = list(self.fs.close_handles(TEST_SHARE_NAME, handle_id=handle_id))

        # Assert 1 handle has been closed
        self.assertEqual(1, num_closed[0])

    @record
    def test_close_all_handle(self):
        pytest.skip("")
        # don't run live, since the test set up was highly manual
        # only run when recording, or playing back in CI
        if not TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        handles = list(self.fs.list_handles(TEST_SHARE_NAME, recursive=True))
        self._validate_handles(handles)

        # Act
        total_num_handle_closed = 0
        for num_closed in self.fs.close_handles(TEST_SHARE_NAME, handle_id="*", recursive=True):
            total_num_handle_closed += num_closed

        # Assert at least 1 handle has been closed
        self.assertTrue(total_num_handle_closed > 1)


# ------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
