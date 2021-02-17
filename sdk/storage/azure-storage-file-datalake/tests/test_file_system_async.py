# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import unittest
import asyncio
import uuid
from datetime import datetime, timedelta

import pytest

from azure.core.exceptions import ResourceNotFoundError, HttpResponseError

from azure.core import MatchConditions
from azure.core.pipeline.transport import AioHttpTransport
from multidict import CIMultiDict, CIMultiDictProxy

from azure.storage.filedatalake import AccessPolicy, generate_directory_sas, DirectorySasPermissions, \
    generate_file_system_sas, generate_account_sas, ResourceTypes, AccountSasPermissions
from azure.storage.filedatalake.aio import DataLakeServiceClient, DataLakeDirectoryClient, FileSystemClient
from azure.storage.filedatalake import PublicAccess
from asynctestcase import (
    StorageTestCase)

# ------------------------------------------------------------------------------
from azure.storage.filedatalake import FileSystemSasPermissions
from testcase import DataLakePreparer

TEST_FILE_SYSTEM_PREFIX = 'filesystem'


# ------------------------------------------------------------------------------

class AiohttpTestTransport(AioHttpTransport):
    """Workaround to vcrpy bug: https://github.com/kevin1024/vcrpy/pull/461
    """

    async def send(self, request, **config):
        response = await super(AiohttpTestTransport, self).send(request, **config)
        if not isinstance(response.headers, CIMultiDictProxy):
            response.headers = CIMultiDictProxy(CIMultiDict(response.internal_response.headers))
            response.content_type = response.headers.get("content-type")
        return response


class FileSystemTest(StorageTestCase):
    def _setUp(self, account_name, account_key):
        url = self._get_account_url(account_name)
        self.dsc = DataLakeServiceClient(url, credential=account_key,
                                         transport=AiohttpTestTransport(), logging_enable=True)
        self.config = self.dsc._config
        self.test_file_systems = []

    def tearDown(self):
        if not self.is_playback():
            loop = asyncio.get_event_loop()
            try:
                for file_system in self.test_file_systems:
                    loop.run_until_complete(self.dsc.delete_file_system(file_system))
                loop.run_until_complete(self.fsc.__aexit__())
            except:
                pass

        return super(FileSystemTest, self).tearDown()

    # --Helpers-----------------------------------------------------------------
    def _get_file_system_reference(self, prefix=TEST_FILE_SYSTEM_PREFIX):
        file_system_name = self.get_resource_name(prefix)
        self.test_file_systems.append(file_system_name)
        return file_system_name

    async def _create_file_system(self, file_system_prefix=TEST_FILE_SYSTEM_PREFIX):
        return await self.dsc.create_file_system(self._get_file_system_reference(prefix=file_system_prefix))

    # --Helpers-----------------------------------------------------------------

    @DataLakePreparer()
    async def test_create_file_system_async(self, datalake_storage_account_name, datalake_storage_account_key):
        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        # Arrange
        file_system_name = self._get_file_system_reference()

        # Act
        file_system_client = self.dsc.get_file_system_client(file_system_name)
        created = await file_system_client.create_file_system()

        # Assert
        self.assertTrue(created)

    @DataLakePreparer()
    async def test_file_system_exists(self, datalake_storage_account_name, datalake_storage_account_key):
        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        # Arrange
        file_system_name = self._get_file_system_reference()

        # Act
        file_system_client1 = self.dsc.get_file_system_client(file_system_name)
        file_system_client2 = self.dsc.get_file_system_client("nonexistentfs")
        await file_system_client1.create_file_system()

        self.assertTrue(await file_system_client1.exists())
        self.assertFalse(await file_system_client2.exists())

    @DataLakePreparer()
    async def test_create_file_system_with_metadata_async(self, datalake_storage_account_name, datalake_storage_account_key):
        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        # Arrange
        metadata = {'hello': 'world', 'number': '42'}
        file_system_name = self._get_file_system_reference()

        # Act
        file_system_client = self.dsc.get_file_system_client(file_system_name)
        created = await file_system_client.create_file_system(metadata=metadata)

        # Assert
        properties = await file_system_client.get_file_system_properties()
        self.assertTrue(created)
        self.assertDictEqual(properties.metadata, metadata)

    @DataLakePreparer()
    async def test_list_file_systems_async(self, datalake_storage_account_name, datalake_storage_account_key):
        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        # Arrange
        file_system_name = self._get_file_system_reference()
        file_system = await self.dsc.create_file_system(file_system_name)

        # Act
        file_systems = []
        async for filesystem in self.dsc.list_file_systems():
            file_systems.append(filesystem)

        # Assert
        self.assertIsNotNone(file_systems)
        self.assertGreaterEqual(len(file_systems), 1)
        self.assertIsNotNone(file_systems[0])
        self.assertNamedItemInContainer(file_systems, file_system.file_system_name)
        self.assertIsNotNone(file_systems[0].has_immutability_policy)
        self.assertIsNotNone(file_systems[0].has_legal_hold)

    @DataLakePreparer()
    async def test_delete_file_system_with_existing_file_system_async(self, datalake_storage_account_name, datalake_storage_account_key):
        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        # Arrange
        file_system = await self._create_file_system()

        # Act
        deleted = await file_system.delete_file_system()

        # Assert
        self.assertIsNone(deleted)

    @DataLakePreparer()
    async def test_rename_file_system(self, datalake_storage_account_name, datalake_storage_account_key):
        if not self.is_playback():
            return
        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        old_name1 = self._get_file_system_reference(prefix="oldcontainer1")
        old_name2 = self._get_file_system_reference(prefix="oldcontainer2")
        new_name = self._get_file_system_reference(prefix="newcontainer")
        filesystem1 = await self.dsc.create_file_system(old_name1)
        await self.dsc.create_file_system(old_name2)

        new_filesystem = await self.dsc._rename_file_system(name=old_name1, new_name=new_name)
        with self.assertRaises(HttpResponseError):
            await self.dsc._rename_file_system(name=old_name2, new_name=new_name)
        with self.assertRaises(HttpResponseError):
            await filesystem1.get_file_system_properties()
        with self.assertRaises(HttpResponseError):
            await self.dsc._rename_file_system(name="badfilesystem", new_name="filesystem")
        props = await new_filesystem.get_file_system_properties()
        self.assertEqual(new_name, props.name)

    @DataLakePreparer()
    async def test_rename_file_system_with_file_system_client(self, datalake_storage_account_name, datalake_storage_account_key):
        pytest.skip("Feature not yet enabled. Make sure to record this test once enabled.")
        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        old_name1 = self._get_file_system_reference(prefix="oldcontainer1")
        old_name2 = self._get_file_system_reference(prefix="oldcontainer2")
        new_name = self._get_file_system_reference(prefix="newcontainer")
        bad_name = self._get_file_system_reference(prefix="badcontainer")
        filesystem1 = await self.dsc.create_file_system(old_name1)
        file_system2 = await self.dsc.create_file_system(old_name2)
        bad_file_system = self.dsc.get_file_system_client(bad_name)

        new_filesystem = await filesystem1._rename_file_system(new_name=new_name)
        with self.assertRaises(HttpResponseError):
            await file_system2._rename_file_system(new_name=new_name)
        with self.assertRaises(HttpResponseError):
            await filesystem1.get_file_system_properties()
        with self.assertRaises(HttpResponseError):
            await bad_file_system._rename_file_system(new_name="filesystem")
        new_file_system_props = await new_filesystem.get_file_system_properties()
        self.assertEqual(new_name, new_file_system_props.name)

    @DataLakePreparer()
    async def test_rename_file_system_with_source_lease(self, datalake_storage_account_name, datalake_storage_account_key):
        if not self.is_playback():
            return
        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        old_name = self._get_file_system_reference(prefix="old")
        new_name = self._get_file_system_reference(prefix="new")
        filesystem = await self.dsc.create_file_system(old_name)
        filesystem_lease_id = await filesystem.acquire_lease()
        with self.assertRaises(HttpResponseError):
            await self.dsc._rename_file_system(name=old_name, new_name=new_name)
        with self.assertRaises(HttpResponseError):
            await self.dsc._rename_file_system(name=old_name, new_name=new_name, lease="bad_id")
        new_filesystem = await self.dsc._rename_file_system(name=old_name, new_name=new_name, lease=filesystem_lease_id)
        props = await new_filesystem.get_file_system_properties()
        self.assertEqual(new_name, props.name)

    @DataLakePreparer()
    async def test_undelete_file_system(self, datalake_storage_account_name, datalake_storage_account_key):
        # Needs soft delete enabled account.
        if not self.is_playback():
            return
        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        name = self._get_file_system_reference(prefix="filesystem")
        filesystem_client = await self.dsc.create_file_system(name)

        await filesystem_client.delete_file_system()
        # to make sure the filesystem deleted
        with self.assertRaises(ResourceNotFoundError):
            await filesystem_client.get_file_system_properties()

        filesystem_list = []
        async for fs in self.dsc.list_file_systems(include_deleted=True):
            filesystem_list.append(fs)
        self.assertTrue(len(filesystem_list) >= 1)

        restored_version = 0
        for filesystem in filesystem_list:
            # find the deleted filesystem and restore it
            if filesystem.deleted and filesystem.name == filesystem_client.file_system_name:
                restored_fs_client = await self.dsc.undelete_file_system(filesystem.name,
                                                                         filesystem.deleted_version,
                                                                         new_name="restored" +
                                                                                  name + str(restored_version))
                restored_version += 1

                # to make sure the deleted filesystem is restored
                props = await restored_fs_client.get_file_system_properties()
                self.assertIsNotNone(props)

    @DataLakePreparer()
    async def test_restore_to_existing_file_system(self, datalake_storage_account_name, datalake_storage_account_key):
        # Needs soft delete enabled account.
        if not self.is_playback():
            return
        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        # get an existing filesystem
        existing_name = self._get_file_system_reference(prefix="existing")
        name = self._get_file_system_reference(prefix="filesystem")
        existing_filesystem_client = await self.dsc.create_file_system(existing_name)
        filesystem_client = await self.dsc.create_file_system(name)

        # Act
        await filesystem_client.delete_file_system()
        # to make sure the filesystem deleted
        with self.assertRaises(ResourceNotFoundError):
            await filesystem_client.get_file_system_properties()

        filesystem_list = []
        async for fs in self.dsc.list_file_systems(include_deleted=True):
            filesystem_list.append(fs)
        self.assertTrue(len(filesystem_list) >= 1)

        for filesystem in filesystem_list:
            # find the deleted filesystem and restore it
            if filesystem.deleted and filesystem.name == filesystem_client.file_system_name:
                with self.assertRaises(HttpResponseError):
                    await self.dsc.undelete_file_system(filesystem.name, filesystem.deleted_version,
                                                        new_name=existing_filesystem_client.file_system_name)

    @DataLakePreparer()
    async def test_restore_file_system_with_sas(self, datalake_storage_account_name, datalake_storage_account_key):
        pytest.skip(
            "We are generating a SAS token therefore play only live but we also need a soft delete enabled account.")
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
        filesystem_client = await dsc.create_file_system(name)
        await filesystem_client.delete_file_system()
        # to make sure the filesystem is deleted
        with self.assertRaises(ResourceNotFoundError):
            await filesystem_client.get_file_system_properties()

        filesystem_list = []
        async for fs in self.dsc.list_file_systems(include_deleted=True):
            filesystem_list.append(fs)
        self.assertTrue(len(filesystem_list) >= 1)

        restored_version = 0
        for filesystem in filesystem_list:
            # find the deleted filesystem and restore it
            if filesystem.deleted and filesystem.name == filesystem_client.file_system_name:
                restored_fs_client = await dsc.undelete_file_system(filesystem.name, filesystem.deleted_version,
                                                                    new_name="restored" + name + str(restored_version))
                restored_version += 1

                # to make sure the deleted filesystem is restored
                props = await restored_fs_client.get_file_system_properties()
                self.assertIsNotNone(props)

    @DataLakePreparer()
    async def test_delete_none_existing_file_system_async(self, datalake_storage_account_name, datalake_storage_account_key):
        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        fake_file_system_client = self.dsc.get_file_system_client("fakeclient")

        # Act
        with self.assertRaises(ResourceNotFoundError):
            await fake_file_system_client.delete_file_system(match_condition=MatchConditions.IfMissing)

    @DataLakePreparer()
    async def test_list_file_systems_with_include_metadata_async(self, datalake_storage_account_name, datalake_storage_account_key):
        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        # Arrange
        file_system = await self._create_file_system()
        metadata = {'hello': 'world', 'number': '42'}
        await file_system.set_file_system_metadata(metadata)

        # Act
        file_systems = []
        async for fs in self.dsc.list_file_systems(name_starts_with=file_system.file_system_name,
                                                   include_metadata=True):
            file_systems.append(fs)

        # Assert
        self.assertIsNotNone(file_systems)
        self.assertGreaterEqual(len(file_systems), 1)
        self.assertIsNotNone(file_systems[0])
        self.assertNamedItemInContainer(file_systems, file_system.file_system_name)
        self.assertDictEqual(file_systems[0].metadata, metadata)

    @DataLakePreparer()
    async def test_set_file_system_acl_async(self, datalake_storage_account_name, datalake_storage_account_key):
        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        # Act
        file_system = await self._create_file_system()
        access_policy = AccessPolicy(permission=FileSystemSasPermissions(read=True),
                                     expiry=datetime.utcnow() + timedelta(hours=1),
                                     start=datetime.utcnow())
        signed_identifier1 = {'testid': access_policy}
        response = await file_system.set_file_system_access_policy(signed_identifier1, public_access=PublicAccess.FileSystem)

        self.assertIsNotNone(response.get('etag'))
        self.assertIsNotNone(response.get('last_modified'))

        acl1 = await file_system.get_file_system_access_policy()
        self.assertIsNotNone(acl1['public_access'])
        self.assertEqual(len(acl1['signed_identifiers']), 1)

        # If set signed identifier without specifying the access policy then it will be default to None
        signed_identifier2 = {'testid': access_policy, 'test2': access_policy}
        await file_system.set_file_system_access_policy(signed_identifier2)
        acl2 = await file_system.get_file_system_access_policy()
        self.assertIsNone(acl2['public_access'])
        self.assertEqual(len(acl2['signed_identifiers']), 2)

    @DataLakePreparer()
    async def test_list_file_systems_by_page_async(self, datalake_storage_account_name, datalake_storage_account_key):
        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        # Arrange
        for i in range(0, 6):
            await self._create_file_system(file_system_prefix="filesystem{}".format(i))

        # Act
        file_systems = []
        async for fs in await self.dsc.list_file_systems(
                results_per_page=3,
                name_starts_with="file",
                include_metadata=True).by_page().__anext__():
            file_systems.append(fs)

        # Assert
        self.assertIsNotNone(file_systems)
        self.assertGreaterEqual(len(file_systems), 3)

    @DataLakePreparer()
    async def test_list_file_systems_with_public_access_async(self, datalake_storage_account_name, datalake_storage_account_key):
        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        # Arrange
        file_system_name = self._get_file_system_reference()
        file_system = self.dsc.get_file_system_client(file_system_name)
        await file_system.create_file_system(public_access="blob")
        metadata = {'hello': 'world', 'number': '42'}
        await file_system.set_file_system_metadata(metadata)

        # Act
        file_systems = []
        async for fs in self.dsc.list_file_systems(name_starts_with=file_system.file_system_name,
                                                   include_metadata=True):
            file_systems.append(fs)

        # Assert
        self.assertIsNotNone(file_systems)
        self.assertGreaterEqual(len(file_systems), 1)
        self.assertIsNotNone(file_systems[0])
        self.assertNamedItemInContainer(file_systems, file_system.file_system_name)
        self.assertDictEqual(file_systems[0].metadata, metadata)
        self.assertTrue(file_systems[0].public_access is PublicAccess.File)

    @DataLakePreparer()
    async def test_get_file_system_properties_async(self, datalake_storage_account_name, datalake_storage_account_key):
        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        # Arrange
        metadata = {'hello': 'world', 'number': '42'}
        file_system = await self._create_file_system()
        await file_system.set_file_system_metadata(metadata)

        # Act
        props = await file_system.get_file_system_properties()

        # Assert
        self.assertIsNotNone(props)
        self.assertDictEqual(props.metadata, metadata)
        self.assertIsNotNone(props.has_immutability_policy)
        self.assertIsNotNone(props.has_legal_hold)

    @DataLakePreparer()
    async def test_service_client_session_closes_after_filesystem_creation(self, datalake_storage_account_name, datalake_storage_account_key):
        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        # Arrange
        dsc2 = DataLakeServiceClient(self.dsc.url, credential=datalake_storage_account_key)
        async with DataLakeServiceClient(
                self.dsc.url, credential=datalake_storage_account_key) as ds_client:
            fs1 = await ds_client.create_file_system(self._get_file_system_reference(prefix="fs1"))
            await fs1.delete_file_system()
        await dsc2.create_file_system(self._get_file_system_reference(prefix="fs2"))
        await dsc2.close()

    @DataLakePreparer()
    async def test_list_paths_async(self, datalake_storage_account_name, datalake_storage_account_key):
        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        # Arrange
        file_system = await self._create_file_system()
        for i in range(0, 6):
            await file_system.create_directory("dir1{}".format(i))

        paths = []
        async for path in file_system.get_paths(upn=True):
            paths.append(path)

        self.assertEqual(len(paths), 6)

    @DataLakePreparer()
    async def test_list_paths_which_are_all_files_async(self, datalake_storage_account_name, datalake_storage_account_key):
        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        # Arrange
        file_system = await self._create_file_system()
        for i in range(0, 6):
            await file_system.create_file("file{}".format(i))

        paths = []
        async for path in file_system.get_paths(upn=True):
            paths.append(path)

        self.assertEqual(len(paths), 6)

    @DataLakePreparer()
    async def test_list_paths_with_max_per_page_async(self, datalake_storage_account_name, datalake_storage_account_key):
        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        # Arrange
        file_system = await self._create_file_system()
        for i in range(0, 6):
            await file_system.create_directory("dir1{}".format(i))

        generator1 = file_system.get_paths(max_results=2, upn=True).by_page()
        paths1 = []
        async for path in await generator1.__anext__():
            paths1.append(path)

        generator2 = file_system.get_paths(max_results=4, upn=True) \
            .by_page(continuation_token=generator1.continuation_token)
        paths2 = []
        async for path in await generator2.__anext__():
            paths2.append(path)

        self.assertEqual(len(paths1), 2)
        self.assertEqual(len(paths2), 4)

    @DataLakePreparer()
    async def test_list_paths_under_specific_path_async(self, datalake_storage_account_name, datalake_storage_account_key):
        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        # Arrange
        file_system = await self._create_file_system()
        for i in range(0, 6):
            dir = await file_system.create_directory("dir1{}".format(i))

            # create a subdirectory under the current directory
            subdir = await dir.create_sub_directory("subdir")
            await subdir.create_sub_directory("subsub")

            # create a file under the current directory
            file_client = await subdir.create_file("file")
            await file_client.append_data(b"abced", 0, 5)
            await file_client.flush_data(5)

        generator1 = file_system.get_paths(path="dir10/subdir", max_results=2, upn=True).by_page()
        paths = []
        async for path in await generator1.__anext__():
            paths.append(path)

        self.assertEqual(len(paths), 2)
        self.assertEqual(paths[0].content_length, 5)

    @DataLakePreparer()
    async def test_list_paths_recursively_async(self, datalake_storage_account_name, datalake_storage_account_key):
        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        # Arrange
        file_system = await self._create_file_system()
        for i in range(0, 6):
            dir = await file_system.create_directory("dir1{}".format(i))

            # create a subdirectory under the current directory
            subdir = await dir.create_sub_directory("subdir")
            await subdir.create_sub_directory("subsub")

            # create a file under the current directory
            await subdir.create_file("file")

        paths = []
        async for path in file_system.get_paths(recursive=True, upn=True):
            paths.append(path)

        # there are 24 subpaths in total
        self.assertEqual(len(paths), 24)

    @DataLakePreparer()
    async def test_list_paths_pages_correctly(self, datalake_storage_account_name, datalake_storage_account_key):
        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        # Arrange
        file_system = await self._create_file_system(file_system_prefix="filesystem1")
        for i in range(0, 6):
            await file_system.create_directory("dir1{}".format(i))
        for i in range(0, 6):
            await file_system.create_file("file{}".format(i))

        generator = file_system.get_paths(max_results=6, upn=True).by_page()
        paths1 = []
        async for path in await generator.__anext__():
            paths1.append(path)
        paths2 = []
        async for path in await generator.__anext__():
            paths2.append(path)

        with self.assertRaises(StopAsyncIteration):
            paths3 = []
            async for path in await generator.__anext__():
                paths3.append(path)

        self.assertEqual(len(paths1), 6)
        self.assertEqual(len(paths2), 6)

    @DataLakePreparer()
    async def test_create_directory_from_file_system_client_async(self, datalake_storage_account_name, datalake_storage_account_key):
        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        # Arrange
        file_system = await self._create_file_system()
        await file_system.create_directory("dir1/dir2")

        paths = []
        async for path in file_system.get_paths(recursive=False, upn=True):
            paths.append(path)

        self.assertEqual(len(paths), 1)
        self.assertEqual(paths[0].name, "dir1")

    @DataLakePreparer()
    async def test_create_file_from_file_system_client_async(self, datalake_storage_account_name, datalake_storage_account_key):
        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        # Arrange
        file_system = await self._create_file_system()
        await file_system.create_file("dir1/dir2/file")

        paths = []
        async for path in file_system.get_paths(recursive=True, upn=True):
            paths.append(path)
        self.assertEqual(len(paths), 3)
        self.assertEqual(paths[0].name, "dir1")
        self.assertEqual(paths[2].is_directory, False)

    @DataLakePreparer()
    async def test_get_root_directory_client_async(self, datalake_storage_account_name, datalake_storage_account_key):
        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        file_system = await self._create_file_system()
        directory_client = file_system._get_root_directory_client()

        acl = 'user::rwx,group::r-x,other::rwx'
        await directory_client.set_access_control(acl=acl)
        access_control = await directory_client.get_access_control()

        self.assertEqual(acl, access_control['acl'])

    @pytest.mark.live_test_only
    @DataLakePreparer()
    async def test_get_access_control_using_delegation_sas_async(self, datalake_storage_account_name, datalake_storage_account_key):
        self._setUp(datalake_storage_account_name, datalake_storage_account_key)

        url = self._get_account_url(datalake_storage_account_name)
        token_credential = self.generate_oauth_token()
        dsc = DataLakeServiceClient(url, token_credential, logging_enable=True)
        file_system_name = self._get_file_system_reference()
        directory_client_name = '/'
        (await dsc.create_file_system(file_system_name)).get_directory_client(directory_client_name)

        directory_client = self.dsc.get_directory_client(file_system_name, directory_client_name)
        random_guid = uuid.uuid4()
        await directory_client.set_access_control(owner=random_guid,
                                                  permissions='0777')
        acl = await directory_client.get_access_control()

        delegation_key = await dsc.get_user_delegation_key(datetime.utcnow(),
                                                           datetime.utcnow() + timedelta(hours=1))

        token = generate_file_system_sas(
            dsc.account_name,
            file_system_name,
            delegation_key,
            permission=FileSystemSasPermissions(read=True, execute=True, manage_access_control=True, manage_ownership=True),
            expiry=datetime.utcnow() + timedelta(hours=1),
            agent_object_id=random_guid
        )
        sas_directory_client = DataLakeDirectoryClient(self.dsc.url, file_system_name, directory_client_name,
                                                       credential=token, logging_enable=True)
        access_control = await sas_directory_client.get_access_control()

        self.assertIsNotNone(access_control)

    @pytest.mark.live_test_only
    @DataLakePreparer()
    async def test_list_paths_using_file_sys_delegation_sas_async(self, datalake_storage_account_name, datalake_storage_account_key):
        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        url = self._get_account_url(datalake_storage_account_name)
        token_credential = self.generate_oauth_token()
        dsc = DataLakeServiceClient(url, token_credential)
        file_system_name = self._get_file_system_reference()
        directory_client_name = '/'
        directory_client = (await dsc.create_file_system(file_system_name)).get_directory_client(directory_client_name)

        random_guid = uuid.uuid4()
        await directory_client.set_access_control(owner=random_guid, permissions='0777')

        delegation_key = await dsc.get_user_delegation_key(datetime.utcnow(),
                                                           datetime.utcnow() + timedelta(hours=1))

        token = generate_file_system_sas(
            dsc.account_name,
            file_system_name,
            delegation_key,
            permission=DirectorySasPermissions(list=True),
            expiry=datetime.utcnow() + timedelta(hours=1),
            agent_object_id=random_guid
        )
        sas_directory_client = FileSystemClient(self.dsc.url, file_system_name,
                                                credential=token)
        paths = list()
        async for path in sas_directory_client.get_paths():
            paths.append(path)

        self.assertEqual(0, 0)

    @DataLakePreparer()
    async def test_file_system_sessions_closes_properly_async(self, datalake_storage_account_name, datalake_storage_account_key):
        self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        # Arrange
        file_system_client = await self._create_file_system("fs")
        async with file_system_client as fs_client:
            async with fs_client.get_file_client("file1.txt") as f_client:
                await f_client.create_file()
            async with fs_client.get_file_client("file2.txt") as f_client:
                await f_client.create_file()
            async with fs_client.get_directory_client("file1") as f_client:
                await f_client.create_directory()
            async with fs_client.get_directory_client("file2") as f_client:
                await f_client.create_directory()

# ------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
