# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import pytest
import unittest
import asyncio
import time
from datetime import datetime, timedelta

from azure.core import MatchConditions
from azure.core.pipeline.transport import AioHttpTransport
from multidict import CIMultiDict, CIMultiDictProxy

from azure.core.exceptions import HttpResponseError, ResourceExistsError, ResourceNotFoundError, \
    ResourceModifiedError
from azure.storage.filedatalake import ContentSettings, DirectorySasPermissions
from azure.storage.filedatalake import generate_directory_sas
from azure.storage.filedatalake.aio import DataLakeServiceClient, DataLakeDirectoryClient

from testcase import (
    StorageTestCase,
    record,
    TestMode

)

# ------------------------------------------------------------------------------
TEST_DIRECTORY_PREFIX = 'directory'


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


class DirectoryTest(StorageTestCase):
    def setUp(self):
        super(DirectoryTest, self).setUp()
        url = self._get_account_url()
        self.dsc = DataLakeServiceClient(url, credential=self.settings.STORAGE_DATA_LAKE_ACCOUNT_KEY,
                                         transport=AiohttpTestTransport())

        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.dsc.__aenter__())
        self.config = self.dsc._config

        self.file_system_name = self.get_resource_name('filesystem')

        if not self.is_playback():
            file_system = self.dsc.get_file_system_client(self.file_system_name)
            try:
                loop.run_until_complete(file_system.create_file_system(timeout=5))
            except ResourceExistsError:
                pass

    def tearDown(self):
        if not self.is_playback():
            try:
                loop = asyncio.get_event_loop()
                loop.run_until_complete(self.dsc.delete_file_system(self.file_system_name))
                loop.run_until_complete(self.dsc.__aexit__())
            except:
                pass

        return super(DirectoryTest, self).tearDown()

    # --Helpers-----------------------------------------------------------------
    def _get_directory_reference(self, prefix=TEST_DIRECTORY_PREFIX):
        directory_name = self.get_resource_name(prefix)
        return directory_name

    async def _create_directory_and_get_directory_client(self, directory_name=None):
        directory_name = directory_name if directory_name else self._get_directory_reference()
        directory_client = self.dsc.get_directory_client(self.file_system_name, directory_name)
        await directory_client.create_directory()
        return directory_client

    async def _create_file_system(self):
        return await self.dsc.create_file_system(self._get_file_system_reference())

    # --Helpers-----------------------------------------------------------------

    async def _test_create_directory(self):
        # Arrange
        directory_name = self._get_directory_reference()
        content_settings = ContentSettings(
            content_language='spanish',
            content_disposition='inline')
        # Act
        directory_client = self.dsc.get_directory_client(self.file_system_name, directory_name)
        created = await directory_client.create_directory(content_settings=content_settings)

        # Assert
        self.assertTrue(created)

    @record
    def test_create_directory_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_create_directory())

    async def _test_using_oauth_token_credential_to_create_directory(self):
        # generate a token with directory level create permission
        directory_name = self._get_directory_reference()

        token_credential = self.generate_async_oauth_token()
        directory_client = DataLakeDirectoryClient(self.dsc.url, self.file_system_name, directory_name,
                                                   credential=token_credential)
        response = await directory_client.create_directory()
        self.assertIsNotNone(response)

    @record
    def test_using_oauth_token_credential_to_create_directory_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_using_oauth_token_credential_to_create_directory())

    async def _test_create_directory_with_match_conditions(self):
        # Arrange
        directory_name = self._get_directory_reference()

        # Act
        directory_client = self.dsc.get_directory_client(self.file_system_name, directory_name)
        created = await directory_client.create_directory(match_condition=MatchConditions.IfMissing)

        # Assert
        self.assertTrue(created)

    @record
    def test_create_directory_with_match_conditions_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_create_directory_with_match_conditions())

    async def _test_create_directory_with_permission(self):
        # Arrange
        directory_name = self._get_directory_reference()

        # Act
        directory_client = self.dsc.get_directory_client(self.file_system_name, directory_name)
        created = await directory_client.create_directory(permissions="rwxr--r--", umask="0000")

        prop = await directory_client.get_access_control()

        # Assert
        self.assertTrue(created)
        self.assertEqual(prop['permissions'], 'rwxr--r--')

    @record
    def test_create_directory_with_permission_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_create_directory_with_permission())

    async def _test_create_directory_with_content_settings(self):
        # Arrange
        directory_name = self._get_directory_reference()
        content_settings = ContentSettings(
            content_language='spanish',
            content_disposition='inline')
        # Act
        directory_client = self.dsc.get_directory_client(self.file_system_name, directory_name)
        created = await directory_client.create_directory(content_settings=content_settings)

        # Assert
        self.assertTrue(created)

    @record
    def test_create_directory_with_content_settings_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_create_directory_with_content_settings())

    async def _test_create_directory_with_metadata(self):
        # Arrange
        directory_name = self._get_directory_reference()
        metadata = {'hello': 'world', 'number': '42'}
        # Act
        directory_client = self.dsc.get_directory_client(self.file_system_name, directory_name)
        created = await directory_client.create_directory(metadata=metadata)

        properties = await directory_client.get_directory_properties()

        # Assert
        self.assertTrue(created)

    @record
    def test_create_directory_with_metadata_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_create_directory_with_metadata())

    async def _test_delete_directory(self):
        # Arrange
        directory_name = self._get_directory_reference()
        metadata = {'hello': 'world', 'number': '42'}
        directory_client = self.dsc.get_directory_client(self.file_system_name, directory_name)
        await directory_client.create_directory(metadata=metadata)

        response = await directory_client.delete_directory()
        # Assert
        self.assertIsNone(response)

    @record
    def test_delete_directory_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_delete_directory())

    async def _test_delete_directory_with_if_modified_since(self):
        # Arrange
        directory_name = self._get_directory_reference()

        directory_client = self.dsc.get_directory_client(self.file_system_name, directory_name)
        await directory_client.create_directory()
        prop = await directory_client.get_directory_properties()

        with self.assertRaises(ResourceModifiedError):
            await directory_client.delete_directory(if_modified_since=prop['last_modified'])

    @record
    def test_delete_directory_with_if_modified_since_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_delete_directory_with_if_modified_since())

    async def _test_create_sub_directory_and_delete_sub_directory(self):
        # Arrange
        directory_name = self._get_directory_reference()
        metadata = {'hello': 'world', 'number': '42'}

        # Create a directory first, to prepare for creating sub directory
        directory_client = self.dsc.get_directory_client(self.file_system_name, directory_name)
        await directory_client.create_directory(metadata=metadata)

        # Create sub directory from the current directory
        sub_directory_name = 'subdir'
        sub_directory_created = await directory_client.create_sub_directory(sub_directory_name)

        # to make sure the sub directory was indeed created by get sub_directory properties from sub directory client
        sub_directory_client = self.dsc.get_directory_client(self.file_system_name,
                                                             directory_name + '/' + sub_directory_name)
        sub_properties = await sub_directory_client.get_directory_properties()

        # Assert
        self.assertTrue(sub_directory_created)
        self.assertTrue(sub_properties)

        # Act
        await directory_client.delete_sub_directory(sub_directory_name)
        with self.assertRaises(ResourceNotFoundError):
            await sub_directory_client.get_directory_properties()

    @record
    def test_create_sub_directory_and_delete_sub_directory_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_create_sub_directory_and_delete_sub_directory())

    async def _test_set_access_control(self):
        directory_name = self._get_directory_reference()
        metadata = {'hello': 'world', 'number': '42'}
        directory_client = self.dsc.get_directory_client(self.file_system_name, directory_name)
        await directory_client.create_directory(metadata=metadata)

        response = await directory_client.set_access_control(permissions='0777')
        # Assert
        self.assertIsNotNone(response)

    @record
    def test_set_access_control_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_set_access_control())

    async def _test_set_access_control_with_acl(self):
        directory_name = self._get_directory_reference()
        metadata = {'hello': 'world', 'number': '42'}
        directory_client = self.dsc.get_directory_client(self.file_system_name, directory_name)
        await directory_client.create_directory(metadata=metadata)

        acl = 'user::rwx,group::r-x,other::rwx'
        await directory_client.set_access_control(acl=acl)
        access_control = await directory_client.get_access_control()

        # Assert

        self.assertIsNotNone(access_control)
        self.assertEqual(acl, access_control['acl'])

    @record
    def test_set_access_control_with_acl_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_set_access_control_with_acl())

    async def _test_set_access_control_if_none_modified(self):
        directory_name = self._get_directory_reference()
        directory_client = self.dsc.get_directory_client(self.file_system_name, directory_name)
        resp = await directory_client.create_directory()

        response = await directory_client.set_access_control(permissions='0777', etag=resp['etag'],
                                                             match_condition=MatchConditions.IfNotModified)
        # Assert
        self.assertIsNotNone(response)

    @record
    def test_set_access_control_if_none_modified_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_set_access_control_if_none_modified())

    async def _test_get_access_control(self):
        directory_name = self._get_directory_reference()
        metadata = {'hello': 'world', 'number': '42'}
        directory_client = self.dsc.get_directory_client(self.file_system_name, directory_name)
        await directory_client.create_directory(metadata=metadata, permissions='0777')

        # Act
        response = await directory_client.get_access_control()
        # Assert
        self.assertIsNotNone(response)

    @record
    def test_get_access_control_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_get_access_control())

    async def _test_get_access_control_with_match_conditions(self):
        directory_name = self._get_directory_reference()
        directory_client = self.dsc.get_directory_client(self.file_system_name, directory_name)
        resp = await directory_client.create_directory(permissions='0777', umask='0000')

        # Act
        response = await directory_client.get_access_control(etag=resp['etag'],
                                                             match_condition=MatchConditions.IfNotModified)
        # Assert
        self.assertIsNotNone(response)
        self.assertEquals(response['permissions'], 'rwxrwxrwx')

    @record
    def test_get_access_control_with_match_conditions_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_get_access_control_with_match_conditions())

    async def _test_rename_from(self):
        metadata = {'hello': 'world', 'number': '42'}
        directory_name = self._get_directory_reference()
        directory_client = self.dsc.get_directory_client(self.file_system_name, directory_name)
        await directory_client.create_directory()

        new_name = "newname"

        new_directory_client = self.dsc.get_directory_client(self.file_system_name, new_name)

        await new_directory_client._rename_path('/' + self.file_system_name + '/' + directory_name, metadata=metadata)
        properties = await new_directory_client.get_directory_properties()

        self.assertIsNotNone(properties)

    @record
    def test_rename_from_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_rename_from())

    async def _test_rename_from_a_shorter_directory_to_longer_directory(self):
        # TODO: investigate why rename shorter path to a longer one does not work
        pytest.skip("")
        directory_name = self._get_directory_reference()
        await self._create_directory_and_get_directory_client(directory_name="old")

        new_name = "newname"
        new_directory_client = await self._create_directory_and_get_directory_client(directory_name=new_name)
        new_directory_client = await new_directory_client.create_sub_directory("newsub")

        await new_directory_client._rename_path('/' + self.file_system_name + '/' + directory_name)
        properties = await new_directory_client.get_directory_properties()

        self.assertIsNotNone(properties)

    @record
    def test_rename_from_a_shorter_directory_to_longer_directory_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_rename_from_a_shorter_directory_to_longer_directory())

    async def _test_rename_from_a_directory_in_another_file_system(self):
        # create a file dir1 under file system1
        old_file_system_name = "oldfilesystem"
        old_dir_name = "olddir"
        old_client = self.dsc.get_file_system_client(old_file_system_name)
        time.sleep(30)
        await old_client.create_file_system()
        await old_client.create_directory(old_dir_name)

        # create a dir2 under file system2
        new_name = "newname"
        time.sleep(5)
        new_directory_client = await self._create_directory_and_get_directory_client(directory_name=new_name)
        new_directory_client = await new_directory_client.create_sub_directory("newsub")

        # rename dir1 under file system1 to dir2 under file system2
        await new_directory_client._rename_path('/' + old_file_system_name + '/' + old_dir_name)
        properties = await new_directory_client.get_directory_properties()

        self.assertIsNotNone(properties)
        await self.dsc.delete_file_system(old_file_system_name)

    @record
    def test_rename_from_a_directory_in_another_file_system_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_rename_from_a_directory_in_another_file_system())

    async def _test_rename_to_an_existing_directory_in_another_file_system(self):
        # create a file dir1 under file system1
        destination_file_system_name = "destfilesystem"
        destination_dir_name = "destdir"
        fs_client = self.dsc.get_file_system_client(destination_file_system_name)
        time.sleep(30)
        await fs_client.create_file_system()
        destination_directory_client = await fs_client.create_directory(destination_dir_name)

        # create a dir2 under file system2
        source_name = "source"
        source_directory_client = await self._create_directory_and_get_directory_client(directory_name=source_name)
        source_directory_client = await source_directory_client.create_sub_directory("subdir")

        # rename dir2 under file system2 to dir1 under file system1
        res = await source_directory_client.rename_directory(
            '/' + destination_file_system_name + '/' + destination_dir_name)

        # the source directory has been renamed to destination directory, so it cannot be found
        with self.assertRaises(HttpResponseError):
            await source_directory_client.get_directory_properties()

        self.assertEquals(res.url, destination_directory_client.url)

    @record
    def test_rename_to_an_existing_directory_in_another_file_system_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_rename_to_an_existing_directory_in_another_file_system())

    async def _test_rename_with_none_existing_destination_condition_and_source_unmodified_condition(self):
        non_existing_dir_name = "nonexistingdir"

        # create a file system1
        destination_file_system_name = self._get_directory_reference("destfilesystem")
        fs_client = self.dsc.get_file_system_client(destination_file_system_name)
        await fs_client.create_file_system()

        # create a dir2 under file system2
        source_name = "source"
        source_directory_client = await self._create_directory_and_get_directory_client(directory_name=source_name)
        source_directory_client = await source_directory_client.create_sub_directory("subdir")

        # rename dir2 under file system2 to a non existing directory under file system1,
        # when dir1 does not exist and dir2 wasn't modified
        properties = await source_directory_client.get_directory_properties()
        etag = properties['etag']
        res = await source_directory_client.rename_directory(
            '/' + destination_file_system_name + '/' + non_existing_dir_name,
            match_condition=MatchConditions.IfMissing,
            source_etag=etag,
            source_match_condition=MatchConditions.IfNotModified)

        # the source directory has been renamed to destination directory, so it cannot be found
        with self.assertRaises(HttpResponseError):
            await source_directory_client.get_directory_properties()

        self.assertEquals(non_existing_dir_name, res.path_name)

    @record
    def test_rename_with_none_existing_destination_condition_and_source_unmodified_condition_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._test_rename_with_none_existing_destination_condition_and_source_unmodified_condition())

    async def _test_rename_to_an_non_existing_directory_in_another_file_system(self):
        # create a file dir1 under file system1
        destination_file_system_name = self._get_directory_reference("destfilesystem")
        non_existing_dir_name = "nonexistingdir"
        fs_client = self.dsc.get_file_system_client(destination_file_system_name)
        await fs_client.create_file_system()

        # create a dir2 under file system2
        source_name = "source"
        source_directory_client = await self._create_directory_and_get_directory_client(directory_name=source_name)
        source_directory_client = await source_directory_client.create_sub_directory("subdir")

        # rename dir2 under file system2 to dir1 under file system1
        res = await source_directory_client.rename_directory(
            '/' + destination_file_system_name + '/' + non_existing_dir_name)

        # the source directory has been renamed to destination directory, so it cannot be found
        with self.assertRaises(HttpResponseError):
            await source_directory_client.get_directory_properties()

        self.assertEquals(non_existing_dir_name, res.path_name)

    @record
    def test_rename_to_an_non_existing_directory_in_another_file_system_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_rename_to_an_non_existing_directory_in_another_file_system())

    async def _test_rename_directory_to_non_empty_directory(self):
        # TODO: investigate why rename non empty dir doesn't work
        pytest.skip("")
        dir1 = await self._create_directory_and_get_directory_client("dir1")
        await dir1.create_sub_directory("subdir")

        dir2 = await self._create_directory_and_get_directory_client("dir2")
        await dir2.rename_directory(dir1.file_system_name + '/' + dir1.path_name)

        with self.assertRaises(HttpResponseError):
            await dir2.get_directory_properties()

    @record
    def test_rename_directory_to_non_empty_directory_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_rename_directory_to_non_empty_directory())

    async def _test_get_properties(self):
        # Arrange
        directory_name = self._get_directory_reference()
        metadata = {'hello': 'world', 'number': '42'}
        directory_client = self.dsc.get_directory_client(self.file_system_name, directory_name)
        await directory_client.create_directory(metadata=metadata)

        properties = await directory_client.get_directory_properties()
        # Assert
        self.assertTrue(properties)
        self.assertIsNotNone(properties.metadata)
        self.assertEqual(properties.metadata['hello'], metadata['hello'])

    @record
    def test_get_properties_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_get_properties())

    async def _test_using_directory_sas_to_read(self):
        # SAS URL is calculated from storage key, so this test runs live only
        if TestMode.need_recording_file(self.test_mode):
            return

        client = await self._create_directory_and_get_directory_client()
        directory_name = client.path_name

        # generate a token with directory level read permission
        token = generate_directory_sas(
            self.dsc.account_name,
            self.file_system_name,
            directory_name,
            account_key=self.dsc.credential.account_key,
            permission=DirectorySasPermissions(read=True),
            expiry=datetime.utcnow() + timedelta(hours=1),
        )

        directory_client = DataLakeDirectoryClient(self.dsc.url, self.file_system_name, directory_name,
                                                   credential=token)
        access_control = await directory_client.get_access_control()

        self.assertIsNotNone(access_control)

    @record
    def test_using_directory_sas_to_read_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_using_directory_sas_to_read())

    async def _test_using_directory_sas_to_create(self):
        # SAS URL is calculated from storage key, so this test runs live only
        if TestMode.need_recording_file(self.test_mode):
            return

        # generate a token with directory level create permission
        directory_name = self._get_directory_reference()
        token = generate_directory_sas(
            self.dsc.account_name,
            self.file_system_name,
            directory_name,
            account_key=self.dsc.credential.account_key,
            permission=DirectorySasPermissions(create=True),
            expiry=datetime.utcnow() + timedelta(hours=1),
        )
        directory_client = DataLakeDirectoryClient(self.dsc.url, self.file_system_name, directory_name,
                                                   credential=token)
        response = await directory_client.create_directory()
        self.assertIsNotNone(response)

    @record
    def test_using_directory_sas_to_create_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_using_directory_sas_to_create())


# ------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
