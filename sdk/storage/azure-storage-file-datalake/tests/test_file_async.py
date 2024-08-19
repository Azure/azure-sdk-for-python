# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import asyncio
import tempfile
import unittest
from datetime import datetime, timedelta
from math import ceil

import pytest
from azure.core import MatchConditions
from azure.core.credentials import AzureSasCredential
from azure.core.exceptions import (
    ClientAuthenticationError,
    HttpResponseError,
    ResourceExistsError,
    ResourceModifiedError,
    ResourceNotFoundError
)
from azure.storage.filedatalake import (
    AccountSasPermissions,
    ContentSettings,
    EncryptionScopeOptions,
    FileSasPermissions,
    FileSystemSasPermissions,
    generate_account_sas,
    generate_file_sas,
    generate_file_system_sas,
    ResourceTypes
)
from azure.storage.filedatalake.aio import DataLakeDirectoryClient, DataLakeFileClient, DataLakeServiceClient, FileSystemClient

from devtools_testutils.aio import recorded_by_proxy_async
from devtools_testutils.storage.aio import AsyncStorageRecordedTestCase
from settings.testcase import DataLakePreparer
# ------------------------------------------------------------------------------

TEST_DIRECTORY_PREFIX = 'directory'
TEST_FILE_PREFIX = 'file'

# ------------------------------------------------------------------------------


class TestFileAsync(AsyncStorageRecordedTestCase):
    async def _setUp(self, account_name, account_key):
        url = self.account_url(account_name, 'dfs')
        self.dsc = DataLakeServiceClient(url, credential=account_key)

        self.config = self.dsc._config

        self.file_system_name = self.get_resource_name('filesystem')

        if not self.is_playback():
            file_system = self.dsc.get_file_system_client(self.file_system_name)
            try:
                await file_system.create_file_system(timeout=5)

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

    def _is_almost_equal(self, first, second, delta):
        if first == second:
            return True
        diff = abs(first - second)
        if delta is not None:
            if diff <= delta:
                return True
        return False

    # --Helpers-----------------------------------------------------------------

    @DataLakePreparer()
    @recorded_by_proxy_async
    async def test_create_file(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        await self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        # Arrange
        directory_name = self._get_directory_reference()

        # Create a directory to put the file under that
        directory_client = self.dsc.get_directory_client(self.file_system_name, directory_name)
        await directory_client.create_directory()

        file_client = directory_client.get_file_client('filename')
        response = await file_client.create_file()

        # Assert
        assert response is not None
    
    @DataLakePreparer()
    @recorded_by_proxy_async
    async def test_create_file_owner_group_acl(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        await self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        test_string = '4cf4e284-f6a8-4540-b53e-c3469af032dc'
        test_string_acl = 'user::rwx,group::r-x,other::rwx'
        # Arrange
        directory_name = self._get_directory_reference()

        # Create a directory to put the file under that
        directory_client = self.dsc.get_directory_client(self.file_system_name, directory_name)
        await directory_client.create_directory()

        file_client = directory_client.get_file_client('filename')
        await file_client.create_file(owner=test_string, group=test_string, acl=test_string_acl)

        # Assert
        acl_properties = await file_client.get_access_control()
        assert acl_properties is not None
        assert acl_properties['owner'] == test_string
        assert acl_properties['group'] == test_string
        assert acl_properties['acl'] == test_string_acl

    @DataLakePreparer()
    @recorded_by_proxy_async
    async def test_create_file_proposed_lease_id(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        await self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        test_string = '4cf4e284-f6a8-4540-b53e-c3469af032dc'
        test_duration = 15
        # Arrange
        directory_name = self._get_directory_reference()

        # Create a directory to put the file under that
        directory_client = self.dsc.get_directory_client(self.file_system_name, directory_name)
        await directory_client.create_directory()

        file_client = directory_client.get_file_client('filename')
        await file_client.create_file(lease_id=test_string, lease_duration=test_duration)

        # Assert
        properties = await file_client.get_file_properties()
        assert properties is not None
        assert properties.lease['status'] == 'locked'
        assert properties.lease['state'] == 'leased'
        assert properties.lease['duration'] == 'fixed'

    @DataLakePreparer()
    @recorded_by_proxy_async
    async def test_create_file_relative_expiry(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        await self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        test_expiry_time = 86400000  # 1 day in milliseconds
        # Arrange
        directory_name = self._get_directory_reference()

        # Create a directory to put the file under that
        directory_client = self.dsc.get_directory_client(self.file_system_name, directory_name)
        await directory_client.create_directory()

        file_client = directory_client.get_file_client('filename')
        await file_client.create_file(expires_on=test_expiry_time)

        # Assert
        file_properties = await file_client.get_file_properties()
        expiry_time = file_properties['expiry_time']
        expiry_time = expiry_time.replace(tzinfo=None)  # Strip timezone info to be able to compare
        creation_time = file_properties['creation_time']
        creation_time = creation_time.replace(tzinfo=None)  # Strip timezone info to be able to compare
        assert file_properties is not None
        assert self._is_almost_equal(expiry_time, creation_time + timedelta(days=1), timedelta(seconds=60)) is True

    @DataLakePreparer()
    @recorded_by_proxy_async
    async def test_create_file_absolute_expiry(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        await self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        test_expiry_time = datetime(2075, 4, 4)
        # Arrange
        directory_name = self._get_directory_reference()

        # Create a directory to put the file under that
        directory_client = self.dsc.get_directory_client(self.file_system_name, directory_name)
        await directory_client.create_directory()

        file_client = directory_client.get_file_client('filename')
        await file_client.create_file(expires_on=test_expiry_time)

        # Assert
        file_properties = await file_client.get_file_properties()
        expiry_time = file_properties['expiry_time']
        expiry_time = expiry_time.replace(tzinfo=None)  # Strip timezone info to be able to compare
        assert file_properties is not None
        assert self._is_almost_equal(expiry_time, test_expiry_time, timedelta(seconds=1)) is True

    @DataLakePreparer()
    @recorded_by_proxy_async
    async def test_create_file_extra_backslashes(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        await self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        # Arrange
        file_client = await self._create_file_and_return_client()

        new_file_client = DataLakeFileClient(self.account_url(datalake_storage_account_name, 'dfs'),
                                             file_client.file_system_name + '/',
                                             '/' + file_client.path_name,
                                             credential=datalake_storage_account_key, logging_enable=True)
        response = await new_file_client.create_file()

        # Assert
        assert response is not None

    @DataLakePreparer()
    @recorded_by_proxy_async
    async def test_file_exists(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        await self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        # Arrange
        directory_name = self._get_directory_reference()

        directory_client = self.dsc.get_directory_client(self.file_system_name, directory_name)
        await directory_client.create_directory()

        file_client1 = directory_client.get_file_client('filename')
        file_client2 = directory_client.get_file_client('nonexistentfile')
        await file_client1.create_file()

        assert await file_client1.exists()
        assert not await file_client2.exists()

    @DataLakePreparer()
    @recorded_by_proxy_async
    async def test_create_file_using_oauth_token_credential(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        await self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        # Arrange
        file_name = self._get_file_reference()
        token_credential = self.get_credential(DataLakeServiceClient, is_async=True)

        # Create a directory to put the file under that
        file_client = DataLakeFileClient(self.dsc.url, self.file_system_name, file_name,
                                         credential=token_credential)

        response = file_client.create_file()

        # Assert
        assert response is not None

    @DataLakePreparer()
    @recorded_by_proxy_async
    async def test_create_file_with_existing_name(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        await self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        # Arrange
        file_client = await self._create_file_and_return_client()

        with pytest.raises(ResourceExistsError):
            # if the file exists then throw error
            # if_none_match='*' is to make sure no existing file
            await file_client.create_file(match_condition=MatchConditions.IfMissing)

    @DataLakePreparer()
    @recorded_by_proxy_async
    async def test_create_file_with_lease_id(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        await self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        # Arrange
        directory_name = self._get_directory_reference()
        directory_client = self.dsc.get_directory_client(self.file_system_name, directory_name)
        await directory_client.create_directory()

        file_client = directory_client.get_file_client('filename')
        # Act
        await file_client.create_file()
        lease = await file_client.acquire_lease(lease_id='00000000-1111-2222-3333-444444444444')
        create_resp = await file_client.create_file(lease=lease)

        # Assert
        file_properties = await file_client.get_file_properties()
        assert file_properties is not None
        assert file_properties.etag == create_resp.get('etag')
        assert file_properties.last_modified == create_resp.get('last_modified')

    @DataLakePreparer()
    @recorded_by_proxy_async
    async def test_create_file_under_root_directory(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        await self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        # Arrange
        # get a file client to interact with the file under root directory
        file_client = self.dsc.get_file_client(self.file_system_name, "filename")

        response = await file_client.create_file()

        # Assert
        assert response is not None

    @DataLakePreparer()
    @recorded_by_proxy_async
    async def test_append_data(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        await self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        directory_name = self._get_directory_reference()

        # Create a directory to put the file under that
        directory_client = self.dsc.get_directory_client(self.file_system_name, directory_name)
        await directory_client.create_directory()

        file_client = directory_client.get_file_client('filename')
        await file_client.create_file()

        # Act
        response = await file_client.append_data(b'abc', 0, 3)

        assert response is not None

    @DataLakePreparer()
    @recorded_by_proxy_async
    async def test_append_data_lease_action(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        await self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        directory_name = self._get_directory_reference()

        # Create a directory to put the file under that
        directory_client = self.dsc.get_directory_client(self.file_system_name, directory_name)
        await directory_client.create_directory()

        file_client = directory_client.get_file_client('filename')
        await file_client.create_file()

        data = b'Hello world'
        lease_id = '670d43d1-ecde-4ae9-9c37-d22d340e7719'

        # Act / Assert
        # ---Acquire---
        await file_client.append_data(data, 0, len(data), lease_action='acquire', lease_duration=30, lease=lease_id)

        lease = (await file_client.get_file_properties()).lease
        assert lease.state == 'leased'
        assert lease.duration == 'fixed'

        # ---Renew---
        await file_client.append_data(data, 0, len(data), lease_action='auto-renew', lease=lease_id)

        lease = (await file_client.get_file_properties()).lease
        assert lease.state == 'leased'
        assert lease.duration == 'fixed'

        # ---Release---
        await file_client.append_data(data, 0, len(data), flush=True, lease_action='release', lease=lease_id)

        lease = (await file_client.get_file_properties()).lease
        assert lease.state == 'available'
        assert not lease.duration

        # ---Acquire and release---
        await file_client.append_data(data, 0, len(data), flush=True, lease_action='acquire-release', lease=lease_id)

        lease = (await file_client.get_file_properties()).lease
        assert lease.state == 'available'
        assert not lease.duration

    @DataLakePreparer()
    @recorded_by_proxy_async
    async def test_append_empty_data(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        await self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        file_client = await self._create_file_and_return_client()

        # Act
        await file_client.flush_data(0)
        file_props = await file_client.get_file_properties()

        assert file_props['size'] == 0

    @DataLakePreparer()
    @recorded_by_proxy_async
    async def test_flush_data(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        await self._setUp(datalake_storage_account_name, datalake_storage_account_key)
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
        assert response is not None
        assert prop['size'] == 3

    @DataLakePreparer()
    @recorded_by_proxy_async
    async def test_flush_data_lease_action(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        await self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        directory_name = self._get_directory_reference()

        # Create a directory to put the file under that
        directory_client = self.dsc.get_directory_client(self.file_system_name, directory_name)
        await directory_client.create_directory()

        file_client = directory_client.get_file_client('filename')
        await file_client.create_file()

        data = b'Hello world'
        lease_id = 'c8107e94-ab42-42ac-92d6-6458764982af'

        # Act / Assert
        # ---Acquire---
        await file_client.append_data(data, 0, len(data))
        await file_client.flush_data(len(data), lease_action='acquire', lease_duration=30, lease=lease_id)

        lease = (await file_client.get_file_properties()).lease
        assert lease.state == 'leased'
        assert lease.duration == 'fixed'

        # ---Renew---
        await file_client.append_data(data, 0, len(data), lease=lease_id)
        await file_client.flush_data(len(data), lease_action='auto-renew', lease=lease_id)

        lease = (await file_client.get_file_properties()).lease
        assert lease.state == 'leased'
        assert lease.duration == 'fixed'

        # ---Release---
        await file_client.append_data(data, 0, len(data), lease=lease_id)
        await file_client.flush_data(len(data), lease_action='release', lease=lease_id)

        lease = (await file_client.get_file_properties()).lease
        assert lease.state == 'available'
        assert not lease.duration

        # ---Acquire and release---
        await file_client.append_data(data, 0, len(data))
        await file_client.flush_data(len(data), lease_action='acquire-release', lease=lease_id)

        lease = (await file_client.get_file_properties()).lease
        assert lease.state == 'available'
        assert not lease.duration

    @DataLakePreparer()
    @recorded_by_proxy_async
    async def test_flush_data_with_bool(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        await self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        directory_name = self._get_directory_reference()

        # Create a directory to put the file under that
        directory_client = self.dsc.get_directory_client(self.file_system_name, directory_name)
        await directory_client.create_directory()

        file_client = directory_client.get_file_client('filename')
        await file_client.create_file()

        # Act
        response = await file_client.append_data(b'abc', 0, 3, flush=True)

        # Assert
        prop = await file_client.get_file_properties()
        assert response is not None
        assert prop['size'] == 3

    @DataLakePreparer()
    @recorded_by_proxy_async
    async def test_flush_data_with_match_condition(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        await self._setUp(datalake_storage_account_name, datalake_storage_account_key)
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
        with pytest.raises(ResourceModifiedError):
            # flush is unsuccessful because extra data were appended.
            await file_client.flush_data(6, etag=resp['etag'], match_condition=MatchConditions.IfNotModified)

    @pytest.mark.live_test_only
    @DataLakePreparer()
    async def test_upload_data_in_substreams(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        await self._setUp(datalake_storage_account_name, datalake_storage_account_key)

        directory_name = self._get_directory_reference()

        # Create a directory to put the file under that
        directory_client = self.dsc.get_directory_client(self.file_system_name, directory_name)
        await directory_client.create_directory()

        file_client = directory_client.get_file_client('filename')
        # Get 16MB data
        raw_data = self.get_random_bytes(16 * 1024 * 1024)
        # Ensure chunk size is greater than threshold (8MB > 4MB) - for optimized upload
        await file_client.upload_data(raw_data, chunk_size=8 * 1024 * 1024, overwrite=True, max_concurrency=3)
        data = await file_client.download_file()
        downloaded_data = await data.readall()
        assert raw_data == downloaded_data

        # Run on single thread
        await file_client.upload_data(raw_data, chunk_size=8 * 1024 * 1024, overwrite=True)
        data = await file_client.download_file()
        downloaded_data = await data.readall()
        assert raw_data == downloaded_data

    @DataLakePreparer()
    @recorded_by_proxy_async
    async def test_upload_data(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        await self._setUp(datalake_storage_account_name, datalake_storage_account_key)

        directory_name = self._get_directory_reference()

        # Create a directory to put the file under that
        directory_client = self.dsc.get_directory_client(self.file_system_name, directory_name)
        await directory_client.create_directory()

        file_client = directory_client.get_file_client('filename')
        data = self.get_random_bytes(400*1024)
        await file_client.upload_data(data, overwrite=True, max_concurrency=5)

        downloaded_data = await (await file_client.download_file()).readall()
        assert data == downloaded_data

    @DataLakePreparer()
    @recorded_by_proxy_async
    async def test_upload_data_to_existing_file(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        await self._setUp(datalake_storage_account_name, datalake_storage_account_key)
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
        with pytest.raises(HttpResponseError):
            await file_client.upload_data(data)
        await file_client.upload_data(data, overwrite=True)

        downloaded_data = await (await file_client.download_file()).readall()
        assert data == downloaded_data

    @DataLakePreparer()
    @recorded_by_proxy_async
    async def test_upload_data_to_existing_file_with_content_settings(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        await self._setUp(datalake_storage_account_name, datalake_storage_account_key)
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

        await file_client.upload_data(data, content_settings=content_settings, etag=etag, match_condition=MatchConditions.IfNotModified)

        downloaded_data = await (await file_client.download_file()).readall()
        properties = await file_client.get_file_properties()

        assert data == downloaded_data
        assert properties.content_settings.content_language == content_settings.content_language

    @DataLakePreparer()
    @recorded_by_proxy_async
    async def test_upload_data_to_existing_file_with_permissions_and_umask(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        await self._setUp(datalake_storage_account_name, datalake_storage_account_key)

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

        await file_client.upload_data(data, overwrite=True, permissions='0777', umask="0000", etag=etag, match_condition=MatchConditions.IfNotModified)

        downloaded_data = await (await file_client.download_file()).readall()
        prop = await file_client.get_access_control()

        assert data == downloaded_data
        assert prop['permissions'] == 'rwxrwxrwx'

    @DataLakePreparer()
    @recorded_by_proxy_async
    async def test_upload_data_from_async_generator(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        await self._setUp(datalake_storage_account_name, datalake_storage_account_key)

        # Create a directory to put the file under
        directory_name = self._get_directory_reference()
        directory_client = self.dsc.get_directory_client(self.file_system_name, directory_name)
        await directory_client.create_directory()

        data = b'Hello Async World!'

        async def data_generator():
            for _ in range(3):
                yield data
                await asyncio.sleep(0.1)

        # Act
        file_client = directory_client.get_file_client('filename')
        await file_client.upload_data(data_generator(), length=len(data*3), overwrite=True)

        # Assert
        result = await (await file_client.download_file()).readall()
        assert result == data*3

    @DataLakePreparer()
    @recorded_by_proxy_async
    async def test_read_file(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        await self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        file_client = await self._create_file_and_return_client()
        data = self.get_random_bytes(1024)

        # upload data to file
        await file_client.append_data(data, 0, len(data))
        await file_client.flush_data(len(data))

        # download the data and make sure it is the same as uploaded data
        downloaded_data = await (await file_client.download_file()).readall()
        assert data == downloaded_data

    @pytest.mark.live_test_only
    @DataLakePreparer()
    async def test_read_file_with_user_delegation_key(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        await self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        # SAS URL is calculated from storage key, so this test runs live only

        # Create file
        file_client = await self._create_file_and_return_client()
        data = self.get_random_bytes(1024)
        # Upload data to file
        await file_client.append_data(data, 0, len(data))
        await file_client.flush_data(len(data))

        # Get user delegation key
        token_credential = self.get_credential(DataLakeServiceClient, is_async=True)
        service_client = DataLakeServiceClient(self.account_url(datalake_storage_account_name, 'dfs'), credential=token_credential)
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

        # download the data and make sure it is the same as uploaded data
        new_file_client = DataLakeFileClient(self.account_url(datalake_storage_account_name, 'dfs'),
                                             file_client.file_system_name,
                                             file_client.path_name,
                                             credential=sas_token)
        downloaded_data = await (await new_file_client.download_file()).readall()
        assert data == downloaded_data

    @DataLakePreparer()
    @recorded_by_proxy_async
    async def test_read_file_into_file(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        await self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        file_client = await self._create_file_and_return_client()
        data = self.get_random_bytes(1024)

        # upload data to file
        await file_client.append_data(data, 0, len(data))
        await file_client.flush_data(len(data))

        # download the data into a file and make sure it is the same as uploaded data
        with tempfile.TemporaryFile() as temp_file:
            download = await file_client.download_file()
            await download.readinto(temp_file)

            temp_file.seek(0)

            # Assert
            actual = temp_file.read()
            assert data == actual

    @DataLakePreparer()
    @recorded_by_proxy_async
    async def test_read_file_to_text(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        await self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        file_client = await self._create_file_and_return_client()
        data = self.get_random_text_data(1024)

        # upload data to file
        await file_client.append_data(data, 0, len(data))
        await file_client.flush_data(len(data))

        # download the text data and make sure it is the same as uploaded data
        downloaded_data = await (await file_client.download_file(encoding="utf-8")).readall()

        # Assert
        assert data == downloaded_data

    @pytest.mark.live_test_only
    @DataLakePreparer()
    async def test_account_sas(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        await self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        # SAS URL is calculated from storage key, so this test runs live only

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

        for credential in [token, AzureSasCredential(token)]:
            # read the created file which is under root directory
            file_client = DataLakeFileClient(self.dsc.url, self.file_system_name, file_name, credential=credential)
            properties = await file_client.get_file_properties()

            # make sure we can read the file properties
            assert properties is not None

            # try to write to the created file with the token
            with pytest.raises(HttpResponseError):
                await file_client.append_data(b"abcd", 0, 4)

    @DataLakePreparer()
    @recorded_by_proxy_async
    async def test_account_sas_raises_if_sas_already_in_uri(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        await self._setUp(datalake_storage_account_name, datalake_storage_account_key)

        with pytest.raises(ValueError):
            DataLakeFileClient(self.dsc.url + "?sig=foo", self.file_system_name, "foo", credential=AzureSasCredential("?foo=bar"))

    @pytest.mark.live_test_only
    @DataLakePreparer()
    async def test_file_sas_only_applies_to_file_level(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        await self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        # SAS URL is calculated from storage key, so this test runs live only

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
        file_client = DataLakeFileClient(self.dsc.url, self.file_system_name, directory_name + '/' + file_name,
                                         credential=token)
        properties = await file_client.get_file_properties()

        # make sure we can read the file properties
        assert properties is not None

        # try to write to the created file with the token
        response = await file_client.append_data(b"abcd", 0, 4, validate_content=True)
        assert response is not None

        # the token is for file level, so users are not supposed to have access to file system level operations
        file_system_client = FileSystemClient(self.dsc.url, self.file_system_name, credential=token)
        with pytest.raises(ClientAuthenticationError):
            await file_system_client.get_file_system_properties()

        # the token is for file level, so users are not supposed to have access to directory level operations
        directory_client = DataLakeDirectoryClient(self.dsc.url, self.file_system_name, directory_name,
                                                   credential=token)
        with pytest.raises(ClientAuthenticationError):
            await directory_client.get_directory_properties()

    @DataLakePreparer()
    @recorded_by_proxy_async
    async def test_delete_file(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        await self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        # Arrange
        file_client = await self._create_file_and_return_client()

        await file_client.delete_file()

        with pytest.raises(ResourceNotFoundError):
            await file_client.get_file_properties()

    @DataLakePreparer()
    @recorded_by_proxy_async
    async def test_delete_file_oauth(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        # Arrange
        await self._setUp(datalake_storage_account_name, datalake_storage_account_key)

        file_name = self._get_file_reference()
        token_credential = self.get_credential(DataLakeServiceClient, is_async=True)

        file_client = DataLakeFileClient(
            self.dsc.url,
            self.file_system_name,
            file_name,
            credential=token_credential)
        await file_client.create_file()

        # Act
        response = await file_client.delete_file()

        # Assert
        assert response is not None

    @DataLakePreparer()
    @recorded_by_proxy_async
    async def test_delete_file_with_if_unmodified_since(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        await self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        # Arrange
        file_client = await self._create_file_and_return_client()

        prop = await file_client.get_file_properties()
        await file_client.delete_file(if_unmodified_since=prop['last_modified'])

        # Make sure the file was deleted
        with pytest.raises(ResourceNotFoundError):
            await file_client.get_file_properties()

    @DataLakePreparer()
    @recorded_by_proxy_async
    async def test_set_access_control(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        await self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        file_client = await self._create_file_and_return_client()

        response = await file_client.set_access_control(permissions='0777')

        # Assert
        assert response is not None

    @DataLakePreparer()
    @recorded_by_proxy_async
    async def test_set_access_control_with_match_conditions(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        await self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        file_client = await self._create_file_and_return_client()

        with pytest.raises(ResourceModifiedError):
            await file_client.set_access_control(permissions='0777', match_condition=MatchConditions.IfMissing)

    @DataLakePreparer()
    @recorded_by_proxy_async
    async def test_get_access_control(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        await self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        file_client = await self._create_file_and_return_client()
        await file_client.set_access_control(permissions='0777')

        # Act
        response = await file_client.get_access_control()

        # Assert
        assert response is not None

    @DataLakePreparer()
    @recorded_by_proxy_async
    async def test_get_access_control_with_if_modified_since(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        await self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        file_client = await self._create_file_and_return_client()
        await file_client.set_access_control(permissions='0777')

        prop = await file_client.get_file_properties()

        # Act
        response = await file_client.get_access_control(if_modified_since=prop['last_modified'] - timedelta(minutes=15))

        # Assert
        assert response is not None

    @DataLakePreparer()
    @recorded_by_proxy_async
    async def test_get_properties(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        await self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        # Arrange
        directory_client = await self._create_directory_and_return_client()

        metadata = {'hello': 'world', 'number': '42'}
        content_settings = ContentSettings(
            content_language='spanish',
            content_disposition='inline')
        file_client = await directory_client.create_file("newfile", metadata=metadata,
                                                         content_settings=content_settings)
        await file_client.append_data(b"abc", 0, 3)
        await file_client.flush_data(3)
        properties = await file_client.get_file_properties()

        # Assert
        assert properties
        assert properties.size == 3
        assert properties.metadata['hello'] == metadata['hello']
        assert properties.content_settings.content_language == content_settings.content_language

    @DataLakePreparer()
    @recorded_by_proxy_async
    async def test_set_access_control_recursive(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        await self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        acl = 'user::rwx,group::r-x,other::rwx'
        file_client = await self._create_file_and_return_client()

        summary = await file_client.set_access_control_recursive(acl=acl)

        # Assert
        assert summary.counters.directories_successful == 0
        assert summary.counters.files_successful == 1
        assert summary.counters.failure_count == 0
        access_control = await file_client.get_access_control()
        assert access_control is not None
        assert acl == access_control['acl']

    @DataLakePreparer()
    @recorded_by_proxy_async
    async def test_update_access_control_recursive(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        await self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        acl = 'user::rwx,group::r-x,other::rwx'
        file_client = await self._create_file_and_return_client()

        summary = await file_client.update_access_control_recursive(acl=acl)

        # Assert
        assert summary.counters.directories_successful == 0
        assert summary.counters.files_successful == 1
        assert summary.counters.failure_count == 0
        access_control = await file_client.get_access_control()
        assert access_control is not None
        assert acl == access_control['acl']

    @DataLakePreparer()
    @recorded_by_proxy_async
    async def test_remove_access_control_recursive(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        await self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        acl = "mask," + "default:user,default:group," + \
              "user:ec3595d6-2c17-4696-8caa-7e139758d24a,group:ec3595d6-2c17-4696-8caa-7e139758d24a," + \
              "default:user:ec3595d6-2c17-4696-8caa-7e139758d24a,default:group:ec3595d6-2c17-4696-8caa-7e139758d24a"
        file_client = await self._create_file_and_return_client()
        summary = await file_client.remove_access_control_recursive(acl=acl)

        # Assert
        assert summary.counters.directories_successful == 0
        assert summary.counters.files_successful == 1
        assert summary.counters.failure_count == 0

    @DataLakePreparer()
    @recorded_by_proxy_async
    async def test_set_expiry(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")
        variables = kwargs.pop('variables', {})

        await self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        # Arrange
        directory_client = await self._create_directory_and_return_client()

        metadata = {'hello': 'world', 'number': '42'}
        content_settings = ContentSettings(
            content_language='spanish',
            content_disposition='inline')
        expiry_time = self.get_datetime_variable(variables, 'expiry_time', datetime.utcnow() + timedelta(hours=1))
        file_client = await directory_client.create_file("newfile", metadata=metadata, content_settings=content_settings)
        await file_client.set_file_expiry("Absolute", expires_on=expiry_time)
        properties = await file_client.get_file_properties()

        # Assert
        assert properties
        assert properties.expiry_time is not None

        return variables

    @DataLakePreparer()
    @recorded_by_proxy_async
    async def test_rename_file_with_non_used_name(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        await self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        file_client = await self._create_file_and_return_client()
        data_bytes = b"abc"
        await file_client.append_data(data_bytes, 0, 3)
        await file_client.flush_data(3)
        new_client = await file_client.rename_file(file_client.file_system_name + '/' + 'newname')

        data = await (await new_client.download_file()).readall()
        assert data == data_bytes
        assert new_client.path_name == "newname"

    @DataLakePreparer()
    @recorded_by_proxy_async
    async def test_rename_file_to_existing_file(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        await self._setUp(datalake_storage_account_name, datalake_storage_account_key)
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
        new_client = await file_client.rename_file(file_client.file_system_name + '/' + existing_file_client.path_name)
        new_url = file_client.url

        data = await (await new_client.download_file()).readall()
        # the existing file was overridden
        assert data == data_bytes

    @DataLakePreparer()
    @recorded_by_proxy_async
    async def test_file_encryption_scope_from_file_system_async(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        # Arrange
        url = self.account_url(datalake_storage_account_name, 'dfs')
        self.dsc = DataLakeServiceClient(url, credential=datalake_storage_account_key, logging_enable=True)
        self.file_system_name = self.get_resource_name('filesystem')
        file_name = 'testfile'
        encryption_scope = EncryptionScopeOptions(default_encryption_scope="hnstestscope1")

        file_system = self.dsc.get_file_system_client(self.file_system_name)
        await file_system.create_file_system(encryption_scope_options=encryption_scope)

        file_client = await file_system.create_file(file_name)
        props = await file_client.get_file_properties()

        # Assert
        assert props
        assert props['encryption_scope'] is not None
        assert props['encryption_scope'] == encryption_scope.default_encryption_scope

    @pytest.mark.live_test_only
    @DataLakePreparer()
    async def test_rename_file_with_file_sas(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        await self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        # SAS URL is calculated from storage key, so this test runs live only
        token = generate_file_sas(self.dsc.account_name,
                                  self.file_system_name,
                                  None,
                                  "oldfile",
                                  datalake_storage_account_key,
                                  permission=FileSasPermissions(read=True, create=True, write=True, delete=True, move=True),
                                  expiry=datetime.utcnow() + timedelta(hours=1),
                                  )

        new_token = generate_file_sas(self.dsc.account_name,
                                      self.file_system_name,
                                      None,
                                      "newname",
                                      datalake_storage_account_key,
                                      permission=FileSasPermissions(read=True, create=True, write=True, delete=True),
                                      expiry=datetime.utcnow() + timedelta(hours=1),
                                      )

        # read the created file which is under root directory
        file_client = DataLakeFileClient(self.dsc.url, self.file_system_name, "oldfile", credential=token)
        await file_client.create_file()
        data_bytes = b"abc"
        await file_client.append_data(data_bytes, 0, 3)
        await file_client.flush_data(3)
        new_client = await file_client.rename_file(file_client.file_system_name+'/'+'newname'+'?'+new_token)

        data = await (await new_client.download_file()).readall()
        assert data == data_bytes
        assert new_client.path_name == "newname"

    @DataLakePreparer()
    @recorded_by_proxy_async
    async def test_rename_file_will_not_change_existing_directory(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        await self._setUp(datalake_storage_account_name, datalake_storage_account_key)
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

        new_client = await f3.rename_file(f1.file_system_name + '/' + f1.path_name)

        assert await (await new_client.download_file()).readall() == b"file3"

        # make sure the data in file2 and file4 weren't touched
        f2_data = await (await f2.download_file()).readall()
        assert f2_data == b"file2"

        f4_data = await (await f4.download_file()).readall()
        assert f4_data == b"file4"

        with pytest.raises(HttpResponseError):
            await (await f3.download_file()).readall()

    @DataLakePreparer()
    @recorded_by_proxy_async
    async def test_rename_file_different_filesystem_with_sas(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        await self._setUp(datalake_storage_account_name, datalake_storage_account_key)

        # Use filesystem SAS without access to new filesystem
        existing_sas = self.generate_sas(
            generate_file_system_sas,
            self.dsc.account_name,
            self.file_system_name,
            self.dsc.credential.account_key,
            FileSystemSasPermissions(write=True, read=True, delete=True),
            datetime.utcnow() + timedelta(hours=1),
        )

        file_client = DataLakeFileClient(self.dsc.url, self.file_system_name, "oldfile", credential=existing_sas)
        await file_client.create_file()
        await file_client.append_data(b"abc", 0, 3, flush=True)

        # Create another filesystem to rename to
        new_file_system = self.dsc.get_file_system_client(self.file_system_name + '2')
        await new_file_system.create_file_system()

        # Get different SAS to new file system
        new_sas = self.generate_sas(
            generate_file_system_sas,
            self.dsc.account_name,
            new_file_system.file_system_name,
            self.dsc.credential.account_key,
            FileSystemSasPermissions(write=True, read=True, delete=True),
            datetime.utcnow() + timedelta(hours=1),
        )

        # ? in new name to test parsing
        new_name = new_file_system.file_system_name + '/' + 'new?file' + '?' + new_sas
        new_client = await file_client.rename_file(new_name)
        new_props = await new_client.get_file_properties()

        assert new_props.name == 'new?file'

        await new_file_system.delete_file_system()

    @DataLakePreparer()
    @recorded_by_proxy_async
    async def test_rename_file_special_chars(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        await self._setUp(datalake_storage_account_name, datalake_storage_account_key)

        file_client = await self._create_file_and_return_client(file="oldfile")
        await file_client.append_data(b"abc", 0, 3, flush=True)

        new_client = await file_client.rename_file(file_client.file_system_name + '/' + '?!@#$%^&*.?test')
        new_props = await new_client.get_file_properties()

        assert new_props.name == '?!@#$%^&*.?test'

    @DataLakePreparer()
    @recorded_by_proxy_async
    async def test_read_file_read(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        await self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        self.dsc._config.max_single_get_size = 1024
        self.dsc._config.max_chunk_get_size = 1024

        file_client = await self._create_file_and_return_client()
        data = b'12345' * 205 * 5  # 5125 bytes

        await file_client.append_data(data, 0, len(data), flush=True)
        stream = await file_client.download_file()

        # Act
        result = bytearray()
        read_size = 512
        num_chunks = int(ceil(len(data) / read_size))
        for i in range(num_chunks):
            content = await stream.read(read_size)
            start = i * read_size
            end = start + read_size
            assert data[start:end] == content
            result.extend(content)

        # Assert
        assert result == data

    @DataLakePreparer()
    @recorded_by_proxy_async
    async def test_create_and_read_file_encryption_context(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        # Arrange
        await self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        url = self.account_url(datalake_storage_account_name, 'dfs')
        self.dsc = DataLakeServiceClient(url, credential=datalake_storage_account_key)
        self.file_system_name = self.get_resource_name('filesystem')
        file_name = 'testfile'
        file_system = self.dsc.get_file_system_client(self.file_system_name)
        try:
            await file_system.create_file_system()
        except:
            pass
        file_client = file_system.get_file_client(file_name)

        # Act
        await file_client.create_file(encryption_context='encryptionContext')

        properties = await file_client.get_file_properties()
        read_response = await file_client.download_file()
        path_response = []
        async for path in file_system.get_paths():
            path_response.append(path)

        assert properties
        assert properties['encryption_context'] is not None
        assert properties['encryption_context'] == 'encryptionContext'

        assert read_response.properties
        assert read_response.properties['encryption_context'] is not None
        assert read_response.properties['encryption_context'] == 'encryptionContext'

        assert path_response[0]['encryption_context']
        assert path_response[0]['encryption_context'] is not None
        assert path_response[0]['encryption_context'] == 'encryptionContext'

    @DataLakePreparer()
    @recorded_by_proxy_async
    async def test_upload_file_encryption_context(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        # Arrange
        await self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        url = self.account_url(datalake_storage_account_name, 'dfs')
        self.dsc = DataLakeServiceClient(url, credential=datalake_storage_account_key)
        self.file_system_name = self.get_resource_name('filesystem')
        data = self.get_random_bytes(200 * 1024)
        file_name = 'testfile'
        file_system = self.dsc.get_file_system_client(self.file_system_name)
        try:
            await file_system.create_file_system()
        except:
            pass
        file_client = file_system.get_file_client(file_name)

        # Act
        await file_client.upload_data(data, overwrite=True, encryption_context='encryptionContext')

        downloaded_data = await (await file_client.download_file()).readall()
        properties = await file_client.get_file_properties()

        # Assert
        assert data == downloaded_data
        assert properties
        assert properties['encryption_context'] is not None
        assert properties['encryption_context'] == 'encryptionContext'

    @DataLakePreparer()
    @recorded_by_proxy_async
    async def test_dir_and_file_properties_owner_group_acl_permissions(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        await self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        # Arrange
        directory_name = self._get_directory_reference()
        directory_client = self.dsc.get_directory_client(self.file_system_name, directory_name)
        await directory_client.create_directory()
        file_client1 = directory_client.get_file_client('filename')
        await file_client1.create_file()

        directory_properties = await directory_client.get_directory_properties()
        file_properties = await file_client1.get_file_properties(upn=True)

        # Assert
        assert directory_properties['owner'] is not None
        assert directory_properties['group'] is not None
        assert directory_properties['permissions'] is not None
        assert directory_properties['acl'] is not None
        assert file_properties['owner'] is not None
        assert file_properties['group'] is not None
        assert file_properties['permissions'] is not None
        assert file_properties['acl'] is not None

    @DataLakePreparer()
    @recorded_by_proxy_async
    async def test_storage_account_audience_file_client(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        # Arrange
        await self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        file_client = await self._create_file_and_return_client()

        # Act
        token_credential = self.get_credential(DataLakeServiceClient, is_async=True)
        fc = DataLakeFileClient(
            self.account_url(datalake_storage_account_name, 'dfs'),
            file_client.file_system_name + '/',
            '/' + file_client.path_name,
            credential=token_credential,
            audience=f'https://{datalake_storage_account_name}.blob.core.windows.net/'
        )

        # Assert
        data = b'Hello world'
        response1 = await fc.get_file_properties()
        response2 = await fc.upload_data(data, overwrite=True)
        assert response1 is not None
        assert response2 is not None

    @DataLakePreparer()
    @recorded_by_proxy_async
    async def test_bad_audience_file_client(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        # Arrange
        await self._setUp(datalake_storage_account_name, datalake_storage_account_key)
        file_client = await self._create_file_and_return_client()

        # Act
        token_credential = self.get_credential(DataLakeServiceClient, is_async=True)
        fc = DataLakeFileClient(
            self.account_url(datalake_storage_account_name, 'dfs'),
            file_client.file_system_name + '/',
            '/' + file_client.path_name,
            credential=token_credential,
            audience=f'https://badaudience.blob.core.windows.net/'
        )

        # Will not raise ClientAuthenticationError despite bad audience due to Bearer Challenge
        data = b'Hello world'
        await fc.get_file_properties()
        await fc.upload_data(data, overwrite=True)


# ------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
