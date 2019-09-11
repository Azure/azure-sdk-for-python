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
from devtools_testutils import ResourceGroupPreparer, StorageAccountPreparer, FakeStorageAccount
from azure.storage.file.file_service_client import FileServiceClient
from azure.storage.file.directory_client import DirectoryClient
from azure.storage.file.file_client import FileClient
from azure.storage.file.share_client import ShareClient
from filetestcase import (
    FileTestCase,
)

# ------------------------------------------------------------------------------
TEST_SHARE_NAME = 'test'
TEST_SHARE_PREFIX = 'share'
FAKE_STORAGE = FakeStorageAccount(
    name='pyacrstorage',
    id='')

# ------------------------------------------------------------------------------

class StorageHandleTest(FileTestCase):
    # --Helpers-----------------------------------------------------------------
    def _get_share_reference(self, fsc, prefix=TEST_SHARE_PREFIX):
        share_name = self.get_resource_name(prefix)
        share = fsc.get_share_client(share_name)
        return share

    def _create_share(self, fsc, prefix=TEST_SHARE_PREFIX):
        share_client = self._get_share_reference(fsc, prefix)
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

    @ResourceGroupPreparer()               
    @StorageAccountPreparer(name_prefix='pyacrstorage', playback_fake_resource=FAKE_STORAGE)
    def test_list_handles_on_share(self, resource_group, location, storage_account, storage_account_key):
        #pytest.skip("")
        # don't run live, since the test set up was highly manual
        # only run when recording, or playing back in CI
        if self.is_live:
            return
        fsc = FileServiceClient(self._account_url(storage_account.name), credential=storage_account_key)
        share = self.fsc.get_share_client(TEST_SHARE_NAME)
        root = share.get_directory_client()

        # Act
        handles = list(root.list_handles(recursive=True))

        # Assert
        self._validate_handles(handles)

#
    @ResourceGroupPreparer()               
    @StorageAccountPreparer(name_prefix='pyacrstorage', playback_fake_resource=FAKE_STORAGE)
    def test_list_handles_on_share_snapshot(self, resource_group, location, storage_account, storage_account_key):
        # don't run live, since the test set up was highly manual
        # only run when recording, or playing back in CI
        if self.is_live:
            return
        fsc = FileServiceClient(self._account_url(storage_account.name), credential=storage_account_key)
        share = self.fsc.get_share_client(TEST_SHARE_NAME, snapshot="2019-05-08T23:27:24.0000000Z")
        root = share.get_directory_client()

        # Act
        handles = list(root.list_handles(recursive=True))

        # Assert
        self._validate_handles(handles)

    @ResourceGroupPreparer()               
    @StorageAccountPreparer(name_prefix='pyacrstorage', playback_fake_resource=FAKE_STORAGE)
    def test_list_handles_with_marker(self, resource_group, location, storage_account, storage_account_key):
        # don't run live, since the test set up was highly manual
        # only run when recording, or playing back in CI
        if self.is_live:
            return
        fsc = FileServiceClient(self._account_url(storage_account.name), credential=storage_account_key)
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

    @ResourceGroupPreparer()               
    @StorageAccountPreparer(name_prefix='pyacrstorage', playback_fake_resource=FAKE_STORAGE)
    def test_list_handles_on_directory(self, resource_group, location, storage_account, storage_account_key):
        # don't run live, since the test set up was highly manual
        # only run when recording, or playing back in CI
        if self.is_live:
            return
        fsc = FileServiceClient(self._account_url(storage_account.name), credential=storage_account_key)
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

    @ResourceGroupPreparer()               
    @StorageAccountPreparer(name_prefix='pyacrstorage', playback_fake_resource=FAKE_STORAGE)
    def test_list_handles_on_file(self, resource_group, location, storage_account, storage_account_key):
        # don't run live, since the test set up was highly manual
        # only run when recording, or playing back in CI
        if self.is_live:
            return
        fsc = FileServiceClient(self._account_url(storage_account.name), credential=storage_account_key)
        share = self.fsc.get_share_client(TEST_SHARE_NAME)
        client = share.get_file_client('wut/bla.txt')

        # Act
        handles = list(client.list_handles())

        # Assert
        self._validate_handles(handles)

    @ResourceGroupPreparer()               
    @StorageAccountPreparer(name_prefix='pyacrstorage', playback_fake_resource=FAKE_STORAGE)
    def test_close_single_handle(self, resource_group, location, storage_account, storage_account_key):
        # don't run live, since the test set up was highly manual
        # only run when recording, or playing back in CI
        if self.is_live:
            return

        # Arrange

        fsc = FileServiceClient(self._account_url(storage_account.name), credential=storage_account_key)
        share = self.fsc.get_share_client(TEST_SHARE_NAME)
        root = share.get_directory_client()
        handles = list(root.list_handles(recursive=True))
        self._validate_handles(handles)

        # Act
        num_closed = root.close_handles(handle=handles[0])

        # Assert 1 handle has been closed
        self.assertEqual(1, num_closed.result())

    @ResourceGroupPreparer()               
    @StorageAccountPreparer(name_prefix='pyacrstorage', playback_fake_resource=FAKE_STORAGE)
    def test_close_all_handle(self, resource_group, location, storage_account, storage_account_key):
        # don't run live, since the test set up was highly manual
        # only run when recording, or playing back in CI
        if self.is_live:
            return

        # Arrange
        fsc = FileServiceClient(self._account_url(storage_account.name), credential=storage_account_key)
        share = self.fsc.get_share_client(TEST_SHARE_NAME)
        root = share.get_directory_client()
        handles = list(root.list_handles(recursive=True))
        self._validate_handles(handles)

        # Act
        num_closed = root.close_handles()
        total_num_handle_closed = num_closed.result()

        # Assert at least 1 handle has been closed
        self.assertTrue(total_num_handle_closed > 1)
