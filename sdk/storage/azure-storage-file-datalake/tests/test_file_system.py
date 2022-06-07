# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import pytest
import unittest
from datetime import datetime, timedelta

from azure.core import MatchConditions
from azure.core.exceptions import ResourceNotFoundError, HttpResponseError, ResourceExistsError

from azure.storage.filedatalake import(
    AccessPolicy,
    AccountSasPermissions,
    DataLakeServiceClient,
    FileSystemSasPermissions,
    PublicAccess,
    ResourceTypes,
    generate_account_sas)

from azure.storage.blob import StorageErrorCode
from settings.testcase import DataLakePreparer
from devtools_testutils.storage import StorageTestCase

# ------------------------------------------------------------------------------
TEST_FILE_SYSTEM_PREFIX = 'filesystem'
# ------------------------------------------------------------------------------


class FileSystemTest(StorageTestCase):
    def _setUp(self, account_name, account_key):
        url = self.account_url(account_name, 'dfs')
        self.dsc = DataLakeServiceClient(url, account_key)
        self.config = self.dsc._config
        self.test_file_systems = []

    def tearDown(self):
        if not self.is_playback():
            try:
                for file_system in self.test_file_systems:
                    self.dsc.delete_file_system(file_system)
            except:
                pass

        return super(FileSystemTest, self).tearDown()

    # --Helpers-----------------------------------------------------------------
    def _get_file_system_reference(self, prefix=TEST_FILE_SYSTEM_PREFIX):
        file_system_name = self.get_resource_name(prefix)
        self.test_file_systems.append(file_system_name)
        return file_system_name

    def _create_file_system(self, file_system_prefix=TEST_FILE_SYSTEM_PREFIX):
        try:
            return self.dsc.create_file_system(self._get_file_system_reference(prefix=file_system_prefix))
        except:
            pass


    # --Test cases for file system ---------------------------------------------

    @DataLakePreparer()
    def test_create_file_system(self, datalake_storage_account_name, datalake_storage_account_key):
        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        # Arrange
        file_system_name = self._get_file_system_reference()

        # Act
        file_system_client = self.dsc.get_file_system_client(file_system_name)
        created = file_system_client.create_file_system()

        # Assert
        self.assertTrue(created)

    @DataLakePreparer()
    def test_create_file_system_extra_backslash(self, datalake_storage_account_name, datalake_storage_account_key):
        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        # Arrange
        file_system_name = self._get_file_system_reference()

        # Act
        file_system_client = self.dsc.get_file_system_client(file_system_name + '/')
        created = file_system_client.create_file_system()

        # Assert
        self.assertTrue(created)

    @DataLakePreparer()
    def test_file_system_exists(self, datalake_storage_account_name, datalake_storage_account_key):
        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        # Arrange
        file_system_name = self._get_file_system_reference()

        # Act
        file_system_client1 = self.dsc.get_file_system_client(file_system_name)
        file_system_client2 = self.dsc.get_file_system_client("nonexistentfs")
        file_system_client1.create_file_system()

        self.assertTrue(file_system_client1.exists())
        self.assertFalse(file_system_client2.exists())

    @DataLakePreparer()
    def test_create_file_system_with_metadata(self, datalake_storage_account_name, datalake_storage_account_key):
        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        # Arrange
        metadata = {'hello': 'world', 'number': '42'}
        file_system_name = self._get_file_system_reference()

        # Act
        file_system_client = self.dsc.get_file_system_client(file_system_name)
        created = file_system_client.create_file_system(metadata=metadata)

        # Assert
        meta = file_system_client.get_file_system_properties().metadata
        self.assertTrue(created)
        self.assertDictEqual(meta, metadata)

    @DataLakePreparer()
    def test_set_file_system_acl(self, datalake_storage_account_name, datalake_storage_account_key):
        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        # Act
        file_system = self._create_file_system()
        access_policy = AccessPolicy(permission=FileSystemSasPermissions(read=True),
                                     expiry=datetime.utcnow() + timedelta(hours=1),
                                     start=datetime.utcnow())
        signed_identifier1 = {'testid': access_policy}
        response = file_system.set_file_system_access_policy(signed_identifier1, public_access=PublicAccess.FileSystem)

        self.assertIsNotNone(response.get('etag'))
        self.assertIsNotNone(response.get('last_modified'))
        acl1 = file_system.get_file_system_access_policy()
        self.assertIsNotNone(acl1['public_access'])
        self.assertEqual(len(acl1['signed_identifiers']), 1)

        # If set signed identifier without specifying the access policy then it will be default to None
        signed_identifier2 = {'testid': access_policy, 'test2': access_policy}
        file_system.set_file_system_access_policy(signed_identifier2)
        acl2 = file_system.get_file_system_access_policy()
        self.assertIsNone(acl2['public_access'])
        self.assertEqual(len(acl2['signed_identifiers']), 2)

    @DataLakePreparer()
    def test_list_file_systemss(self, datalake_storage_account_name, datalake_storage_account_key):
        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
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

    @pytest.mark.live_test_only
    @DataLakePreparer()
    def test_list_file_systems_account_sas(self, datalake_storage_account_name, datalake_storage_account_key):
        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        # Arrange
        file_system_name = self._get_file_system_reference()
        file_system = self.dsc.create_file_system(file_system_name)
        sas_token = generate_account_sas(
            datalake_storage_account_name,
            datalake_storage_account_key,
            ResourceTypes(service=True),
            AccountSasPermissions(list=True),
            datetime.utcnow() + timedelta(hours=1),
        )

        # Act
        dsc = DataLakeServiceClient(self.account_url(datalake_storage_account_name, 'dfs'), credential=sas_token)
        file_systems = list(dsc.list_file_systems())

        # Assert
        self.assertIsNotNone(file_systems)
        self.assertGreaterEqual(len(file_systems), 1)
        self.assertIsNotNone(file_systems[0])
        self.assertNamedItemInContainer(file_systems, file_system.file_system_name)

    @DataLakePreparer()
    def test_rename_file_system(self, datalake_storage_account_name, datalake_storage_account_key):
        if not self.is_playback():
            return
        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        old_name1 = self._get_file_system_reference(prefix="oldcontainer1")
        old_name2 = self._get_file_system_reference(prefix="oldcontainer2")
        new_name = self._get_file_system_reference(prefix="newcontainer")
        filesystem1 = self.dsc.create_file_system(old_name1)
        self.dsc.create_file_system(old_name2)

        new_filesystem = self.dsc._rename_file_system(name=old_name1, new_name=new_name)
        with self.assertRaises(HttpResponseError):
            self.dsc._rename_file_system(name=old_name2, new_name=new_name)
        with self.assertRaises(HttpResponseError):
            filesystem1.get_file_system_properties()
        with self.assertRaises(HttpResponseError):
            self.dsc._rename_file_system(name="badfilesystem", new_name="filesystem")
        self.assertEqual(new_name, new_filesystem.get_file_system_properties().name)

    @pytest.mark.skip(reason="Feature not yet enabled. Record when enabled.")
    @DataLakePreparer()
    def test_rename_file_system_with_file_system_client(self, datalake_storage_account_name, datalake_storage_account_key):
        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        old_name1 = self._get_file_system_reference(prefix="oldcontainer1")
        old_name2 = self._get_file_system_reference(prefix="oldcontainer2")
        new_name = self._get_file_system_reference(prefix="newcontainer")
        bad_name = self._get_file_system_reference(prefix="badcontainer")
        filesystem1 = self.dsc.create_file_system(old_name1)
        file_system2 = self.dsc.create_file_system(old_name2)
        bad_file_system = self.dsc.get_file_system_client(bad_name)

        new_filesystem = filesystem1._rename_file_system(new_name=new_name)
        with self.assertRaises(HttpResponseError):
            file_system2._rename_file_system(new_name=new_name)
        with self.assertRaises(HttpResponseError):
            filesystem1.get_file_system_properties()
        with self.assertRaises(HttpResponseError):
            bad_file_system._rename_file_system(new_name="filesystem")
        self.assertEqual(new_name, new_filesystem.get_file_system_properties().name)

    @DataLakePreparer()
    def test_list_system_filesystems(self, datalake_storage_account_name, datalake_storage_account_key):
        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        # Arrange
        dsc = DataLakeServiceClient(self.dsc.url, credential=datalake_storage_account_key)
        # Act
        filesystems = list(dsc.list_file_systems(include_system=True))

        # Assert
        found = False
        for fs in filesystems:
            if fs.name == "$logs":
                found = True
        self.assertEqual(found, True)

    @DataLakePreparer()
    def test_rename_file_system_with_source_lease(self, datalake_storage_account_name, datalake_storage_account_key):
        if not self.is_playback():
            return
        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        old_name = self._get_file_system_reference(prefix="old")
        new_name = self._get_file_system_reference(prefix="new")
        filesystem = self.dsc.create_file_system(old_name)
        filesystem_lease_id = filesystem.acquire_lease()
        with self.assertRaises(HttpResponseError):
            self.dsc._rename_file_system(name=old_name, new_name=new_name)
        with self.assertRaises(HttpResponseError):
            self.dsc._rename_file_system(name=old_name, new_name=new_name, lease="bad_id")
        new_filesystem = self.dsc._rename_file_system(name=old_name, new_name=new_name, lease=filesystem_lease_id)
        self.assertEqual(new_name, new_filesystem.get_file_system_properties().name)

    @DataLakePreparer()
    def test_undelete_file_system(self, datalake_storage_account_name, datalake_storage_account_key):
        # TODO: Needs soft delete enabled account in ARM template.
        if not self.is_playback():
            return
        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        name = self._get_file_system_reference("testfs")
        filesystem_client = self.dsc.create_file_system(name)

        # Act
        filesystem_client.delete_file_system()
        # to make sure the filesystem deleted
        with self.assertRaises(ResourceNotFoundError):
            filesystem_client.get_file_system_properties()

        filesystem_list = list(self.dsc.list_file_systems(include_deleted=True))
        self.assertTrue(len(filesystem_list) >= 1)

        for filesystem in filesystem_list:
            # find the deleted filesystem and restore it
            if filesystem.deleted and filesystem.name == filesystem_client.file_system_name:
                restored_fs_client = self.dsc.undelete_file_system(filesystem.name, filesystem.deleted_version)

                # to make sure the deleted filesystem is restored
                props = restored_fs_client.get_file_system_properties()
                self.assertIsNotNone(props)

    @pytest.mark.skip(reason="We are generating a SAS token therefore play only live but we also need a soft delete enabled account.")
    @DataLakePreparer()
    def test_restore_file_system_with_sas(self, datalake_storage_account_name, datalake_storage_account_key):
        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        token = generate_account_sas(
            self.dsc.account_name,
            self.dsc.credential.account_key,
            ResourceTypes(service=True, file_system=True),
            AccountSasPermissions(read=True, write=True, list=True, delete=True),
            datetime.utcnow() + timedelta(hours=1),
        )
        dsc = DataLakeServiceClient(self.dsc.url, token)
        name = self._get_file_system_reference(prefix="filesystem")
        filesystem_client = dsc.create_file_system(name)
        filesystem_client.delete_file_system()
        # to make sure the filesystem is deleted
        with self.assertRaises(ResourceNotFoundError):
            filesystem_client.get_file_system_properties()

        filesystem_list = list(dsc.list_file_systems(include_deleted=True))
        self.assertTrue(len(filesystem_list) >= 1)

        restored_version = 0
        for filesystem in filesystem_list:
            # find the deleted filesystem and restore it
            if filesystem.deleted and filesystem.name == filesystem_client.file_system_name:
                restored_fs_client = dsc.undelete_file_system(filesystem.name, filesystem.deleted_version)

                # to make sure the deleted filesystem is restored
                props = restored_fs_client.get_file_system_properties()
                self.assertIsNotNone(props)

    @DataLakePreparer()
    def test_delete_file_system_with_existing_file_system(self, datalake_storage_account_name, datalake_storage_account_key):
        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        # Arrange
        file_system = self._create_file_system()

        # Act
        deleted = file_system.delete_file_system()

        # Assert
        self.assertIsNone(deleted)

    @DataLakePreparer()
    def test_delete_none_existing_file_system(self, datalake_storage_account_name, datalake_storage_account_key):
        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        fake_file_system_client = self.dsc.get_file_system_client("fakeclient")

        # Act
        with self.assertRaises(ResourceNotFoundError):
            fake_file_system_client.delete_file_system(match_condition=MatchConditions.IfMissing)

    @DataLakePreparer()
    def test_list_file_systems_with_include_metadata(self, datalake_storage_account_name, datalake_storage_account_key):
        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
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

    @DataLakePreparer()
    def test_list_file_systems_by_page(self, datalake_storage_account_name, datalake_storage_account_key):
        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        # Arrange
        for i in range(0, 6):
            self._create_file_system(file_system_prefix="filesystem{}".format(i))

        # Act
        file_systems = list(next(self.dsc.list_file_systems(
            results_per_page=3,
            name_starts_with="file",
            include_metadata=True).by_page()))

        # Assert
        self.assertIsNotNone(file_systems)
        self.assertGreaterEqual(len(file_systems), 3)

    @DataLakePreparer()
    def test_list_file_systems_with_public_access(self, datalake_storage_account_name, datalake_storage_account_key):
        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
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

    @DataLakePreparer()
    def test_get_file_system_properties(self, datalake_storage_account_name, datalake_storage_account_key):
        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
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

    @DataLakePreparer()
    def test_service_client_session_closes_after_filesystem_creation(self, datalake_storage_account_name, datalake_storage_account_key):
        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        # Arrange
        dsc2 = DataLakeServiceClient(self.dsc.url, credential=datalake_storage_account_key)
        with DataLakeServiceClient(self.dsc.url, credential=datalake_storage_account_key) as ds_client:
            fs1 = ds_client.create_file_system(self._get_file_system_reference(prefix="fs1"))
            fs1.delete_file_system()
        dsc2.create_file_system(self._get_file_system_reference(prefix="fs2"))
        dsc2.close()

    @DataLakePreparer()
    def test_list_paths(self, datalake_storage_account_name, datalake_storage_account_key):
        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        # Arrange
        file_system = self._create_file_system()
        for i in range(0, 6):
            file_system.create_directory("dir1{}".format(i))

        paths = list(file_system.get_paths(upn=True))

        self.assertEqual(len(paths), 6)
        self.assertTrue(isinstance(paths[0].last_modified, datetime))

    @DataLakePreparer()
    def test_list_paths_create_expiry(self, datalake_storage_account_name, datalake_storage_account_key):
        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        # Arrange
        file_system = self._create_file_system()
        file_client = file_system.create_file('file1')

        expires_on = datetime.utcnow() + timedelta(days=1)
        file_client.set_file_expiry("Absolute", expires_on=expires_on)

        # Act
        paths = list(file_system.get_paths(upn=True))

        # Assert
        self.assertEqual(1, len(paths))
        props = file_client.get_file_properties()
        # Properties do not include microseconds so let them vary by 1 second
        self.assertAlmostEqual(props.creation_time, paths[0].creation_time, delta=timedelta(seconds=1))
        self.assertAlmostEqual(props.expiry_time, paths[0].expiry_time, delta=timedelta(seconds=1))

    @DataLakePreparer()
    def test_list_paths_no_expiry(self, datalake_storage_account_name, datalake_storage_account_key):
        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        # Arrange
        file_system = self._create_file_system()
        file_system.create_file('file1')

        # Act
        paths = list(file_system.get_paths(upn=True))

        # Assert
        self.assertEqual(1, len(paths))
        self.assertIsNone(paths[0].expiry_time)

    @DataLakePreparer()
    def test_get_deleted_paths(self, datalake_storage_account_name, datalake_storage_account_key):
        # TODO: Needs soft delete enabled account in ARM template.
        if not self.is_playback():
            return
        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        # Arrange
        file_system = self._create_file_system()
        file0 = file_system.create_file("file0")
        file1 = file_system.create_file("file1")

        dir1 = file_system.create_directory("dir1")
        dir2 = file_system.create_directory("dir2")
        dir3 = file_system.create_directory("dir3")
        file_in_dir3 = dir3.create_file("file_in_dir3")
        file_in_subdir = dir3.create_file("subdir/file_in_subdir")

        file0.delete_file()
        file1.delete_file()
        dir1.delete_directory()
        dir2.delete_directory()
        file_in_dir3.delete_file()
        file_in_subdir.delete_file()
        deleted_paths = list(file_system.list_deleted_paths())
        dir3_paths = list(file_system.list_deleted_paths(path_prefix="dir3/"))

        # Assert
        self.assertEqual(len(deleted_paths), 6)
        self.assertEqual(len(dir3_paths), 2)
        self.assertIsNotNone(dir3_paths[0].deletion_id)
        self.assertIsNotNone(dir3_paths[1].deletion_id)
        self.assertEqual(dir3_paths[0].name, 'dir3/file_in_dir3')
        self.assertEqual(dir3_paths[1].name, 'dir3/subdir/file_in_subdir')

        paths_generator1 = file_system.list_deleted_paths(results_per_page=2).by_page()
        paths1 = list(next(paths_generator1))

        paths_generator2 = file_system.list_deleted_paths(results_per_page=4).by_page(
            continuation_token=paths_generator1.continuation_token)
        paths2 = list(next(paths_generator2))

        # Assert
        self.assertEqual(len(paths1), 2)
        self.assertEqual(len(paths2), 4)

    @DataLakePreparer()
    def test_list_paths_which_are_all_files(self, datalake_storage_account_name, datalake_storage_account_key):
        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        # Arrange
        file_system = self._create_file_system()
        for i in range(0, 6):
            file_system.create_file("file{}".format(i))

        paths = list(file_system.get_paths(upn=True))

        self.assertEqual(len(paths), 6)

    @DataLakePreparer()
    def test_list_paths_with_max_per_page(self, datalake_storage_account_name, datalake_storage_account_key):
        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
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

    @DataLakePreparer()
    def test_list_paths_under_specific_path(self, datalake_storage_account_name, datalake_storage_account_key):
        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
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

    @DataLakePreparer()
    def test_list_paths_recursively(self, datalake_storage_account_name, datalake_storage_account_key):
        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        # Arrange
        file_system = self._create_file_system()
        for i in range(0, 6):
            file_system.create_directory("dir1{}".format(i))

            # create a subdirectory under the current directory
            subdir = file_system.get_directory_client("dir1{}".format(i)).create_sub_directory("subdir")
            subdir.create_sub_directory("subsub")

            # create a file under the current directory
            subdir.create_file("file")

        paths = list(file_system.get_paths(recursive=True, upn=True))

        # there are 24 subpaths in total
        self.assertEqual(len(paths), 24)

    @DataLakePreparer()
    def test_list_paths_pages_correctly(self, datalake_storage_account_name, datalake_storage_account_key):
        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        # Arrange
        file_system = self._create_file_system(file_system_prefix="fs1")
        for i in range(0, 6):
            file_system.create_directory("dir1{}".format(i))
        for i in range(0, 6):
            file_system.create_file("file{}".format(i))

        generator = file_system.get_paths(max_results=6, upn=True).by_page()
        paths1 = list(next(generator))
        paths2 = list(next(generator))
        with self.assertRaises(StopIteration):
            list(next(generator))

        self.assertEqual(len(paths1), 6)
        self.assertEqual(len(paths2), 6)

    @DataLakePreparer()
    def test_create_directory_from_file_system_client(self, datalake_storage_account_name, datalake_storage_account_key):
        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        # Arrange
        file_system = self._create_file_system()
        file_system.create_directory("dir1/dir2")

        paths = list(file_system.get_paths(recursive=False, upn=True))

        self.assertEqual(len(paths), 1)
        self.assertEqual(paths[0].name, "dir1")

    @DataLakePreparer()
    def test_create_file_from_file_system_client(self, datalake_storage_account_name, datalake_storage_account_key):
        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        # Arrange
        file_system = self._create_file_system()
        file_system.create_file("dir1/dir2/file")

        paths = list(file_system.get_paths(recursive=True, upn=True))

        self.assertEqual(len(paths), 3)
        self.assertEqual(paths[0].name, "dir1")
        self.assertEqual(paths[2].is_directory, False)

    @DataLakePreparer()
    def test_get_root_directory_client(self, datalake_storage_account_name, datalake_storage_account_key):
        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        file_system = self._create_file_system()
        directory_client = file_system._get_root_directory_client()

        acl = 'user::rwx,group::r-x,other::rwx'
        directory_client.set_access_control(acl=acl)
        access_control = directory_client.get_access_control()

        self.assertEqual(acl, access_control['acl'])

    @DataLakePreparer()
    def test_file_system_sessions_closes_properly(self, datalake_storage_account_name, datalake_storage_account_key):
        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        # Arrange
        file_system_client = self._create_file_system("fenrhxsbfvsdvdsvdsadb")
        with file_system_client as fs_client:
            with fs_client.get_file_client("file1.txt") as f_client:
                f_client.create_file()
            with fs_client.get_file_client("file2.txt") as f_client:
                f_client.create_file()
            with fs_client.get_directory_client("file1") as f_client:
                f_client.create_directory()
            with fs_client.get_directory_client("file2") as f_client:
                f_client.create_directory()

    @DataLakePreparer()
    def test_undelete_dir_with_version_id(self, datalake_storage_account_name, datalake_storage_account_key):
        # TODO: Needs soft delete enabled account in ARM template.
        if not self.is_playback():
            return
        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        file_system_client = self._create_file_system("fs")
        dir_path = 'dir10'
        dir_client = file_system_client.create_directory(dir_path)
        resp = dir_client.delete_directory()
        with self.assertRaises(HttpResponseError):
            file_system_client.get_file_client(dir_path).get_file_properties()
        restored_dir_client = file_system_client._undelete_path(dir_path, resp['deletion_id'])
        resp = restored_dir_client.get_directory_properties()
        self.assertIsNotNone(resp)

    @DataLakePreparer()
    def test_undelete_file_with_version_id(self, datalake_storage_account_name, datalake_storage_account_key):
        # TODO: Needs soft delete enabled account in ARM template.
        if not self.is_playback():
            return
        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        file_system_client = self._create_file_system("fs1")
        file_path = 'dir10/fileŇ'
        dir_client = file_system_client.create_file(file_path)
        resp = dir_client.delete_file()
        with self.assertRaises(HttpResponseError):
            file_system_client.get_file_client(file_path).get_file_properties()
        restored_file_client = file_system_client._undelete_path(file_path, resp['deletion_id'])
        resp = restored_file_client.get_file_properties()
        self.assertIsNotNone(resp)

    @DataLakePreparer()
    def test_delete_files_simple_no_raise(self, datalake_storage_account_name, datalake_storage_account_key):
        # Arrange
        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        filesystem = self._create_file_system("fs1")
        data = b'hello world'
        files = ['file1', 'file2', 'file3', 'dir1', 'dir2']

        try:
            # create file1
            filesystem.get_file_client(files[0]).upload_data(data, overwrite=True)

            # create file2
            file2 = filesystem.get_file_client(files[1])
            file2.upload_data(data, overwrite=True)

            # create file3
            file3 = filesystem.get_file_client(files[2])
            file3.upload_data(data, overwrite=True)

            # create dir1
            # empty directory can be deleted using delete_files
            filesystem.get_directory_client(files[3]).create_directory(),

            # create dir2
            dir2 = filesystem.get_directory_client(files[4])
            dir2.create_directory()

        except:
            pass

        # Act
        response = filesystem.delete_files(
            files[0],
            files[1],
            files[2],
            files[3],
            files[4],
        )

        # Assert
        self.assertEqual(len(response), len(files))
        self.assertIsNone(response[0])
        self.assertIsNone(response[1])
        self.assertIsNone(response[2])
        self.assertIsNone(response[3])
        self.assertIsNone(response[4])

    @DataLakePreparer()
    def test_delete_files_with_failed_subrequest(self, datalake_storage_account_name, datalake_storage_account_key):
        # Arrange
        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        filesystem = self._create_file_system("fs2")
        data = b'hello world'
        files = ['file1', 'file2', 'file3', 'dir1', 'dir8']

        try:
            # create file1
            filesystem.get_file_client(files[0]).upload_data(data, overwrite=True)

            # create file2
            file2 = filesystem.get_file_client(files[1])
            file2.upload_data(data, overwrite=True)

            # create file3
            file3 = filesystem.get_file_client(files[2])
            file3.upload_data(data, overwrite=True)

            # create dir1 with file4 inside
            dir1 = filesystem.get_directory_client(files[3])
            dir1.create_file("file4")
        except:
            pass

        # Act
        response = filesystem.delete_files(
            files[0],
            files[1],
            files[2],
            files[3],  # dir1 is not empty
            files[4],  # dir8 doesn't exist
        )

        # Assert
        self.assertEqual(len(response), len(files))
        self.assertIsNone(response[0])
        self.assertIsNone(response[1])
        self.assertIsNone(response[2])
        self.assertEqual(response[3].error_code, StorageErrorCode.directory_not_empty)
        self.assertEqual(response[3].status_code, 409)
        self.assertEqual(response[4].error_code, StorageErrorCode.path_not_found)
        self.assertEqual(response[4].status_code, 404)

    @DataLakePreparer()
    def test_serialized_error(self, datalake_storage_account_name, datalake_storage_account_key):
        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        # Arrange
        file_system = self._create_file_system()
        dir = file_system.create_directory("dir1")
        dir.delete_directory()

        # Assert
        try:
            dir.delete_directory()
        except HttpResponseError as e:
            self.assertEqual(e.error_code, StorageErrorCode.path_not_found)
            self.assertEqual(e.status_code, 404)

# ------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
