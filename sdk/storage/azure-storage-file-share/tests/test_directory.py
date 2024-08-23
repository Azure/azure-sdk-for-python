# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import unittest
from datetime import datetime, timedelta

import pytest
from azure.core.exceptions import ClientAuthenticationError, ResourceExistsError, ResourceNotFoundError
from azure.storage.fileshare import (
    ContentSettings,
    generate_share_sas,
    NTFSAttributes,
    ShareDirectoryClient,
    ShareSasPermissions,
    ShareServiceClient,
    StorageErrorCode,
)

from devtools_testutils import recorded_by_proxy
from devtools_testutils.storage import StorageRecordedTestCase
from settings.testcase import FileSharePreparer
# ------------------------------------------------------------------------------
TEST_FILE_PERMISSIONS = 'O:S-1-5-21-2127521184-1604012920-1887927527-21560751G:S-1-5-21-2127521184-' \
                        '1604012920-1887927527-513D:AI(A;;FA;;;SY)(A;;FA;;;BA)(A;;0x1200a9;;;' \
                        'S-1-5-21-397955417-626881126-188441444-3053964)'
TEST_INTENT = "backup"


class TestStorageDirectory(StorageRecordedTestCase):
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
    @recorded_by_proxy
    def test_create_directories(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        share_client = self.fsc.get_share_client(self.share_name)

        # Act
        created = share_client.create_directory('dir1')

        # Assert
        assert created

    @FileSharePreparer()
    @recorded_by_proxy
    def test_create_directories_with_metadata(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        share_client = self.fsc.get_share_client(self.share_name)
        metadata = {'hello': 'world', 'number': '42'}

        # Act
        directory = share_client.create_directory('dir1', metadata=metadata)

        # Assert
        md = directory.get_directory_properties().metadata
        assert md == metadata

    @FileSharePreparer()
    @recorded_by_proxy
    def test_create_directories_fail_on_exist(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        share_client = self.fsc.get_share_client(self.share_name)

        # Act
        created = share_client.create_directory('dir1')
        with pytest.raises(ResourceExistsError):
            share_client.create_directory('dir1')

        # Assert
        assert created

    @FileSharePreparer()
    @recorded_by_proxy
    def test_create_directory_set_smb_properties(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

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
        assert directory_properties is not None
        assert file_creation_time == directory_properties.creation_time
        assert file_last_write_time == directory_properties.last_write_time
        assert file_change_time == directory_properties.change_time
        assert 'ReadOnly' in directory_properties.file_attributes
        assert 'Directory' in directory_properties.file_attributes

    @FileSharePreparer()
    @recorded_by_proxy
    def test_create_directory_with_oauth(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")
        token_credential = self.get_credential(ShareServiceClient)

        self._setup(storage_account_name, storage_account_key)
        share_client = self.fsc.get_share_client(self.share_name)

        directory_client = ShareDirectoryClient(
            self.account_url(storage_account_name, 'file'),
            share_client.share_name, 'dir1',
            credential=token_credential,
            token_intent=TEST_INTENT)

        # Act
        created = directory_client.create_directory()

        # Assert
        assert created

    @FileSharePreparer()
    @recorded_by_proxy
    def test_create_directory_with_trailing_dot(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        share_client = self.fsc.get_share_client(self.share_name)
        directory_name = 'dir1'

        directory_client = ShareDirectoryClient(
            self.account_url(storage_account_name, 'file'),
            share_client.share_name, directory_name + '.',
            credential=storage_account_key,
            allow_trailing_dot=True)

        # Act
        created = directory_client.create_directory()

        # Assert
        assert created
        assert directory_client.directory_path == directory_name + '.'

    @FileSharePreparer()
    @recorded_by_proxy
    def test_create_subdirectories(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        share_client = self.fsc.get_share_client(self.share_name)
        directory = share_client.create_directory('dir1')

        # Act
        created = directory.create_subdirectory('dir2')

        # Assert
        assert created
        assert created.directory_path == 'dir1/dir2'

    @FileSharePreparer()
    @recorded_by_proxy
    def test_create_subdirectories_with_metadata(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        share_client = self.fsc.get_share_client(self.share_name)
        directory = share_client.create_directory('dir1')
        metadata = {'hello': 'world', 'number': '42'}

        # Act
        created = directory.create_subdirectory('dir2', metadata=metadata)

        # Assert
        assert created
        assert created.directory_path == 'dir1/dir2'
        sub_metadata = created.get_directory_properties().metadata
        assert sub_metadata == metadata

    @FileSharePreparer()
    @recorded_by_proxy
    def test_create_subdirectory_in_root(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        share_client = self.fsc.get_share_client(self.share_name)
        share_client.create_directory('dir1')

        # Act
        rooted_directory = share_client.get_directory_client()
        sub_dir_client = rooted_directory.get_subdirectory_client('dir2')
        sub_dir_client.create_directory()

        list_dir = list(share_client.list_directories_and_files())

        # Assert
        assert len(list_dir) == 2
        assert list_dir[0]['name'] == 'dir1'
        assert list_dir[1]['name'] == 'dir2'

    @FileSharePreparer()
    @recorded_by_proxy
    def test_create_file_in_directory(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        file_data = b'12345678' * 1024
        file_name = self.get_resource_name('file')
        share_client = self.fsc.get_share_client(self.share_name)
        directory = share_client.create_directory('dir1')

        # Act
        new_file = directory.upload_file(file_name, file_data)

        # Assert
        file_content = new_file.download_file().readall()
        assert file_content == file_data

    @FileSharePreparer()
    @recorded_by_proxy
    def test_delete_file_in_directory(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        file_name = self.get_resource_name('file')
        share_client = self.fsc.get_share_client(self.share_name)
        directory = share_client.create_directory('dir1')
        new_file = directory.upload_file(file_name, "hello world")

        # Act
        deleted = directory.delete_file(file_name)

        # Assert
        assert deleted is None
        with pytest.raises(ResourceNotFoundError):
            new_file.get_file_properties()

    @FileSharePreparer()
    @recorded_by_proxy
    def test_share_directory_exists(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        share_client = self.fsc.get_share_client(self.share_name)
        directory = share_client.create_directory('dir1')

        directory2 = share_client.get_directory_client("dir2")

        assert directory.exists()
        assert not directory2.exists()

    @FileSharePreparer()
    @recorded_by_proxy
    def test_delete_subdirectories(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        share_client = self.fsc.get_share_client(self.share_name)
        directory = share_client.create_directory('dir1')
        directory.create_subdirectory('dir2')

        # Act
        deleted = directory.delete_subdirectory('dir2')

        # Assert
        assert deleted is None
        subdir = directory.get_subdirectory_client('dir2')
        with pytest.raises(ResourceNotFoundError):
            subdir.get_directory_properties()

    @FileSharePreparer()
    @recorded_by_proxy
    def test_get_directory_properties(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        share_client = self.fsc.get_share_client(self.share_name)
        directory = share_client.create_directory('dir1')

        # Act
        props = directory.get_directory_properties()

        # Assert
        assert props is not None
        assert props.etag is not None
        assert props.last_modified is not None

    @FileSharePreparer()
    @recorded_by_proxy
    def test_get_directory_properties_oauth(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")
        token_credential = self.get_credential(ShareServiceClient)

        self._setup(storage_account_name, storage_account_key)
        share_client = self.fsc.get_share_client(self.share_name)

        directory_client = ShareDirectoryClient(
            self.account_url(storage_account_name, 'file'),
            share_client.share_name, 'dir1',
            credential=token_credential,
            token_intent=TEST_INTENT)

        # Act
        directory_client.create_directory()
        props = directory_client.get_directory_properties()

        # Assert
        assert props is not None
        assert props.etag is not None
        assert props.last_modified is not None

    @FileSharePreparer()
    @recorded_by_proxy
    def test_get_directory_properties_with_snapshot(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

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
        assert props is not None
        assert props.etag is not None
        assert props.last_modified is not None
        assert metadata == props.metadata

    @FileSharePreparer()
    @recorded_by_proxy
    def test_get_directory_properties_with_trailing_dot(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        share_client = self.fsc.get_share_client(self.share_name)
        directory = ShareDirectoryClient(
            self.account_url(storage_account_name, 'file'),
            share_client.share_name, 'dir1.',
            credential=storage_account_key,
            allow_trailing_dot=True)

        # Act
        directory.create_directory()
        props = directory.get_directory_properties()

        # Assert
        assert props is not None
        assert props.etag is not None
        assert props.last_modified is not None

    @FileSharePreparer()
    @recorded_by_proxy
    def test_get_directory_metadata_with_snapshot(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

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
        assert snapshot_metadata is not None
        assert metadata == snapshot_metadata

    @FileSharePreparer()
    @recorded_by_proxy
    def test_get_directory_properties_with_non_existing_directory(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        share_client = self.fsc.get_share_client(self.share_name)
        directory = share_client.get_directory_client('dir1')

        # Act
        with pytest.raises(ResourceNotFoundError):
            directory.get_directory_properties()

            # Assert

    @FileSharePreparer()
    @recorded_by_proxy
    def test_directory_exists(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        share_client = self.fsc.get_share_client(self.share_name)
        directory = share_client.create_directory('dir1')

        # Act
        exists = directory.get_directory_properties()

        # Assert
        assert exists

    @FileSharePreparer()
    @recorded_by_proxy
    def test_directory_not_exists(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        share_client = self.fsc.get_share_client(self.share_name)
        directory = share_client.get_directory_client('dir1')

        # Act
        with pytest.raises(ResourceNotFoundError):
            directory.get_directory_properties()

        # Assert

    @FileSharePreparer()
    @recorded_by_proxy
    def test_directory_parent_not_exists(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        share_client = self.fsc.get_share_client(self.share_name)
        directory = share_client.get_directory_client('missing1/missing2')

        # Act
        with pytest.raises(ResourceNotFoundError) as e:
            directory.get_directory_properties()

        # Assert
        assert e.value.error_code == StorageErrorCode.parent_not_found

    @FileSharePreparer()
    @recorded_by_proxy
    def test_directory_exists_with_snapshot(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

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
        assert exists

    @FileSharePreparer()
    @recorded_by_proxy
    def test_directory_not_exists_with_snapshot(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        share_client = self.fsc.get_share_client(self.share_name)
        snapshot = share_client.create_snapshot()
        directory = share_client.create_directory('dir1')

        # Act
        share_client = self.fsc.get_share_client(self.share_name, snapshot=snapshot)
        snap_dir = share_client.get_directory_client('dir1')

        with pytest.raises(ResourceNotFoundError):
            snap_dir.get_directory_properties()

        # Assert

    @FileSharePreparer()
    @recorded_by_proxy
    def test_get_set_directory_metadata(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        share_client = self.fsc.get_share_client(self.share_name)
        directory = share_client.create_directory('dir1')
        metadata = {'hello': 'world', 'number': '43'}

        # Act
        directory.set_directory_metadata(metadata)
        md = directory.get_directory_properties().metadata

        # Assert
        assert md == metadata

    @FileSharePreparer()
    @recorded_by_proxy
    def test_get_set_directory_metadata_with_oauth(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")
        token_credential = self.get_credential(ShareServiceClient)

        self._setup(storage_account_name, storage_account_key)
        share_client = self.fsc.get_share_client(self.share_name)
        directory_client = ShareDirectoryClient(
            self.account_url(storage_account_name, 'file'),
            share_client.share_name, 'dir1',
            credential=token_credential,
            token_intent=TEST_INTENT)
        metadata = {'hello': 'world', 'number': '43'}

        # Act
        directory_client.create_directory()
        directory_client.set_directory_metadata(metadata)
        md = directory_client.get_directory_properties().metadata

        # Assert
        assert md == metadata

    @FileSharePreparer()
    @recorded_by_proxy
    def test_set_directory_properties_with_empty_smb_properties(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        share_client = self.fsc.get_share_client(self.share_name)
        directory_client = share_client.create_directory('dir1')
        directory_properties_on_creation = directory_client.get_directory_properties()

        # Act
        directory_client.set_http_headers()
        directory_properties = directory_client.get_directory_properties()

        # Assert
        # Make sure set empty smb_properties doesn't change smb_properties
        assert directory_properties_on_creation.creation_time == directory_properties.creation_time
        assert directory_properties_on_creation.last_write_time == directory_properties.last_write_time
        assert directory_properties_on_creation.permission_key == directory_properties.permission_key

    @FileSharePreparer()
    @recorded_by_proxy
    def test_set_directory_properties_with_oauth(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")
        token_credential = self.get_credential(ShareServiceClient)

        self._setup(storage_account_name, storage_account_key)
        share_client = self.fsc.get_share_client(self.share_name)

        directory_client = ShareDirectoryClient(
            self.account_url(storage_account_name, 'file'),
            share_client.share_name, 'dir1',
            credential=token_credential,
            token_intent=TEST_INTENT)

        # Act
        directory_client.create_directory()
        directory_properties_on_creation = directory_client.get_directory_properties()
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
            file_change_time=new_change_time
        )
        directory_properties = directory_client.get_directory_properties()

        # Assert
        assert directory_properties is not None
        assert directory_properties.creation_time == new_creation_time
        assert directory_properties.last_write_time == new_last_write_time
        assert directory_properties.change_time == new_change_time

    @FileSharePreparer()
    @recorded_by_proxy
    def test_set_directory_properties_with_file_permission_key(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

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
        assert directory_properties is not None
        assert directory_properties.creation_time == new_creation_time
        assert directory_properties.last_write_time == new_last_write_time
        assert directory_properties.change_time == new_change_time

    @FileSharePreparer()
    @recorded_by_proxy
    def test_set_http_headers_with_trailing_dot(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        share_client = self.fsc.get_share_client(self.share_name)
        directory_client = ShareDirectoryClient(
            self.account_url(storage_account_name, 'file'),
            share_client.share_name, 'dir1.',
            credential=storage_account_key,
            allow_trailing_dot=True)
        directory_client.create_directory()

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
        assert directory_properties is not None
        assert directory_properties.creation_time == new_creation_time
        assert directory_properties.last_write_time == new_last_write_time
        assert directory_properties.change_time == new_change_time

    @FileSharePreparer()
    @recorded_by_proxy
    def test_list_subdirectories_and_files(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

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
        assert len(list_dir) == 6
        assert list_dir[0]['name'] == 'subdir1'
        assert list_dir[0]['is_directory'] == True
        assert list_dir[1]['name'] == 'subdir2'
        assert list_dir[1]['is_directory'] == True
        assert list_dir[2]['name'] == 'subdir3'
        assert list_dir[2]['is_directory'] == True
        assert list_dir[3]['name'] == 'file1'
        assert list_dir[3]['is_directory'] == False
        assert list_dir[4]['name'] == 'file2'
        assert list_dir[4]['is_directory'] == False
        assert list_dir[5]['name'] == 'file3'
        assert list_dir[5]['is_directory'] == False

    @FileSharePreparer()
    @recorded_by_proxy
    def test_list_subdirectories_and_files_oauth(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")
        token_credential = self.get_credential(ShareServiceClient)

        self._setup(storage_account_name, storage_account_key)
        share_client = self.fsc.get_share_client(self.share_name)

        directory_client = ShareDirectoryClient(
            self.account_url(storage_account_name, 'file'),
            share_client.share_name, 'dir1',
            credential=token_credential,
            token_intent=TEST_INTENT)

        # Act
        directory_client.create_directory()
        directory_client.create_subdirectory("subdir1")
        directory_client.create_subdirectory("subdir2")
        directory_client.create_subdirectory("subdir3")
        directory_client.upload_file("file1", "data1")
        directory_client.upload_file("file2", "data2")
        directory_client.upload_file("file3", "data3")

        # Act
        list_dir = list(directory_client.list_directories_and_files())

        # Assert
        assert len(list_dir) == 6
        assert list_dir[0]['name'] == 'subdir1'
        assert list_dir[0]['is_directory'] == True
        assert list_dir[1]['name'] == 'subdir2'
        assert list_dir[1]['is_directory'] == True
        assert list_dir[2]['name'] == 'subdir3'
        assert list_dir[2]['is_directory'] == True
        assert list_dir[3]['name'] == 'file1'
        assert list_dir[3]['is_directory'] == False
        assert list_dir[4]['name'] == 'file2'
        assert list_dir[4]['is_directory'] == False
        assert list_dir[5]['name'] == 'file3'
        assert list_dir[5]['is_directory'] == False

    @FileSharePreparer()
    @recorded_by_proxy
    def test_list_subdirectories_with_trailing_dot(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        share_client = self.fsc.get_share_client(self.share_name)
        directory = ShareDirectoryClient(
            self.account_url(storage_account_name, 'file'),
            share_client.share_name, 'dir1.',
            credential=storage_account_key,
            allow_trailing_dot=True)
        directory.create_directory()
        directory.create_subdirectory("subdir1.")
        directory.create_subdirectory("subdir2.")
        directory.create_subdirectory("subdir3.")
        # Act
        list_dir = list(directory.list_directories_and_files())

        # Assert
        assert len(list_dir) == 3
        assert list_dir[0]['name'] == 'subdir1.'
        assert list_dir[0]['is_directory'] == True
        assert list_dir[1]['name'] == 'subdir2.'
        assert list_dir[1]['is_directory'] == True
        assert list_dir[2]['name'] == 'subdir3.'
        assert list_dir[2]['is_directory'] == True

    @FileSharePreparer()
    @recorded_by_proxy
    def test_list_subdirectories_and_files_encoded(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        share_client = self.fsc.get_share_client(self.share_name)
        directory = share_client.create_directory('directory\uFFFE')
        directory.create_subdirectory("subdir1\uFFFE")
        directory.upload_file("file\uFFFE", "data1")

        # Act
        list_dir = list(directory.list_directories_and_files())

        # Assert
        assert len(list_dir) == 2
        assert list_dir[0]['name'] == 'subdir1\uFFFE'
        assert list_dir[0]['is_directory'] == True
        assert list_dir[1]['name'] == 'file\uFFFE'
        assert list_dir[1]['is_directory'] == False

    @FileSharePreparer()
    @recorded_by_proxy
    def test_list_subdirectories_and_files_encoded_prefix(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        share_client = self.fsc.get_share_client(self.share_name)
        directory = share_client.create_directory('\uFFFFdirectory')
        directory.create_subdirectory("\uFFFFsubdir1")
        directory.upload_file("\uFFFFfile", "data1")

        # Act
        list_dir = list(directory.list_directories_and_files(name_starts_with="\uFFFF"))

        # Assert
        assert len(list_dir) == 2
        assert list_dir[0]['name'] == '\uFFFFsubdir1'
        assert list_dir[0]['is_directory'] == True
        assert list_dir[1]['name'] == '\uFFFFfile'
        assert list_dir[1]['is_directory'] == False

    @FileSharePreparer()
    @recorded_by_proxy
    def test_list_subdirectories_and_files_include_other_data(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

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

        assert len(list_dir) == 6
        assert list_dir[0].etag is not None
        assert list_dir[1].file_attributes is not None
        assert list_dir[1].last_access_time is not None
        assert list_dir[1].last_write_time is not None
        assert list_dir[2].change_time is not None
        assert list_dir[2].creation_time is not None
        assert list_dir[2].file_id is not None
        try:
            share_client.delete_share()
        except:
            pass

    @FileSharePreparer()
    @recorded_by_proxy
    def test_list_subdirectories_and_files_include_extended_info(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        share_client = self.fsc.get_share_client(self.share_name)
        directory = share_client.create_directory('dir1')
        directory.create_subdirectory("subdir1")

        list_dir = list(directory.list_directories_and_files(include_extended_info=True))
        assert len(list_dir) == 1
        assert list_dir[0].file_id is not None
        assert list_dir[0].file_attributes is None
        assert list_dir[0].last_access_time is None

    @FileSharePreparer()
    @recorded_by_proxy
    def test_list_subdirectories_and_files_with_prefix(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

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
        assert len(list_dir) == 3
        assert list_dir[0]['name'] == 'subdir1'
        assert list_dir[0]['is_directory'] == True
        assert list_dir[1]['name'] == 'subdir2'
        assert list_dir[1]['is_directory'] == True
        assert list_dir[2]['name'] == 'subdir3'
        assert list_dir[2]['is_directory'] == True

    @FileSharePreparer()
    @recorded_by_proxy
    def test_list_subdirectories_and_files_with_snapshot(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

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
        assert len(list_dir) == 3
        assert list_dir[0]['name'] == 'subdir1'
        assert list_dir[0]['is_directory'] == True
        assert list_dir[1]['name'] == 'subdir2'
        assert list_dir[1]['is_directory'] == True
        assert list_dir[2]['name'] == 'file1'
        assert list_dir[2]['is_directory'] == False
        assert list_dir[2]['size'] == 5

    @FileSharePreparer()
    @recorded_by_proxy
    def test_list_nested_subdirectories_and_files(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

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
        assert len(list_dir) == 2
        assert list_dir[0]['name'] == 'subdir1'
        assert list_dir[0]['is_directory'] == True
        assert list_dir[1]['name'] == 'file1'
        assert list_dir[1]['is_directory'] == False
        assert list_dir[1]['size'] == 5

    @FileSharePreparer()
    @recorded_by_proxy
    def test_delete_directory_with_existing_share(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        share_client = self.fsc.get_share_client(self.share_name)
        directory = share_client.create_directory('dir1')

        # Act
        deleted = directory.delete_directory()

        # Assert
        assert deleted is None
        with pytest.raises(ResourceNotFoundError):
            directory.get_directory_properties()

    @FileSharePreparer()
    @recorded_by_proxy
    def test_delete_directory_with_existing_share_oauth(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")
        token_credential = self.get_credential(ShareServiceClient)

        self._setup(storage_account_name, storage_account_key)
        share_client = self.fsc.get_share_client(self.share_name)

        directory_client = ShareDirectoryClient(
            self.account_url(storage_account_name, 'file'),
            share_client.share_name, 'dir1',
            credential=token_credential,
            token_intent=TEST_INTENT)

        # Act
        created = directory_client.create_directory()
        deleted = directory_client.delete_directory()

        # Assert
        assert deleted is None
        with pytest.raises(ResourceNotFoundError):
            directory_client.get_directory_properties()

    @FileSharePreparer()
    @recorded_by_proxy
    def test_delete_directory_with_trailing_dot(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        share_client = self.fsc.get_share_client(self.share_name)

        directory = ShareDirectoryClient(
            self.account_url(storage_account_name, 'file'),
            share_client.share_name, 'dir1.',
            credential=storage_account_key,
            allow_trailing_dot=True)

        # Act
        directory.create_directory()
        deleted = directory.delete_directory()

        # Assert
        assert deleted is None
        with pytest.raises(ResourceNotFoundError):
            directory.get_directory_properties()

    @FileSharePreparer()
    @recorded_by_proxy
    def test_delete_directory_with_non_existing_directory(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        share_client = self.fsc.get_share_client(self.share_name)
        directory = share_client.get_directory_client('dir1')

        # Act
        with pytest.raises(ResourceNotFoundError):
            directory.delete_directory()

        # Assert

    @FileSharePreparer()
    @recorded_by_proxy
    def test_get_directory_properties_server_encryption(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        share_client = self.fsc.get_share_client(self.share_name)
        directory = share_client.create_directory('dir1')

        # Act
        props = directory.get_directory_properties()

        # Assert
        assert props is not None
        assert props.etag is not None
        assert props.last_modified is not None
        assert props.server_encrypted

    @FileSharePreparer()
    @recorded_by_proxy
    def test_rename_directory(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        share_client = self.fsc.get_share_client(self.share_name)

        source_directory = share_client.create_directory('dir1')

        # Act
        new_directory = source_directory.rename_directory('dir2')

        # Assert
        props = new_directory.get_directory_properties()
        assert props is not None

    @FileSharePreparer()
    @recorded_by_proxy
    def test_rename_directory_with_oauth(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")
        token_credential = self.get_credential(ShareServiceClient)

        self._setup(storage_account_name, storage_account_key)
        share_client = self.fsc.get_share_client(self.share_name)

        directory_client = ShareDirectoryClient(
            self.account_url(storage_account_name, 'file'),
            share_client.share_name, 'dir1',
            credential=token_credential,
            token_intent=TEST_INTENT)

        # Act
        directory_client.create_directory()
        new_directory = directory_client.rename_directory('dir2')

        # Assert
        props = new_directory.get_directory_properties()
        assert props is not None

    @FileSharePreparer()
    @recorded_by_proxy
    def test_rename_directory_different_directory(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

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
        assert props is not None

    @FileSharePreparer()
    @recorded_by_proxy
    def test_rename_directory_ignore_readonly(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

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
        assert props is not None
        assert props.is_directory

    @FileSharePreparer()
    @recorded_by_proxy
    def test_rename_directory_file_permission(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        share_client = self.fsc.get_share_client(self.share_name)
        file_permission_key = share_client.create_permission_for_share(TEST_FILE_PERMISSIONS)

        source_directory = share_client.create_directory('dir1')

        # Act
        new_directory = source_directory.rename_directory('dir2', file_permission=TEST_FILE_PERMISSIONS)

        # Assert
        props = new_directory.get_directory_properties()
        assert props is not None
        assert file_permission_key == props.permission_key

    @FileSharePreparer()
    @recorded_by_proxy
    def test_rename_directory_preserve_permission(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        share_client = self.fsc.get_share_client(self.share_name)

        source_directory = share_client.create_directory('dir1', file_permission=TEST_FILE_PERMISSIONS)
        source_props = source_directory.get_directory_properties()
        source_permission_key = source_props.permission_key

        # Act
        new_directory = source_directory.rename_directory('dir2', file_permission='preserve')

        # Assert
        props = new_directory.get_directory_properties()
        assert props is not None
        assert source_permission_key == props.permission_key

    @FileSharePreparer()
    @recorded_by_proxy
    def test_rename_directory_smb_properties(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

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
        assert props is not None
        assert props.is_directory
        assert str(file_attributes), props.file_attributes.replace(' ' == '')
        assert file_creation_time == props.creation_time
        assert file_last_write_time == props.last_write_time
        assert file_change_time == props.change_time

    @FileSharePreparer()
    @recorded_by_proxy
    def test_rename_directory_dest_lease(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        share_client = self.fsc.get_share_client(self.share_name)

        source_directory = share_client.create_directory('dir1')
        dest_directory = share_client.create_directory('dir2')
        dest_file = dest_directory.upload_file('test', b'Hello World')
        lease = dest_file.acquire_lease(lease_id='00000000-1111-2222-3333-444444444444')

        # Act
        new_directory = source_directory.rename_directory(
            dest_directory.directory_path + '/' + dest_file.file_name,
            overwrite=True, destination_lease=lease)

        # Assert
        props = new_directory.get_directory_properties()
        assert props is not None
        assert props.is_directory

    @FileSharePreparer()
    @recorded_by_proxy
    def test_rename_directory_share_sas(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        share_client = self.fsc.get_share_client(self.share_name)

        token = self.generate_sas(
            generate_share_sas,
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
        assert props is not None

    @FileSharePreparer()
    @recorded_by_proxy
    def test_rename_directory_trailing_dot(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        share_client = self.fsc.get_share_client(self.share_name)
        dest_dir_name = 'dir2' + '.'

        directory_client = ShareDirectoryClient(
            self.account_url(storage_account_name, 'file'),
            share_client.share_name, 'dir1.',
            credential=storage_account_key,
            allow_trailing_dot=True,
            allow_source_trailing_dot=True)

        # Act
        directory_client.create_directory()
        new_directory_client = directory_client.rename_directory(dest_dir_name)

        # Assert
        assert new_directory_client.directory_path == dest_dir_name

    @FileSharePreparer()
    @recorded_by_proxy
    def test_storage_account_audience_directory_client(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        self._setup(storage_account_name, storage_account_key)
        share_client = self.fsc.get_share_client(self.share_name)
        directory_client = ShareDirectoryClient(
            self.account_url(storage_account_name, 'file'),
            share_client.share_name, 'dir1.',
            credential=storage_account_key
        )
        directory_client.exists()

        # Act
        token_credential = self.get_credential(ShareServiceClient)
        directory_client = ShareDirectoryClient(
            self.account_url(storage_account_name, 'file'),
            share_client.share_name, 'dir1.',
            credential=token_credential,
            token_intent=TEST_INTENT,
            audience=f'https://{storage_account_name}.file.core.windows.net'
        )

        # Assert
        response = directory_client.exists()
        assert response is not None

    @FileSharePreparer()
    @recorded_by_proxy
    def test_bad_audience_directory_client(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        self._setup(storage_account_name, storage_account_key)
        share_client = self.fsc.get_share_client(self.share_name)
        directory_client = ShareDirectoryClient(
            self.account_url(storage_account_name, 'file'),
            share_client.share_name, 'dir1.',
            credential=storage_account_key
        )
        directory_client.exists()

        # Act
        token_credential = self.get_credential(ShareServiceClient)
        directory_client = ShareDirectoryClient(
            self.account_url(storage_account_name, 'file'),
            share_client.share_name, 'dir1.',
            credential=token_credential,
            token_intent=TEST_INTENT,
            audience=f'https://badaudience.file.core.windows.net'
        )

        # Assert
        directory_client.exists()

    @FileSharePreparer()
    @recorded_by_proxy
    def test_file_permission_format_directory(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        share_client = self.fsc.get_share_client(self.share_name)
        user_given_permission_sddl = ("O:S-1-5-21-2127521184-1604012920-1887927527-21560751G:S-1-5-21-2127521184-"
                                      "1604012920-1887927527-513D:AI(A;;FA;;;SY)(A;;FA;;;BA)(A;;0x1200a9;;;"
                                      "S-1-5-21-397955417-626881126-188441444-3053964)S:NO_ACCESS_CONTROL")
        user_given_permission_binary = ("AQAUhGwAAACIAAAAAAAAABQAAAACAFgAAwAAAAAAFAD/AR8AAQEAAAAAAAUSAAAAAAAYAP8BHw"
                                        "ABAgAAAAAABSAAAAAgAgAAAAAkAKkAEgABBQAAAAAABRUAAABZUbgXZnJdJWRjOwuMmS4AAQUA"
                                        "AAAAAAUVAAAAoGXPfnhLm1/nfIdwr/1IAQEFAAAAAAAFFQAAAKBlz354S5tf53yHcAECAAA=")

        directory_client = share_client.create_directory(
            'dir1',
            file_permission=user_given_permission_binary,
            file_permission_format="binary"
        )

        props = directory_client.get_directory_properties()
        assert props is not None
        assert props.permission_key is not None

        directory_client.set_http_headers(
            file_permission=user_given_permission_binary,
            file_permission_format="binary"
        )

        props = directory_client.get_directory_properties()
        assert props is not None
        assert props.permission_key is not None

        server_returned_permission = share_client.get_permission_for_share(
            props.permission_key,
            file_permission_format="sddl"
        )
        assert server_returned_permission == user_given_permission_sddl

        new_directory_client = directory_client.rename_directory(
            'dir2',
            file_permission=user_given_permission_binary,
            file_permission_format="binary"
        )
        props = new_directory_client.get_directory_properties()
        assert props is not None
        assert props.permission_key is not None

        server_returned_permission = share_client.get_permission_for_share(
            props.permission_key,
            file_permission_format="binary"
        )
        assert server_returned_permission == user_given_permission_binary

        new_directory_client.delete_directory()

# ------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
