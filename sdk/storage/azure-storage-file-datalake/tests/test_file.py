# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import pytest
import unittest
import re
import sys
import unittest

from azure.storage.file.datalake import ContentSettings, generate_account_sas, generate_file_sas, \
    ResourceTypes, AccountSasPermissions, \
    DataLakeFileClient, FileSystemClient, DataLakeDirectoryClient, FileSasPermissions
from azure.storage.file.datalake._generated.models import StorageErrorException
from testcase import (
    StorageTestCase,
    TestMode,
    record,
)
from datetime import datetime, timedelta

from azure.core.exceptions import HttpResponseError, ResourceExistsError, ResourceNotFoundError, \
    ClientAuthenticationError
from azure.storage.blob import (
    BlobServiceClient,
    BlobType,
    BlobBlock,
)
from azure.storage.file.datalake import DataLakeServiceClient



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

    def _create_file_and_return_client(self, directory=None, file=None):
        if directory:
            self._create_directory_and_return_client(directory)
        if not file:
            file = self._get_file_reference()
        file_client = self.dsc.get_file_client(self.file_system_name, directory, file)
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
        blob_properties = file_client.get_file_properties()
        self.assertIsNotNone(blob_properties)
        self.assertEqual(blob_properties.etag, create_resp.get('etag'))
        self.assertEqual(blob_properties.last_modified, create_resp.get('last_modified'))

    @record
    def test_create_file_under_root_directory(self):
        # Arrange
        # get a file client to interact with the file under root directory
        file_client = self.dsc.get_file_client(self.file_system_name, None, "filename")

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
        file_name = self._get_file_reference()
        self._create_file_and_return_client(directory=None, file=file_name)

        # generate a token with file level read permission
        token = generate_account_sas(
            self.dsc.account_name,
            self.dsc.credential.account_key,
            ResourceTypes(file_system=True, object=True),
            AccountSasPermissions(read=True),
            datetime.utcnow() + timedelta(hours=1),
        )

        # read the created file which is under root directory
        file_client = DataLakeFileClient(self.dsc.url, self.file_system_name, None, file_name, credential=token)
        properties = file_client.get_file_properties()

        # make sure we can read the file properties
        self.assertIsNotNone(properties)

        # try to write to the created file with the token
        with self.assertRaises(StorageErrorException):
            file_client.append_data(b"abcd", 0, 4)

    @record
    def test_file_sas_only_applies_to_file_level(self):
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
        file_client = DataLakeFileClient(self.dsc.url, self.file_system_name, directory_name, file_name,
                                         credential=token)
        properties = file_client.get_file_properties()

        # make sure we can read the file properties
        self.assertIsNotNone(properties)

        # try to write to the created file with the token
        response = file_client.append_data(b"abcd", 0, 4)
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
    def test_delete_directory(self):
        # Arrange
        directory_name = self._get_directory_reference()
        metadata = {'hello': 'world', 'number': '42'}
        directory_client = self.dsc.get_directory_client(self.file_system_name, directory_name)
        directory_client.create_directory(metadata=metadata)

        response = directory_client.delete_directory()
        # Assert
        self.assertIsNone(response)

    @record
    def test_create_sub_directory_and_delete_sub_directory(self):
        # Arrange
        directory_name = self._get_directory_reference()
        metadata = {'hello': 'world', 'number': '42'}

        # Create a directory first, to prepare for creating sub directory
        directory_client = self.dsc.get_directory_client(self.file_system_name, directory_name)
        directory_client.create_directory(metadata=metadata)

        # Create sub directory from the current directory
        sub_directory_name = 'subdir'
        sub_directory_created = directory_client.create_sub_directory(sub_directory_name)

        # to make sure the sub directory was indeed created by get sub_directory properties from sub directory client
        sub_directory_client = self.dsc.get_directory_client(self.file_system_name,
                                                             directory_name+'/'+sub_directory_name)
        sub_properties = sub_directory_client.get_directory_properties()

        # Assert
        self.assertTrue(sub_directory_created)
        self.assertTrue(sub_properties)

        # Act
        directory_client.delete_sub_directory(sub_directory_name)
        with self.assertRaises(ResourceNotFoundError):
            sub_directory_client.get_directory_properties()

    @record
    def test_set_access_control(self):
        directory_name = self._get_directory_reference()
        metadata = {'hello': 'world', 'number': '42'}
        directory_client = self.dsc.get_directory_client(self.file_system_name, directory_name)
        directory_client.create_directory(metadata=metadata)

        response = directory_client.set_access_control(permissions='0777')
        # Assert
        self.assertIsNotNone(response)

    @record
    def test_get_access_control(self):
        directory_name = self._get_directory_reference()
        metadata = {'hello': 'world', 'number': '42'}
        directory_client = self.dsc.get_directory_client(self.file_system_name, directory_name)
        directory_client.create_directory(metadata=metadata, permissions='0777')

        # Act
        response = directory_client.get_access_control()
        # Assert
        self.assertIsNotNone(response)

    @record
    def test_get_properties(self):
        # Arrange
        directory_name = self._get_directory_reference()
        metadata = {'hello': 'world', 'number': '42'}
        directory_client = self.dsc.get_directory_client(self.file_system_name, directory_name)
        directory_client.create_directory(metadata=metadata)

        file_client = directory_client.get_file_client("newfile")
        file_client.create_file()
        properties = file_client.get_file_properties()
        # Assert
        self.assertTrue(properties)


# ------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
