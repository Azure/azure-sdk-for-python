# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import unittest

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
        self.fs = self._create_storage_service(FileService, self.settings)

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
        # don't run live, since the test set up was highly manual
        # only run when recording, or playing back in CI
        if not TestMode.need_recording_file(self.test_mode):
            return

        # Act
        handles = list(self.fs.list_handles(TEST_SHARE_NAME, recursive=True))

        # Assert
        self._validate_handles(handles)

#
    @record
    def test_list_handles_on_share_snapshot(self):
        # don't run live, since the test set up was highly manual
        # only run when recording, or playing back in CI
        if not TestMode.need_recording_file(self.test_mode):
            return

        # Act
        handles = list(self.fs.list_handles(TEST_SHARE_NAME, recursive=True,
                                            snapshot="2019-05-08T23:27:24.0000000Z"))

        # Assert
        self._validate_handles(handles)

    @record
    def test_list_handles_with_marker(self):
        # don't run live, since the test set up was highly manual
        # only run when recording, or playing back in CI
        if not TestMode.need_recording_file(self.test_mode):
            return

        # Act
        handle_generator = self.fs.list_handles(TEST_SHARE_NAME, recursive=True, max_results=1)

        # Assert
        self.assertIsNotNone(handle_generator.next_marker)
        handles = list(handle_generator)
        self._validate_handles(handles)

        # Note down a handle that we saw
        old_handle = handles[0]

        # Continue listing
        remaining_handles = list(
            self.fs.list_handles(TEST_SHARE_NAME, recursive=True, marker=handle_generator.next_marker))
        self._validate_handles(handles)

        # Make sure the old handle did not appear
        # In other words, the marker worked
        old_handle_not_present = all([old_handle.handle_id != handle.handle_id for handle in remaining_handles])
        self.assertTrue(old_handle_not_present)

    @record
    def test_list_handles_on_directory(self):
        # don't run live, since the test set up was highly manual
        # only run when recording, or playing back in CI
        if not TestMode.need_recording_file(self.test_mode):
            return

        # Act
        handles = list(self.fs.list_handles(TEST_SHARE_NAME, directory_name='wut', recursive=True))

        # Assert
        self._validate_handles(handles)

        # Act
        handles = list(self.fs.list_handles(TEST_SHARE_NAME, directory_name='wut', recursive=False))

        # Assert recursive option is functioning when disabled
        self.assertTrue(len(handles) == 0)

    @record
    def test_list_handles_on_file(self):
        # don't run live, since the test set up was highly manual
        # only run when recording, or playing back in CI
        if not TestMode.need_recording_file(self.test_mode):
            return

        # Act
        handles = list(self.fs.list_handles(TEST_SHARE_NAME, directory_name='wut', file_name='bla.txt'))

        # Assert
        self._validate_handles(handles)

    @record
    def test_close_single_handle(self):
        # don't run live, since the test set up was highly manual
        # only run when recording, or playing back in CI
        if not TestMode.need_recording_file(self.test_mode):
            return

        # Arrange
        handles = list(self.fs.list_handles(TEST_SHARE_NAME, recursive=True))
        self._validate_handles(handles)
        handle_id = handles[0].handle_id

        # Act
        num_closed = list(self.fs.close_handles(TEST_SHARE_NAME, handle_id=handle_id))

        # Assert 1 handle has been closed
        self.assertEqual(1, num_closed[0])

    @record
    def test_close_all_handle(self):
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
