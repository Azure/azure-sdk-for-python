# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import asyncio
import base64
import os
import tempfile
import uuid
from datetime import datetime, timedelta

import pytest
import requests
from azure.core.credentials import AzureNamedKeyCredential, AzureSasCredential
from azure.core.exceptions import HttpResponseError, ResourceExistsError, ResourceNotFoundError
from azure.storage.blob.aio import BlobServiceClient
from azure.storage.fileshare import (
    AccessPolicy,
    AccountSasPermissions,
    ContentSettings,
    FileSasPermissions,
    generate_account_sas,
    generate_file_sas,
    generate_share_sas,
    NTFSAttributes,
    ResourceTypes,
    ShareSasPermissions,
    StorageErrorCode
)
from azure.storage.fileshare.aio import ShareFileClient, ShareServiceClient

from devtools_testutils.aio import recorded_by_proxy_async
from devtools_testutils.storage.aio import AsyncStorageRecordedTestCase
from settings.testcase import FileSharePreparer
from test_helpers_async import ProgressTracker

# ------------------------------------------------------------------------------
TEST_SHARE_PREFIX = 'share'
TEST_DIRECTORY_PREFIX = 'dir'
TEST_FILE_PREFIX = 'file'
TEST_BLOB_PREFIX = 'blob'
LARGE_FILE_SIZE = 64 * 1024 + 5
TEST_FILE_PERMISSIONS = 'O:S-1-5-21-2127521184-1604012920-1887927527-21560751G:S-1-5-21-2127521184-' \
                        '1604012920-1887927527-513D:AI(A;;FA;;;SY)(A;;FA;;;BA)(A;;0x1200a9;;;' \
                        'S-1-5-21-397955417-626881126-188441444-3053964)'
TEST_INTENT = "backup"
# ------------------------------------------------------------------------------


class TestStorageFileAsync(AsyncStorageRecordedTestCase):
    def _setup(self, storage_account_name, storage_account_key, rmt_account=None, rmt_key=None):
        url = self.account_url(storage_account_name, "file")
        blob_url = self.account_url(storage_account_name, "blob")
        credential = storage_account_key

        # test chunking functionality by reducing the threshold
        # for chunking and the size of each chunk, otherwise
        # the tests would take too long to execute
        self.fsc = ShareServiceClient(
            url, credential=credential, max_range_size=4 * 1024)
        self.bsc = BlobServiceClient(blob_url, credential=credential)
        self.source_container_name = self.get_resource_name('sourceshare')
        self.share_name = self.get_resource_name('utshare')
        self.short_byte_data = self.get_random_bytes(1024)

        remote_url = self.account_url(rmt_account, "file")
        remote_credential = rmt_key
        if rmt_account:
            self.fsc2 = ShareServiceClient(remote_url, credential=remote_credential)
            self.remote_share_name = None

    def _teardown(self, FILE_PATH):
        if os.path.isfile(FILE_PATH):
            try:
                os.remove(FILE_PATH)
            except:
                pass

    # --Helpers-----------------------------------------------------------------
    def _get_file_reference(self):
        return self.get_resource_name(TEST_FILE_PREFIX)

    async def _create_source_blob(self):
        try:
            await self.bsc.create_container(self.source_container_name)
        except:
            pass
        blob_client = self.bsc.get_blob_client(self.source_container_name, self.get_resource_name(TEST_BLOB_PREFIX))
        await blob_client.upload_blob(b'abcdefghijklmnop' * 32, overwrite=True)
        return blob_client

    async def _setup_share(self, storage_account_name, storage_account_key, remote=False):
        share_name = self.remote_share_name if remote else self.share_name
        async with ShareServiceClient(
                self.account_url(storage_account_name, "file"),
                credential=storage_account_key,
                max_range_size=4 * 1024) as fsc:
            if not self.is_playback():
                try:
                    await fsc.create_share(share_name)
                except:
                    pass

    async def _create_file(self, storage_account_name, storage_account_key, file_name=None):
        await self._setup_share(storage_account_name, storage_account_key)
        file_name = self._get_file_reference() if file_name is None else file_name
        share_client = self.fsc.get_share_client(self.share_name)
        file_client = share_client.get_file_client(file_name)
        await file_client.upload_file(self.short_byte_data)
        return file_client

    async def _create_empty_file(self, storage_account_name, storage_account_key, file_name=None, file_size=2048):
        await self._setup_share(storage_account_name, storage_account_key)
        file_name = self._get_file_reference() if file_name is None else file_name
        share_client = self.fsc.get_share_client(self.share_name)
        file_client = share_client.get_file_client(file_name)
        await file_client.create_file(file_size)
        return file_client

    async def _get_file_client(self, storage_account_name, storage_account_key):
        await self._setup_share(storage_account_name, storage_account_key)
        file_name = self._get_file_reference()
        share_client = self.fsc.get_share_client(self.share_name)
        file_client = share_client.get_file_client(file_name)
        return file_client

    async def _create_remote_share(self):
        self.remote_share_name = self.get_resource_name('remoteshare')
        remote_share = self.fsc2.get_share_client(self.remote_share_name)
        try:
            await remote_share.create_share()
        except ResourceExistsError:
            pass
        return remote_share

    async def _create_remote_file(self, file_data=None):
        if not file_data:
            file_data = b'12345678' * 1024
        source_file_name = self._get_file_reference()
        remote_share = self.fsc2.get_share_client(self.remote_share_name)
        remote_file = remote_share.get_file_client(source_file_name)
        await remote_file.upload_file(file_data)
        return remote_file

    async def _wait_for_async_copy(self, share_name, file_path):
        count = 0
        share_client = self.fsc.get_share_client(share_name)
        file_client = share_client.get_file_client(file_path)
        properties = await file_client.get_file_properties()
        while properties.copy.status != 'success':
            count = count + 1
            if count > 10:
                self.fail('Timed out waiting for async copy to complete.')
            self.sleep(6)
            properties = await file_client.get_file_properties()
        assert properties.copy.status == 'success'

    async def assertFileEqual(self, file_client, expected_data):
        content = await file_client.download_file()
        actual_data = await content.readall()
        assert actual_data == expected_data

    class NonSeekableFile(object):
        def __init__(self, wrapped_file):
            self.wrapped_file = wrapped_file

        def write(self, data):
            self.wrapped_file.write(data)

        def read(self, count):
            return self.wrapped_file.read(count)

    # --Test cases for files ----------------------------------------------
    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_make_file_url(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)

        share = self.fsc.get_share_client("vhds")
        file_client = share.get_file_client("vhd_dir/my.vhd")

        # Act
        res = file_client.url

        # Assert
        assert res == ('https://' + storage_account_name + '.file.core.windows.net/vhds/vhd_dir/my.vhd')

    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_make_file_url_no_directory(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        share = self.fsc.get_share_client("vhds")
        file_client = share.get_file_client("my.vhd")

        # Act
        res = file_client.url

        # Assert
        assert res == ('https://' + storage_account_name + '.file.core.windows.net/vhds/my.vhd')

    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_make_file_url_with_protocol(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        url = self.account_url(storage_account_name, "file").replace('https', 'http')
        fsc = ShareServiceClient(url, credential=storage_account_key)
        share = fsc.get_share_client("vhds")
        file_client = share.get_file_client("vhd_dir/my.vhd")

        # Act
        res = file_client.url

        # Assert
        assert res == ('http://' + storage_account_name + '.file.core.windows.net/vhds/vhd_dir/my.vhd')

    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_make_file_url_with_sas(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        # cspell:disable-next-line
        sas = '?sv=2015-04-05&st=2015-04-29T22%3A18%3A26Z&se=2015-04-30T02%3A23%3A26Z&sr=b&sp=rw&sip=168.1.5.60-168.1.5.70&spr=https&sig=Z%2FRHIX5Xcg0Mq2rqI3OlWTjEg2tYkboXr1P9ZUXDtkk%3D'
        file_client = ShareFileClient(
            self.account_url(storage_account_name, "file"),
            share_name="vhds",
            file_path="vhd_dir/my.vhd",
            credential=sas
        )

        # Act
        res = file_client.url

        # Assert
        assert res == ('https://' + storage_account_name + '.file.core.windows.net/vhds/vhd_dir/my.vhd{}'.format(sas))

    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_create_file(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        await self._setup_share(storage_account_name, storage_account_key)
        file_name = self._get_file_reference()
        async with ShareFileClient(
            self.account_url(storage_account_name, "file"),
            share_name=self.share_name,
            file_path=file_name,
            credential=storage_account_key) as file_client:

            # Act
            resp = await file_client.create_file(1024)

            # Assert
            props = await file_client.get_file_properties()
            assert props is not None
            assert props.etag == resp['etag']
            assert props.last_modified == resp['last_modified']

    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_create_file_with_oauth(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")
        token_credential = self.generate_oauth_token()

        self._setup(storage_account_name, storage_account_key)
        await self._setup_share(storage_account_name, storage_account_key)
        file_name = self._get_file_reference()
        async with ShareFileClient(
                self.account_url(storage_account_name, "file"),
                share_name=self.share_name,
                file_path=file_name,
                credential=token_credential,
                token_intent=TEST_INTENT) as file_client:
            # Act
            resp = await file_client.create_file(1024)

            # Assert
            props = await file_client.get_file_properties()
            assert props is not None
            assert props.etag == resp['etag']
            assert props.last_modified == resp['last_modified']

    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_create_file_with_oauth_no_token_intent(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")
        token_credential = self.generate_oauth_token()

        self._setup(storage_account_name, storage_account_key)
        await self._setup_share(storage_account_name, storage_account_key)
        file_name = self._get_file_reference()

        # Assert
        with pytest.raises(ValueError):
            file_client = ShareFileClient(
                self.account_url(storage_account_name, "file"),
                share_name=self.share_name,
                file_path=file_name,
                credential=token_credential
            )

    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_create_file_with_trailing_dot(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        await self._setup_share(storage_account_name, storage_account_key)
        file_name = self._get_file_reference()
        async with ShareFileClient(
                self.account_url(storage_account_name, "file"),
                share_name=self.share_name,
                file_path=file_name + '.',
                credential=storage_account_key,
                allow_trailing_dot=True) as file_client:
            # Act
            resp = await file_client.create_file(1024)

            # Assert
            props = await file_client.get_file_properties()
            assert props is not None
            assert props.etag == resp['etag']
            assert props.last_modified == resp['last_modified']
            assert props.name == file_name + '.'

    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_create_file_with_trailing_dot_false(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        await self._setup_share(storage_account_name, storage_account_key)
        file_name = self._get_file_reference()
        file_client = ShareFileClient(
            self.account_url(storage_account_name, "file"),
            share_name=self.share_name,
            file_path=file_name + '.',
            credential=storage_account_key,
            allow_trailing_dot=False)

        # Act
        resp = await file_client.create_file(1024)

        # create file client with dot
        file_client_dotted = ShareFileClient(
            self.account_url(storage_account_name, "file"),
            share_name=self.share_name,
            file_path=file_name + '.',
            credential=storage_account_key,
            allow_trailing_dot=False)

        # create file client without dot
        file_client_no_dot = ShareFileClient(
            self.account_url(storage_account_name, "file"),
            share_name=self.share_name,
            file_path=file_name,
            credential=storage_account_key,
            allow_trailing_dot=False)

        props = await file_client.get_file_properties()
        props_dotted = await file_client_dotted.get_file_properties()
        props_no_dot = await file_client_no_dot.get_file_properties()

        # Assert
        assert props.name == file_name + '.'
        assert props.path == file_name + '.'
        assert props_dotted.name == file_name + '.'
        assert props_dotted.path == file_name + '.'
        assert props_no_dot.name == file_name
        assert props_no_dot.path == file_name

    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_create_file_with_metadata(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        await self._setup_share(storage_account_name, storage_account_key)
        metadata = {'hello': 'world', 'number': '42'}
        file_name = self._get_file_reference()
        async with ShareFileClient(
            self.account_url(storage_account_name, "file"),
            share_name=self.share_name,
            file_path=file_name,
            credential=storage_account_key) as file_client:

            # Act
            resp = await file_client.create_file(1024, metadata=metadata)

            # Assert
            props = await file_client.get_file_properties()
            assert props is not None
            assert props.etag == resp['etag']
            assert props.last_modified == resp['last_modified']
            assert props.metadata == metadata

    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_create_file_with_metadata_with_trailing_dot(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        await self._setup_share(storage_account_name, storage_account_key)
        metadata = {'hello': 'world', 'number': '42'}
        file_name = self._get_file_reference()
        async with ShareFileClient(
                self.account_url(storage_account_name, "file"),
                share_name=self.share_name,
                file_path=file_name + '.',
                credential=storage_account_key,
                allow_trailing_dot=True) as file_client:
            # Act
            resp = await file_client.create_file(1024, metadata=metadata)

            # Assert
            props = await file_client.get_file_properties()
            assert props is not None
            assert props.etag == resp['etag']
            assert props.last_modified == resp['last_modified']
            assert props.metadata == metadata
            assert props.name == file_name + '.'

    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_create_file_when_file_permission_is_too_long(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        file_client = await self._get_file_client(storage_account_name, storage_account_key)
        permission = str(self.get_random_bytes(8 * 1024 + 1))
        with pytest.raises(ValueError):
            await file_client.create_file(1024, file_permission=permission)

    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_create_file_with_invalid_file_permission(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        file_name = await self._get_file_client(storage_account_name, storage_account_key)

        with pytest.raises(HttpResponseError):
            await file_name.create_file(1024, file_permission="abcde")

    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_create_file_with_lease(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        file_client = await self._get_file_client(storage_account_name, storage_account_key)
        await file_client.create_file(1024)

        lease = await file_client.acquire_lease(lease_id='00000000-1111-2222-3333-444444444444')
        resp = await file_client.create_file(1024, lease=lease)
        assert resp is not None

        # There is currently a lease on the file so there should be an exception when delete the file without lease
        with pytest.raises(HttpResponseError):
            await file_client.delete_file()

        # There is currently a lease on the file so delete the file with the lease will succeed
        await file_client.delete_file(lease=lease)

    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_create_file_with_lease_oauth(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")
        token_credential = self.generate_oauth_token()

        self._setup(storage_account_name, storage_account_key)
        await self._setup_share(storage_account_name, storage_account_key)
        file_name = self._get_file_reference()
        file_client = ShareFileClient(
            self.account_url(storage_account_name, "file"),
            share_name=self.share_name,
            file_path=file_name,
            credential=token_credential,
            token_intent=TEST_INTENT)
        await file_client.create_file(1024)

        lease = await file_client.acquire_lease(lease_id='00000000-1111-2222-3333-444444444444')
        resp = await file_client.create_file(1024, lease=lease)
        assert resp is not None

        # There is currently a lease on the file so there should be an exception when delete the file without lease
        with pytest.raises(HttpResponseError):
            await file_client.delete_file()

        # There is currently a lease on the file so delete the file with the lease will succeed
        await file_client.delete_file(lease=lease)

    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_create_file_with_changed_lease(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        file_client = await self._get_file_client(storage_account_name, storage_account_key)
        await file_client.create_file(1024)

        lease = await file_client.acquire_lease(lease_id='00000000-1111-2222-3333-444444444444')
        old_lease_id = lease.id
        await lease.change('44444444-3333-2222-1111-000000000000')

        # use the old lease id to create file will throw exception.
        with pytest.raises(HttpResponseError):
            await file_client.create_file(1024, lease=old_lease_id)

        # use the new lease to create file will succeed.
        resp = await file_client.create_file(1024, lease=lease)

        assert resp is not None

    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_create_file_with_changed_lease_oauth(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")
        token_credential = self.generate_oauth_token()

        self._setup(storage_account_name, storage_account_key)
        await self._setup_share(storage_account_name, storage_account_key)
        file_name = self._get_file_reference()
        file_client = ShareFileClient(
            self.account_url(storage_account_name, "file"),
            share_name=self.share_name,
            file_path=file_name,
            credential=token_credential,
            token_intent=TEST_INTENT)
        await file_client.create_file(1024)

        lease = await file_client.acquire_lease(lease_id='00000000-1111-2222-3333-444444444444')
        old_lease_id = lease.id
        await lease.change('44444444-3333-2222-1111-000000000000')

        # use the old lease id to create file will throw exception.
        with pytest.raises(HttpResponseError):
            await file_client.create_file(1024, lease=old_lease_id)

        # use the new lease to create file will succeed.
        resp = await file_client.create_file(1024, lease=lease)

        assert resp is not None

    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_lease_operations_trailing_dot(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        await self._setup_share(storage_account_name, storage_account_key)
        file_name = self._get_file_reference()
        file_client = ShareFileClient(
            self.account_url(storage_account_name, "file"),
            share_name=self.share_name,
            file_path=file_name + '.',
            credential=storage_account_key,
            allow_trailing_dot=True)
        await file_client.create_file(1024)

        lease = await file_client.acquire_lease(lease_id='00000000-1111-2222-3333-444444444444')
        old_lease_id = lease.id
        await lease.change('44444444-3333-2222-1111-000000000000')

        # use the old lease id to create file will throw exception.
        with pytest.raises(HttpResponseError):
            await file_client.create_file(1024, lease=old_lease_id)

        # use the new lease to create file will succeed.
        resp = await file_client.create_file(1024, lease=lease)

        # break the lease
        await lease.break_lease()

        # create file without lease to show lease is broken
        resp = await file_client.create_file(1024)
        props = await file_client.get_file_properties()

        # Assert
        assert resp is not None
        assert props.name == file_name + '.'

    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_create_file_will_set_all_smb_properties(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        file_client = await self._get_file_client(storage_account_name, storage_account_key)

        # Act
        await file_client.create_file(1024)
        file_properties = await file_client.get_file_properties()

        # Assert
        assert file_properties is not None
        assert file_properties.change_time is not None
        assert file_properties.creation_time is not None
        assert file_properties.file_attributes is not None
        assert file_properties.last_write_time is not None

    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_create_file_set_smb_properties(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        file_client = await self._get_file_client(storage_account_name, storage_account_key)

        file_attributes = NTFSAttributes(read_only=True, archive=True)
        file_creation_time = file_last_write_time = file_change_time = datetime(2022, 3, 10, 10, 14, 30, 500000)

        # Act
        await file_client.create_file(
            size=1024,
            file_attributes=file_attributes,
            file_creation_time=file_creation_time,
            file_last_write_time=file_last_write_time,
            file_change_time=file_change_time)
        file_properties = await file_client.get_file_properties()

        # Assert
        assert file_properties is not None
        assert file_creation_time == file_properties.creation_time
        assert file_last_write_time == file_properties.last_write_time
        assert file_change_time == file_properties.change_time
        assert 'ReadOnly' in file_properties.file_attributes
        assert 'Archive' in file_properties.file_attributes

    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_file_exists(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        file_client = await self._create_file(storage_account_name, storage_account_key)

        # Act
        exists = await file_client.get_file_properties()

        # Assert
        assert exists

    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_snapshot_exists(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        await self._setup_share(storage_account_name, storage_account_key)
        share_client = self.fsc.get_share_client(self.share_name)
        directory_name = self.get_resource_name("directory")
        directory_client = await share_client.create_directory(directory_name)
        file_name = self._get_file_reference()
        file_client = directory_client.get_file_client(file_name)
        await file_client.upload_file(self.short_byte_data)

        snapshot = await share_client.create_snapshot()
        share_snapshot_client = self.fsc.get_share_client(self.share_name, snapshot=snapshot)
        file_snapshot_client = share_snapshot_client.get_directory_client(directory_name).get_file_client(file_name)

        await file_client.delete_file()

        # Act
        props = await file_snapshot_client.download_file()

        # Assert
        assert props

    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_file_not_exists(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        file_name = self._get_file_reference()
        file_client = ShareFileClient(
            self.account_url(storage_account_name, "file"),
            share_name=self.share_name,
            file_path="missingdir/" + file_name,
            credential=storage_account_key)

        # Act
        with pytest.raises(ResourceNotFoundError):
            await file_client.get_file_properties()

    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_file_exists_with_snapshot(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        file_client = await self._create_file(storage_account_name, storage_account_key)
        share_client = self.fsc.get_share_client(self.share_name)
        snapshot = await share_client.create_snapshot()
        await file_client.delete_file()

        # Act
        snapshot_client = ShareFileClient(
            self.account_url(storage_account_name, "file"),
            share_name=self.share_name,
            file_path=file_client.file_name,
            snapshot=snapshot,
            credential=storage_account_key)
        props = await snapshot_client.get_file_properties()

        # Assert
        assert props

    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_file_not_exists_with_snapshot(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        await self._setup_share(storage_account_name, storage_account_key)
        share_client = self.fsc.get_share_client(self.share_name)
        snapshot = await share_client.create_snapshot()

        file_client = await self._create_file(storage_account_name, storage_account_key)

        # Act
        snapshot_client = ShareFileClient(
            self.account_url(storage_account_name, "file"),
            share_name=self.share_name,
            file_path=file_client.file_name,
            snapshot=snapshot,
            credential=storage_account_key)

        # Assert
        with pytest.raises(ResourceNotFoundError):
            await snapshot_client.get_file_properties()

    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_resize_file(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        file_client = await self._create_file(storage_account_name, storage_account_key)

        # Act
        await file_client.resize_file(5)

        # Assert
        props = await file_client.get_file_properties()
        assert props.size == 5

    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_resize_file_with_lease(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        file_client = await self._create_file(storage_account_name, storage_account_key)
        lease = await file_client.acquire_lease(lease_id='00000000-1111-2222-3333-444444444444')

        # Act
        with pytest.raises(HttpResponseError):
            await file_client.resize_file(5)
        await file_client.resize_file(5, lease=lease)

        # Assert
        props = await file_client.get_file_properties()
        assert props.size == 5

    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_set_file_properties(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        file_client = await self._create_file(storage_account_name, storage_account_key)

        # Act
        content_settings = ContentSettings(
            content_language='spanish',
            content_disposition='inline')
        resp = await file_client.set_http_headers(content_settings=content_settings)

        # Assert
        properties = await file_client.get_file_properties()
        assert properties.content_settings.content_language == content_settings.content_language
        assert properties.content_settings.content_disposition == content_settings.content_disposition
        assert properties.last_write_time is not None
        assert properties.creation_time is not None
        assert properties.permission_key is not None

    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_set_file_properties_trailing_dot(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        await self._setup_share(storage_account_name, storage_account_key)
        file_name = self._get_file_reference()
        file_client = ShareFileClient(
                self.account_url(storage_account_name, "file"),
                share_name=self.share_name,
                file_path=file_name + '.',
                credential=storage_account_key,
                allow_trailing_dot=True)
        await file_client.create_file(1024)

        # Act
        content_settings = ContentSettings(
            content_language='spanish',
            content_disposition='inline')
        resp = await file_client.set_http_headers(content_settings=content_settings)

        # Assert
        properties = await file_client.get_file_properties()
        assert properties.content_settings.content_language == content_settings.content_language
        assert properties.content_settings.content_disposition == content_settings.content_disposition
        assert properties.last_write_time is not None
        assert properties.creation_time is not None
        assert properties.permission_key is not None
        assert properties.name == file_name + '.'

    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_set_file_properties_with_file_permission(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        file_client = await self._create_file(storage_account_name, storage_account_key)
        properties_on_creation = await file_client.get_file_properties()

        content_settings = ContentSettings(
            content_language='spanish',
            content_disposition='inline')

        ntfs_attributes = NTFSAttributes(archive=True, temporary=True)
        last_write_time = properties_on_creation.last_write_time + timedelta(hours=3)
        creation_time = properties_on_creation.creation_time + timedelta(hours=3)
        change_time = properties_on_creation.change_time + timedelta(hours=3)

        # Act
        await file_client.set_http_headers(
            content_settings=content_settings,
            file_attributes=ntfs_attributes,
            file_last_write_time=last_write_time,
            file_creation_time=creation_time,
            file_change_time=change_time
        )

        # Assert
        properties = await file_client.get_file_properties()
        assert properties.content_settings.content_language == content_settings.content_language
        assert properties.content_settings.content_disposition == content_settings.content_disposition
        assert properties.creation_time == creation_time
        assert properties.last_write_time == last_write_time
        assert properties.change_time == change_time
        assert "Archive" in properties.file_attributes
        assert "Temporary" in properties.file_attributes

    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_set_file_properties_with_oauth(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")
        token_credential = self.generate_oauth_token()

        self._setup(storage_account_name, storage_account_key)
        await self._setup_share(storage_account_name, storage_account_key)
        file_name = self._get_file_reference()
        async with ShareFileClient(
                self.account_url(storage_account_name, "file"),
                share_name=self.share_name,
                file_path=file_name,
                credential=token_credential,
                token_intent=TEST_INTENT) as file_client:
            # Act
            await file_client.create_file(1024)
            content_settings = ContentSettings(content_language='spanish', content_disposition='inline')
            resp = await file_client.set_http_headers(content_settings=content_settings)

            # Assert
            properties = await file_client.get_file_properties()
            assert properties.content_settings.content_language == content_settings.content_language
            assert properties.content_settings.content_disposition == content_settings.content_disposition
            assert properties.last_write_time is not None
            assert properties.creation_time is not None
            assert properties.permission_key is not None

    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_get_file_properties(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        file_client = await self._create_file(storage_account_name, storage_account_key)

        # Act
        properties = await file_client.get_file_properties()

        # Assert
        assert properties is not None
        assert properties.size == len(self.short_byte_data)

    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_get_file_properties_with_oauth(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")
        token_credential = self.generate_oauth_token()

        self._setup(storage_account_name, storage_account_key)
        await self._setup_share(storage_account_name, storage_account_key)
        file_name = self._get_file_reference()
        async with ShareFileClient(
                self.account_url(storage_account_name, "file"),
                share_name=self.share_name,
                file_path=file_name,
                credential=token_credential,
                token_intent=TEST_INTENT) as file_client:

            # Act
            resp = await file_client.create_file(1024)
            properties = await file_client.get_file_properties()

        # Assert
        assert properties is not None
        assert properties.size == len(self.short_byte_data)

    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_get_file_properties_trailing_dot(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        await self._setup_share(storage_account_name, storage_account_key)
        file_name = self._get_file_reference()
        file_client = ShareFileClient(
            self.account_url(storage_account_name, "file"),
            share_name=self.share_name,
            file_path=file_name + '.',
            credential=storage_account_key,
            allow_trailing_dot=True)
        await file_client.create_file(1024)

        # Ensure allow_trailing_dot=True is enforced properly by attempting to connect without trailing dot
        file_client_no_dot = ShareFileClient(
            self.account_url(storage_account_name, "file"),
            share_name=self.share_name,
            file_path=file_name,
            credential=storage_account_key)
        with pytest.raises(HttpResponseError):
            await file_client_no_dot.get_file_properties()

        # Act
        properties = await file_client.get_file_properties()

        # Assert
        assert properties is not None

    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_get_file_properties_with_invalid_lease_fails(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        file_client = await self._create_file(storage_account_name, storage_account_key)
        await file_client.acquire_lease(lease_id='00000000-1111-2222-3333-444444444444')

        # Act
        with pytest.raises(HttpResponseError):
            await file_client.get_file_properties(lease='44444444-3333-2222-1111-000000000000')

        # get properties on a leased file will succeed
        properties = await file_client.get_file_properties()

        # Assert
        assert properties is not None
        assert properties.size == len(self.short_byte_data)

    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_get_file_properties_with_snapshot(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        file_client = await self._create_file(storage_account_name, storage_account_key)
        metadata = {"test1": "foo", "test2": "bar"}
        await file_client.set_file_metadata(metadata)

        share_client = self.fsc.get_share_client(self.share_name)
        snapshot = await share_client.create_snapshot()

        metadata2 = {"test100": "foo100", "test200": "bar200"}
        await file_client.set_file_metadata(metadata2)

        # Act
        file_props = await file_client.get_file_properties()
        snapshot_client = ShareFileClient(
            self.account_url(storage_account_name, "file"),
            share_name=self.share_name,
            file_path=file_client.file_name,
            snapshot=snapshot,
            credential=storage_account_key)
        snapshot_props = await snapshot_client.get_file_properties()
        # Assert
        assert file_props is not None
        assert snapshot_props is not None
        assert snapshot_props.snapshot == snapshot_client.snapshot
        assert metadata == snapshot_props.metadata

    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_get_file_metadata_with_snapshot(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        file_client = await self._create_file(storage_account_name, storage_account_key)
        metadata = {"test1": "foo", "test2": "bar"}
        await file_client.set_file_metadata(metadata)

        share_client = self.fsc.get_share_client(self.share_name)
        snapshot = await share_client.create_snapshot()
        snapshot_client = ShareFileClient(
            self.account_url(storage_account_name, "file"),
            share_name=self.share_name,
            file_path=file_client.file_name,
            snapshot=snapshot,
            credential=storage_account_key)

        metadata2 = {"test100": "foo100", "test200": "bar200"}
        await file_client.set_file_metadata(metadata2)

        # Act
        file_metadata = await file_client.get_file_properties()
        file_snapshot_metadata = await snapshot_client.get_file_properties()

        # Assert
        assert metadata2 == file_metadata.metadata
        assert metadata == file_snapshot_metadata.metadata

    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_get_file_properties_with_non_existing_file(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        file_name = self._get_file_reference()
        file_client = ShareFileClient(
            self.account_url(storage_account_name, "file"),
            share_name=self.share_name,
            file_path=file_name,
            credential=storage_account_key)

        # Act
        with pytest.raises(ResourceNotFoundError):
            await file_client.get_file_properties()

            # Assert

    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_get_file_metadata(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        file_client = await self._create_file(storage_account_name, storage_account_key)

        # Act
        md = await file_client.get_file_properties()

        # Assert
        assert md.metadata is not None
        assert 0 == len(md.metadata)

    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_set_file_metadata_with_upper_case(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        metadata = {'hello': 'world', 'number': '42', 'UP': 'UPval'}
        file_client = await self._create_file(storage_account_name, storage_account_key)

        # Act
        await file_client.set_file_metadata(metadata)

        # Assert
        props = await file_client.get_file_properties()
        md = props.metadata
        assert 3 == len(md)
        assert md['hello'] == 'world'
        assert md['number'] == '42'
        assert md['UP'] == 'UPval'
        assert not 'up' in md

    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_set_file_metadata_with_oauth(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")
        token_credential = self.generate_oauth_token()

        self._setup(storage_account_name, storage_account_key)
        await self._setup_share(storage_account_name, storage_account_key)
        file_name = self._get_file_reference()
        async with ShareFileClient(
                self.account_url(storage_account_name, "file"),
                share_name=self.share_name,
                file_path=file_name,
                credential=token_credential,
                token_intent=TEST_INTENT) as file_client:
            metadata = {'hello': 'world', 'number': '42', 'UP': 'UPval'}

            # Act
            resp = await file_client.create_file(1024)
            await file_client.set_file_metadata(metadata)

            # Assert
            props = await file_client.get_file_properties()
            md = props.metadata
            assert 3 == len(md)
            assert md['hello'] == 'world'
            assert md['number'] == '42'
            assert md['UP'] == 'UPval'
            assert not 'up' in md

    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_break_lease_with_broken_period_fails(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        file_client = await self._create_file(storage_account_name, storage_account_key)
        lease = await file_client.acquire_lease(lease_id='00000000-1111-2222-3333-444444444444')

        # Assert
        assert lease is not None
        with pytest.raises(TypeError):
            await lease.break_lease(lease_break_period=5)

    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_set_file_metadata_with_broken_lease(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        metadata = {'hello': 'world', 'number': '42', 'UP': 'UPval'}
        file_client = await self._create_file(storage_account_name, storage_account_key)

        lease = await file_client.acquire_lease(lease_id='00000000-1111-2222-3333-444444444444')
        with pytest.raises(HttpResponseError):
            await file_client.set_file_metadata(metadata)

        lease_id_to_be_broken = lease.id
        await lease.break_lease()

        # Act
        # lease is broken, set metadata doesn't require a lease
        await file_client.set_file_metadata({'hello': 'world'})
        props = await file_client.get_file_properties()
        # Assert
        assert 1 == len(props.metadata)
        assert props.metadata['hello'] == 'world'

        # Act
        await file_client.acquire_lease(lease_id=lease_id_to_be_broken)
        await file_client.set_file_metadata(metadata, lease=lease_id_to_be_broken)
        # Assert
        props = await file_client.get_file_properties()
        md = props.metadata
        assert 3 == len(md)
        assert md['hello'] == 'world'
        assert md['number'] == '42'
        assert md['UP'] == 'UPval'
        assert not 'up' in md

    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_delete_file_with_existing_file(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        file_client = await self._create_file(storage_account_name, storage_account_key)

        # Act
        await file_client.delete_file()

        # Assert
        with pytest.raises(ResourceNotFoundError):
            await file_client.get_file_properties()

    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_delete_file_with_existing_file_oauth(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")
        token_credential = self.generate_oauth_token()

        self._setup(storage_account_name, storage_account_key)
        await self._setup_share(storage_account_name, storage_account_key)
        file_name = self._get_file_reference()
        file_client = ShareFileClient(
            self.account_url(storage_account_name, "file"),
            share_name=self.share_name,
            file_path=file_name,
            credential=token_credential,
            token_intent=TEST_INTENT)

        # Act
        resp = await file_client.create_file(1024)
        await file_client.delete_file()

        # Assert
        with pytest.raises(ResourceNotFoundError):
            await file_client.get_file_properties()

    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_delete_file_with_existing_file_trailing_dot(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        await self._setup_share(storage_account_name, storage_account_key)
        file_name = self._get_file_reference()
        file_client = ShareFileClient(
            self.account_url(storage_account_name, "file"),
            share_name=self.share_name,
            file_path=file_name + '.',
            credential=storage_account_key,
            allow_trailing_dot=True)
        await file_client.create_file(1024)

        # Act
        await file_client.delete_file()

        # Assert
        with pytest.raises(ResourceNotFoundError):
            await file_client.get_file_properties()

    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_delete_file_with_non_existing_file(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        file_name = self._get_file_reference()
        file_client = ShareFileClient(
            self.account_url(storage_account_name, "file"),
            share_name=self.share_name,
            file_path=file_name,
            credential=storage_account_key)

        # Act
        with pytest.raises(ResourceNotFoundError):
            await file_client.delete_file()

            # Assert

    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_update_range(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        file_client = await self._create_file(storage_account_name, storage_account_key)

        # Act
        data = b'abcdefghijklmnop' * 32
        await file_client.upload_range(data, offset=0, length=512)

        # Assert
        content = await file_client.download_file()
        content = await content.readall()
        assert data == content[:512]
        assert self.short_byte_data[512:] == content[512:]

    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_update_range_with_oauth(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")
        token_credential = self.generate_oauth_token()

        self._setup(storage_account_name, storage_account_key)
        await self._setup_share(storage_account_name, storage_account_key)
        file_client = ShareFileClient(
            self.account_url(storage_account_name, "file"),
            share_name=self.share_name,
            file_path='file1',
            credential=token_credential,
            token_intent=TEST_INTENT)

        # Act
        await file_client.upload_file(self.short_byte_data)
        data = b'abcdefghijklmnop' * 32
        await file_client.upload_range(data, offset=0, length=512)

        # Assert
        content = await file_client.download_file()
        content = await content.readall()
        assert data == content[:512]
        assert self.short_byte_data[512:] == content[512:]

    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_update_range_trailing_dot(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        await self._setup_share(storage_account_name, storage_account_key)
        file_name = self._get_file_reference()
        file_client = ShareFileClient(
            self.account_url(storage_account_name, "file"),
            share_name=self.share_name,
            file_path=file_name + '.',
            credential=storage_account_key,
            allow_trailing_dot=True)
        await file_client.upload_file(self.short_byte_data)

        # Act
        data = b'abcdefghijklmnop' * 32
        await file_client.upload_range(data, offset=0, length=512)
        props = await file_client.get_file_properties()

        # Assert
        content = await file_client.download_file()
        content = await content.readall()
        assert data == content[:512]
        assert self.short_byte_data[512:] == content[512:]
        assert props.name == file_name + '.'

    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_update_range_with_lease(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        file_client = await self._create_file(storage_account_name, storage_account_key)
        lease = await file_client.acquire_lease(lease_id='00000000-1111-2222-3333-444444444444')

        # Act
        data = b'abcdefghijklmnop' * 32
        with pytest.raises(HttpResponseError):
            await file_client.upload_range(data, offset=0, length=512)
        await file_client.upload_range(data, offset=0, length=512, lease=lease)

        # Assert
        content = await file_client.download_file()
        content = await content.readall()
        assert data == content[:512]
        assert self.short_byte_data[512:] == content[512:]

    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_update_range_with_md5(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        file_client = await self._create_file(storage_account_name, storage_account_key)

        # Act
        data = b'abcdefghijklmnop' * 32
        await file_client.upload_range(data, offset=0, length=512, validate_content=True)

        # Assert

    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_update_range_last_written_mode_now(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        file_client = await self._create_file(storage_account_name, storage_account_key)
        current_last_write_time = (await file_client.get_file_properties()).last_write_time

        # Act
        data = b'abcdefghijklmnop' * 32
        await file_client.upload_range(data, offset=0, length=512, file_last_write_mode="Now")

        # Assert
        new_last_write_time = (await file_client.get_file_properties()).last_write_time
        assert current_last_write_time != new_last_write_time

    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_update_range_last_written_mode_preserve(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        file_client = await self._create_file(storage_account_name, storage_account_key)
        current_last_write_time = (await file_client.get_file_properties()).last_write_time

        # Act
        data = b'abcdefghijklmnop' * 32
        await file_client.upload_range(data, offset=0, length=512, file_last_write_mode="Preserve")

        # Assert
        new_last_write_time = (await file_client.get_file_properties()).last_write_time
        assert current_last_write_time == new_last_write_time

    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_update_range_from_file_url_when_source_file_does_not_have_enough_bytes(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        source_file_name = 'testfile1'
        source_file_client = await self._create_file(storage_account_name, storage_account_key, file_name=source_file_name)

        destination_file_name = 'filetoupdate'
        destination_file_client = await self._create_file(storage_account_name, storage_account_key, file_name=destination_file_name)

        # generate SAS for the source file
        sas_token_for_source_file = self.generate_sas(
            generate_file_sas,
            source_file_client.account_name,
            source_file_client.share_name,
            source_file_client.file_path,
            source_file_client.credential.account_key)

        source_file_url = source_file_client.url + '?' + sas_token_for_source_file

        # Act
        with pytest.raises(HttpResponseError):
            # when the source file has less bytes than 2050, throw exception
            await destination_file_client.upload_range_from_url(source_file_url, offset=0, length=2050, source_offset=0)

    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_update_range_from_file_url(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        source_file_name = 'testfile'
        source_file_client = await self._create_file(storage_account_name, storage_account_key, file_name=source_file_name)
        data = b'abcdefghijklmnop' * 32
        await source_file_client.upload_range(data, offset=0, length=512)

        destination_file_name = 'filetoupdate'
        destination_file_client = await self._create_empty_file(storage_account_name, storage_account_key, file_name=destination_file_name)

        # generate SAS for the source file
        sas_token_for_source_file = self.generate_sas(
            generate_file_sas,
            source_file_client.account_name,
            source_file_client.share_name,
            source_file_client.file_path,
            source_file_client.credential.account_key,
            FileSasPermissions(read=True),
            expiry=datetime.utcnow() + timedelta(hours=1))

        source_file_url = source_file_client.url + '?' + sas_token_for_source_file
        # Act
        await destination_file_client.upload_range_from_url(source_file_url, offset=0, length=512, source_offset=0)

        # Assert
        # To make sure the range of the file is actually updated
        file_ranges = await destination_file_client.get_ranges()
        file_content = await destination_file_client.download_file(offset=0, length=512)
        file_content = await file_content.readall()
        assert 1 == len(file_ranges)
        assert 0 == file_ranges[0].get('start')
        assert 511 == file_ranges[0].get('end')
        assert data == file_content

    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_update_range_from_file_url_with_oauth(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        source_blob_client = await self._create_source_blob()
        access_token = await self.generate_oauth_token().get_token("https://storage.azure.com/.default")
        token = "Bearer {}".format(access_token.token)

        destination_file_name = 'filetoupdate'
        destination_file_client = await self._create_empty_file(
            storage_account_name, storage_account_key, file_name=destination_file_name)
        with pytest.raises(HttpResponseError):
            await destination_file_client.upload_range_from_url(
                source_blob_client.url, offset=0, length=512, source_offset=0)

        await destination_file_client.upload_range_from_url(
            source_blob_client.url, offset=0, length=512, source_offset=0, source_authorization=token)

    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_update_range_from_file_url_with_lease(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        source_file_name = 'testfile'
        source_file_client = await self._create_file(storage_account_name, storage_account_key, file_name=source_file_name)
        data = b'abcdefghijklmnop' * 32
        await source_file_client.upload_range(data, offset=0, length=512)

        destination_file_name = 'filetoupdate'
        destination_file_client = await self._create_empty_file(storage_account_name, storage_account_key, file_name=destination_file_name)
        lease = await destination_file_client.acquire_lease(lease_id='00000000-1111-2222-3333-444444444444')

        # generate SAS for the source file
        sas_token_for_source_file = self.generate_sas(
            generate_file_sas,
            source_file_client.account_name,
            source_file_client.share_name,
            source_file_client.file_path,
            source_file_client.credential.account_key,
            FileSasPermissions(read=True),
            expiry=datetime.utcnow() + timedelta(hours=1))

        source_file_url = source_file_client.url + '?' + sas_token_for_source_file
        # Act
        with pytest.raises(HttpResponseError):
            await destination_file_client.upload_range_from_url(source_file_url, offset=0, length=512, source_offset=0)
        await destination_file_client.upload_range_from_url(source_file_url, offset=0, length=512, source_offset=0,
                                                            lease=lease)

        # Assert
        # To make sure the range of the file is actually updated
        file_ranges = await destination_file_client.get_ranges()
        file_content = await destination_file_client.download_file(offset=0, length=512)
        file_content = await file_content.readall()
        assert 1 == len(file_ranges)
        assert 0 == file_ranges[0].get('start')
        assert 511 == file_ranges[0].get('end')
        assert data == file_content

    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_update_big_range_from_file_url(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        source_file_name = 'testfile1'
        end = 1048575

        source_file_client = await self._create_empty_file(storage_account_name, storage_account_key, file_name=source_file_name, file_size=1024 * 1024)
        data = b'abcdefghijklmnop' * 65536
        await source_file_client.upload_range(data, offset=0, length=end+1)

        destination_file_name = 'filetoupdate1'
        destination_file_client = await self._create_empty_file(storage_account_name, storage_account_key, file_name=destination_file_name, file_size=1024 * 1024)

        # generate SAS for the source file
        sas_token_for_source_file = self.generate_sas(
            generate_file_sas,
            source_file_client.account_name,
            source_file_client.share_name,
            source_file_client.file_path,
            source_file_client.credential.account_key,
            FileSasPermissions(read=True),
            expiry=datetime.utcnow() + timedelta(hours=1))

        source_file_url = source_file_client.url + '?' + sas_token_for_source_file

        # Act
        await destination_file_client.upload_range_from_url(source_file_url, offset=0, length=end+1, source_offset=0)

        # Assert
        # To make sure the range of the file is actually updated
        file_ranges = await destination_file_client.get_ranges()
        file_content = await destination_file_client.download_file(offset=0, length=end + 1)
        file_content = await file_content.readall()
        assert 1 == len(file_ranges)
        assert 0 == file_ranges[0].get('start')
        assert end == file_ranges[0].get('end')
        assert data == file_content

    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_update_range_from_file_url_last_written_mode_now(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        source_file_client = await self._create_file(storage_account_name, storage_account_key, file_name='testfile')
        data = b'abcdefghijklmnop' * 32
        await source_file_client.upload_range(data, offset=0, length=512)

        destination_file_client = await self._create_empty_file(
            storage_account_name,
            storage_account_key,
            file_name='filetoupdate')
        current_last_write_time = (await destination_file_client.get_file_properties()).last_write_time

        # generate SAS for the source file
        sas_token_for_source_file = self.generate_sas(
            generate_file_sas,
            source_file_client.account_name,
            source_file_client.share_name,
            source_file_client.file_path,
            source_file_client.credential.account_key,
            FileSasPermissions(read=True),
            expiry=datetime.utcnow() + timedelta(hours=1))

        source_file_url = source_file_client.url + '?' + sas_token_for_source_file

        # Act
        await destination_file_client.upload_range_from_url(source_file_url, offset=0, length=512, source_offset=0,
                                                            file_last_write_mode="Now")

        # Assert
        new_last_write_time = (await destination_file_client.get_file_properties()).last_write_time
        assert current_last_write_time != new_last_write_time

    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_update_range_from_file_url_last_written_mode_preserve(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        source_file_client = await self._create_file(storage_account_name, storage_account_key, file_name='testfile')
        data = b'abcdefghijklmnop' * 32
        await source_file_client.upload_range(data, offset=0, length=512)

        destination_file_client = await self._create_empty_file(
            storage_account_name,
            storage_account_key,
            file_name='filetoupdate')
        current_last_write_time = (await destination_file_client.get_file_properties()).last_write_time

        # generate SAS for the source file
        sas_token_for_source_file = self.generate_sas(
            generate_file_sas,
            source_file_client.account_name,
            source_file_client.share_name,
            source_file_client.file_path,
            source_file_client.credential.account_key,
            FileSasPermissions(read=True),
            expiry=datetime.utcnow() + timedelta(hours=1))

        source_file_url = source_file_client.url + '?' + sas_token_for_source_file

        # Act
        await destination_file_client.upload_range_from_url(source_file_url, offset=0, length=512, source_offset=0,
                                                            file_last_write_mode="Preserve")

        # Assert
        new_last_write_time = (await destination_file_client.get_file_properties()).last_write_time
        assert current_last_write_time == new_last_write_time

    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_clear_range(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        file_client = await self._create_file(storage_account_name, storage_account_key)

        # Act
        resp = await file_client.clear_range(offset=0, length=512)

        # Assert
        content = await file_client.download_file()
        content = await content.readall()
        assert b'\x00' * 512 == content[:512]
        assert self.short_byte_data[512:] == content[512:]

    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_clear_range_trailing_dot(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        await self._setup_share(storage_account_name, storage_account_key)
        file_name = self._get_file_reference()
        file_client = ShareFileClient(
            self.account_url(storage_account_name, "file"),
            share_name=self.share_name,
            file_path=file_name + '.',
            credential=storage_account_key,
            allow_trailing_dot=True)
        await file_client.upload_file(self.short_byte_data)

        # Act
        resp = await file_client.clear_range(offset=0, length=512)
        props = await file_client.get_file_properties()

        # Assert
        content = await file_client.download_file()
        content = await content.readall()
        assert b'\x00' * 512 == content[:512]
        assert self.short_byte_data[512:] == content[512:]
        assert props.name == file_name + '.'

    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_update_file_unicode(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        file_client = await self._create_file(storage_account_name, storage_account_key)

        # Act
        data = u'abcdefghijklmnop' * 32
        await file_client.upload_range(data, offset=0, length=512)

        encoded = data.encode('utf-8')

        # Assert
        content = await file_client.download_file()
        content = await content.readall()
        assert encoded == content[:512]
        assert self.short_byte_data[512:] == content[512:]

        # Assert

    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_list_ranges_none(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        file_name = self._get_file_reference()
        await self._setup_share(storage_account_name, storage_account_key)
        file_client = ShareFileClient(
            self.account_url(storage_account_name, "file"),
            share_name=self.share_name,
            file_path=file_name,
            credential=storage_account_key)
        await file_client.create_file(1024)

        # Act
        ranges = await file_client.get_ranges()

        # Assert
        assert ranges is not None
        assert len(ranges) == 0

    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_list_ranges_none_trailing_dot(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        file_name = self._get_file_reference()
        await self._setup_share(storage_account_name, storage_account_key)
        file_client = ShareFileClient(
            self.account_url(storage_account_name, "file"),
            share_name=self.share_name,
            file_path=file_name + '.',
            credential=storage_account_key,
            allow_trailing_dot=True)
        await file_client.create_file(1024)

        # Act
        ranges = await file_client.get_ranges()
        props = await file_client.get_file_properties()

        # Assert
        assert ranges is not None
        assert len(ranges) == 0
        assert props.name == file_name + '.'

    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_list_ranges_none_with_invalid_lease_fails(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        file_name = self._get_file_reference()
        await self._setup_share(storage_account_name, storage_account_key)
        file_client = ShareFileClient(
            self.account_url(storage_account_name, "file"),
            share_name=self.share_name,
            file_path=file_name,
            credential=storage_account_key)
        await file_client.create_file(1024)
        await file_client.acquire_lease(lease_id='00000000-1111-2222-3333-444444444444')

        # Act
        with pytest.raises(HttpResponseError):
            await file_client.get_ranges(lease='44444444-3333-2222-1111-000000000000')

        # Get ranges on a leased file will succeed without provide the lease
        ranges = await file_client.get_ranges()

        # Assert
        assert ranges is not None
        assert len(ranges) == 0

    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_list_ranges_diff(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        file_name = self._get_file_reference()
        await self._setup_share(storage_account_name, storage_account_key)
        file_client = ShareFileClient(
            self.account_url(storage_account_name, "file"),
            share_name=self.share_name,
            file_path=file_name,
            credential=storage_account_key)

        await file_client.create_file(2048)
        share_client = self.fsc.get_share_client(self.share_name)
        snapshot1 = await share_client.create_snapshot()

        data = self.get_random_bytes(1536)
        await file_client.upload_range(data, offset=0, length=1536)
        snapshot2 = await share_client.create_snapshot()
        await file_client.clear_range(offset=512, length=512)

        ranges1, cleared1 = await file_client.get_ranges_diff(previous_sharesnapshot=snapshot1)
        ranges2, cleared2 = await file_client.get_ranges_diff(previous_sharesnapshot=snapshot2['snapshot'])

        # Assert
        assert ranges1 is not None
        assert isinstance(ranges1, list)
        assert len(ranges1) == 2
        assert isinstance(cleared1, list)
        assert len(cleared1) == 1
        assert ranges1[0]['start'] == 0
        assert ranges1[0]['end'] == 511
        assert cleared1[0]['start'] == 512
        assert cleared1[0]['end'] == 1023
        assert ranges1[1]['start'] == 1024
        assert ranges1[1]['end'] == 1535

        assert ranges2 is not None
        assert isinstance(ranges2, list)
        assert len(ranges2) == 0
        assert isinstance(cleared2, list)
        assert len(cleared2) == 1
        assert cleared2[0]['start'] == 512
        assert cleared2[0]['end'] == 1023

    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_list_ranges_diff_with_oauth(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")
        token_credential = self.generate_oauth_token()

        self._setup(storage_account_name, storage_account_key)
        file_name = self._get_file_reference()
        await self._setup_share(storage_account_name, storage_account_key)
        file_client = ShareFileClient(
            self.account_url(storage_account_name, "file"),
            share_name=self.share_name,
            file_path=file_name,
            credential=token_credential,
            token_intent=TEST_INTENT)

        await file_client.create_file(2048)
        share_client = self.fsc.get_share_client(self.share_name)
        snapshot1 = await share_client.create_snapshot()

        data = self.get_random_bytes(1536)
        await file_client.upload_range(data, offset=0, length=1536)
        snapshot2 = await share_client.create_snapshot()
        await file_client.clear_range(offset=512, length=512)

        ranges1, cleared1 = await file_client.get_ranges_diff(previous_sharesnapshot=snapshot1)
        ranges2, cleared2 = await file_client.get_ranges_diff(previous_sharesnapshot=snapshot2['snapshot'])

        # Assert
        assert ranges1 is not None
        assert isinstance(ranges1, list)
        assert len(ranges1) == 2
        assert isinstance(cleared1, list)
        assert len(cleared1) == 1
        assert ranges1[0]['start'] == 0
        assert ranges1[0]['end'] == 511
        assert cleared1[0]['start'] == 512
        assert cleared1[0]['end'] == 1023
        assert ranges1[1]['start'] == 1024
        assert ranges1[1]['end'] == 1535

        assert ranges2 is not None
        assert isinstance(ranges2, list)
        assert len(ranges2) == 0
        assert isinstance(cleared2, list)
        assert len(cleared2) == 1
        assert cleared2[0]['start'] == 512
        assert cleared2[0]['end'] == 1023

    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_list_ranges_diff_trailing_dot(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        file_name = self._get_file_reference()
        await self._setup_share(storage_account_name, storage_account_key)
        file_client = ShareFileClient(
            self.account_url(storage_account_name, "file"),
            share_name=self.share_name,
            file_path=file_name + '.',
            credential=storage_account_key,
            allow_trailing_dot=True)

        await file_client.create_file(2048)
        share_client = self.fsc.get_share_client(self.share_name)
        snapshot1 = await share_client.create_snapshot()

        data = self.get_random_bytes(1536)
        await file_client.upload_range(data, offset=0, length=1536)
        snapshot2 = await share_client.create_snapshot()
        await file_client.clear_range(offset=512, length=512)

        ranges1, cleared1 = await file_client.get_ranges_diff(previous_sharesnapshot=snapshot1)
        ranges2, cleared2 = await file_client.get_ranges_diff(previous_sharesnapshot=snapshot2['snapshot'])
        props = await file_client.get_file_properties()

        # Assert
        assert ranges1 is not None
        assert isinstance(ranges1, list)
        assert len(ranges1) == 2
        assert isinstance(cleared1, list)
        assert len(cleared1) == 1
        assert ranges1[0]['start'] == 0
        assert ranges1[0]['end'] == 511
        assert cleared1[0]['start'] == 512
        assert cleared1[0]['end'] == 1023
        assert ranges1[1]['start'] == 1024
        assert ranges1[1]['end'] == 1535

        assert ranges2 is not None
        assert isinstance(ranges2, list)
        assert len(ranges2) == 0
        assert isinstance(cleared2, list)
        assert len(cleared2) == 1
        assert cleared2[0]['start'] == 512
        assert cleared2[0]['end'] == 1023

        assert props.name == file_name + '.'

    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_list_ranges_2(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        file_name = self._get_file_reference()
        await self._setup_share(storage_account_name, storage_account_key)
        file_client = ShareFileClient(
            self.account_url(storage_account_name, "file"),
            share_name=self.share_name,
            file_path=file_name,
            credential=storage_account_key)
        await file_client.create_file(2048)

        data = b'abcdefghijklmnop' * 32
        resp1 = await file_client.upload_range(data, offset=0, length=512)
        resp2 = await file_client.upload_range(data, offset=1024, length=512)

        # Act
        ranges = await file_client.get_ranges()

        # Assert
        assert ranges is not None
        assert len(ranges) == 2
        assert ranges[0]['start'] == 0
        assert ranges[0]['end'] == 511
        assert ranges[1]['start'] == 1024
        assert ranges[1]['end'] == 1535

    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_list_ranges_none_from_snapshot(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        file_name = self._get_file_reference()
        await self._setup_share(storage_account_name, storage_account_key)
        file_client = ShareFileClient(
            self.account_url(storage_account_name, "file"),
            share_name=self.share_name,
            file_path=file_name,
            credential=storage_account_key)
        await file_client.create_file(1024)
        
        share_client = self.fsc.get_share_client(self.share_name)
        snapshot = await share_client.create_snapshot()
        snapshot_client = ShareFileClient(
            self.account_url(storage_account_name, "file"),
            share_name=self.share_name,
            file_path=file_client.file_name,
            snapshot=snapshot,
            credential=storage_account_key)

        await file_client.delete_file()

        # Act
        ranges = await snapshot_client.get_ranges()

        # Assert
        assert ranges is not None
        assert len(ranges) == 0

    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_list_ranges_none_from_snapshot_with_oauth(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")
        token_credential = self.generate_oauth_token()

        self._setup(storage_account_name, storage_account_key)
        file_name = self._get_file_reference()
        await self._setup_share(storage_account_name, storage_account_key)
        file_client = ShareFileClient(
            self.account_url(storage_account_name, "file"),
            share_name=self.share_name,
            file_path=file_name,
            credential=token_credential,
            token_intent=TEST_INTENT)
        await file_client.create_file(1024)

        share_client = self.fsc.get_share_client(self.share_name)
        snapshot = await share_client.create_snapshot()
        snapshot_client = ShareFileClient(
            self.account_url(storage_account_name, "file"),
            share_name=self.share_name,
            file_path=file_client.file_name,
            snapshot=snapshot,
            credential=token_credential,
            token_intent=TEST_INTENT)

        await file_client.delete_file()

        # Act
        ranges = await snapshot_client.get_ranges()

        # Assert
        assert ranges is not None
        assert len(ranges) == 0

    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_list_ranges_2_from_snapshot(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        file_name = self._get_file_reference()
        await self._setup_share(storage_account_name, storage_account_key)
        file_client = ShareFileClient(
            self.account_url(storage_account_name, "file"),
            share_name=self.share_name,
            file_path=file_name,
            credential=storage_account_key)
        await file_client.create_file(2048)
        data = b'abcdefghijklmnop' * 32
        resp1 = await file_client.upload_range(data, offset=0, length=512)
        resp2 = await file_client.upload_range(data, offset=1024, length=512)
        
        share_client = self.fsc.get_share_client(self.share_name)
        snapshot = await share_client.create_snapshot()
        snapshot_client = ShareFileClient(
            self.account_url(storage_account_name, "file"),
            share_name=self.share_name,
            file_path=file_client.file_name,
            snapshot=snapshot,
            credential=storage_account_key)

        await file_client.delete_file()

        # Act
        ranges = await snapshot_client.get_ranges()

        # Assert
        assert ranges is not None
        assert len(ranges) == 2
        assert ranges[0]['start'] == 0
        assert ranges[0]['end'] == 511
        assert ranges[1]['start'] == 1024
        assert ranges[1]['end'] == 1535

    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_copy_file_with_existing_file(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        source_client = await self._create_file(storage_account_name, storage_account_key)
        file_client = ShareFileClient(
            self.account_url(storage_account_name, "file"),
            share_name=self.share_name,
            file_path='file1copy',
            credential=storage_account_key)

        # Act
        copy = await file_client.start_copy_from_url(source_client.url)

        # Assert
        assert copy is not None
        assert copy['copy_status'] == 'success'
        assert copy['copy_id'] is not None

        copy_file = await file_client.download_file()
        content = await copy_file.readall()
        assert content == self.short_byte_data

    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_copy_file_with_existing_file_oauth(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")
        token_credential = self.generate_oauth_token()

        self._setup(storage_account_name, storage_account_key)
        source_client = await self._create_file(storage_account_name, storage_account_key)
        file_client = ShareFileClient(
            self.account_url(storage_account_name, "file"),
            share_name=self.share_name,
            file_path='file1copy',
            credential=token_credential,
            token_intent=TEST_INTENT)

        # Act
        copy = await file_client.start_copy_from_url(source_client.url)

        # Assert
        assert copy is not None
        assert copy['copy_status'] == 'success'
        assert copy['copy_id'] is not None

        copy_file = await file_client.download_file()
        content = await copy_file.readall()
        assert content == self.short_byte_data

    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_copy_file_with_existing_file_trailing_dot(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        await self._setup_share(storage_account_name, storage_account_key)
        file_name = self._get_file_reference()
        source_client = ShareFileClient(
            self.account_url(storage_account_name, "file"),
            share_name=self.share_name,
            file_path=file_name + '.',
            credential=storage_account_key,
            allow_trailing_dot=True,
            allow_source_trailing_dot=True)
        await source_client.upload_file(self.short_byte_data)

        file_client = ShareFileClient(
            self.account_url(storage_account_name, "file"),
            share_name=self.share_name,
            file_path='file1copy.',
            credential=storage_account_key,
            allow_trailing_dot=True,
            allow_source_trailing_dot=True)

    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_copy_existing_file_with_lease(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        source_client = await self._create_file(storage_account_name, storage_account_key)
        file_client = ShareFileClient(
            self.account_url(storage_account_name, "file"),
            share_name=self.share_name,
            file_path='file1copy',
            credential=storage_account_key)
        await file_client.create_file(1024)
        lease = await file_client.acquire_lease(lease_id='00000000-1111-2222-3333-444444444444')

        # Act
        with pytest.raises(HttpResponseError):
            await file_client.start_copy_from_url(source_client.url)

        copy = await file_client.start_copy_from_url(source_client.url, lease=lease)

        # Assert
        assert copy is not None
        assert copy['copy_status'] == 'success'
        assert copy['copy_id'] is not None

        copy_file = await file_client.download_file()
        content = await copy_file.readall()
        assert content == self.short_byte_data

    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_copy_file_ignore_readonly(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        source_file = await self._create_file(storage_account_name, storage_account_key)
        dest_file = ShareFileClient(
            self.account_url(storage_account_name, "file"),
            share_name=self.share_name,
            file_path='file1copy',
            credential=storage_account_key)

        file_attributes = NTFSAttributes(read_only=True)
        await dest_file.create_file(1024, file_attributes=file_attributes)

        # Act
        with pytest.raises(HttpResponseError):
            await dest_file.start_copy_from_url(source_file.url)

        copy = await dest_file.start_copy_from_url(source_file.url, ignore_read_only=True)

        # Assert
        assert copy is not None
        assert copy['copy_status'] == 'success'
        assert copy['copy_id'] is not None

        copy_file = await dest_file.download_file()
        content = await copy_file.readall()
        assert content == self.short_byte_data

    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_copy_file_with_specifying_acl_copy_behavior_attributes(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        source_client = await self._create_file(storage_account_name, storage_account_key)
        file_client = ShareFileClient(
            self.account_url(storage_account_name, "file"),
            share_name=self.share_name,
            file_path='file1copy',
            credential=storage_account_key)
        source_props = await source_client.get_file_properties()

        file_creation_time = source_props.creation_time - timedelta(hours=1)
        file_last_write_time = source_props.last_write_time - timedelta(hours=1)
        file_change_time = source_props.change_time - timedelta(hours=1)
        file_attributes = "Temporary|NoScrubData"

        # Act
        copy = await file_client.start_copy_from_url(
            source_client.url,
            ignore_read_only=True,
            file_permission=TEST_FILE_PERMISSIONS,
            file_attributes=file_attributes,
            file_creation_time=file_creation_time,
            file_last_write_time=file_last_write_time,
            file_change_time=file_change_time,
        )

        # Assert
        dest_prop = await file_client.get_file_properties()
        # to make sure the attributes are the same as the set ones
        assert file_creation_time == dest_prop['creation_time']
        assert file_last_write_time == dest_prop['last_write_time']
        assert file_change_time == dest_prop['change_time']
        assert 'Temporary' in dest_prop['file_attributes']
        assert 'NoScrubData' in dest_prop['file_attributes']

        assert copy is not None
        assert copy['copy_status'] == 'success'
        assert copy['copy_id'] is not None

        copy_file = await file_client.download_file()
        content = await copy_file.readall()
        assert content == self.short_byte_data

    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_copy_file_with_specifying_acl_and_attributes_from_source(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        source_client = await self._create_file(storage_account_name, storage_account_key)
        source_prop = await source_client.get_file_properties()
        file_client = ShareFileClient(
            self.account_url(storage_account_name, "file"),
            share_name=self.share_name,
            file_path='file1copy',
            credential=storage_account_key)

        # Act
        copy = await file_client.start_copy_from_url(
            source_client.url,
            permission_key='source'
        )

        # Assert
        dest_prop = await file_client.get_file_properties()
        # to make sure the acl is copied from source
        assert source_prop['permission_key'] == dest_prop['permission_key']

        assert copy is not None
        assert copy['copy_status'] == 'success'
        assert copy['copy_id'] is not None

        copy_file = await file_client.download_file()
        content = await copy_file.readall()
        assert content == self.short_byte_data

    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_copy_file_async_private_file_async(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")
        secondary_storage_account_name = kwargs.pop("secondary_storage_account_name")
        secondary_storage_account_key = kwargs.pop("secondary_storage_account_key")

        self._setup(storage_account_name, storage_account_key, secondary_storage_account_name, secondary_storage_account_key)
        await self._setup_share(storage_account_name, storage_account_key)
        await self._create_remote_share()
        source_file = await self._create_remote_file()

        # Act
        target_file_name = 'targetfile'
        file_client = ShareFileClient(
            self.account_url(storage_account_name, "file"),
            share_name=self.share_name,
            file_path=target_file_name,
            credential=storage_account_key)
        with pytest.raises(HttpResponseError) as e:
            await file_client.start_copy_from_url(source_file.url)

        # Assert
        assert e.value.error_code == StorageErrorCode.cannot_verify_copy_source
        await self.fsc2.delete_share(self.remote_share_name)

    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_copy_file_async_private_file_with_sas_async(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")
        secondary_storage_account_name = kwargs.pop("secondary_storage_account_name")
        secondary_storage_account_key = kwargs.pop("secondary_storage_account_key")

        self._setup(storage_account_name, storage_account_key, secondary_storage_account_name, secondary_storage_account_key)
        data = b'12345678' * 1024
        await self._create_remote_share()
        source_file = await self._create_remote_file(file_data=data)
        sas_token = self.generate_sas(
            generate_file_sas,
            source_file.account_name,
            source_file.share_name,
            source_file.file_path,
            source_file.credential.account_key,
            permission=FileSasPermissions(read=True),
            expiry=datetime.utcnow() + timedelta(hours=1),
        )
        source_url = source_file.url + '?' + sas_token

        # Act
        target_file_name = 'targetfile'
        await self._setup_share(storage_account_name, storage_account_key)
        file_client = ShareFileClient(
            self.account_url(storage_account_name, "file"),
            share_name=self.share_name,
            file_path=target_file_name,
            credential=storage_account_key)
        copy_resp = await file_client.start_copy_from_url(source_url)

        # Assert
        assert copy_resp['copy_status'] in ['success', 'pending']
        await self._wait_for_async_copy(self.share_name, target_file_name) 

        content = await file_client.download_file()
        actual_data = await content.readall()
        assert actual_data == data

    @pytest.mark.live_test_only
    @FileSharePreparer()
    async def test_abort_copy_file_async(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")
        secondary_storage_account_name = kwargs.pop("secondary_storage_account_name")
        secondary_storage_account_key = kwargs.pop("secondary_storage_account_key")

        self._setup(storage_account_name, storage_account_key, secondary_storage_account_name, secondary_storage_account_key)
        data = b'12345678' * 1024 * 1024
        await self._setup_share(storage_account_name, storage_account_key)
        await self._create_remote_share()
        source_file = await self._create_remote_file(file_data=data)
        sas_token = self.generate_sas(
            generate_file_sas,
            source_file.account_name,
            source_file.share_name,
            source_file.file_path,
            source_file.credential.account_key,
            permission=FileSasPermissions(read=True),
            expiry=datetime.utcnow() + timedelta(hours=1),
        )
        source_url = source_file.url + '?' + sas_token

        # Act
        target_file_name = 'targetfile'
        file_client = ShareFileClient(
            self.account_url(storage_account_name, "file"),
            share_name=self.share_name,
            file_path=target_file_name,
            credential=storage_account_key)
        copy_resp = await file_client.start_copy_from_url(source_url)
        assert copy_resp['copy_status'] == 'pending'
        await file_client.abort_copy(copy_resp)

        # Assert
        target_file = await file_client.download_file()
        content = await target_file.readall()
        assert content == b''
        assert target_file.properties.copy.status == 'aborted'

    @pytest.mark.live_test_only
    @FileSharePreparer()
    async def test_abort_copy_file_async_with_oauth(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")
        secondary_storage_account_name = kwargs.pop("secondary_storage_account_name")
        secondary_storage_account_key = kwargs.pop("secondary_storage_account_key")
        token_credential = self.generate_oauth_token()

        self._setup(storage_account_name, storage_account_key, secondary_storage_account_name, secondary_storage_account_key)
        data = b'12345678' * 1024 * 1024
        await self._setup_share(storage_account_name, storage_account_key)
        await self._create_remote_share()
        source_file = await self._create_remote_file(file_data=data)
        sas_token = self.generate_sas(
            generate_file_sas,
            source_file.account_name,
            source_file.share_name,
            source_file.file_path,
            source_file.credential.account_key,
            permission=FileSasPermissions(read=True),
            expiry=datetime.utcnow() + timedelta(hours=1),
        )
        source_url = source_file.url + '?' + sas_token

        # Act
        target_file_name = 'targetfile'
        file_client = ShareFileClient(
            self.account_url(storage_account_name, "file"),
            share_name=self.share_name,
            file_path=target_file_name,
            credential=token_credential,
            token_intent=TEST_INTENT)
        copy_resp = await file_client.start_copy_from_url(source_url)
        assert copy_resp['copy_status'] == 'pending'
        await file_client.abort_copy(copy_resp)

        # Assert
        target_file = await file_client.download_file()
        content = await target_file.readall()
        assert content == b''
        assert target_file.properties.copy.status == 'aborted'

    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_abort_copy_file_with_synchronous_copy_fails(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        source_file = await self._create_file(storage_account_name, storage_account_key)

        # Act
        target_file_name = 'targetfile'
        file_client = ShareFileClient(
            self.account_url(storage_account_name, "file"),
            share_name=self.share_name,
            file_path=target_file_name,
            credential=storage_account_key)
        copy_resp = await file_client.start_copy_from_url(source_file.url)

        with pytest.raises(HttpResponseError):
            await file_client.abort_copy(copy_resp)

        # Assert
        assert copy_resp['copy_status'] == 'success'

    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_unicode_get_file_unicode_name(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        file_name = '啊齄丂狛狜'
        await self._setup_share(storage_account_name, storage_account_key)
        file_client = ShareFileClient(
            self.account_url(storage_account_name, "file"),
            share_name=self.share_name,
            file_path=file_name,
            credential=storage_account_key)
        await file_client.upload_file(b'hello world')

        # Act
        content = await file_client.download_file()
        content = await content.readall()

        # Assert
        assert content == b'hello world'

    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_unicode_get_file_unicode_name_with_lease(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        file_name = '啊齄丂狛狜'
        await self._setup_share(storage_account_name, storage_account_key)
        file_client = ShareFileClient(
            self.account_url(storage_account_name, "file"),
            share_name=self.share_name,
            file_path=file_name,
            credential=storage_account_key)
        await file_client.create_file(1024)
        lease = await file_client.acquire_lease(lease_id='00000000-1111-2222-3333-444444444444')

        with pytest.raises(HttpResponseError):
            await file_client.upload_file(b'hello world')

        await file_client.upload_file(b'hello world', lease=lease)

        # Act
        # download the file with a wrong lease id will fail
        with pytest.raises(HttpResponseError):
            await file_client.upload_file(b'hello world', lease='44444444-3333-2222-1111-000000000000')

        content = await file_client.download_file()
        content = await content.readall()

        # Assert
        assert content == b'hello world'

    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_file_unicode_data(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        file_name = self._get_file_reference()
        await self._setup_share(storage_account_name, storage_account_key)
        file_client = ShareFileClient(
            self.account_url(storage_account_name, "file"),
            share_name=self.share_name,
            file_path=file_name,
            credential=storage_account_key)

        # Act
        data = u'hello world啊齄丂狛狜'.encode('utf-8')
        await file_client.upload_file(data)

        # Assert
        content = await file_client.download_file()
        content = await content.readall()
        assert content == data

    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_file_unicode_data_and_file_attributes(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        file_client = await self._get_file_client(storage_account_name, storage_account_key)

        # Act
        data = u'hello world啊齄丂狛狜'.encode('utf-8')
        await file_client.upload_file(data, file_attributes=NTFSAttributes(temporary=True))

        # Assert
        content = await file_client.download_file()
        transformed_content = await content.readall()
        properties = await file_client.get_file_properties()
        assert transformed_content == data
        assert 'Temporary' in properties.file_attributes

    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_unicode_get_file_binary_data(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        base64_data = 'AAECAwQFBgcICQoLDA0ODxAREhMUFRYXGBkaGxwdHh8gISIjJCUmJygpKissLS4vMDEyMzQ1Njc4OTo7PD0+P0BBQkNERUZHSElKS0xNTk9QUVJTVFVWV1hZWltcXV5fYGFiY2RlZmdoaWprbG1ub3BxcnN0dXZ3eHl6e3x9fn+AgYKDhIWGh4iJiouMjY6PkJGSk5SVlpeYmZqbnJ2en6ChoqOkpaanqKmqq6ytrq+wsbKztLW2t7i5uru8vb6/wMHCw8TFxsfIycrLzM3Oz9DR0tPU1dbX2Nna29zd3t/g4eLj5OXm5+jp6uvs7e7v8PHy8/T19vf4+fr7/P3+/wABAgMEBQYHCAkKCwwNDg8QERITFBUWFxgZGhscHR4fICEiIyQlJicoKSorLC0uLzAxMjM0NTY3ODk6Ozw9Pj9AQUJDREVGR0hJSktMTU5PUFFSU1RVVldYWVpbXF1eX2BhYmNkZWZnaGlqa2xtbm9wcXJzdHV2d3h5ent8fX5/gIGCg4SFhoeIiYqLjI2Oj5CRkpOUlZaXmJmam5ydnp+goaKjpKWmp6ipqqusra6vsLGys7S1tre4ubq7vL2+v8DBwsPExcbHyMnKy8zNzs/Q0dLT1NXW19jZ2tvc3d7f4OHi4+Tl5ufo6err7O3u7/Dx8vP09fb3+Pn6+/z9/v8AAQIDBAUGBwgJCgsMDQ4PEBESExQVFhcYGRobHB0eHyAhIiMkJSYnKCkqKywtLi8wMTIzNDU2Nzg5Ojs8PT4/QEFCQ0RFRkdISUpLTE1OT1BRUlNUVVZXWFlaW1xdXl9gYWJjZGVmZ2hpamtsbW5vcHFyc3R1dnd4eXp7fH1+f4CBgoOEhYaHiImKi4yNjo+QkZKTlJWWl5iZmpucnZ6foKGio6SlpqeoqaqrrK2ur7CxsrO0tba3uLm6u7y9vr/AwcLDxMXGx8jJysvMzc7P0NHS09TV1tfY2drb3N3e3+Dh4uPk5ebn6Onq6+zt7u/w8fLz9PX29/j5+vv8/f7/AAECAwQFBgcICQoLDA0ODxAREhMUFRYXGBkaGxwdHh8gISIjJCUmJygpKissLS4vMDEyMzQ1Njc4OTo7PD0+P0BBQkNERUZHSElKS0xNTk9QUVJTVFVWV1hZWltcXV5fYGFiY2RlZmdoaWprbG1ub3BxcnN0dXZ3eHl6e3x9fn+AgYKDhIWGh4iJiouMjY6PkJGSk5SVlpeYmZqbnJ2en6ChoqOkpaanqKmqq6ytrq+wsbKztLW2t7i5uru8vb6/wMHCw8TFxsfIycrLzM3Oz9DR0tPU1dbX2Nna29zd3t/g4eLj5OXm5+jp6uvs7e7v8PHy8/T19vf4+fr7/P3+/w=='
        binary_data = base64.b64decode(base64_data)
        await self._setup_share(storage_account_name, storage_account_key)

        file_name = self._get_file_reference()
        file_client = ShareFileClient(
            self.account_url(storage_account_name, "file"),
            share_name=self.share_name,
            file_path=file_name,
            credential=storage_account_key)
        await file_client.upload_file(binary_data)

        # Act
        content = await file_client.download_file()
        content = await content.readall()

        # Assert
        assert content == binary_data

    @pytest.mark.live_test_only
    @FileSharePreparer()
    async def test_create_file_from_bytes_with_progress(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        await self._setup_share(storage_account_name, storage_account_key)
        file_name = self._get_file_reference()
        data = self.get_random_bytes(LARGE_FILE_SIZE)
        file_client = ShareFileClient(
            self.account_url(storage_account_name, "file"),
            share_name=self.share_name,
            file_path=file_name,
            credential=storage_account_key,
            max_range_size=4 * 1024)

        # Act
        progress = []
        def callback(response):
            current = response.context['upload_stream_current']
            total = response.context['data_stream_total']
            if current is not None:
                progress.append((current, total))

        await file_client.upload_file(data, max_concurrency=2, raw_response_hook=callback)

        # Assert
        await self.assertFileEqual(file_client, data)

    @pytest.mark.live_test_only
    @FileSharePreparer()
    async def test_create_file_from_bytes_with_index(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        file_name = self._get_file_reference()
        await self._setup_share(storage_account_name, storage_account_key)
        data = self.get_random_bytes(LARGE_FILE_SIZE)
        index = 1024
        file_client = ShareFileClient(
            self.account_url(storage_account_name, "file"),
            share_name=self.share_name,
            file_path=file_name,
            credential=storage_account_key,
            max_range_size=4 * 1024)

        # Act
        response = await file_client.upload_file(data[index:], max_concurrency=2)
        assert isinstance(response, dict)
        assert 'last_modified' in response
        assert 'etag' in response

        # Assert
        await self.assertFileEqual(file_client, data[1024:])

    @pytest.mark.live_test_only
    @FileSharePreparer()
    async def test_create_file_from_bytes_with_index_and_count(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        file_name = self._get_file_reference()
        await self._setup_share(storage_account_name, storage_account_key)
        data = self.get_random_bytes(LARGE_FILE_SIZE)
        index = 512
        count = 1024
        file_client = ShareFileClient(
            self.account_url(storage_account_name, "file"),
            share_name=self.share_name,
            file_path=file_name,
            credential=storage_account_key,
            max_range_size=4 * 1024)

        # Act
        response = await file_client.upload_file(data[index:], length=count, max_concurrency=2)
        assert isinstance(response, dict)
        assert 'last_modified' in response
        assert 'etag' in response

        # Assert
        await self.assertFileEqual(file_client, data[index:index + count])

    @pytest.mark.live_test_only
    @FileSharePreparer()
    async def test_create_file_from_path(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        file_name = self._get_file_reference()
        await self._setup_share(storage_account_name, storage_account_key)
        data = self.get_random_bytes(LARGE_FILE_SIZE)
        file_client = ShareFileClient(
            self.account_url(storage_account_name, "file"),
            share_name=self.share_name,
            file_path=file_name,
            credential=storage_account_key,
            max_range_size=4 * 1024)

        # Act
        with tempfile.TemporaryFile() as temp_file:
            temp_file.write(data)
            temp_file.seek(0)
            response = await file_client.upload_file(temp_file, max_concurrency=2)
            assert isinstance(response, dict)
            assert 'last_modified' in response
            assert 'etag' in response

        # Assert
        await self.assertFileEqual(file_client, data)

    @pytest.mark.live_test_only
    @FileSharePreparer()
    async def test_create_file_from_path_with_progress(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        file_name = self._get_file_reference()
        await self._setup_share(storage_account_name, storage_account_key)
        data = self.get_random_bytes(LARGE_FILE_SIZE)
        file_client = ShareFileClient(
            self.account_url(storage_account_name, "file"),
            share_name=self.share_name,
            file_path=file_name,
            credential=storage_account_key,
            max_range_size=4 * 1024)

        # Act
        progress = []
        def callback(response):
            current = response.context['upload_stream_current']
            total = response.context['data_stream_total']
            if current is not None:
                progress.append((current, total))

        with tempfile.TemporaryFile() as temp_file:
            temp_file.write(data)
            temp_file.seek(0)
            response = await file_client.upload_file(temp_file, max_concurrency=2, raw_response_hook=callback)
            assert isinstance(response, dict)
            assert 'last_modified' in response
            assert 'etag' in response

        # Assert
        await self.assertFileEqual(file_client, data)
        self.assert_upload_progress(len(data), self.fsc._config.max_range_size, progress, unknown_size=False)

    @pytest.mark.live_test_only
    @FileSharePreparer()
    async def test_create_file_from_stream(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        file_name = self._get_file_reference()
        await self._setup_share(storage_account_name, storage_account_key)
        data = self.get_random_bytes(LARGE_FILE_SIZE)
        file_client = ShareFileClient(
            self.account_url(storage_account_name, "file"),
            share_name=self.share_name,
            file_path=file_name,
            credential=storage_account_key,
            max_range_size=4 * 1024)

        # Act
        file_size = len(data)
        with tempfile.TemporaryFile() as temp_file:
            temp_file.write(data)
            temp_file.seek(0)
            response = await file_client.upload_file(temp_file, max_concurrency=2)
            assert isinstance(response, dict)
            assert 'last_modified' in response
            assert 'etag' in response

        # Assert
        await self.assertFileEqual(file_client, data[:file_size])

    @pytest.mark.live_test_only
    @FileSharePreparer()
    async def test_create_file_from_stream_non_seekable(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        file_name = self._get_file_reference()
        await self._setup_share(storage_account_name, storage_account_key)
        data = self.get_random_bytes(LARGE_FILE_SIZE)
        file_client = ShareFileClient(
            self.account_url(storage_account_name, "file"),
            share_name=self.share_name,
            file_path=file_name,
            credential=storage_account_key,
            max_range_size=4 * 1024)

        # Act
        file_size = len(data)
        with tempfile.TemporaryFile() as temp_file:
            temp_file.write(data)
            temp_file.seek(0)
            non_seekable_file = TestStorageFileAsync.NonSeekableFile(temp_file)
            await file_client.upload_file(non_seekable_file, length=file_size, max_concurrency=1)

        # Assert
        await self.assertFileEqual(file_client, data[:file_size])

    @pytest.mark.live_test_only
    @FileSharePreparer()
    async def test_create_file_from_stream_with_progress(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        file_name = self._get_file_reference()
        await self._setup_share(storage_account_name, storage_account_key)
        data = self.get_random_bytes(LARGE_FILE_SIZE)
        file_client = ShareFileClient(
            self.account_url(storage_account_name, "file"),
            share_name=self.share_name,
            file_path=file_name,
            credential=storage_account_key,
            max_range_size=4 * 1024)

        # Act
        progress = []
        def callback(response):
            current = response.context['upload_stream_current']
            total = response.context['data_stream_total']
            if current is not None:
                progress.append((current, total))

        file_size = len(data)
        with tempfile.TemporaryFile() as temp_file:
            temp_file.write(data)
            temp_file.seek(0)
            await file_client.upload_file(temp_file, max_concurrency=2, raw_response_hook=callback)

        # Assert
        await self.assertFileEqual(file_client, data[:file_size])
        self.assert_upload_progress(len(data), self.fsc._config.max_range_size, progress, unknown_size=False)

    @pytest.mark.live_test_only
    @FileSharePreparer()
    async def test_create_file_from_stream_truncated(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        file_name = self._get_file_reference()
        await self._setup_share(storage_account_name, storage_account_key)
        data = self.get_random_bytes(LARGE_FILE_SIZE)
        file_client = ShareFileClient(
            self.account_url(storage_account_name, "file"),
            share_name=self.share_name,
            file_path=file_name,
            credential=storage_account_key,
            max_range_size=4 * 1024)

        # Act
        file_size = len(data) - 512
        with tempfile.TemporaryFile() as temp_file:
            temp_file.write(data)
            temp_file.seek(0)
            await file_client.upload_file(temp_file, length=file_size, max_concurrency=4)

        # Assert
        await self.assertFileEqual(file_client, data[:file_size])

    @pytest.mark.live_test_only
    @FileSharePreparer()
    async def test_create_file_from_stream_with_progress_truncated(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        file_name = self._get_file_reference()
        await self._setup_share(storage_account_name, storage_account_key)
        data = self.get_random_bytes(LARGE_FILE_SIZE)
        file_client = ShareFileClient(
            self.account_url(storage_account_name, "file"),
            share_name=self.share_name,
            file_path=file_name,
            credential=storage_account_key,
            max_range_size=4 * 1024)

        # Act
        progress = []
        def callback(response):
            current = response.context['upload_stream_current']
            total = response.context['data_stream_total']
            if current is not None:
                progress.append((current, total))

        file_size = len(data) - 5
        with tempfile.TemporaryFile() as temp_file:
            temp_file.write(data)
            temp_file.seek(0)
            await file_client.upload_file(temp_file, length=file_size, max_concurrency=2, raw_response_hook=callback)

        # Assert
        await self.assertFileEqual(file_client, data[:file_size])
        self.assert_upload_progress(file_size, self.fsc._config.max_range_size, progress, unknown_size=False)

    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_create_file_from_async_generator(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        await self._setup_share(storage_account_name, storage_account_key)
        file_name = self._get_file_reference()
        data = b'Hello Async World!'

        async def data_generator():
            for _ in range(3):
                yield data
                await asyncio.sleep(0.1)

        file_client = ShareFileClient(
            self.account_url(storage_account_name, "file"),
            share_name=self.share_name,
            file_path=file_name,
            credential=storage_account_key)

        # Act
        file_size = len(data*3)
        await file_client.upload_file(data_generator(), length=file_size)

        # Assert
        await self.assertFileEqual(file_client, data*3)

    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_create_file_from_text(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        file_name = self._get_file_reference()
        await self._setup_share(storage_account_name, storage_account_key)
        text = u'hello 啊齄丂狛狜 world'
        data = text.encode('utf-8')
        file_client = ShareFileClient(
            self.account_url(storage_account_name, "file"),
            share_name=self.share_name,
            file_path=file_name,
            credential=storage_account_key,
            max_range_size=4 * 1024)

        # Act
        await file_client.upload_file(text)

        # Assert
        await self.assertFileEqual(file_client, data)

    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_create_file_from_text_with_encoding(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        file_name = self._get_file_reference()
        await self._setup_share(storage_account_name, storage_account_key)
        text = u'hello 啊齄丂狛狜 world'
        data = text.encode('utf-16')
        file_client = ShareFileClient(
            self.account_url(storage_account_name, "file"),
            share_name=self.share_name,
            file_path=file_name,
            credential=storage_account_key,
            max_range_size=4 * 1024)

        # Act
        await file_client.upload_file(text, encoding='UTF-16')

        # Assert
        await self.assertFileEqual(file_client, data)
        self._teardown(file_name)

    @pytest.mark.live_test_only
    @FileSharePreparer()
    async def test_create_file_from_text_chunked_upload(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        file_name = self._get_file_reference()
        await self._setup_share(storage_account_name, storage_account_key)
        data = self.get_random_text_data(LARGE_FILE_SIZE)
        encoded_data = data.encode('utf-8')
        file_client = ShareFileClient(
            self.account_url(storage_account_name, "file"),
            share_name=self.share_name,
            file_path=file_name,
            credential=storage_account_key,
            max_range_size=4 * 1024)

        # Act
        await file_client.upload_file(data)

        # Assert
        await self.assertFileEqual(file_client, encoded_data)
        self._teardown(file_name)

    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_create_file_with_md5_small(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        file_name = self._get_file_reference()
        await self._setup_share(storage_account_name, storage_account_key)
        data = self.get_random_bytes(512)
        file_client = ShareFileClient(
            self.account_url(storage_account_name, "file"),
            share_name=self.share_name,
            file_path=file_name,
            credential=storage_account_key,
            max_range_size=4 * 1024)

        # Act
        await file_client.upload_file(data, validate_content=True)
        self._teardown(file_name)
        # Assert

    @pytest.mark.live_test_only
    @FileSharePreparer()
    async def test_create_file_with_md5_large(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        file_name = self._get_file_reference()
        await self._setup_share(storage_account_name, storage_account_key)
        data = self.get_random_bytes(LARGE_FILE_SIZE)
        file_client = ShareFileClient(
            self.account_url(storage_account_name, "file"),
            share_name=self.share_name,
            file_path=file_name,
            credential=storage_account_key,
            max_range_size=4 * 1024)

        # Act
        await file_client.upload_file(data, validate_content=True, max_concurrency=2)
        self._teardown(file_name)
        # Assert

    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_create_file_progress(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        await self._setup_share(storage_account_name, storage_account_key)

        file_name = self._get_file_reference()
        file_client = ShareFileClient(
            self.account_url(storage_account_name, "file"),
            share_name=self.share_name,
            file_path=file_name,
            credential=storage_account_key,
            max_range_size=1024)

        data = b'a' * 5 * 1024
        progress = ProgressTracker(len(data), 1024)

        # Act
        await file_client.upload_file(data, progress_hook=progress.assert_progress)

        # Assert
        progress.assert_complete()

    @pytest.mark.live_test_only
    @FileSharePreparer()
    async def test_create_file_progress_parallel(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # parallel tests introduce random order of requests, can only run live
        self._setup(storage_account_name, storage_account_key)
        await self._setup_share(storage_account_name, storage_account_key)

        file_name = self._get_file_reference()
        file_client = ShareFileClient(
            self.account_url(storage_account_name, "file"),
            share_name=self.share_name,
            file_path=file_name,
            credential=storage_account_key,
            max_range_size=1024)

        data = b'a' * 5 * 1024
        progress = ProgressTracker(len(data), 1024)

        # Act
        await file_client.upload_file(data, progress_hook=progress.assert_progress, max_concurrency=3)

        # Assert
        progress.assert_complete()

    # --Test cases for sas & acl ------------------------------------------------
    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_sas_access_file(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        file_client = await self._create_file(storage_account_name, storage_account_key)
        token = self.generate_sas(
            generate_file_sas,
            file_client.account_name,
            file_client.share_name,
            file_client.file_path,
            file_client.credential.account_key,
            permission=FileSasPermissions(read=True),
            expiry=datetime.utcnow() + timedelta(hours=1),
        )

        # Act
        file_client = ShareFileClient(
            self.account_url(storage_account_name, "file"),
            share_name=self.share_name,
            file_path=file_client.file_name,
            credential=token)
        content = await file_client.download_file()
        content = await content.readall()

        # Assert
        assert self.short_byte_data == content

    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_sas_signed_identifier(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")
        variables = kwargs.pop('variables', {})

        self._setup(storage_account_name, storage_account_key)
        file_client = await self._create_file(storage_account_name, storage_account_key)
        share_client = self.fsc.get_share_client(self.share_name)

        access_policy = AccessPolicy()
        start_time = self.get_datetime_variable(variables, 'start_time', datetime.utcnow() - timedelta(hours=1))
        expiry_time = self.get_datetime_variable(variables, 'expiry_time', datetime.utcnow() + timedelta(hours=1))
        access_policy.start = start_time
        access_policy.expiry = expiry_time
        access_policy.permission = FileSasPermissions(read=True)
        identifiers = {'testid': access_policy}
        await share_client.set_share_access_policy(identifiers)

        token = self.generate_sas(
            generate_file_sas,
            file_client.account_name,
            file_client.share_name,
            file_client.file_path,
            file_client.credential.account_key,
            policy_id='testid')

        # Act
        sas_file = ShareFileClient.from_file_url(
            file_client.url,
            credential=token)

        content = await file_client.download_file()
        content = await content.readall()

        # Assert
        assert self.short_byte_data == content

        return variables

    @pytest.mark.live_test_only
    @FileSharePreparer()
    async def test_account_sas(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        file_client = await self._create_file(storage_account_name, storage_account_key)
        token = self.generate_sas(
            generate_account_sas,
            self.fsc.account_name,
            self.fsc.credential.account_key,
            ResourceTypes(object=True),
            AccountSasPermissions(read=True),
            datetime.utcnow() + timedelta(hours=1),
        )

        # Act
        file_client = ShareFileClient(
            self.account_url(storage_account_name, "file"),
            share_name=self.share_name,
            file_path=file_client.file_name,
            credential=token)

        response = requests.get(file_client.url)

        # Assert
        assert response.ok
        assert self.short_byte_data == response.content

    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_account_sas_credential(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        file_client = await self._create_file(storage_account_name, storage_account_key)
        token = self.generate_sas(
            generate_account_sas,
            self.fsc.account_name,
            self.fsc.credential.account_key,
            ResourceTypes(object=True),
            AccountSasPermissions(read=True),
            datetime.utcnow() + timedelta(hours=1),
        )

        # Act
        file_client = ShareFileClient(
            self.account_url(storage_account_name, "file"),
            share_name=self.share_name,
            file_path=file_client.file_name,
            credential=AzureSasCredential(token))

        properties = await file_client.get_file_properties()

        # Assert
        assert properties is not None

    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_azure_named_key_credential_access(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")


        self._setup(storage_account_name, storage_account_key)
        file_client = await self._create_file(storage_account_name, storage_account_key)
        named_key = AzureNamedKeyCredential(storage_account_name, storage_account_key)

        # Act
        file_client = ShareFileClient(
            self.account_url(storage_account_name, "file"),
            share_name=self.share_name,
            file_path=file_client.file_name,
            credential=named_key)

        properties = await file_client.get_file_properties()

        # Assert
        assert properties is not None

    @FileSharePreparer()
    async def test_account_sas_raises_if_sas_already_in_uri(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")

        with pytest.raises(ValueError):
            ShareFileClient(
                self.account_url(storage_account_name, "file") + "?sig=foo",
                share_name="foo",
                file_path="foo",
                credential=AzureSasCredential("?foo=bar"))

    @pytest.mark.live_test_only
    @FileSharePreparer()
    async def test_shared_read_access_file(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        file_client = await self._create_file(storage_account_name, storage_account_key)
        token = self.generate_sas(
            generate_file_sas,
            file_client.account_name,
            file_client.share_name,
            file_client.file_path,
            file_client.credential.account_key,
            permission=FileSasPermissions(read=True),
            expiry=datetime.utcnow() + timedelta(hours=1),
        )

        # Act
        file_client = ShareFileClient(
            self.account_url(storage_account_name, "file"),
            share_name=self.share_name,
            file_path=file_client.file_name,
            credential=token)
        response = requests.get(file_client.url)

        # Assert
        assert response.ok
        assert self.short_byte_data == response.content

    @pytest.mark.live_test_only
    @FileSharePreparer()
    async def test_shared_read_access_file_with_content_query_params(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        file_client = await self._create_file(storage_account_name, storage_account_key)
        token = self.generate_sas(
            generate_file_sas,
            file_client.account_name,
            file_client.share_name,
            file_client.file_path,
            file_client.credential.account_key,
            permission=FileSasPermissions(read=True),
            expiry=datetime.utcnow() + timedelta(hours=1),
            cache_control='no-cache',
            content_disposition='inline',
            content_encoding='utf-8',
            content_language='fr',
            content_type='text',
        )

        # Act
        file_client = ShareFileClient(
            self.account_url(storage_account_name, "file"),
            share_name=self.share_name,
            file_path=file_client.file_name,
            credential=token)
        response = requests.get(file_client.url)

        # Assert
        assert self.short_byte_data == response.content
        assert response.headers['cache-control'] == 'no-cache'
        assert response.headers['content-disposition'] == 'inline'
        assert response.headers['content-encoding'] == 'utf-8'
        assert response.headers['content-language'] == 'fr'
        assert response.headers['content-type'] == 'text'

    @pytest.mark.live_test_only
    @FileSharePreparer()
    async def test_shared_write_access_file(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        updated_data = b'updated file data'
        file_client_admin = await self._create_file(storage_account_name, storage_account_key)
        token = self.generate_sas(
            generate_file_sas,
            file_client_admin.account_name,
            file_client_admin.share_name,
            file_client_admin.file_path,
            file_client_admin.credential.account_key,
            permission=FileSasPermissions(write=True),
            expiry=datetime.utcnow() + timedelta(hours=1),
        )
        file_client = ShareFileClient(
            self.account_url(storage_account_name, "file"),
            share_name=self.share_name,
            file_path=file_client_admin.file_name,
            credential=token)

        # Act
        headers = {'x-ms-range': 'bytes=0-16', 'x-ms-write': 'update'}
        response = requests.put(file_client.url + '&comp=range', headers=headers, data=updated_data)

        # Assert
        assert response.ok
        file_content = await file_client_admin.download_file()
        file_content = await file_content.readall()
        assert updated_data == file_content[:len(updated_data)]

    @pytest.mark.live_test_only
    @FileSharePreparer()
    async def test_shared_delete_access_file(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        file_client_admin = await self._create_file(storage_account_name, storage_account_key)
        token = self.generate_sas(
            generate_file_sas,
            file_client_admin.account_name,
            file_client_admin.share_name,
            file_client_admin.file_path,
            file_client_admin.credential.account_key,
            permission=FileSasPermissions(delete=True),
            expiry=datetime.utcnow() + timedelta(hours=1),
        )
        file_client = ShareFileClient(
            self.account_url(storage_account_name, "file"),
            share_name=self.share_name,
            file_path=file_client_admin.file_name,
            credential=token)

        # Act
        response = requests.delete(file_client.url)

        # Assert
        assert response.ok
        with pytest.raises(ResourceNotFoundError):
            await file_client_admin.download_file()

    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_rename_file(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        source_file = await self._create_file(storage_account_name, storage_account_key, 'file1')

        # Act
        new_file = await source_file.rename_file('file2')

        # Assert
        assert 'file2' == new_file.file_name
        props = await new_file.get_file_properties()
        assert props is not None

    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_rename_file_with_oauth(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        await self._setup_share(storage_account_name, storage_account_key)
        file_name = self._get_file_reference()
        async with ShareFileClient(
                self.account_url(storage_account_name, "file"),
                share_name=self.share_name,
                file_path=file_name,
                credential=storage_account_key) as file_client:
            # Act
            resp = await file_client.create_file(1024)
            new_file = await file_client.rename_file('file2')

            # Assert
            assert 'file2' == new_file.file_name
            props = await new_file.get_file_properties()
            assert props is not None


    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_rename_file_different_directory(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        await self._setup_share(storage_account_name, storage_account_key)
        share_client = self.fsc.get_share_client(self.share_name)

        source_directory = await share_client.create_directory('dir1')
        dest_directory = await share_client.create_directory('dir2')
        source_file = await source_directory.upload_file('file1', self.short_byte_data)

        # Act
        new_file = await source_file.rename_file(dest_directory.directory_path + '/' + source_file.file_name)

        # Assert
        assert 'dir2' in new_file.file_path
        props = await new_file.get_file_properties()
        assert props is not None

    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_rename_file_ignore_readonly(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        await self._setup_share(storage_account_name, storage_account_key)
        share_client = self.fsc.get_share_client(self.share_name)

        source_file = share_client.get_file_client('file1')
        await source_file.create_file(1024)
        dest_file = share_client.get_file_client('file2')

        file_attributes = NTFSAttributes(read_only=True)
        await dest_file.create_file(1024, file_attributes=file_attributes)

        # Act
        new_file = await source_file.rename_file(dest_file.file_name, overwrite=True, ignore_read_only=True)

        # Assert
        assert 'file2' == new_file.file_name
        props = await new_file.get_file_properties()
        assert props is not None

    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_rename_file_file_permission(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        await self._setup_share(storage_account_name, storage_account_key)
        share_client = self.fsc.get_share_client(self.share_name)
        file_permission_key = await share_client.create_permission_for_share(TEST_FILE_PERMISSIONS)

        source_file = share_client.get_file_client('file1')
        await source_file.create_file(1024)

        # Act
        new_file = await source_file.rename_file('file2', file_permission=TEST_FILE_PERMISSIONS)

        # Assert
        props = await new_file.get_file_properties()
        assert props is not None
        assert file_permission_key == props.permission_key

    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_rename_file_preserve_permission(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        await self._setup_share(storage_account_name, storage_account_key)
        share_client = self.fsc.get_share_client(self.share_name)

        source_file = share_client.get_file_client('file1')
        await source_file.create_file(1024, file_permission=TEST_FILE_PERMISSIONS)

        source_props = await source_file.get_file_properties()
        source_permission_key = source_props.permission_key

        # Act
        new_file = await source_file.rename_file('file2', file_permission='preserve')

        # Assert
        props = await new_file.get_file_properties()
        assert props is not None
        assert source_permission_key == props.permission_key

    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_rename_file_smb_properties(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        source_file = await self._create_file(storage_account_name, storage_account_key, 'file1')

        file_attributes = NTFSAttributes(read_only=True, archive=True)
        file_creation_time = datetime(2022, 1, 26, 10, 9, 30, 500000)
        file_last_write_time = datetime(2022, 1, 26, 10, 14, 30, 500000)
        file_change_time = datetime(2022, 3, 7, 10, 14, 30, 500000)

        # Act
        new_file = await source_file.rename_file(
            'file2',
            file_attributes=file_attributes,
            file_creation_time=file_creation_time,
            file_last_write_time=file_last_write_time,
            file_change_time=file_change_time)

        # Assert
        props = await new_file.get_file_properties()
        assert props is not None
        assert str(file_attributes), props.file_attributes.replace(' ' == '')
        assert file_creation_time == props.creation_time
        assert file_last_write_time == props.last_write_time
        assert file_change_time == props.change_time

    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_rename_file_content_type(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        source_file = await self._create_file(storage_account_name, storage_account_key, 'file1')
        content_type = 'text/plain'

        # Act
        new_file = await source_file.rename_file(
            'file2',
            content_type=content_type)

        # Assert
        props = await new_file.get_file_properties()
        assert props is not None
        assert content_type == props.content_settings.content_type

    @FileSharePreparer()
    @recorded_by_proxy_async
    async def test_rename_file_with_lease(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)

        source_file = await self._create_file(storage_account_name, storage_account_key, 'file1')
        dest_file = await self._create_file(storage_account_name, storage_account_key, 'file2')
        source_lease = await source_file.acquire_lease(lease_id='00000000-1111-2222-3333-444444444444')
        dest_lease = await dest_file.acquire_lease(lease_id='00000000-1111-2222-3333-444444444444')

        # Act
        new_file = await source_file.rename_file(
            dest_file.file_name,
            overwrite=True,
            source_lease=source_lease,
            destination_lease=dest_lease)

        # Assert
        assert 'file2' == new_file.file_name
        props = await new_file.get_file_properties()
        assert props is not None

    @pytest.mark.live_test_only
    @FileSharePreparer()
    async def test_rename_file_share_sas(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        await self._setup_share(storage_account_name, storage_account_key)
        share_client = self.fsc.get_share_client(self.share_name)

        token = self.generate_sas(
            generate_share_sas,
            share_client.account_name,
            share_client.share_name,
            share_client.credential.account_key,
            expiry=datetime.utcnow() + timedelta(hours=1),
            permission=ShareSasPermissions(read=True, write=True))

        source_file = ShareFileClient(
            self.account_url(storage_account_name, 'file'),
            share_client.share_name, 'file1',
            credential=token)
        await source_file.create_file(1024)

        # Act
        new_file = await source_file.rename_file('file2' + '?' + token)

        # Assert
        assert 'file2' == new_file.file_name
        props = await new_file.get_file_properties()
        assert props is not None
