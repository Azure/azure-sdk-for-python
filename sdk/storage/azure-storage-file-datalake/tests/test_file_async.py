# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import unittest
from datetime import datetime, timedelta
import asyncio

from azure.core import MatchConditions

from azure.core.exceptions import HttpResponseError, ResourceExistsError, ResourceNotFoundError, \
    ClientAuthenticationError, ResourceModifiedError
from azure.storage.filedatalake import ContentSettings, generate_account_sas, generate_file_sas, \
    ResourceTypes, AccountSasPermissions, FileSasPermissions
from azure.storage.filedatalake.aio import DataLakeServiceClient, FileSystemClient, DataLakeDirectoryClient, \
    DataLakeFileClient
from azure.storage.filedatalake._generated.models import StorageErrorException
from testcase import (
    StorageTestCase,
    record,
    TestMode
)

# ------------------------------------------------------------------------------
TEST_DIRECTORY_PREFIX = 'directory'
TEST_FILE_PREFIX = 'file'
FILE_PATH = 'file_output.temp.dat'
# ------------------------------------------------------------------------------


class FileTest(StorageTestCase):
    def setUp(self):
        super(FileTest, self).setUp()
        url = self._get_account_url()
        self.dsc = DataLakeServiceClient(url, credential=self.settings.STORAGE_DATA_LAKE_ACCOUNT_KEY)
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.dsc.__aenter__())

        self.config = self.dsc._config

        self.file_system_name = self.get_resource_name('filesystem')

        if not self.is_playback():
            file_system = self.dsc.get_file_system_client(self.file_system_name)
            try:
                loop = asyncio.get_event_loop()
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

        return super(FileTest, self).tearDown()

    # --Helpers-----------------------------------------------------------------
    def _get_directory_reference(self, prefix=TEST_DIRECTORY_PREFIX):
        directory_name = self.get_resource_name(prefix)
        return directory_name

    def _get_file_reference(self, prefix=TEST_FILE_PREFIX):
        file_name = self.get_resource_name(prefix)
        return file_name

    async def _create_file_system(self):
        return await self.dsc.create_file_system(self._get_file_system_reference())

    async def _create_directory_and_return_client(self, directory=None):
        directory_name = directory if directory else self._get_directory_reference()
        directory_client = self.dsc.get_directory_client(self.file_system_name, directory_name)
        await directory_client.create_directory()
        return directory_client

    async def _create_file_and_return_client(self, directory="", file=None):
        if directory:
            await self._create_directory_and_return_client(directory)
        if not file:
            file = self._get_file_reference()
        file_client = self.dsc.get_file_client(self.file_system_name, directory + '/' + file)
        await file_client.create_file()
        return file_client

    # --Helpers-----------------------------------------------------------------

    async def _test_create_file(self):
        # Arrange
        directory_name = self._get_directory_reference()

        # Create a directory to put the file under that
        directory_client = self.dsc.get_directory_client(self.file_system_name, directory_name)
        await directory_client.create_directory()

        file_client = directory_client.get_file_client('filename')
        response = await file_client.create_file()

        # Assert
        self.assertIsNotNone(response)

    @record
    def test_create_file_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_create_file())

    async def _test_create_file_using_oauth_token_credential(self):
        # Arrange
        file_name = self._get_file_reference()
        token_credential = self.generate_async_oauth_token()

        # Create a directory to put the file under that
        file_client = DataLakeFileClient(self.dsc.url, self.file_system_name, file_name,
                                         credential=token_credential)

        response = await file_client.create_file()

        # Assert
        self.assertIsNotNone(response)

    @record
    def test_create_file_using_oauth_token_credential_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_create_file_using_oauth_token_credential())

    async def _test_create_file_with_existing_name(self):
        # Arrange
        file_client = await self._create_file_and_return_client()

        with self.assertRaises(ResourceExistsError):
            # if the file exists then throw error
            # if_none_match='*' is to make sure no existing file
            await file_client.create_file(match_condition=MatchConditions.IfMissing)

    @record
    def test_create_file_with_existing_name_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_create_file_with_existing_name())

    async def _test_create_file_with_lease_id(self):
        # Arrange
        directory_name = self._get_directory_reference()
        directory_client = self.dsc.get_directory_client(self.file_system_name, directory_name)
        await directory_client.create_directory()

        file_client = directory_client.get_file_client('filename')
        # Act
        await file_client.create_file()
        lease = await file_client.acquire_lease()
        create_resp = await file_client.create_file(lease=lease)

        # Assert
        file_properties = await file_client.get_file_properties()
        self.assertIsNotNone(file_properties)
        self.assertEqual(file_properties.etag, create_resp.get('etag'))
        self.assertEqual(file_properties.last_modified, create_resp.get('last_modified'))

    @record
    def test_create_file_with_lease_id_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_create_file_with_lease_id())

    async def _test_create_file_under_root_directory(self):
        # Arrange
        # get a file client to interact with the file under root directory
        file_client = self.dsc.get_file_client(self.file_system_name, "filename")

        response = await file_client.create_file()

        # Assert
        self.assertIsNotNone(response)

    @record
    def test_create_file_under_root_directory_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_create_file_under_root_directory())

    async def _test_append_data(self):
        directory_name = self._get_directory_reference()

        # Create a directory to put the file under that
        directory_client = self.dsc.get_directory_client(self.file_system_name, directory_name)
        await directory_client.create_directory()

        file_client = directory_client.get_file_client('filename')
        await file_client.create_file()

        # Act
        response = await file_client.append_data(b'abc', 0, 3)

        self.assertIsNotNone(response)

    @record
    def test_append_data_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_append_data())

    async def _test_append_empty_data(self):
        file_client = await self._create_file_and_return_client()

        # Act
        await file_client.flush_data(0)
        file_props = await file_client.get_file_properties()

        self.assertIsNotNone(file_props['size'], 0)

    @record
    def test_append_empty_data_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_append_empty_data())

    async def _test_flush_data(self):
        directory_name = self._get_directory_reference()

        # Create a directory to put the file under that
        directory_client = self.dsc.get_directory_client(self.file_system_name, directory_name)
        await directory_client.create_directory()

        file_client = directory_client.get_file_client('filename')
        await file_client.create_file()

        # Act
        await file_client.append_data(b'abc', 0, 3)
        response = await file_client.flush_data(3)

        # Assert
        prop = await file_client.get_file_properties()
        self.assertIsNotNone(response)
        self.assertEqual(prop['size'], 3)

    @record
    def test_flush_data_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_flush_data())

    async def _test_flush_data_with_match_condition(self):
        directory_name = self._get_directory_reference()

        # Create a directory to put the file under that
        directory_client = self.dsc.get_directory_client(self.file_system_name, directory_name)
        await directory_client.create_directory()

        file_client = directory_client.get_file_client('filename')
        resp = await file_client.create_file()

        # Act
        await file_client.append_data(b'abc', 0, 3)

        # flush is successful because it isn't touched
        response = await file_client.flush_data(3, etag=resp['etag'], match_condition=MatchConditions.IfNotModified)

        await file_client.append_data(b'abc', 3, 3)
        with self.assertRaises(ResourceModifiedError):
            # flush is unsuccessful because extra data were appended.
            await file_client.flush_data(6, etag=resp['etag'], match_condition=MatchConditions.IfNotModified)

    @record
    def test_flush_data_with_match_condition_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_flush_data_with_match_condition())

    async def _test_upload_data(self):
        # parallel upload cannot be recorded
        if TestMode.need_recording_file(self.test_mode):
            return
        directory_name = self._get_directory_reference()

        # Create a directory to put the file under that
        directory_client = self.dsc.get_directory_client(self.file_system_name, directory_name)
        await directory_client.create_directory()

        file_client = directory_client.get_file_client('filename')
        data = self.get_random_bytes(400*1024)
        await file_client.upload_data(data, overwrite=True, max_concurrency=5)

        downloaded_data = await (await file_client.download_file()).readall()
        self.assertEqual(data, downloaded_data)

    def test_upload_data_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_upload_data())

    async def _test_upload_data_to_existing_file_async(self):
        directory_name = self._get_directory_reference()

        # Create a directory to put the file under that
        directory_client = self.dsc.get_directory_client(self.file_system_name, directory_name)
        await directory_client.create_directory()

        # create an existing file
        file_client = directory_client.get_file_client('filename')
        await file_client.create_file()
        await file_client.append_data(b"abc", 0)
        await file_client.flush_data(3)

        # to override the existing file
        data = self.get_random_bytes(100)
        with self.assertRaises(HttpResponseError):
            await file_client.upload_data(data, max_concurrency=5)
        await file_client.upload_data(data, overwrite=True, max_concurrency=5)

        downloaded_data = await (await file_client.download_file()).readall()
        self.assertEqual(data, downloaded_data)

    @record
    def test_upload_data_to_existing_file_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_upload_data_to_existing_file_async())

    async def _test_upload_data_to_existing_file_with_content_settings_async(self):
        # etag in async recording file cannot be parsed properly
        if TestMode.need_recording_file(self.test_mode):
            return
        directory_name = self._get_directory_reference()

        # Create a directory to put the file under that
        directory_client = self.dsc.get_directory_client(self.file_system_name, directory_name)
        await directory_client.create_directory()

        # create an existing file
        file_client = directory_client.get_file_client('filename')
        resp = await file_client.create_file()
        etag = resp['etag']

        # to override the existing file
        data = self.get_random_bytes(100)
        content_settings = ContentSettings(
            content_language='spanish',
            content_disposition='inline')

        await file_client.upload_data(data, max_concurrency=5,
                                      content_settings=content_settings, etag=etag,
                                      match_condition=MatchConditions.IfNotModified)

        downloaded_data = await (await file_client.download_file()).readall()
        properties = await file_client.get_file_properties()

        self.assertEqual(data, downloaded_data)
        self.assertEqual(properties.content_settings.content_language, content_settings.content_language)

    @record
    def test_upload_data_to_existing_file_with_content_settings_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_upload_data_to_existing_file_with_content_settings_async())

    async def _test_upload_data_to_existing_file_with_permissions_and_umask_async(self):
        # etag in async recording file cannot be parsed properly
        if TestMode.need_recording_file(self.test_mode):
            return
        directory_name = self._get_directory_reference()

        # Create a directory to put the file under that
        directory_client = self.dsc.get_directory_client(self.file_system_name, directory_name)
        await directory_client.create_directory()

        # create an existing file
        file_client = directory_client.get_file_client('filename')
        resp = await file_client.create_file()
        etag = resp['etag']

        # to override the existing file
        data = self.get_random_bytes(100)

        await file_client.upload_data(data,
                                      overwrite=True, max_concurrency=5,
                                      permissions='0777', umask="0000",
                                      etag=etag,
                                      match_condition=MatchConditions.IfNotModified)

        downloaded_data = await (await file_client.download_file()).readall()
        prop = await file_client.get_access_control()

        self.assertEqual(data, downloaded_data)
        self.assertEqual(prop['permissions'], 'rwxrwxrwx')

    @record
    def test_upload_data_to_existing_file_with_permission_and_umask_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_upload_data_to_existing_file_with_permissions_and_umask_async())

    async def _test_read_file(self):
        file_client = await self._create_file_and_return_client()
        data = self.get_random_bytes(1024)

        # upload data to file
        await file_client.append_data(data, 0, len(data))
        await file_client.flush_data(len(data))

        # doanload the data and make sure it is the same as uploaded data
        downloaded_data = await (await file_client.download_file()).readall()
        self.assertEqual(data, downloaded_data)

    @record
    def test_read_file_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_read_file())

    async def _test_read_file_with_user_delegation_key(self):
        # SAS URL is calculated from storage key, so this test runs live only
        if TestMode.need_recording_file(self.test_mode):
            return

        # Create file
        file_client = await self._create_file_and_return_client()
        data = self.get_random_bytes(1024)
        # Upload data to file
        await file_client.append_data(data, 0, len(data))
        await file_client.flush_data(len(data))

        # Get user delegation key
        token_credential = self.generate_async_oauth_token()
        service_client = DataLakeServiceClient(self._get_oauth_account_url(), credential=token_credential)
        user_delegation_key = await service_client.get_user_delegation_key(datetime.utcnow(),
                                                                     datetime.utcnow() + timedelta(hours=1))

        sas_token = generate_file_sas(file_client.account_name,
                                      file_client.file_system_name,
                                      None,
                                      file_client.path_name,
                                      user_delegation_key,
                                      permission=FileSasPermissions(read=True, create=True, write=True, delete=True),
                                      expiry=datetime.utcnow() + timedelta(hours=1),
                                      )

        # doanload the data and make sure it is the same as uploaded data
        new_file_client = DataLakeFileClient(self._get_account_url(),
                                             file_client.file_system_name,
                                             file_client.path_name,
                                             credential=sas_token)
        downloaded_data = await (await new_file_client.download_file()).readall()
        self.assertEqual(data, downloaded_data)

    @record
    def test_read_file_with_user_delegation_key_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_read_file_with_user_delegation_key())

    async def _test_read_file_into_file(self):
        file_client = await self._create_file_and_return_client()
        data = self.get_random_bytes(1024)

        # upload data to file
        await file_client.append_data(data, 0, len(data))
        await file_client.flush_data(len(data))

        # doanload the data into a file and make sure it is the same as uploaded data
        with open(FILE_PATH, 'wb') as stream:
            download = await file_client.download_file(max_concurrency=2)
            await download.readinto(stream)

        # Assert
        with open(FILE_PATH, 'rb') as stream:
            actual = stream.read()
            self.assertEqual(data, actual)

    @record
    def test_read_file_into_file_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_read_file_into_file())

    async def _test_read_file_to_text(self):
        file_client = await self._create_file_and_return_client()
        data = self.get_random_text_data(1024)

        # upload data to file
        await file_client.append_data(data, 0, len(data))
        await file_client.flush_data(len(data))

        # doanload the text data and make sure it is the same as uploaded data
        downloaded_data = await (await file_client.download_file(max_concurrency=2, encoding="utf-8")).readall()

        # Assert
        self.assertEqual(data, downloaded_data)

    @record
    def test_read_file_to_text_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_read_file_to_text())

    async def _test_account_sas(self):
        # SAS URL is calculated from storage key, so this test runs live only
        if TestMode.need_recording_file(self.test_mode):
            return

        file_name = self._get_file_reference()
        # create a file under root directory
        await self._create_file_and_return_client(file=file_name)

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
        properties = await file_client.get_file_properties()

        # make sure we can read the file properties
        self.assertIsNotNone(properties)

        # try to write to the created file with the token
        with self.assertRaises(HttpResponseError):
            await file_client.append_data(b"abcd", 0, 4)

    @record
    def test_account_sas_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_account_sas())

    async def _test_file_sas_only_applies_to_file_level(self):
        # SAS URL is calculated from storage key, so this test runs live only
        if TestMode.need_recording_file(self.test_mode):
            return

        file_name = self._get_file_reference()
        directory_name = self._get_directory_reference()
        await self._create_file_and_return_client(directory=directory_name, file=file_name)

        # generate a token with file level read and write permissions
        token = generate_file_sas(
            self.dsc.account_name,
            self.file_system_name,
            directory_name,
            file_name,
            self.dsc.credential.account_key,
            permission=FileSasPermissions(read=True, write=True),
            expiry=datetime.utcnow() + timedelta(hours=1),
        )

        # read the created file which is under root directory
        file_client = DataLakeFileClient(self.dsc.url, self.file_system_name, directory_name+'/'+file_name,
                                         credential=token)
        properties = await file_client.get_file_properties()

        # make sure we can read the file properties
        self.assertIsNotNone(properties)

        # try to write to the created file with the token
        response = await file_client.append_data(b"abcd", 0, 4, validate_content=True)
        self.assertIsNotNone(response)

        # the token is for file level, so users are not supposed to have access to file system level operations
        file_system_client = FileSystemClient(self.dsc.url, self.file_system_name, credential=token)
        with self.assertRaises(ClientAuthenticationError):
            await file_system_client.get_file_system_properties()

        # the token is for file level, so users are not supposed to have access to directory level operations
        directory_client = DataLakeDirectoryClient(self.dsc.url, self.file_system_name, directory_name,
                                                   credential=token)
        with self.assertRaises(ClientAuthenticationError):
            await directory_client.get_directory_properties()

    @record
    def test_file_sas_only_applies_to_file_level_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_file_sas_only_applies_to_file_level())

    async def _test_delete_file(self):
        # Arrange
        file_client = await self._create_file_and_return_client()

        await file_client.delete_file()

        with self.assertRaises(ResourceNotFoundError):
            await file_client.get_file_properties()

    @record
    def test_delete_file_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_delete_file())

    async def _test_delete_file_with_if_unmodified_since(self):
        # Arrange
        file_client = await self._create_file_and_return_client()

        prop = await file_client.get_file_properties()
        await file_client.delete_file(if_unmodified_since=prop['last_modified'])

        # Make sure the file was deleted
        with self.assertRaises(ResourceNotFoundError):
            await file_client.get_file_properties()

    @record
    def test_delete_file_with_if_unmodified_since_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_delete_file_with_if_unmodified_since())

    async def _test_set_access_control(self):
        file_client = await self._create_file_and_return_client()

        response = await file_client.set_access_control(permissions='0777')

        # Assert
        self.assertIsNotNone(response)

    @record
    def test_set_access_control_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_set_access_control())

    async def _test_set_access_control_with_match_conditions(self):
        file_client = await self._create_file_and_return_client()

        with self.assertRaises(ResourceModifiedError):
            await file_client.set_access_control(permissions='0777', match_condition=MatchConditions.IfMissing)

    @record
    def test_set_access_control_with_match_conditions_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_set_access_control_with_match_conditions())

    async def _test_get_access_control(self):
        file_client = await self._create_file_and_return_client()
        await file_client.set_access_control(permissions='0777')

        # Act
        response = await file_client.get_access_control()

        # Assert
        self.assertIsNotNone(response)

    @record
    def test_get_access_control_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_get_access_control())

    async def _test_get_access_control_with_if_modified_since(self):
        file_client = await self._create_file_and_return_client()
        await file_client.set_access_control(permissions='0777')

        prop = await file_client.get_file_properties()

        # Act
        response = await file_client.get_access_control(if_modified_since=prop['last_modified']-timedelta(minutes=15))

        # Assert
        self.assertIsNotNone(response)

    @record
    def test_get_access_control_with_if_modified_since_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_get_access_control_with_if_modified_since())

    async def _test_get_properties(self):
        # Arrange
        directory_client = await self._create_directory_and_return_client()

        metadata = {'hello': 'world', 'number': '42'}
        content_settings = ContentSettings(
            content_language='spanish',
            content_disposition='inline')
        file_client = await directory_client.create_file("newfile", metadata=metadata, content_settings=content_settings)
        await file_client.append_data(b"abc", 0, 3)
        await file_client.flush_data(3)
        properties = await file_client.get_file_properties()

        # Assert
        self.assertTrue(properties)
        self.assertEqual(properties.size, 3)
        self.assertEqual(properties.metadata['hello'], metadata['hello'])
        self.assertEqual(properties.content_settings.content_language, content_settings.content_language)

    @record
    def test_get_properties_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_get_properties())

    async def _test_rename_file_with_non_used_name(self):
        file_client = await self._create_file_and_return_client()
        data_bytes = b"abc"
        await file_client.append_data(data_bytes, 0, 3)
        await file_client.flush_data(3)
        new_client = await file_client.rename_file(file_client.file_system_name+'/'+'newname')

        data = await (await new_client.download_file()).readall()
        self.assertEqual(data, data_bytes)
        self.assertEqual(new_client.path_name, "newname")

    @record
    def test_rename_file_with_non_used_name_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_rename_file_with_non_used_name())

    async def _test_rename_file_to_existing_file(self):
        # create the existing file
        existing_file_client = await self._create_file_and_return_client(file="existingfile")
        await existing_file_client.append_data(b"a", 0, 1)
        await existing_file_client.flush_data(1)
        old_url = existing_file_client.url

        # prepare to rename the file to the existing file
        file_client = await self._create_file_and_return_client()
        data_bytes = b"abc"
        await file_client.append_data(data_bytes, 0, 3)
        await file_client.flush_data(3)
        new_client = await file_client.rename_file(file_client.file_system_name+'/'+existing_file_client.path_name)
        new_url = file_client.url

        data = await (await new_client.download_file()).readall()
        # the existing file was overridden
        self.assertEqual(data, data_bytes)

    @record
    def test_rename_file_to_existing_file_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_rename_file_to_existing_file())

    async def _test_rename_file_will_not_change_existing_directory(self):
        if TestMode.need_recording_file(self.test_mode):
            return
        # create none empty directory(with 2 files)
        dir1 = await self._create_directory_and_return_client(directory="dir1")
        f1 = await dir1.create_file("file1")
        await f1.append_data(b"file1", 0, 5)
        await f1.flush_data(5)
        f2 = await dir1.create_file("file2")
        await f2.append_data(b"file2", 0, 5)
        await f2.flush_data(5)

        # create another none empty directory(with 2 files)
        dir2 = await self._create_directory_and_return_client(directory="dir2")
        f3 = await dir2.create_file("file3")
        await f3.append_data(b"file3", 0, 5)
        await f3.flush_data(5)
        f4 = await dir2.create_file("file4")
        await f4.append_data(b"file4", 0, 5)
        await f4.flush_data(5)

        new_client = await f3.rename_file(f1.file_system_name+'/'+f1.path_name)

        self.assertEqual(await (await new_client.download_file()).readall(), b"file3")

        # make sure the data in file2 and file4 weren't touched
        f2_data = await (await f2.download_file()).readall()
        self.assertEqual(f2_data, b"file2")

        f4_data = await (await f4.download_file()).readall()
        self.assertEqual(f4_data, b"file4")

        with self.assertRaises(HttpResponseError):
            await (await f3.download_file()).readall()

    @record
    def test_rename_file_will_not_change_existing_directory_async(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._test_rename_file_will_not_change_existing_directory())

# ------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
