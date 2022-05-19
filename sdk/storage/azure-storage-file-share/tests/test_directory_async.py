# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import unittest
import asyncio
import pytest
from datetime import datetime, timedelta

from azure.core.exceptions import ResourceNotFoundError, ResourceExistsError
from azure.core.pipeline.transport import AioHttpTransport
from multidict import CIMultiDict, CIMultiDictProxy
from azure.storage.fileshare import (
    generate_share_sas,
    NTFSAttributes,
    ShareSasPermissions,
    StorageErrorCode
)
from azure.storage.fileshare.aio import ShareDirectoryClient, ShareServiceClient
from settings.testcase import FileSharePreparer
from devtools_testutils.storage.aio import AsyncStorageTestCase

# ------------------------------------------------------------------------------
TEST_FILE_PERMISSIONS = 'O:S-1-5-21-2127521184-1604012920-1887927527-21560751G:S-1-5-21-2127521184-' \
                        '1604012920-1887927527-513D:AI(A;;FA;;;SY)(A;;FA;;;BA)(A;;0x1200a9;;;' \
                        'S-1-5-21-397955417-626881126-188441444-3053964)'

class AiohttpTestTransport(AioHttpTransport):
    """Workaround to vcrpy bug: https://github.com/kevin1024/vcrpy/pull/461
    """
    async def send(self, request, **config):
        response = await super(AiohttpTestTransport, self).send(request, **config)
        if not isinstance(response.headers, CIMultiDictProxy):
            response.headers = CIMultiDictProxy(CIMultiDict(response.internal_response.headers))
            response.content_type = response.headers.get("content-type")
        return response


class StorageDirectoryTest(AsyncStorageTestCase):
    # --Helpers-----------------------------------------------------------------
    async def _setup(self, storage_account_name, storage_account_key):
        url = self.account_url(storage_account_name, "file")
        credential = storage_account_key
        self.fsc = ShareServiceClient(url, credential=credential, transport=AiohttpTestTransport())
        self.share_name = self.get_resource_name('utshare')
        if not self.is_playback():
            try:
                await self.fsc.create_share(self.share_name)
            except:
                pass

    def _teardown(self, FILE_PATH):
        if os.path.isfile(FILE_PATH):
            try:
                os.remove(FILE_PATH)
            except:
                pass

    # --Test cases for directories ----------------------------------------------
    @FileSharePreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_create_directories_async(self, storage_account_name, storage_account_key):
        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        share_client = self.fsc.get_share_client(self.share_name)

        # Act
        created = await share_client.create_directory('dir1')

        # Assert
        self.assertTrue(created)

    @FileSharePreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_create_directories_with_metadata_async(self, storage_account_name, storage_account_key):
        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        share_client = self.fsc.get_share_client(self.share_name)
        metadata = {'hello': 'world', 'number': '42'}

        # Act
        directory = await share_client.create_directory('dir1', metadata=metadata)

        # Assert
        props = await directory.get_directory_properties()
        self.assertDictEqual(props.metadata, metadata)

    @FileSharePreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_create_directories_fail_on_exist_async(self, storage_account_name, storage_account_key):
        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        share_client = self.fsc.get_share_client(self.share_name)

        # Act
        created = await share_client.create_directory('dir1')
        with self.assertRaises(ResourceExistsError):
            await share_client.create_directory('dir1')

        # Assert
        self.assertTrue(created)

    @FileSharePreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_create_directory_set_smb_properties(self, storage_account_name, storage_account_key):
        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        share_client = self.fsc.get_share_client(self.share_name)

        directory_client = share_client.get_directory_client('dir1')
        file_attributes = NTFSAttributes(read_only=True, directory=True)
        file_creation_time = file_last_write_time = file_change_time = datetime(2022, 3, 10, 10, 14, 30, 500000)

        # Act
        await directory_client.create_directory(
            file_attributes=file_attributes,
            file_creation_time=file_creation_time,
            file_last_write_time=file_last_write_time,
            file_change_time=file_change_time)
        directory_properties = await directory_client.get_directory_properties()

        # Assert
        self.assertIsNotNone(directory_properties)
        self.assertEqual(file_creation_time, directory_properties.creation_time)
        self.assertEqual(file_last_write_time, directory_properties.last_write_time)
        self.assertEqual(file_change_time, directory_properties.change_time)
        self.assertIn('ReadOnly', directory_properties.file_attributes)
        self.assertIn('Directory', directory_properties.file_attributes)

    @FileSharePreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_create_subdirectories_async(self, storage_account_name, storage_account_key):
        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        share_client = self.fsc.get_share_client(self.share_name)
        directory = await share_client.create_directory('dir1')

        # Act
        created = await directory.create_subdirectory('dir2')

        # Assert
        self.assertTrue(created)
        self.assertEqual(created.directory_path, 'dir1/dir2')


    @FileSharePreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_create_subdirectories_with_metadata_async(self, storage_account_name, storage_account_key):
        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        share_client = self.fsc.get_share_client(self.share_name)
        directory = await share_client.create_directory('dir1')
        metadata = {'hello': 'world', 'number': '42'}

        # Act
        created = await directory.create_subdirectory('dir2', metadata=metadata)

        # Assert
        self.assertTrue(created)
        self.assertEqual(created.directory_path, 'dir1/dir2')
        properties = await created.get_directory_properties()
        self.assertEqual(properties.metadata, metadata)

    @FileSharePreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_create_file_in_directory_async(self, storage_account_name, storage_account_key):
        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        file_data = b'12345678' * 1024
        file_name = self.get_resource_name('file')
        share_client = self.fsc.get_share_client(self.share_name)
        directory = await share_client.create_directory('dir1')

        # Act
        new_file = await directory.upload_file(file_name, file_data)

        # Assert
        file_content = await new_file.download_file()
        file_content = await file_content.readall()
        self.assertEqual(file_content, file_data)

    @FileSharePreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_delete_file_in_directory_async(self, storage_account_name, storage_account_key):
        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        file_name = self.get_resource_name('file')
        share_client = self.fsc.get_share_client(self.share_name)
        directory = await share_client.create_directory('dir1')
        new_file = await directory.upload_file(file_name, "hello world")

        # Act
        deleted = await directory.delete_file(file_name)

        # Assert
        self.assertIsNone(deleted)
        with self.assertRaises(ResourceNotFoundError):
            await new_file.get_file_properties()

    @FileSharePreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_delete_subdirectories_async(self, storage_account_name, storage_account_key):
        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        share_client = self.fsc.get_share_client(self.share_name)
        directory = await share_client.create_directory('dir1')
        await directory.create_subdirectory('dir2')

        # Act
        deleted = await directory.delete_subdirectory('dir2')

        # Assert
        self.assertIsNone(deleted)
        subdir = directory.get_subdirectory_client('dir2')
        with self.assertRaises(ResourceNotFoundError):
            await subdir.get_directory_properties()

    @FileSharePreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_get_directory_properties_async(self, storage_account_name, storage_account_key):
        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        share_client = self.fsc.get_share_client(self.share_name)
        directory = await share_client.create_directory('dir1')

        # Act
        props = await directory.get_directory_properties()

        # Assert
        self.assertIsNotNone(props)
        self.assertIsNotNone(props.etag)
        self.assertIsNotNone(props.last_modified)

    @FileSharePreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_get_directory_properties_with_snapshot_async(self, storage_account_name, storage_account_key):
        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        share_client = self.fsc.get_share_client(self.share_name)
        metadata = {"test1": "foo", "test2": "bar"}
        directory = await share_client.create_directory('dir1', metadata=metadata)
        snapshot1 = await share_client.create_snapshot()
        metadata2 = {"test100": "foo100", "test200": "bar200"}
        await directory.set_directory_metadata(metadata2)

        # Act
        share_client = self.fsc.get_share_client(self.share_name, snapshot=snapshot1)
        snap_dir = share_client.get_directory_client('dir1')
        props = await snap_dir.get_directory_properties()

        # Assert
        self.assertIsNotNone(props)
        self.assertIsNotNone(props.etag)
        self.assertIsNotNone(props.last_modified)
        self.assertDictEqual(metadata, props.metadata)

    @FileSharePreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_get_directory_metadata_with_snapshot_async(self, storage_account_name, storage_account_key):
        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        share_client = self.fsc.get_share_client(self.share_name)
        metadata = {"test1": "foo", "test2": "bar"}
        directory = await share_client.create_directory('dir1', metadata=metadata)
        snapshot1 = await share_client.create_snapshot()
        metadata2 = {"test100": "foo100", "test200": "bar200"}
        await directory.set_directory_metadata(metadata2)

        # Act
        share_client = self.fsc.get_share_client(self.share_name, snapshot=snapshot1)
        snap_dir = share_client.get_directory_client('dir1')
        snapshot_props = await snap_dir.get_directory_properties()

        # Assert
        self.assertIsNotNone(snapshot_props.metadata)
        self.assertDictEqual(metadata, snapshot_props.metadata)

    @FileSharePreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_get_directory_properties_with_non_existing_directory_async(self, storage_account_name, storage_account_key):
        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        share_client = self.fsc.get_share_client(self.share_name)
        directory = share_client.get_directory_client('dir1')

        # Act
        with self.assertRaises(ResourceNotFoundError):
            await directory.get_directory_properties()

            # Assert

    @FileSharePreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_share_directory_exists_async(self, storage_account_name, storage_account_key):
        await self._setup(storage_account_name, storage_account_key)
        share_client = self.fsc.get_share_client(self.share_name)
        directory = await share_client.create_directory('dir1')

        directory2 = share_client.get_directory_client("dir2")

        exists = await directory.exists()
        exists2 = await directory2.exists()
        self.assertTrue(exists)
        self.assertFalse(exists2)

    @FileSharePreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_directory_exists_async(self, storage_account_name, storage_account_key):
        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        share_client = self.fsc.get_share_client(self.share_name)
        directory = await share_client.create_directory('dir1')

        # Act
        exists = await directory.get_directory_properties()

        # Assert
        self.assertTrue(exists)

    @FileSharePreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_directory_not_exists_async(self, storage_account_name, storage_account_key):
        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        share_client = self.fsc.get_share_client(self.share_name)
        directory = share_client.get_directory_client('dir1')

        # Act
        with self.assertRaises(ResourceNotFoundError):
            await directory.get_directory_properties()

        # Assert

    @FileSharePreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_directory_parent_not_exists_async(self, storage_account_name, storage_account_key):
        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        share_client = self.fsc.get_share_client(self.share_name)
        directory = share_client.get_directory_client('missing1/missing2')

        # Act
        with self.assertRaises(ResourceNotFoundError) as e:
            await directory.get_directory_properties()

        # Assert
        self.assertEqual(e.exception.error_code, StorageErrorCode.parent_not_found)

    @FileSharePreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_directory_exists_with_snapshot_async(self, storage_account_name, storage_account_key):
        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        share_client = self.fsc.get_share_client(self.share_name)
        directory = await share_client.create_directory('dir1')
        snapshot = await share_client.create_snapshot()
        await directory.delete_directory()

        # Act
        share_client = self.fsc.get_share_client(self.share_name, snapshot=snapshot)
        snap_dir = share_client.get_directory_client('dir1')
        exists = await snap_dir.get_directory_properties()

        # Assert
        self.assertTrue(exists)

    @FileSharePreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_directory_not_exists_with_snapshot_async(self, storage_account_name, storage_account_key):
        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        share_client = self.fsc.get_share_client(self.share_name)
        snapshot = await share_client.create_snapshot()
        directory = await share_client.create_directory('dir1')

        # Act
        share_client = self.fsc.get_share_client(self.share_name, snapshot=snapshot)
        snap_dir = share_client.get_directory_client('dir1')

        with self.assertRaises(ResourceNotFoundError):
            await snap_dir.get_directory_properties()

        # Assert

    @FileSharePreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_get_set_directory_metadata_async(self, storage_account_name, storage_account_key):
        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        share_client = self.fsc.get_share_client(self.share_name)
        directory = await share_client.create_directory('dir1')
        metadata = {'hello': 'world', 'number': '43'}

        # Act
        await directory.set_directory_metadata(metadata)
        props = await directory.get_directory_properties()

        # Assert
        self.assertDictEqual(props.metadata, metadata)

    @FileSharePreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_set_directory_properties_with_empty_smb_properties(self, storage_account_name, storage_account_key):
        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        share_client = self.fsc.get_share_client(self.share_name)
        directory_client = await share_client.create_directory('dir1')
        directory_properties_on_creation = await directory_client.get_directory_properties()

        # Act
        await directory_client.set_http_headers()
        directory_properties = await directory_client.get_directory_properties()

        # Assert
        # Make sure set empty smb_properties doesn't change smb_properties
        self.assertEqual(directory_properties_on_creation.creation_time,
                          directory_properties.creation_time)
        self.assertEqual(directory_properties_on_creation.last_write_time,
                          directory_properties.last_write_time)
        self.assertEqual(directory_properties_on_creation.permission_key,
                          directory_properties.permission_key)

    @FileSharePreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_set_directory_properties_with_file_permission_key(self, storage_account_name, storage_account_key):
        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        share_client = self.fsc.get_share_client(self.share_name)
        directory_client = await share_client.create_directory('dir1')

        directory_properties_on_creation = await directory_client.get_directory_properties()
        permission_key = directory_properties_on_creation.permission_key
        last_write_time = directory_properties_on_creation.last_write_time
        creation_time = directory_properties_on_creation.creation_time
        change_time = directory_properties_on_creation.change_time

        new_last_write_time = last_write_time + timedelta(hours=1)
        new_creation_time = creation_time + timedelta(hours=1)
        new_change_time = change_time + timedelta(hours=1)

        # Act
        await directory_client.set_http_headers(
            file_attributes='None',
            file_creation_time=new_creation_time,
            file_last_write_time=new_last_write_time,
            file_change_time=new_change_time,
            permission_key=permission_key)
        directory_properties = await directory_client.get_directory_properties()

        # Assert
        self.assertIsNotNone(directory_properties)
        self.assertEqual(directory_properties.creation_time, new_creation_time)
        self.assertEqual(directory_properties.last_write_time, new_last_write_time)

    @FileSharePreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_list_subdirectories_and_files_async(self, storage_account_name, storage_account_key):
        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        share_client = self.fsc.get_share_client(self.share_name)
        directory = await share_client.create_directory('dir1')
        await asyncio.gather(
            directory.create_subdirectory("subdir1"),
            directory.create_subdirectory("subdir2"),
            directory.create_subdirectory("subdir3"),
            directory.upload_file("file1", "data1"),
            directory.upload_file("file2", "data2"),
            directory.upload_file("file3", "data3"))

        # Act
        list_dir = []
        async for d in directory.list_directories_and_files():
            list_dir.append(d)

        # Assert
        self.assertEqual(len(list_dir), 6)
        self.assertEqual(len(list_dir), 6)
        self.assertEqual(list_dir[0]['name'], 'subdir1')
        self.assertEqual(list_dir[0]['is_directory'], True)
        self.assertEqual(list_dir[1]['name'], 'subdir2')
        self.assertEqual(list_dir[1]['is_directory'], True)
        self.assertEqual(list_dir[2]['name'], 'subdir3')
        self.assertEqual(list_dir[2]['is_directory'], True)
        self.assertEqual(list_dir[3]['name'], 'file1')
        self.assertEqual(list_dir[3]['is_directory'], False)
        self.assertEqual(list_dir[3]['size'], 5)
        self.assertEqual(list_dir[4]['name'], 'file2')
        self.assertEqual(list_dir[4]['is_directory'], False)
        self.assertEqual(list_dir[4]['size'], 5)
        self.assertEqual(list_dir[5]['name'], 'file3')
        self.assertEqual(list_dir[5]['is_directory'], False)
        self.assertEqual(list_dir[5]['size'], 5)

    @FileSharePreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_list_subdirectories_and_files_include_other_data_async(self, storage_account_name, storage_account_key):
        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        share_client = self.fsc.get_share_client(self.share_name)
        directory = await share_client.create_directory('dir1')
        await asyncio.gather(
            directory.create_subdirectory("subdir1"),
            directory.create_subdirectory("subdir2"),
            directory.create_subdirectory("subdir3"),
            directory.upload_file("file1", "data1"),
            directory.upload_file("file2", "data2"),
            directory.upload_file("file3", "data3"))

        # Act
        list_dir = []
        async for d in directory.list_directories_and_files(include=["timestamps", "Etag", "Attributes", "PermissionKey"]):
            list_dir.append(d)

        self.assertEqual(len(list_dir), 6)
        self.assertIsNotNone(list_dir[0].etag)
        self.assertIsNotNone(list_dir[1].file_attributes)
        self.assertIsNotNone(list_dir[1].last_access_time)
        self.assertIsNotNone(list_dir[1].last_write_time)
        self.assertIsNotNone(list_dir[2].change_time)
        self.assertIsNotNone(list_dir[2].creation_time)
        self.assertIsNotNone(list_dir[2].file_id)

        try:
            await share_client.delete_share()
        except:
            pass

    @FileSharePreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_list_subdirectories_and_files_include_extended_info_async(self, storage_account_name, storage_account_key):
        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        share_client = self.fsc.get_share_client(self.share_name)
        directory = await share_client.create_directory('dir1')
        await asyncio.gather(
            directory.create_subdirectory("subdir1"))

        # Act
        list_dir = []
        async for d in directory.list_directories_and_files(include_extended_info=True):
            list_dir.append(d)

        self.assertEqual(len(list_dir), 1)
        self.assertIsNotNone(list_dir[0].file_id)
        self.assertIsNone(list_dir[0].file_attributes)
        self.assertIsNone(list_dir[0].last_access_time)

    @FileSharePreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_list_subdirectories_and_files_with_prefix_async(self, storage_account_name, storage_account_key):
        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        share_client = self.fsc.get_share_client(self.share_name)
        directory = await share_client.create_directory('dir1')
        await asyncio.gather(
            directory.create_subdirectory("subdir1"),
            directory.create_subdirectory("subdir2"),
            directory.create_subdirectory("subdir3"),
            directory.upload_file("file1", "data1"),
            directory.upload_file("file2", "data2"),
            directory.upload_file("file3", "data3"))

        # Act
        list_dir = []
        async for d in directory.list_directories_and_files(name_starts_with="sub"):
            list_dir.append(d)

        # Assert
        self.assertEqual(len(list_dir), 3)
        self.assertEqual(list_dir[0]['name'], 'subdir1')
        self.assertEqual(list_dir[0]['is_directory'], True)
        self.assertEqual(list_dir[1]['name'], 'subdir2')
        self.assertEqual(list_dir[1]['is_directory'], True)
        self.assertEqual(list_dir[2]['name'], 'subdir3')
        self.assertEqual(list_dir[2]['is_directory'], True)

    @FileSharePreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_list_subdirectories_and_files_with_snapshot_async(self, storage_account_name, storage_account_key):
        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        share_client = self.fsc.get_share_client(self.share_name)
        directory = await share_client.create_directory('dir1')
        await asyncio.gather(
            directory.create_subdirectory("subdir1"),
            directory.create_subdirectory("subdir2"),
            directory.upload_file("file1", "data1"))
        
        snapshot = await share_client.create_snapshot()
        await asyncio.gather(
            directory.create_subdirectory("subdir3"),
            directory.upload_file("file2", "data2"),
            directory.upload_file("file3", "data3"))

        share_client = self.fsc.get_share_client(self.share_name, snapshot=snapshot)
        snapshot_dir = share_client.get_directory_client('dir1')

        # Act
        list_dir = []
        async for d in snapshot_dir.list_directories_and_files():
            list_dir.append(d)

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
    @AsyncStorageTestCase.await_prepared_test
    async def test_list_nested_subdirectories_and_files_async(self, storage_account_name, storage_account_key):
        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        share_client = self.fsc.get_share_client(self.share_name)
        directory = await share_client.create_directory('dir1')
        subdir = await directory.create_subdirectory("subdir1")
        await subdir.create_subdirectory("subdir2")
        await subdir.create_subdirectory("subdir3")
        await asyncio.gather(
            directory.upload_file("file1", "data1"),
            subdir.upload_file("file2", "data2"),
            subdir.upload_file("file3", "data3"))

        # Act
        list_dir = []
        async for d in directory.list_directories_and_files():
            list_dir.append(d)

        # Assert
        self.assertEqual(len(list_dir), 2)
        self.assertEqual(list_dir[0]['name'], 'subdir1')
        self.assertEqual(list_dir[0]['is_directory'], True)
        self.assertEqual(list_dir[1]['name'], 'file1')
        self.assertEqual(list_dir[1]['is_directory'], False)
        self.assertEqual(list_dir[1]['size'], 5)

    @FileSharePreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_delete_directory_with_existing_share_async(self, storage_account_name, storage_account_key):
        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        share_client = self.fsc.get_share_client(self.share_name)
        directory = await share_client.create_directory('dir1')

        # Act
        deleted = await directory.delete_directory()

        # Assert
        self.assertIsNone(deleted)
        with self.assertRaises(ResourceNotFoundError):
            await directory.get_directory_properties()

    @FileSharePreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_delete_directory_with_non_existing_directory_async(self, storage_account_name, storage_account_key):
        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        share_client = self.fsc.get_share_client(self.share_name)
        directory = share_client.get_directory_client('dir1')

        # Act
        with self.assertRaises(ResourceNotFoundError):
            await directory.delete_directory()

        # Assert

    @FileSharePreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_get_directory_properties_server_encryption_async(self, storage_account_name, storage_account_key):
        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        share_client = self.fsc.get_share_client(self.share_name)
        directory = await share_client.create_directory('dir1')

        # Act
        props = await directory.get_directory_properties()

        # Assert
        self.assertIsNotNone(props)
        self.assertIsNotNone(props.etag)
        self.assertIsNotNone(props.last_modified)
        self.assertTrue(props.server_encrypted)

    @FileSharePreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_rename_directory(self, storage_account_name, storage_account_key):
        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        share_client = self.fsc.get_share_client(self.share_name)

        source_directory = await share_client.create_directory('dir1')

        # Act
        new_directory = await source_directory.rename_directory('dir2')

        # Assert
        props = await new_directory.get_directory_properties()
        self.assertIsNotNone(props)

    @FileSharePreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_rename_directory_different_directory(self, storage_account_name, storage_account_key):
        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        share_client = self.fsc.get_share_client(self.share_name)

        parent_source_directory = await share_client.create_directory('dir1')
        source_directory = await parent_source_directory.create_subdirectory('sub1')

        dest_parent_directory = await share_client.create_directory('dir2')

        # Act
        new_directory_path = dest_parent_directory.directory_path + '/sub2'
        new_directory = await source_directory.rename_directory(new_directory_path)

        # Assert
        props = await new_directory.get_directory_properties()
        self.assertIsNotNone(props)

    @FileSharePreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_rename_directory_ignore_readonly(self, storage_account_name, storage_account_key):
        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        share_client = self.fsc.get_share_client(self.share_name)

        source_directory = await share_client.create_directory('dir1')
        dest_directory = await share_client.create_directory('dir2')
        dest_file = dest_directory.get_file_client('test')

        file_attributes = NTFSAttributes(read_only=True)
        await dest_file.create_file(1024, file_attributes=file_attributes)

        # Act
        new_directory = await source_directory.rename_directory(
            dest_directory.directory_path + '/' + dest_file.file_name,
            overwrite=True, ignore_read_only=True)

        # Assert
        props = await new_directory.get_directory_properties()
        self.assertIsNotNone(props)
        self.assertTrue(props.is_directory)

    @FileSharePreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_rename_directory_file_permission(self, storage_account_name, storage_account_key):
        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        share_client = self.fsc.get_share_client(self.share_name)
        file_permission_key = await share_client.create_permission_for_share(TEST_FILE_PERMISSIONS)

        source_directory = await share_client.create_directory('dir1')

        # Act
        new_directory = await source_directory.rename_directory('dir2', file_permission=TEST_FILE_PERMISSIONS)

        # Assert
        props = await new_directory.get_directory_properties()
        self.assertIsNotNone(props)
        self.assertEqual(file_permission_key, props.permission_key)

    @FileSharePreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_rename_directory_preserve_permission(self, storage_account_name, storage_account_key):
        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        share_client = self.fsc.get_share_client(self.share_name)

        source_directory = await share_client.create_directory('dir1', file_permission=TEST_FILE_PERMISSIONS)
        source_props = await source_directory.get_directory_properties()
        source_permission_key = source_props.permission_key

        # Act
        new_directory = await source_directory.rename_directory('dir2', file_permission='preserve')

        # Assert
        props = await new_directory.get_directory_properties()
        self.assertIsNotNone(props)
        self.assertEqual(source_permission_key, props.permission_key)

    @FileSharePreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_rename_directory_smb_properties(self, storage_account_name, storage_account_key):
        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        share_client = self.fsc.get_share_client(self.share_name)

        source_directory = await share_client.create_directory('dir1')

        file_attributes = NTFSAttributes(read_only=True, directory=True)
        file_creation_time = datetime(2022, 1, 26, 10, 9, 30, 500000)
        file_last_write_time = datetime(2022, 1, 26, 10, 14, 30, 500000)
        file_change_time = datetime(2022, 3, 7, 10, 14, 30, 500000)

        # Act
        new_directory = await source_directory.rename_directory(
            'dir2',
            file_attributes=file_attributes,
            file_creation_time=file_creation_time,
            file_last_write_time=file_last_write_time,
            file_change_time=file_change_time)

        # Assert
        props = await new_directory.get_directory_properties()
        self.assertIsNotNone(props)
        self.assertTrue(props.is_directory)
        self.assertEqual(str(file_attributes), props.file_attributes.replace(' ', ''))
        self.assertEqual(file_creation_time, props.creation_time)
        self.assertEqual(file_last_write_time, props.last_write_time)
        self.assertEqual(file_change_time, props.change_time)

    @FileSharePreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_rename_directory_dest_lease(self, storage_account_name, storage_account_key):
        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        share_client = self.fsc.get_share_client(self.share_name)

        source_directory = await share_client.create_directory('dir1')
        dest_directory = await share_client.create_directory('dir2')
        dest_file = await dest_directory.upload_file('test', b'Hello World')
        lease = await dest_file.acquire_lease()

        # Act
        new_directory = await source_directory.rename_directory(
            dest_directory.directory_path + '/' + dest_file.file_name,
            overwrite=True, destination_lease=lease)

        # Assert
        props = await new_directory.get_directory_properties()
        self.assertIsNotNone(props)
        self.assertTrue(props.is_directory)

    @pytest.mark.live_test_only
    @FileSharePreparer()
    @AsyncStorageTestCase.await_prepared_test
    async def test_rename_directory_share_sas(self, storage_account_name, storage_account_key):
        # Arrange
        await self._setup(storage_account_name, storage_account_key)
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
        await source_directory.create_directory()

        # Act
        new_directory = await source_directory.rename_directory('dir2' + '?' + token)

        # Assert
        props = await new_directory.get_directory_properties()
        self.assertIsNotNone(props)

# ------------------------------------------------------------------------------
