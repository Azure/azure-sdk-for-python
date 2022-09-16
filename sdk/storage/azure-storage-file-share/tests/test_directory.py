# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import unittest
import pytest
from datetime import datetime, timedelta

from azure.core.exceptions import ResourceNotFoundError, ResourceExistsError
from azure.storage.fileshare import (
    generate_share_sas,
    NTFSAttributes,
    ShareDirectoryClient,
    ShareSasPermissions,
    ShareServiceClient,
    StorageErrorCode,
)
from devtools_testutils.storage import StorageTestCase
from settings.testcase import FileSharePreparer
# ------------------------------------------------------------------------------
TEST_FILE_PERMISSIONS = 'O:S-1-5-21-2127521184-1604012920-1887927527-21560751G:S-1-5-21-2127521184-' \
                        '1604012920-1887927527-513D:AI(A;;FA;;;SY)(A;;FA;;;BA)(A;;0x1200a9;;;' \
                        'S-1-5-21-397955417-626881126-188441444-3053964)'


class StorageDirectoryTest(StorageTestCase):
    def _setup(self, storage_account_name, storage_account_key):
        url = self.account_url(storage_account_name, "file")
        credential = storage_account_key
        self.fsc = ShareServiceClient(url, credential=credential)
        self.share_name = self.get_resource_name('utshare')

        if not self.is_playback():
            try:
                self.fsc.create_share(self.share_name)
            except:
                pass

    def _teardown(self, FILE_PATH):
        if os.path.isfile(FILE_PATH):
            try:
                os.remove(FILE_PATH)
            except:
                pass
    # --Helpers-----------------------------------------------------------------

    # --Test cases for directories ----------------------------------------------
    @FileSharePreparer()
    def test_create_directories(self, storage_account_name, storage_account_key):
        self._setup(storage_account_name, storage_account_key)
        share_client = self.fsc.get_share_client(self.share_name)

        # Act
        created = share_client.create_directory('dir1')

        # Assert
        self.assertTrue(created)

    @FileSharePreparer()
    def test_create_directories_with_metadata(self, storage_account_name, storage_account_key):
        self._setup(storage_account_name, storage_account_key)
        share_client = self.fsc.get_share_client(self.share_name)
        metadata = {'hello': 'world', 'number': '42'}

        # Act
        directory = share_client.create_directory('dir1', metadata=metadata)

        # Assert
        md = directory.get_directory_properties().metadata
        self.assertDictEqual(md, metadata)

    @FileSharePreparer()
    def test_create_directories_fail_on_exist(self, storage_account_name, storage_account_key):
        self._setup(storage_account_name, storage_account_key)
        share_client = self.fsc.get_share_client(self.share_name)

        # Act
        created = share_client.create_directory('dir1')
        with self.assertRaises(ResourceExistsError):
            share_client.create_directory('dir1')

        # Assert
        self.assertTrue(created)

    @FileSharePreparer()
    def test_create_directory_set_smb_properties(self, storage_account_name, storage_account_key):
        self._setup(storage_account_name, storage_account_key)
        share_client = self.fsc.get_share_client(self.share_name)

        directory_client = share_client.get_directory_client('dir1')
        file_attributes = NTFSAttributes(read_only=True, directory=True)
        file_creation_time = file_last_write_time = file_change_time = datetime(2022, 3, 10, 10, 14, 30, 500000)

        # Act
        directory_client.create_directory(
            file_attributes=file_attributes,
            file_creation_time=file_creation_time,
            file_last_write_time=file_last_write_time,
            file_change_time=file_change_time)
        directory_properties = directory_client.get_directory_properties()

        # Assert
        self.assertIsNotNone(directory_properties)
        self.assertEqual(file_creation_time, directory_properties.creation_time)
        self.assertEqual(file_last_write_time, directory_properties.last_write_time)
        self.assertEqual(file_change_time, directory_properties.change_time)
        self.assertIn('ReadOnly', directory_properties.file_attributes)
        self.assertIn('Directory', directory_properties.file_attributes)

    @FileSharePreparer()
    def test_create_subdirectories(self, storage_account_name, storage_account_key):
        self._setup(storage_account_name, storage_account_key)
        share_client = self.fsc.get_share_client(self.share_name)
        directory = share_client.create_directory('dir1')

        # Act
        created = directory.create_subdirectory('dir2')

        # Assert
        self.assertTrue(created)
        self.assertEqual(created.directory_path, 'dir1/dir2')

    @FileSharePreparer()
    def test_create_subdirectories_with_metadata(self, storage_account_name, storage_account_key):
        self._setup(storage_account_name, storage_account_key)
        share_client = self.fsc.get_share_client(self.share_name)
        directory = share_client.create_directory('dir1')
        metadata = {'hello': 'world', 'number': '42'}

        # Act
        created = directory.create_subdirectory('dir2', metadata=metadata)

        # Assert
        self.assertTrue(created)
        self.assertEqual(created.directory_path, 'dir1/dir2')
        sub_metadata = created.get_directory_properties().metadata
        self.assertEqual(sub_metadata, metadata)

    @FileSharePreparer()
    def test_create_file_in_directory(self, storage_account_name, storage_account_key):
        self._setup(storage_account_name, storage_account_key)
        file_data = b'12345678' * 1024
        file_name = self.get_resource_name('file')
        share_client = self.fsc.get_share_client(self.share_name)
        directory = share_client.create_directory('dir1')

        # Act
        new_file = directory.upload_file(file_name, file_data)

        # Assert
        file_content = new_file.download_file().readall()
        self.assertEqual(file_content, file_data)

    @FileSharePreparer()
    def test_delete_file_in_directory(self, storage_account_name, storage_account_key):
        self._setup(storage_account_name, storage_account_key)
        file_name = self.get_resource_name('file')
        share_client = self.fsc.get_share_client(self.share_name)
        directory = share_client.create_directory('dir1')
        new_file = directory.upload_file(file_name, "hello world")

        # Act
        deleted = directory.delete_file(file_name)

        # Assert
        self.assertIsNone(deleted)
        with self.assertRaises(ResourceNotFoundError):
            new_file.get_file_properties()

    @FileSharePreparer()
    def test_share_directory_exists(self, storage_account_name, storage_account_key):
        self._setup(storage_account_name, storage_account_key)
        share_client = self.fsc.get_share_client(self.share_name)
        directory = share_client.create_directory('dir1')

        directory2 = share_client.get_directory_client("dir2")

        self.assertTrue(directory.exists())
        self.assertFalse(directory2.exists())

    @FileSharePreparer()
    def test_delete_subdirectories(self, storage_account_name, storage_account_key):
        self._setup(storage_account_name, storage_account_key)
        share_client = self.fsc.get_share_client(self.share_name)
        directory = share_client.create_directory('dir1')
        directory.create_subdirectory('dir2')

        # Act
        deleted = directory.delete_subdirectory('dir2')

        # Assert
        self.assertIsNone(deleted)
        subdir = directory.get_subdirectory_client('dir2')
        with self.assertRaises(ResourceNotFoundError):
            subdir.get_directory_properties()

    @FileSharePreparer()
    def test_get_directory_properties(self, storage_account_name, storage_account_key):
        self._setup(storage_account_name, storage_account_key)
        share_client = self.fsc.get_share_client(self.share_name)
        directory = share_client.create_directory('dir1')

        # Act
        props = directory.get_directory_properties()

        # Assert
        self.assertIsNotNone(props)
        self.assertIsNotNone(props.etag)
        self.assertIsNotNone(props.last_modified)

    @FileSharePreparer()
    def test_get_directory_properties_with_snapshot(self, storage_account_name, storage_account_key):
        self._setup(storage_account_name, storage_account_key)
        share_client = self.fsc.get_share_client(self.share_name)
        metadata = {"test1": "foo", "test2": "bar"}
        directory = share_client.create_directory('dir1', metadata=metadata)
        snapshot1 = share_client.create_snapshot()
        metadata2 = {"test100": "foo100", "test200": "bar200"}
        directory.set_directory_metadata(metadata2)

        # Act
        share_client = self.fsc.get_share_client(self.share_name, snapshot=snapshot1)
        snap_dir = share_client.get_directory_client('dir1')
        props = snap_dir.get_directory_properties()

        # Assert
        self.assertIsNotNone(props)
        self.assertIsNotNone(props.etag)
        self.assertIsNotNone(props.last_modified)
        self.assertDictEqual(metadata, props.metadata)

    @FileSharePreparer()
    def test_get_directory_metadata_with_snapshot(self, storage_account_name, storage_account_key):
        self._setup(storage_account_name, storage_account_key)
        share_client = self.fsc.get_share_client(self.share_name)
        metadata = {"test1": "foo", "test2": "bar"}
        directory = share_client.create_directory('dir1', metadata=metadata)
        snapshot1 = share_client.create_snapshot()
        metadata2 = {"test100": "foo100", "test200": "bar200"}
        directory.set_directory_metadata(metadata2)

        # Act
        share_client = self.fsc.get_share_client(self.share_name, snapshot=snapshot1)
        snap_dir = share_client.get_directory_client('dir1')
        snapshot_metadata = snap_dir.get_directory_properties().metadata

        # Assert
        self.assertIsNotNone(snapshot_metadata)
        self.assertDictEqual(metadata, snapshot_metadata)

    @FileSharePreparer()
    def test_get_directory_properties_with_non_existing_directory(self, storage_account_name, storage_account_key):
        self._setup(storage_account_name, storage_account_key)
        share_client = self.fsc.get_share_client(self.share_name)
        directory = share_client.get_directory_client('dir1')

        # Act
        with self.assertRaises(ResourceNotFoundError):
            directory.get_directory_properties()

            # Assert

    @FileSharePreparer()
    def test_directory_exists(self, storage_account_name, storage_account_key):
        self._setup(storage_account_name, storage_account_key)
        share_client = self.fsc.get_share_client(self.share_name)
        directory = share_client.create_directory('dir1')

        # Act
        exists = directory.get_directory_properties()

        # Assert
        self.assertTrue(exists)

    @FileSharePreparer()
    def test_directory_not_exists(self, storage_account_name, storage_account_key):
        self._setup(storage_account_name, storage_account_key)
        share_client = self.fsc.get_share_client(self.share_name)
        directory = share_client.get_directory_client('dir1')

        # Act
        with self.assertRaises(ResourceNotFoundError):
            directory.get_directory_properties()

        # Assert

    @FileSharePreparer()
    def test_directory_parent_not_exists(self, storage_account_name, storage_account_key):
        self._setup(storage_account_name, storage_account_key)
        share_client = self.fsc.get_share_client(self.share_name)
        directory = share_client.get_directory_client('missing1/missing2')

        # Act
        with self.assertRaises(ResourceNotFoundError) as e:
            directory.get_directory_properties()

        # Assert
        self.assertEqual(e.exception.error_code, StorageErrorCode.parent_not_found)

    @FileSharePreparer()
    def test_directory_exists_with_snapshot(self, storage_account_name, storage_account_key):
        self._setup(storage_account_name, storage_account_key)
        share_client = self.fsc.get_share_client(self.share_name)
        directory = share_client.create_directory('dir1')
        snapshot = share_client.create_snapshot()
        directory.delete_directory()

        # Act
        share_client = self.fsc.get_share_client(self.share_name, snapshot=snapshot)
        snap_dir = share_client.get_directory_client('dir1')
        exists = snap_dir.get_directory_properties()

        # Assert
        self.assertTrue(exists)

    @FileSharePreparer()
    def test_directory_not_exists_with_snapshot(self, storage_account_name, storage_account_key):
        self._setup(storage_account_name, storage_account_key)
        share_client = self.fsc.get_share_client(self.share_name)
        snapshot = share_client.create_snapshot()
        directory = share_client.create_directory('dir1')

        # Act
        share_client = self.fsc.get_share_client(self.share_name, snapshot=snapshot)
        snap_dir = share_client.get_directory_client('dir1')

        with self.assertRaises(ResourceNotFoundError):
            snap_dir.get_directory_properties()

        # Assert

    @FileSharePreparer()
    def test_get_set_directory_metadata(self, storage_account_name, storage_account_key):
        self._setup(storage_account_name, storage_account_key)
        share_client = self.fsc.get_share_client(self.share_name)
        directory = share_client.create_directory('dir1')
        metadata = {'hello': 'world', 'number': '43'}

        # Act
        directory.set_directory_metadata(metadata)
        md = directory.get_directory_properties().metadata

        # Assert
        self.assertDictEqual(md, metadata)

    @FileSharePreparer()
    def test_set_directory_properties_with_empty_smb_properties(self, storage_account_name, storage_account_key):
        self._setup(storage_account_name, storage_account_key)
        share_client = self.fsc.get_share_client(self.share_name)
        directory_client = share_client.create_directory('dir1')
        directory_properties_on_creation = directory_client.get_directory_properties()

        # Act
        directory_client.set_http_headers()
        directory_properties = directory_client.get_directory_properties()

        # Assert
        # Make sure set empty smb_properties doesn't change smb_properties
        self.assertEqual(directory_properties_on_creation.creation_time,
                          directory_properties.creation_time)
        self.assertEqual(directory_properties_on_creation.last_write_time,
                          directory_properties.last_write_time)
        self.assertEqual(directory_properties_on_creation.permission_key,
                          directory_properties.permission_key)

    @FileSharePreparer()
    def test_set_directory_properties_with_file_permission_key(self, storage_account_name, storage_account_key):
        self._setup(storage_account_name, storage_account_key)
        share_client = self.fsc.get_share_client(self.share_name)
        directory_client = share_client.create_directory('dir1')

        directory_properties_on_creation = directory_client.get_directory_properties()
        permission_key = directory_properties_on_creation.permission_key
        last_write_time = directory_properties_on_creation.last_write_time
        creation_time = directory_properties_on_creation.creation_time
        change_time = directory_properties_on_creation.change_time

        new_last_write_time = last_write_time + timedelta(hours=1)
        new_creation_time = creation_time + timedelta(hours=1)
        new_change_time = change_time + timedelta(hours=1)

        # Act
        directory_client.set_http_headers(
            file_attributes='None',
            file_creation_time=new_creation_time,
            file_last_write_time=new_last_write_time,
            file_change_time=new_change_time,
            permission_key=permission_key)
        directory_properties = directory_client.get_directory_properties()

        # Assert
        self.assertIsNotNone(directory_properties)
        self.assertEqual(directory_properties.creation_time, new_creation_time)
        self.assertEqual(directory_properties.last_write_time, new_last_write_time)
        self.assertEqual(directory_properties.change_time, new_change_time)

    @FileSharePreparer()
    def test_list_subdirectories_and_files(self, storage_account_name, storage_account_key):
        self._setup(storage_account_name, storage_account_key)
        share_client = self.fsc.get_share_client(self.share_name)
        directory = share_client.create_directory('dir1')
        directory.create_subdirectory("subdir1")
        directory.create_subdirectory("subdir2")
        directory.create_subdirectory("subdir3")
        directory.upload_file("file1", "data1")
        directory.upload_file("file2", "data2")
        directory.upload_file("file3", "data3")

        # Act
        list_dir = list(directory.list_directories_and_files())

        # Assert
        self.assertEqual(len(list_dir), 6)
        self.assertEqual(list_dir[0]['name'], 'subdir1')
        self.assertEqual(list_dir[0]['is_directory'], True)
        self.assertEqual(list_dir[1]['name'], 'subdir2')
        self.assertEqual(list_dir[1]['is_directory'], True)
        self.assertEqual(list_dir[2]['name'], 'subdir3')
        self.assertEqual(list_dir[2]['is_directory'], True)
        self.assertEqual(list_dir[3]['name'], 'file1')
        self.assertEqual(list_dir[3]['is_directory'], False)
        self.assertEqual(list_dir[4]['name'], 'file2')
        self.assertEqual(list_dir[4]['is_directory'], False)
        self.assertEqual(list_dir[5]['name'], 'file3')
        self.assertEqual(list_dir[5]['is_directory'], False)

    @FileSharePreparer()
    def test_list_subdirectories_and_files_include_other_data(self, storage_account_name, storage_account_key):
        self._setup(storage_account_name, storage_account_key)
        share_client = self.fsc.get_share_client(self.share_name)
        directory = share_client.create_directory('dir1')
        directory.create_subdirectory("subdir1")
        directory.create_subdirectory("subdir2")
        directory.create_subdirectory("subdir3")
        directory.upload_file("file1", "data1")
        directory.upload_file("file2", "data2")
        directory.upload_file("file3", "data3")

        # Act
        list_dir = list(directory.list_directories_and_files(include=["timestamps", "Etag", "Attributes", "PermissionKey"]))

        self.assertEqual(len(list_dir), 6)
        self.assertIsNotNone(list_dir[0].etag)
        self.assertIsNotNone(list_dir[1].file_attributes)
        self.assertIsNotNone(list_dir[1].last_access_time)
        self.assertIsNotNone(list_dir[1].last_write_time)
        self.assertIsNotNone(list_dir[2].change_time)
        self.assertIsNotNone(list_dir[2].creation_time)
        self.assertIsNotNone(list_dir[2].file_id)
        try:
            share_client.delete_share()
        except:
            pass

    @FileSharePreparer()
    def test_list_subdirectories_and_files_include_extended_info(self, storage_account_name, storage_account_key):
        self._setup(storage_account_name, storage_account_key)
        share_client = self.fsc.get_share_client(self.share_name)
        directory = share_client.create_directory('dir1')
        directory.create_subdirectory("subdir1")

        list_dir = list(directory.list_directories_and_files(include_extended_info=True))
        self.assertEqual(len(list_dir), 1)
        self.assertIsNotNone(list_dir[0].file_id)
        self.assertIsNone(list_dir[0].file_attributes)
        self.assertIsNone(list_dir[0].last_access_time)

    @FileSharePreparer()
    def test_list_subdirectories_and_files_with_prefix(self, storage_account_name, storage_account_key):
        self._setup(storage_account_name, storage_account_key)
        share_client = self.fsc.get_share_client(self.share_name)
        directory = share_client.create_directory('dir1')
        directory.create_subdirectory("subdir1")
        directory.create_subdirectory("subdir2")
        directory.create_subdirectory("subdir3")
        directory.upload_file("file1", "data1")
        directory.upload_file("file2", "data2")
        directory.upload_file("file3", "data3")

        # Act
        list_dir = list(directory.list_directories_and_files(name_starts_with="sub"))

        # Assert
        self.assertEqual(len(list_dir), 3)
        self.assertEqual(list_dir[0]['name'], 'subdir1')
        self.assertEqual(list_dir[0]['is_directory'], True)
        self.assertEqual(list_dir[1]['name'], 'subdir2')
        self.assertEqual(list_dir[1]['is_directory'], True)
        self.assertEqual(list_dir[2]['name'], 'subdir3')
        self.assertEqual(list_dir[2]['is_directory'], True)

    @FileSharePreparer()
    def test_list_subdirectories_and_files_with_snapshot(self, storage_account_name, storage_account_key):
        self._setup(storage_account_name, storage_account_key)
        share_client = self.fsc.get_share_client(self.share_name)
        directory = share_client.create_directory('dir1')
        directory.create_subdirectory("subdir1")
        directory.create_subdirectory("subdir2")
        directory.upload_file("file1", "data1")
        
        snapshot = share_client.create_snapshot()
        directory.create_subdirectory("subdir3")
        directory.upload_file("file2", "data2")
        directory.upload_file("file3", "data3")

        share_client = self.fsc.get_share_client(self.share_name, snapshot=snapshot)
        snapshot_dir = share_client.get_directory_client('dir1')

        # Act
        list_dir = list(snapshot_dir.list_directories_and_files())

        # Assert
        self.assertEqual(len(list_dir), 3)
        self.assertEqual(list_dir[0]['name'], 'subdir1')
        self.assertEqual(list_dir[0]['is_directory'], True)
        self.assertEqual(list_dir[1]['name'], 'subdir2')
        self.assertEqual(list_dir[1]['is_directory'], True)
        self.assertEqual(list_dir[2]['name'], 'file1')
        self.assertEqual(list_dir[2]['is_directory'], False)
        self.assertEqual(list_dir[2]['size'], 5)

    @FileSharePreparer()
    def test_list_nested_subdirectories_and_files(self, storage_account_name, storage_account_key):
        self._setup(storage_account_name, storage_account_key)
        share_client = self.fsc.get_share_client(self.share_name)
        directory = share_client.create_directory('dir1')
        subdir = directory.create_subdirectory("subdir1")
        subdir.create_subdirectory("subdir2")
        subdir.create_subdirectory("subdir3")
        directory.upload_file("file1", "data1")
        subdir.upload_file("file2", "data2")
        subdir.upload_file("file3", "data3")

        # Act
        list_dir = list(directory.list_directories_and_files())

        # Assert
        self.assertEqual(len(list_dir), 2)
        self.assertEqual(list_dir[0]['name'], 'subdir1')
        self.assertEqual(list_dir[0]['is_directory'], True)
        self.assertEqual(list_dir[1]['name'], 'file1')
        self.assertEqual(list_dir[1]['is_directory'], False)
        self.assertEqual(list_dir[1]['size'], 5)

    @FileSharePreparer()
    def test_delete_directory_with_existing_share(self, storage_account_name, storage_account_key):
        self._setup(storage_account_name, storage_account_key)
        share_client = self.fsc.get_share_client(self.share_name)
        directory = share_client.create_directory('dir1')

        # Act
        deleted = directory.delete_directory()

        # Assert
        self.assertIsNone(deleted)
        with self.assertRaises(ResourceNotFoundError):
            directory.get_directory_properties()

    @FileSharePreparer()
    def test_delete_directory_with_non_existing_directory(self, storage_account_name, storage_account_key):
        self._setup(storage_account_name, storage_account_key)
        share_client = self.fsc.get_share_client(self.share_name)
        directory = share_client.get_directory_client('dir1')

        # Act
        with self.assertRaises(ResourceNotFoundError):
            directory.delete_directory()

        # Assert

    @FileSharePreparer()
    def test_get_directory_properties_server_encryption(self, storage_account_name, storage_account_key):
        self._setup(storage_account_name, storage_account_key)
        share_client = self.fsc.get_share_client(self.share_name)
        directory = share_client.create_directory('dir1')

        # Act
        props = directory.get_directory_properties()

        # Assert
        self.assertIsNotNone(props)
        self.assertIsNotNone(props.etag)
        self.assertIsNotNone(props.last_modified)
        self.assertTrue(props.server_encrypted)

    @FileSharePreparer()
    def test_rename_directory(self, storage_account_name, storage_account_key):
        self._setup(storage_account_name, storage_account_key)
        share_client = self.fsc.get_share_client(self.share_name)

        source_directory = share_client.create_directory('dir1')

        # Act
        new_directory = source_directory.rename_directory('dir2')

        # Assert
        props = new_directory.get_directory_properties()
        self.assertIsNotNone(props)

    @FileSharePreparer()
    def test_rename_directory_different_directory(self, storage_account_name, storage_account_key):
        self._setup(storage_account_name, storage_account_key)
        share_client = self.fsc.get_share_client(self.share_name)

        parent_source_directory = share_client.create_directory('dir1')
        source_directory = parent_source_directory.create_subdirectory('sub1')

        dest_parent_directory = share_client.create_directory('dir2')

        # Act
        new_directory_path = dest_parent_directory.directory_path + '/sub2'
        new_directory = source_directory.rename_directory(new_directory_path)

        # Assert
        props = new_directory.get_directory_properties()
        self.assertIsNotNone(props)

    @FileSharePreparer()
    def test_rename_directory_ignore_readonly(self, storage_account_name, storage_account_key):
        self._setup(storage_account_name, storage_account_key)
        share_client = self.fsc.get_share_client(self.share_name)

        source_directory = share_client.create_directory('dir1')
        dest_directory = share_client.create_directory('dir2')
        dest_file = dest_directory.get_file_client('test')

        file_attributes = NTFSAttributes(read_only=True)
        dest_file.create_file(1024, file_attributes=file_attributes)

        # Act
        new_directory = source_directory.rename_directory(
            dest_directory.directory_path + '/' + dest_file.file_name,
            overwrite=True, ignore_read_only=True)

        # Assert
        props = new_directory.get_directory_properties()
        self.assertIsNotNone(props)
        self.assertTrue(props.is_directory)

    @FileSharePreparer()
    def test_rename_directory_file_permission(self, storage_account_name, storage_account_key):
        self._setup(storage_account_name, storage_account_key)
        share_client = self.fsc.get_share_client(self.share_name)
        file_permission_key = share_client.create_permission_for_share(TEST_FILE_PERMISSIONS)

        source_directory = share_client.create_directory('dir1')

        # Act
        new_directory = source_directory.rename_directory('dir2', file_permission=TEST_FILE_PERMISSIONS)

        # Assert
        props = new_directory.get_directory_properties()
        self.assertIsNotNone(props)
        self.assertEqual(file_permission_key, props.permission_key)

    @FileSharePreparer()
    def test_rename_directory_preserve_permission(self, storage_account_name, storage_account_key):
        self._setup(storage_account_name, storage_account_key)
        share_client = self.fsc.get_share_client(self.share_name)

        source_directory = share_client.create_directory('dir1', file_permission=TEST_FILE_PERMISSIONS)
        source_props = source_directory.get_directory_properties()
        source_permission_key = source_props.permission_key

        # Act
        new_directory = source_directory.rename_directory('dir2', file_permission='preserve')

        # Assert
        props = new_directory.get_directory_properties()
        self.assertIsNotNone(props)
        self.assertEqual(source_permission_key, props.permission_key)

    @FileSharePreparer()
    def test_rename_directory_smb_properties(self, storage_account_name, storage_account_key):
        self._setup(storage_account_name, storage_account_key)
        share_client = self.fsc.get_share_client(self.share_name)

        source_directory = share_client.create_directory('dir1')

        file_attributes = NTFSAttributes(read_only=True, directory=True)
        file_creation_time = datetime(2022, 1, 26, 10, 9, 30, 500000)
        file_last_write_time = datetime(2022, 1, 26, 10, 14, 30, 500000)
        file_change_time = datetime(2022, 3, 7, 10, 14, 30, 500000)

        # Act
        new_directory = source_directory.rename_directory(
            'dir2',
            file_attributes=file_attributes,
            file_creation_time=file_creation_time,
            file_last_write_time=file_last_write_time,
            file_change_time=file_change_time)

        # Assert
        props = new_directory.get_directory_properties()
        self.assertIsNotNone(props)
        self.assertTrue(props.is_directory)
        self.assertEqual(str(file_attributes), props.file_attributes.replace(' ', ''))
        self.assertEqual(file_creation_time, props.creation_time)
        self.assertEqual(file_last_write_time, props.last_write_time)
        self.assertEqual(file_change_time, props.change_time)

    @FileSharePreparer()
    def test_rename_directory_dest_lease(self, storage_account_name, storage_account_key):
        self._setup(storage_account_name, storage_account_key)
        share_client = self.fsc.get_share_client(self.share_name)

        source_directory = share_client.create_directory('dir1')
        dest_directory = share_client.create_directory('dir2')
        dest_file = dest_directory.upload_file('test', b'Hello World')
        lease = dest_file.acquire_lease()

        # Act
        new_directory = source_directory.rename_directory(
            dest_directory.directory_path + '/' + dest_file.file_name,
            overwrite=True, destination_lease=lease)

        # Assert
        props = new_directory.get_directory_properties()
        self.assertIsNotNone(props)
        self.assertTrue(props.is_directory)

    @pytest.mark.live_test_only
    @FileSharePreparer()
    def test_rename_directory_share_sas(self, storage_account_name, storage_account_key):
        self._setup(storage_account_name, storage_account_key)
        share_client = self.fsc.get_share_client(self.share_name)

        token = generate_share_sas(
            share_client.account_name,
            share_client.share_name,
            share_client.credential.account_key,
            expiry=datetime.utcnow() + timedelta(hours=1),
            permission=ShareSasPermissions(read=True, write=True))

        source_directory = ShareDirectoryClient(
            self.account_url(storage_account_name, 'file'),
            share_client.share_name, 'dir1',
            credential=token)
        source_directory.create_directory()

        # Act
        new_directory = source_directory.rename_directory('dir2' + '?' + token)

        # Assert
        props = new_directory.get_directory_properties()
        self.assertIsNotNone(props)


# ------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
