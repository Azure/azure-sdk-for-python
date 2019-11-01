# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import unittest

from azure.storage.file.datalake import DataLakeServiceClient, PublicAccess
from testcase import (
    StorageTestCase,
    record,
)

# ------------------------------------------------------------------------------
TEST_FILE_SYSTEM_PREFIX = 'filesystem'
# ------------------------------------------------------------------------------


class FileSystemTest(StorageTestCase):
    def setUp(self):
        super(FileSystemTest, self).setUp()
        url = self._get_account_url()
        self.dsc = DataLakeServiceClient(url, credential=self.settings.STORAGE_DATA_LAKE_ACCOUNT_KEY)
        self.config = self.dsc._config
        self.test_file_systems = []

    def tearDown(self):
        if not self.is_playback():
            try:
                self.dsc.delete_file_system(self.file_system_name)
            except:
                pass

        return super(FileSystemTest, self).tearDown()

    # --Helpers-----------------------------------------------------------------
    def _get_file_system_reference(self, prefix=TEST_FILE_SYSTEM_PREFIX):
        file_system_name = self.get_resource_name(prefix)
        self.test_file_systems.append(file_system_name)
        return file_system_name

    def _create_file_system(self):
        return self.dsc.create_file_system(self._get_file_system_reference())


    # --Helpers-----------------------------------------------------------------

    @record
    def test_create_file_system(self):
        # Arrange
        file_system_name = self._get_file_system_reference()

        # Act
        file_system_client = self.dsc.get_file_system_client(file_system_name)
        created = file_system_client.create_file_system()

        # Assert
        self.assertTrue(created)

    @record
    def test_list_file_systemss(self):
        # Arrange
        file_system_name = self._get_file_system_reference()
        file_system = self.dsc.create_file_system(file_system_name)

        # Act
        file_systems = list(self.dsc.list_file_systems())

        # Assert
        self.assertIsNotNone(file_systems)
        self.assertGreaterEqual(len(file_systems), 1)
        self.assertIsNotNone(file_systems[0])
        self.assertNamedItemInContainer(file_systems, file_system.file_system_name)
        self.assertIsNotNone(file_systems[0].has_immutability_policy)
        self.assertIsNotNone(file_systems[0].has_legal_hold)

    @record
    def test_delete_file_system_with_existing_file_system(self):
        # Arrange
        file_system = self._create_file_system()

        # Act
        deleted = file_system.delete_file_system()

        # Assert
        self.assertIsNone(deleted)

    @record
    def test_list_file_systems_with_include_metadata(self):
        # Arrange
        file_system = self._create_file_system()
        metadata = {'hello': 'world', 'number': '42'}
        resp = file_system.set_file_system_metadata(metadata)

        # Act
        file_systems = list(self.dsc.list_file_systems(
            name_starts_with=file_system.file_system_name,
            include_metadata=True))

        # Assert
        self.assertIsNotNone(file_systems)
        self.assertGreaterEqual(len(file_systems), 1)
        self.assertIsNotNone(file_systems[0])
        self.assertNamedItemInContainer(file_systems, file_system.file_system_name)
        self.assertDictEqual(file_systems[0].metadata, metadata)

    @record
    def test_list_file_systems_by_page(self):
        # Arrange
        for i in range(0, 6):
            self._create_file_system()

        # Act
        file_systems = list(next(self.dsc.list_file_systems(
            results_per_page=3,
            name_starts_with="file",
            include_metadata=True).by_page()))

        # Assert
        self.assertIsNotNone(file_systems)
        self.assertGreaterEqual(len(file_systems), 3)

    @record
    def test_list_file_systems_with_public_access(self):
        # Arrange
        file_system_name = self._get_file_system_reference()
        file_system = self.dsc.get_file_system_client(file_system_name)
        file_system.create_file_system(public_access="blob")
        metadata = {'hello': 'world', 'number': '42'}
        resp = file_system.set_file_system_metadata(metadata)

        # Act
        file_systems = list(self.dsc.list_file_systems(
            name_starts_with=file_system.file_system_name,
            include_metadata=True))

        # Assert
        self.assertIsNotNone(file_systems)
        self.assertGreaterEqual(len(file_systems), 1)
        self.assertIsNotNone(file_systems[0])
        self.assertNamedItemInContainer(file_systems, file_system.file_system_name)
        self.assertDictEqual(file_systems[0].metadata, metadata)
        self.assertTrue(file_systems[0].public_access is PublicAccess.File)

    @record
    def test_get_file_system_properties(self):
        # Arrange
        metadata = {'hello': 'world', 'number': '42'}
        file_system = self._create_file_system()
        file_system.set_file_system_metadata(metadata)

        # Act
        props = file_system.get_file_system_properties()

        # Assert
        self.assertIsNotNone(props)
        self.assertDictEqual(props.metadata, metadata)
        self.assertIsNotNone(props.has_immutability_policy)
        self.assertIsNotNone(props.has_legal_hold)

    @record
    def test_list_paths(self):
        # Arrange
        file_system = self._create_file_system()
        for i in range(0, 6):
            file_system.create_directory("dir1{}".format(i))

        paths = list(file_system.get_paths(upn=True))

        self.assertEqual(len(paths), 6)

    @record
    def test_list_paths_with_max_per_page(self):
        # Arrange
        file_system = self._create_file_system()
        for i in range(0, 6):
            file_system.create_directory("dir1{}".format(i))

        generator1 = file_system.get_paths(max_results=2, upn=True).by_page()
        paths1 = list(next(generator1))

        generator2 = file_system.get_paths(max_results=4, upn=True)\
            .by_page(continuation_token=generator1.continuation_token)
        paths2 = list(next(generator2))

        self.assertEqual(len(paths1), 2)
        self.assertEqual(len(paths2), 4)

    @record
    def test_list_paths_under_specific_path(self):
        # Arrange
        file_system = self._create_file_system()
        for i in range(0, 6):
            file_system.create_directory("dir1{}".format(i))

            # create a subdirectory under the current directory
            subdir = file_system.get_directory_client("dir1{}".format(i)).create_sub_directory("subdir")
            subdir.create_sub_directory("subsub")

            # create a file under the current directory
            file_client = subdir.create_file("file")
            file_client.append_data(b"abced", 0, 5)
            file_client.flush_data(5)

        generator1 = file_system.get_paths(path="dir10/subdir", max_results=2, upn=True).by_page()
        paths = list(next(generator1))

        self.assertEqual(len(paths), 2)
        self.assertEqual(paths[0].content_length, 5)
# ------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
