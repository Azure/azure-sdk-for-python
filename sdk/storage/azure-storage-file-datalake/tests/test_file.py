# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import unittest
from datetime import datetime, timedelta

from azure.core.exceptions import HttpResponseError, ResourceExistsError, ResourceNotFoundError, \
    ClientAuthenticationError
from azure.storage.filedatalake import ContentSettings, generate_account_sas, generate_file_sas, \
    ResourceTypes, AccountSasPermissions, \
    DataLakeFileClient, FileSystemClient, DataLakeDirectoryClient, FileSasPermissions
from azure.storage.filedatalake import DataLakeServiceClient
from azure.storage.filedatalake._generated.models import StorageErrorException
from testcase import (
    StorageTestCase,
    record,
    TestMode
)

# ------------------------------------------------------------------------------
TEST_DIRECTORY_PREFIX = 'directory'
TEST_FILE_PREFIX = 'file'
# ------------------------------------------------------------------------------


class FileTest(StorageTestCase):
    def setUp(self):
        super(FileTest, self).setUp()
        url = self._get_account_url()
        self.dsc = DataLakeServiceClient(url, credential=self.settings.STORAGE_DATA_LAKE_ACCOUNT_KEY)
        self.config = self.dsc._config

        self.file_system_name = self.get_resource_name('filesystem')

        if not self.is_playback():
            file_system = self.dsc.get_file_system_client(self.file_system_name)
            try:
                file_system.create_file_system(timeout=5)
            except ResourceExistsError:
                pass

    def tearDown(self):
        if not self.is_playback():
            try:
                self.dsc.delete_file_system(self.file_system_name)
            except:
                pass

        return super(FileTest, self).tearDown()

    # --Helpers-----------------------------------------------------------------
    def _get_directory_reference(self, prefix=TEST_DIRECTORY_PREFIX):
        directory_name = self.get_resource_name(prefix)
        return directory_name

    def _get_file_reference(self, prefix=TEST_FILE_PREFIX):
        file_name = self.get_resource_name(prefix)
        return file_name

    def _create_file_system(self):
        return self.dsc.create_file_system(self._get_file_system_reference())

    def _create_directory_and_return_client(self, directory=None):
        directory_name = directory if directory else self._get_directory_reference()
        directory_client = self.dsc.get_directory_client(self.file_system_name, directory_name)
        directory_client.create_directory()
        return directory_client

    def _create_file_and_return_client(self, directory="", file=None):
        if directory:
            self._create_directory_and_return_client(directory)
        if not file:
            file = self._get_file_reference()
        file_client = self.dsc.get_file_client(self.file_system_name, directory + '/' + file)
        file_client.create_file()
        return file_client

    # --Helpers-----------------------------------------------------------------

    @record
    def test_create_file(self):
        # Arrange
        directory_name = self._get_directory_reference()

        # Create a directory to put the file under that
        directory_client = self.dsc.get_directory_client(self.file_system_name, directory_name)
        directory_client.create_directory()

        file_client = directory_client.get_file_client('filename')
        response = file_client.create_file()

        # Assert
        self.assertIsNotNone(response)

    @record
    def test_create_file_with_lease_id(self):
        # Arrange
        directory_name = self._get_directory_reference()
        directory_client = self.dsc.get_directory_client(self.file_system_name, directory_name)
        directory_client.create_directory()

        file_client = directory_client.get_file_client('filename')
        # Act
        file_client.create_file()
        lease = file_client.acquire_lease()
        create_resp = file_client.create_file(lease=lease)

        # Assert
        file_properties = file_client.get_file_properties()
        self.assertIsNotNone(file_properties)
        self.assertEqual(file_properties.etag, create_resp.get('etag'))
        self.assertEqual(file_properties.last_modified, create_resp.get('last_modified'))

    @record
    def test_create_file_under_root_directory(self):
        # Arrange
        # get a file client to interact with the file under root directory
        file_client = self.dsc.get_file_client(self.file_system_name, "filename")

        response = file_client.create_file()

        # Assert
        self.assertIsNotNone(response)

    @record
    def test_append_data(self):
        directory_name = self._get_directory_reference()

        # Create a directory to put the file under that
        directory_client = self.dsc.get_directory_client(self.file_system_name, directory_name)
        directory_client.create_directory()

        file_client = directory_client.get_file_client('filename')
        file_client.create_file()

        # Act
        response = file_client.append_data(b'abc', 0, 3)

        self.assertIsNotNone(response)

    @record
    def test_flush_data(self):
        directory_name = self._get_directory_reference()

        # Create a directory to put the file under that
        directory_client = self.dsc.get_directory_client(self.file_system_name, directory_name)
        directory_client.create_directory()

        file_client = directory_client.get_file_client('filename')
        file_client.create_file()

        # Act
        file_client.append_data(b'abc', 0, 3)
        response = file_client.flush_data(3)

        self.assertIsNotNone(response)

    @record
    def test_read_file(self):
        file_client = self._create_file_and_return_client()
        data = self.get_random_bytes(1024)

        # upload data to file
        file_client.append_data(data, 0, len(data))
        file_client.flush_data(len(data))

        # doanload the data and make sure it is the same as uploaded data
        downloaded_data = file_client.read_file()
        self.assertEqual(data, downloaded_data)

    @record
    def test_account_sas(self):
        # SAS URL is calculated from storage key, so this test runs live only
        if TestMode.need_recording_file(self.test_mode):
            return

        file_name = self._get_file_reference()
        # create a file under root directory
        self._create_file_and_return_client(file=file_name)

        # generate a token with file level read permission
        token = generate_account_sas(
            self.dsc.account_name,
            self.dsc.credential.account_key,
            ResourceTypes(file_system=True, object=True),
            AccountSasPermissions(read=True),
            datetime.utcnow() + timedelta(hours=1),
        )

        # read the created file which is under root directory
        file_client = DataLakeFileClient(self.dsc.url, self.file_system_name, file_name, credential=token)
        properties = file_client.get_file_properties()

        # make sure we can read the file properties
        self.assertIsNotNone(properties)

        # try to write to the created file with the token
        with self.assertRaises(StorageErrorException):
            file_client.append_data(b"abcd", 0, 4)

    @record
    def test_file_sas_only_applies_to_file_level(self):
        # SAS URL is calculated from storage key, so this test runs live only
        if TestMode.need_recording_file(self.test_mode):
            return

        file_name = self._get_file_reference()
        directory_name = self._get_directory_reference()
        self._create_file_and_return_client(directory=directory_name, file=file_name)

        # generate a token with file level read and write permissions
        token = generate_file_sas(
            self.dsc.account_name,
            self.file_system_name,
            directory_name,
            file_name,
            account_key=self.dsc.credential.account_key,
            permission=FileSasPermissions(read=True, write=True),
            expiry=datetime.utcnow() + timedelta(hours=1),
        )

        # read the created file which is under root directory
        file_client = DataLakeFileClient(self.dsc.url, self.file_system_name, directory_name+'/'+file_name,
                                         credential=token)
        properties = file_client.get_file_properties()

        # make sure we can read the file properties
        self.assertIsNotNone(properties)

        # try to write to the created file with the token
        response = file_client.append_data(b"abcd", 0, 4, validate_content=True)
        self.assertIsNotNone(response)

        # the token is for file level, so users are not supposed to have access to file system level operations
        file_system_client = FileSystemClient(self.dsc.url, self.file_system_name, credential=token)
        with self.assertRaises(ClientAuthenticationError):
            file_system_client.get_file_system_properties()

        # the token is for file level, so users are not supposed to have access to directory level operations
        directory_client = DataLakeDirectoryClient(self.dsc.url, self.file_system_name, directory_name,
                                                   credential=token)
        with self.assertRaises(ClientAuthenticationError):
            directory_client.get_directory_properties()

    @record
    def test_delete_file(self):
        # Arrange
        file_client = self._create_file_and_return_client()

        file_client.delete_file()

        with self.assertRaises(ResourceNotFoundError):
            file_client.get_file_properties()

    @record
    def test_set_access_control(self):
        file_client = self._create_file_and_return_client()

        response = file_client.set_access_control(permissions='0777')\

        # Assert
        self.assertIsNotNone(response)

    @record
    def test_get_access_control(self):
        file_client = self._create_file_and_return_client()
        file_client.set_access_control(permissions='0777')

        # Act
        response = file_client.get_access_control()

        # Assert
        self.assertIsNotNone(response)

    @record
    def test_get_properties(self):
        # Arrange
        directory_client = self._create_directory_and_return_client()

        metadata = {'hello': 'world', 'number': '42'}
        content_settings = ContentSettings(
            content_language='spanish',
            content_disposition='inline')
        file_client = directory_client.create_file("newfile", metadata=metadata, content_settings=content_settings)
        file_client.append_data(b"abc", 0, 3)
        file_client.flush_data(3)
        properties = file_client.get_file_properties()

        # Assert
        self.assertTrue(properties)
        self.assertEqual(properties.size, 3)
        self.assertEqual(properties.metadata['hello'], metadata['hello'])
        self.assertEqual(properties.content_settings.content_language, content_settings.content_language)

    @record
    def test_rename_file_with_non_used_name(self):
        file_client = self._create_file_and_return_client()
        data_bytes = b"abc"
        file_client.append_data(data_bytes, 0, 3)
        file_client.flush_data(3)
        new_client = file_client.rename_file(file_client.file_system_name+'/'+'newname')

        data = new_client.read_file()
        self.assertEqual(data, data_bytes)
        self.assertEqual(new_client.path_name, "newname")

    @record
    def test_rename_file_to_existing_file(self):
        # create the existing file
        existing_file_client = self._create_file_and_return_client(file="existingfile")
        existing_file_client.append_data(b"a", 0, 1)
        existing_file_client.flush_data(1)
        old_url = existing_file_client.url

        # prepare to rename the file to the existing file
        file_client = self._create_file_and_return_client()
        data_bytes = b"abc"
        file_client.append_data(data_bytes, 0, 3)
        file_client.flush_data(3)
        new_client = file_client.rename_file(file_client.file_system_name+'/'+existing_file_client.path_name)
        new_url = file_client.url

        data = new_client.read_file()
        # the existing file was overridden
        self.assertEqual(data, data_bytes)

    @record
    def test_rename_file_will_not_change_existing_directory(self):
        # create none empty directory(with 2 files)
        dir1 = self._create_directory_and_return_client(directory="dir1")
        f1 = dir1.create_file("file1")
        f1.append_data(b"file1", 0, 5)
        f1.flush_data(5)
        f2 = dir1.create_file("file2")
        f2.append_data(b"file2", 0, 5)
        f2.flush_data(5)

        # create another none empty directory(with 2 files)
        dir2 = self._create_directory_and_return_client(directory="dir2")
        f3 = dir2.create_file("file3")
        f3.append_data(b"file3", 0, 5)
        f3.flush_data(5)
        f4 = dir2.create_file("file4")
        f4.append_data(b"file4", 0, 5)
        f4.flush_data(5)

        new_client = f3.rename_file(f1.file_system_name+'/'+f1.path_name)

        self.assertEqual(new_client.read_file(), b"file3")

        # make sure the data in file2 and file4 weren't touched
        f2_data = f2.read_file()
        self.assertEqual(f2_data, b"file2")

        f4_data = f4.read_file()
        self.assertEqual(f4_data, b"file4")

        with self.assertRaises(HttpResponseError):
            f3.read_file()

# ------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
