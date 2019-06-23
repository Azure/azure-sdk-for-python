# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import unittest

from azure.common import (
    AzureConflictHttpError,
    AzureMissingResourceHttpError,
)

from azure.storage.file import (
    FileService,
    DeleteSnapshot,
)
from tests.testcase import (
    StorageTestCase,
    record,
    LogCaptured,
)


# ------------------------------------------------------------------------------


class StorageDirectoryTest(StorageTestCase):
    def setUp(self):
        super(StorageDirectoryTest, self).setUp()

        self.fs = self._create_storage_service(FileService, self.settings)
        self.share_name = self.get_resource_name('utshare')

        if not self.is_playback():
            self.fs.create_share(self.share_name)

    def tearDown(self):
        if not self.is_playback():
            try:
                self.fs.delete_share(self.share_name, delete_snapshots=DeleteSnapshot.Include)
            except:
                pass

        return super(StorageDirectoryTest, self).tearDown()

    # --Helpers-----------------------------------------------------------------

    # --Test cases for directories ----------------------------------------------
    @record
    def test_create_directories(self):
        # Arrange

        # Act
        created = self.fs.create_directory(self.share_name, 'dir1')

        # Assert
        self.assertTrue(created)

    @record
    def test_create_directories_with_metadata(self):
        # Arrange
        metadata = {'hello': 'world', 'number': '42'}

        # Act
        self.fs.create_directory(self.share_name, 'dir1', metadata=metadata)

        # Assert
        md = self.fs.get_directory_metadata(self.share_name, 'dir1')
        self.assertDictEqual(md, metadata)

    @record
    def test_create_directories_fail_on_exist(self):
        # Arrange

        # Act
        created = self.fs.create_directory(self.share_name, 'dir1')
        with self.assertRaises(AzureConflictHttpError):
            self.fs.create_directory(self.share_name, 'dir1', fail_on_exist=True)

        # Assert
        self.assertTrue(created)

    @record
    def test_create_directory_with_already_existing_directory(self):
        # Arrange

        # Act
        created1 = self.fs.create_directory(self.share_name, 'dir1')
        created2 = self.fs.create_directory(self.share_name, 'dir1')

        # Assert
        self.assertTrue(created1)
        self.assertFalse(created2)

    @record
    def test_get_directory_properties(self):
        # Arrange
        self.fs.create_directory(self.share_name, 'dir1')

        # Act
        props = self.fs.get_directory_properties(self.share_name, 'dir1')

        # Assert
        self.assertIsNotNone(props)
        self.assertIsNotNone(props.properties.etag)
        self.assertIsNotNone(props.properties.last_modified)

    @record
    def test_get_directory_properties_with_snapshot(self):
        # Arrange
        metadata = {"test1": "foo", "test2": "bar"}
        self.fs.create_directory(self.share_name, 'dir1', metadata)
        snapshot1 = self.fs.snapshot_share(self.share_name)
        metadata2 = {"test100": "foo100", "test200": "bar200"}
        self.fs.set_directory_metadata(self.share_name, 'dir1', metadata2)

        # Act
        props = self.fs.get_directory_properties(self.share_name, 'dir1', snapshot=snapshot1.snapshot)

        # Assert
        self.assertIsNotNone(props)
        self.assertIsNotNone(props.properties.etag)
        self.assertIsNotNone(props.properties.last_modified)
        self.assertDictEqual(metadata, props.metadata)

    @record
    def test_get_directory_metadata_with_snapshot(self):
        # Arrange
        metadata = {"test1": "foo", "test2": "bar"}
        self.fs.create_directory(self.share_name, 'dir1', metadata)
        snapshot1 = self.fs.snapshot_share(self.share_name)
        metadata2 = {"test100": "foo100", "test200": "bar200"}
        self.fs.set_directory_metadata(self.share_name, 'dir1', metadata2)

        # Act
        snapshot_metadata = self.fs.get_directory_metadata(self.share_name, 'dir1', snapshot=snapshot1.snapshot)

        # Assert
        self.assertIsNotNone(snapshot_metadata)
        self.assertDictEqual(metadata, snapshot_metadata)

    @record
    def test_get_directory_properties_with_non_existing_directory(self):
        # Arrange

        # Act
        with self.assertRaises(AzureMissingResourceHttpError):
            self.fs.get_directory_properties(self.share_name, 'dir1')

            # Assert

    @record
    def test_directory_exists(self):
        # Arrange
        self.fs.create_directory(self.share_name, 'dir1')

        # Act
        exists = self.fs.exists(self.share_name, 'dir1')

        # Assert
        self.assertTrue(exists)

    @record
    def test_directory_not_exists(self):
        # Arrange

        # Act
        with LogCaptured(self) as log_captured:
            exists = self.fs.exists(self.share_name, 'missing')

            log_as_str = log_captured.getvalue()
            self.assertTrue('ERROR' not in log_as_str)

        # Assert
        self.assertFalse(exists)

    @record
    def test_directory_parent_not_exists(self):
        # Arrange

        # Act
        with LogCaptured(self) as log_captured:
            exists = self.fs.exists(self.share_name, 'missing1/missing2')

            log_as_str = log_captured.getvalue()
            self.assertTrue('ERROR' not in log_as_str)

        # Assert
        self.assertFalse(exists)

    @record
    def test_directory_exists_with_snapshot(self):
        # Arrange
        self.fs.create_directory(self.share_name, 'dir1')
        snapshot = self.fs.snapshot_share(self.share_name)
        self.fs.delete_directory(self.share_name, 'dir1')

        # Act
        exists = self.fs.exists(self.share_name, 'dir1', snapshot=snapshot.snapshot)

        # Assert
        self.assertTrue(exists)

    @record
    def test_directory_not_exists_with_snapshot(self):
        # Arrange
        snapshot = self.fs.snapshot_share(self.share_name)
        self.fs.create_directory(self.share_name, 'dir1')

        # Act
        exists = self.fs.exists(self.share_name, 'dir1', snapshot=snapshot.snapshot)

        # Assert
        self.assertFalse(exists)

    @record
    def test_get_set_directory_metadata(self):
        # Arrange
        metadata = {'hello': 'world', 'number': '43'}
        self.fs.create_directory(self.share_name, 'dir1')

        # Act
        self.fs.set_directory_metadata(self.share_name, 'dir1', metadata)
        md = self.fs.get_directory_metadata(self.share_name, 'dir1')

        # Assert
        self.assertDictEqual(md, metadata)

    @record
    def test_delete_directory_with_existing_share(self):
        # Arrange
        self.fs.create_directory(self.share_name, 'dir1')

        # Act
        deleted = self.fs.delete_directory(self.share_name, 'dir1')

        # Assert
        self.assertTrue(deleted)
        with self.assertRaises(AzureMissingResourceHttpError):
            self.fs.get_directory_properties(self.share_name, 'dir1')

    @record
    def test_delete_directory_with_existing_directory_fail_not_exist(self):
        # Arrange
        self.fs.create_directory(self.share_name, 'dir1')

        # Act
        deleted = self.fs.delete_directory(self.share_name, 'dir1')

        # Assert
        self.assertTrue(deleted)
        with self.assertRaises(AzureMissingResourceHttpError):
            self.fs.get_directory_properties(self.share_name, 'dir1')

    @record
    def test_delete_directory_with_non_existing_directory(self):
        # Arrange

        # Act
        with LogCaptured(self) as log_captured:
            deleted = self.fs.delete_directory(self.share_name, 'dir1', False)

            log_as_str = log_captured.getvalue()
            self.assertTrue('ERROR' not in log_as_str)

        # Assert
        self.assertFalse(deleted)

    @record
    def test_delete_directory_with_non_existing_directory_fail_not_exist(self):
        # Arrange

        # Act
        with LogCaptured(self) as log_captured:
            with self.assertRaises(AzureMissingResourceHttpError):
                self.fs.delete_directory(self.share_name, 'dir1', True)

            log_as_str = log_captured.getvalue()
            self.assertTrue('ERROR' in log_as_str)

            # Assert

    @record
    def test_get_directory_properties_server_encryption(self):
        # Arrange
        self.fs.create_directory(self.share_name, 'dir1')

        # Act
        props = self.fs.get_directory_properties(self.share_name, 'dir1')

        # Assert
        self.assertIsNotNone(props)
        self.assertIsNotNone(props.properties.etag)
        self.assertIsNotNone(props.properties.last_modified)

        if self.is_file_encryption_enabled():
            self.assertTrue(props.properties.server_encrypted)
        else:
            self.assertFalse(props.properties.server_encrypted)


# ------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
