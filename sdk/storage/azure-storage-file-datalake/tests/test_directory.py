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

from azure.storage.file.datalake import ContentSettings
from testcase import (
    StorageTestCase,
    TestMode,
    record,
)
from datetime import datetime, timedelta

from azure.core.exceptions import HttpResponseError, ResourceExistsError, ResourceNotFoundError
from azure.storage.blob import (
    BlobServiceClient,
    BlobType,
    BlobBlock,
)
from azure.storage.file.datalake import DataLakeServiceClient



# ------------------------------------------------------------------------------
TEST_DIRECTORY_PREFIX = 'directory'
# ------------------------------------------------------------------------------


class DirectoryTest(StorageTestCase):
    def setUp(self):
        super(DirectoryTest, self).setUp()
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

        return super(DirectoryTest, self).tearDown()

    # --Helpers-----------------------------------------------------------------
    def _get_directory_reference(self, prefix=TEST_DIRECTORY_PREFIX):
        directory_name = self.get_resource_name(prefix)
        return directory_name

    def _create_file_system(self):
        return self.dsc.create_file_system(self._get_file_system_reference())


    # --Helpers-----------------------------------------------------------------

    @record
    def test_create_directory(self):
        # Arrange
        directory_name = self._get_directory_reference()
        content_settings = ContentSettings(
            content_language='spanish',
            content_disposition='inline')
        # Act
        directory_client = self.dsc.get_directory_client(self.file_system_name, directory_name)
        created = directory_client.create_directory(content_settings=content_settings)

        # Assert
        self.assertTrue(created)

    @record
    def test_create_directory_with_content_settings(self):
        # Arrange
        directory_name = self._get_directory_reference()
        content_settings = ContentSettings(
            content_language='spanish',
            content_disposition='inline')
        # Act
        directory_client = self.dsc.get_directory_client(self.file_system_name, directory_name)
        created = directory_client.create_directory(content_settings=content_settings)

        # Assert
        self.assertTrue(created)

    @record
    def test_create_directory_with_metadata(self):
        # Arrange
        directory_name = self._get_directory_reference()
        metadata = {'hello': 'world', 'number': '42'}
        # Act
        directory_client = self.dsc.get_directory_client(self.file_system_name, directory_name)
        created = directory_client.create_directory(metadata=metadata)

        properties = directory_client.get_directory_properties()

        # Assert
        self.assertTrue(created)

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

        properties = directory_client.get_directory_properties()
        # Assert
        self.assertTrue(properties)

    @record
    def test_rename(self):
        directory_name = self._get_directory_reference()
        directory_client = self.dsc.get_directory_client(self.file_system_name, directory_name)
        directory_client.create_directory()

        new_name = "newname"
        new_directory_client = self.dsc.get_directory_client(self.file_system_name, new_name)

        new_directory_client.rename_path('/'+self.file_system_name+'/'+directory_name)
        properties = new_directory_client.get_directory_properties()

        self.assertIsNotNone(properties)

    @record
    def test_get_properties(self):
        # Arrange
        directory_name = self._get_directory_reference()
        metadata = {'hello': 'world', 'number': '42'}
        directory_client = self.dsc.get_directory_client(self.file_system_name, directory_name)
        directory_client.create_directory(metadata=metadata)

        properties = directory_client.get_directory_properties()
        # Assert
        self.assertTrue(properties)

# ------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
