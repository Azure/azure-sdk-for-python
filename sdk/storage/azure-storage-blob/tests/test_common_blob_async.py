# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import asyncio
import os
import tempfile
import uuid
from datetime import datetime, timedelta
from enum import Enum
from io import BytesIO

import aiohttp
import pytest
import requests
from azure.core import MatchConditions
from azure.core.credentials import AzureSasCredential, AzureNamedKeyCredential
from azure.core.exceptions import (
    HttpResponseError,
    ResourceNotFoundError,
    ResourceExistsError,
    ClientAuthenticationError, ResourceModifiedError)
from azure.core.pipeline.transport import AioHttpTransport
from azure.mgmt.storage.aio import StorageManagementClient
from azure.storage.blob.aio import (
    BlobClient,
    BlobServiceClient,
    ContainerClient,
    download_blob_from_url,
    upload_blob_to_url)
from azure.storage.blob import (
    AccessPolicy,
    AccountSasPermissions,
    BlobImmutabilityPolicyMode,
    BlobProperties,
    BlobSasPermissions,
    BlobType,
    ContainerSasPermissions,
    ContentSettings,
    ImmutabilityPolicy,
    RehydratePriority,
    ResourceTypes,
    RetentionPolicy,
    Services,
    StandardBlobTier,
    StorageErrorCode,
    generate_account_sas,
    generate_container_sas,
    generate_blob_sas)
from devtools_testutils.fake_credentials_async import AsyncFakeCredential
from devtools_testutils.aio import recorded_by_proxy_async
from devtools_testutils.storage.aio import AsyncStorageRecordedTestCase
from settings.testcase import BlobPreparer
from test_helpers_async import AsyncStream

# ------------------------------------------------------------------------------
TEST_CONTAINER_PREFIX = 'container'
TEST_BLOB_PREFIX = 'blob'
# ------------------------------------------------------------------------------


class TestStorageCommonBlobAsync(AsyncStorageRecordedTestCase):
    # --Helpers-----------------------------------------------------------------
    async def _setup(self, storage_account_name, key):
        self.bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=key)
        self.container_name = self.get_resource_name('utcontainer')
        self.source_container_name = self.get_resource_name('utcontainersource')
        self.byte_data = self.get_random_bytes(1024)
        if self.is_live:
            try:
                await self.bsc.create_container(self.container_name)
            except ResourceExistsError:
                pass
            try:
                await self.bsc.create_container(self.source_container_name)
            except ResourceExistsError:
                pass

    async def _create_source_blob(self, data):
        blob_client = self.bsc.get_blob_client(self.source_container_name, self.get_resource_name(TEST_BLOB_PREFIX))
        await blob_client.upload_blob(data, overwrite=True)
        return blob_client

    async def _create_blob(self, tags=None, data=b'', **kwargs):
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        await blob.upload_blob(data, tags=tags, overwrite=True, **kwargs)
        return blob

    async def _setup_remote(self, storage_account_name, key):
        self.bsc2 = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=key)
        self.remote_container_name = 'rmt'

    def _teardown(self, file_path):
        if os.path.isfile(file_path):
            try:
                os.remove(file_path)
            except:
                pass

    def _get_container_reference(self):
        return self.get_resource_name(TEST_CONTAINER_PREFIX)

    def _get_blob_reference(self):
        return self.get_resource_name(TEST_BLOB_PREFIX)

    async def _create_block_blob(self, overwrite=False, tags=None, standard_blob_tier=None):
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        await blob.upload_blob(self.byte_data, length=len(self.byte_data), overwrite=overwrite, tags=tags,
                              standard_blob_tier=standard_blob_tier)
        return blob_name

    async def _create_empty_block_blob(self, overwrite=False, tags=None):
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        await blob.upload_blob("", length=0, overwrite=overwrite, tags=tags)
        return blob_name

    async def _create_remote_container(self):
        self.remote_container_name = self.get_resource_name('remotectnr')
        remote_container = self.bsc2.get_container_client(self.remote_container_name)
        try:
            await remote_container.create_container()
        except ResourceExistsError:
            pass

    async def _create_remote_block_blob(self, blob_data=None):
        if not blob_data:
            blob_data = b'12345678' * 1024 * 1024
        source_blob_name = self._get_blob_reference()
        source_blob = self.bsc2.get_blob_client(self.remote_container_name, source_blob_name)
        await source_blob.upload_blob(blob_data, overwrite=True)
        return source_blob

    async def _wait_for_async_copy(self, blob):
        count = 0
        props = await blob.get_blob_properties()
        while props.copy.status == 'pending':
            count = count + 1
            if count > 10:
                self.fail('Timed out waiting for async copy to complete.')
            self.sleep(6)
            props = await blob.get_blob_properties()
        return props

    def _assert_blob_is_soft_deleted(self, blob):
        assert blob.deleted
        assert blob.deleted_time is not None
        assert blob.remaining_retention_days is not None

    def _assert_blob_not_soft_deleted(self, blob):
        assert not blob.deleted
        assert blob.deleted_time is None
        assert blob.remaining_retention_days is None

    # -- Common test cases for blobs ----------------------------------------------
    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_start_copy_from_url_with_oauth(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        # Create source blob
        source_blob_data = self.get_random_bytes(16 * 1024 + 5)
        source_blob_client = await self._create_source_blob(data=source_blob_data)
        # Create destination blob
        destination_blob_client = await self._create_blob()
        access_token = await self.get_credential(BlobServiceClient, is_async=True).get_token("https://storage.azure.com/.default")
        token = "Bearer {}".format(access_token.token)

        with pytest.raises(HttpResponseError):
            await destination_blob_client.start_copy_from_url(source_blob_client.url, requires_sync=True)
        with pytest.raises(ValueError):
            await destination_blob_client.start_copy_from_url(
                source_blob_client.url, source_authorization=token, requires_sync=False)

        await destination_blob_client.start_copy_from_url(
            source_blob_client.url, source_authorization=token, requires_sync=True)
        destination_blob = await destination_blob_client.download_blob()
        destination_blob_data = await destination_blob.readall()
        assert source_blob_data == destination_blob_data

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_blob_exists(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        blob_name = await self._create_block_blob()

        # Act
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        exists = await blob.get_blob_properties()

        # Assert
        assert exists

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_blob_exists_with_if_tags(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        await self._setup(storage_account_name, storage_account_key)
        tags = {"tag1 name": "my tag", "tag2": "secondtag", "tag3": "thirdtag"}

        blob_name = await self._create_block_blob(overwrite=True, tags=tags)

        # Act
        blob = self.bsc.get_blob_client(self.container_name, blob_name)

        with pytest.raises(ResourceModifiedError):
            await blob.get_blob_properties(if_tags_match_condition="\"tag1\"='first tag'")
        await blob.get_blob_properties(if_tags_match_condition="\"tag1 name\"='my tag' AND \"tag2\"='secondtag'")

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_blob_not_exists(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        blob_name = self._get_blob_reference()

        # Act
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        with pytest.raises(ResourceNotFoundError):
            await blob.get_blob_properties()

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_blob_snapshot_exists(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        blob_name = await self._create_block_blob()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        snapshot = await blob.create_snapshot()

        # Act
        blob = self.bsc.get_blob_client(self.container_name, blob_name, snapshot=snapshot)
        prop = await blob.get_blob_properties()

        # Assert
        assert prop
        assert snapshot['snapshot'] == prop.snapshot

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_upload_blob_from_generator(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        await self._setup(storage_account_name, storage_account_key)
        blob_name = self._get_blob_reference()
        # Act
        raw_data = self.get_random_bytes(3 * 1024 * 1024) + b"hello random text"

        def data_generator():
            for i in range(0, 2):
                yield raw_data

        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        await blob.upload_blob(data=data_generator())
        dl_blob = await blob.download_blob()
        data = await dl_blob.readall()

        # Assert
        assert data == raw_data*2

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_upload_blob_from_async_generator(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        await self._setup(storage_account_name, storage_account_key)
        blob_name = self._get_blob_reference()
        data = b'Hello Async World!'

        async def data_generator():
            for _ in range(3):
                yield data
                await asyncio.sleep(0.1)

        # Act
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        await blob.upload_blob(data=data_generator())

        # Assert
        result = await (await blob.download_blob()).readall()
        assert result == data*3

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_upload_blob_from_async_generator_chunks(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        await self._setup(storage_account_name, storage_account_key)
        self.bsc._config.max_single_put_size = 1024
        self.bsc._config.max_block_size = 1024

        blob_name = self._get_blob_reference()
        data = b'abc' * 1024

        async def data_generator():
            for _ in range(3):
                yield data
                await asyncio.sleep(0.1)

        # Act
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        await blob.upload_blob(data=data_generator())

        # Assert
        result = await (await blob.download_blob()).readall()
        assert result == data*3

    @pytest.mark.live_test_only
    @BlobPreparer()
    async def test_upload_blob_from_async_generator_chunks_parallel(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        await self._setup(storage_account_name, storage_account_key)
        self.bsc._config.max_single_put_size = 1024
        self.bsc._config.max_block_size = 1024

        blob_name = self._get_blob_reference()
        data = b'abcde' * 1024

        async def data_generator():
            for _ in range(3):
                yield data
                await asyncio.sleep(0.1)

        # Act
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        await blob.upload_blob(data=data_generator(), max_concurrency=3, overwrite=True)

        # Assert
        result = await (await blob.download_blob()).readall()
        assert result == data * 3

    @pytest.mark.live_test_only
    @BlobPreparer()
    async def test_upload_blob_from_pipe(self, **kwargs):
        # Different OSs have different behavior, so this can't be recorded.
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        await self._setup(storage_account_name, storage_account_key)
        blob_name = self._get_blob_reference()
        data = b"Hello World"

        reader_fd, writer_fd = os.pipe()

        with os.fdopen(writer_fd, 'wb') as writer:
            writer.write(data)

        # Act
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        with os.fdopen(reader_fd, mode='rb') as reader:
            await blob.upload_blob(data=reader, overwrite=True)

        blob_data = await (await blob.download_blob()).readall()

        # Assert
        assert data == blob_data

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_upload_blob_from_async_stream_single_chunk(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        await self._setup(storage_account_name, storage_account_key)
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)

        data = b"Hello Async World!"
        stream = AsyncStream(data)

        # Act
        await blob.upload_blob(stream, overwrite=True)
        blob_data = await (await blob.download_blob()).readall()

        # Assert
        assert data == blob_data

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_upload_blob_from_async_stream_chunks(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        await self._setup(storage_account_name, storage_account_key)
        self.bsc._config.max_single_put_size = 1024
        self.bsc._config.max_block_size = 1024

        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)

        data = b"12345" * 1024
        stream = AsyncStream(data)

        # Act
        await blob.upload_blob(stream, overwrite=True)
        blob_data = await (await blob.download_blob()).readall()

        # Assert
        assert data == blob_data

    @pytest.mark.live_test_only
    @BlobPreparer()
    async def test_upload_blob_from_async_stream_chunks_parallel(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        await self._setup(storage_account_name, storage_account_key)
        self.bsc._config.max_single_put_size = 1024
        self.bsc._config.max_block_size = 1024

        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)

        data = b"12345" * 1024
        stream = AsyncStream(data)

        # Act
        await blob.upload_blob(stream, overwrite=True, max_concurrency=3)
        blob_data = await (await blob.download_blob()).readall()

        # Assert
        assert data == blob_data

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_blob_snapshot_not_exists(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        blob_name = await self._create_block_blob()

        # Act
        blob = self.bsc.get_blob_client(self.container_name, blob_name, snapshot="1988-08-18T07:52:31.6690068Z")
        with pytest.raises(ResourceNotFoundError):
            await blob.get_blob_properties()

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_blob_container_not_exists(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # In this case both the blob and container do not exist
        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        blob_name = self._get_blob_reference()

        # Act
        blob = self.bsc.get_blob_client(self._get_container_reference(), blob_name)
        with pytest.raises(ResourceNotFoundError):
            await blob.get_blob_properties()

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_create_blob_with_question_mark(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        blob_name = '?ques?tion?'
        blob_data = '???'

        # Act
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        await blob.upload_blob(blob_data)

        # Assert
        stream = await blob.download_blob(encoding='utf-8')
        data = await stream.readall()
        assert data is not None
        assert data == blob_data

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_create_blob_with_equal_sign(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        blob_name = '=ques=tion!'
        blob_data = '???'

        # Act
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        await blob.upload_blob(blob_data)

        # Assert
        stream = await blob.download_blob(encoding='utf-8')
        data = await stream.readall()
        assert data is not None
        assert data == blob_data

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_create_blob_with_special_chars(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        # Act
        for c in '-._ /()$=\',~':
            blob_name = '{0}a{0}a{0}'.format(c)
            blob_data = c
            blob = self.bsc.get_blob_client(self.container_name, blob_name)
            await blob.upload_blob(blob_data, length=len(blob_data))

            data = await (await blob.download_blob()).readall()
            content = data.decode('utf-8')
            assert content == blob_data

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_create_blob_and_download_blob_with_vid(self, **kwargs):
        versioned_storage_account_name = kwargs.pop("versioned_storage_account_name")
        versioned_storage_account_key = kwargs.pop("versioned_storage_account_key")

        # Arrange
        await self._setup(versioned_storage_account_name, versioned_storage_account_key)
        # Act
        for c in '-._ /()$=\',~':
            blob_name = '{0}a{0}a{0}'.format(c)
            blob_data = c
            blob = self.bsc.get_blob_client(self.container_name, blob_name)
            resp = await blob.upload_blob(blob_data, length=len(blob_data), overwrite=True)
            assert resp.get('version_id') is not None

            data = await (await blob.download_blob(version_id=resp.get('version_id'))).readall()
            content = data.decode('utf-8')
            assert content == blob_data

        # Assert

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_create_blob_with_lease_id(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        blob_name = await self._create_block_blob()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        lease = await blob.acquire_lease(lease_id='00000000-1111-2222-3333-444444444444')

        # Act
        data = b'hello world again'
        resp = await blob.upload_blob(data, length=len(data), lease=lease)

        # Assert
        assert resp.get('etag') is not None
        stream = await blob.download_blob(lease=lease)
        content = await stream.readall()
        assert content == data

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_create_blob_with_metadata(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        blob_name = self._get_blob_reference()
        metadata = {'hello': 'world', 'number': '42'}

        # Act
        data = b'hello world'
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        resp = await blob.upload_blob(data, length=len(data), metadata=metadata)

        # Assert
        assert resp.get('etag') is not None
        md = (await blob.get_blob_properties()).metadata
        assert md == metadata

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_upload_blob_with_dictionary(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        await self._setup(storage_account_name, storage_account_key)
        blob_name = 'test_blob'
        blob_data = {'hello': 'world'}

        # Act
        blob = self.bsc.get_blob_client(self.container_name, blob_name)

        # Assert
        with pytest.raises(TypeError):
            await blob.upload_blob(blob_data)

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_create_blob_with_generator(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        await self._setup(storage_account_name, storage_account_key)

        # Act
        def gen():
            yield "hello"
            yield "world!"
            yield " eom"
        blob = self.bsc.get_blob_client(self.container_name, "gen_blob")
        resp = await blob.upload_blob(data=gen())

        # Assert
        assert resp.get('etag') is not None
        content = await (await blob.download_blob()).readall()
        assert content == b"helloworld! eom"

    @pytest.mark.live_test_only
    @BlobPreparer()
    async def test_create_blob_with_requests(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        await self._setup(storage_account_name, storage_account_key)
        # Act
        uri = "https://en.wikipedia.org/wiki/Microsoft"
        data = requests.get(uri, stream=True)
        blob = self.bsc.get_blob_client(self.container_name, "msft")
        resp = await blob.upload_blob(data=data.raw, overwrite=True)

        assert resp.get('etag') is not None

    @pytest.mark.live_test_only
    @BlobPreparer()
    async def test_create_blob_with_aiohttp(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        await self._setup(storage_account_name, storage_account_key)

        # Create a blob to download with aiohttp using SAS
        data = b'a' * 1024 * 1024
        blob = await self._create_blob(data=data)

        sas = self.generate_sas(
            generate_blob_sas,
            blob.account_name,
            blob.container_name,
            blob.blob_name,
            account_key=storage_account_key,
            permission=BlobSasPermissions(read=True),
            expiry=datetime.utcnow() + timedelta(hours=1),
        )

        # Act
        uri = blob.url + '?' + sas
        async with aiohttp.ClientSession() as session:
            async with session.get(uri) as data:
                async for text, _ in data.content.iter_chunks():
                    blob2 = self.bsc.get_blob_client(self.container_name, blob.blob_name + '_copy')
                    resp = await blob2.upload_blob(data=text, overwrite=True)
                    assert resp.get('etag') is not None

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_get_blob_with_existing_blob(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        blob_name = await self._create_block_blob()

        # Act
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        stream = await blob.download_blob()
        content = await stream.readall()

        # Assert
        assert content == self.byte_data

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_get_blob_with_snapshot(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        blob_name = await self._create_block_blob()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        snap = await blob.create_snapshot()
        snapshot = self.bsc.get_blob_client(
            self.container_name, blob_name, snapshot=snap)

        # Act
        stream = await snapshot.download_blob()
        content = await stream.readall()

        # Assert
        assert content == self.byte_data

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_get_blob_with_snapshot_previous(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        blob_name = await self._create_block_blob()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        snap = await blob.create_snapshot()
        snapshot = self.bsc.get_blob_client(
            self.container_name, blob_name, snapshot=snap)

        upload_data = b'hello world again'
        await blob.upload_blob(upload_data, length=len(upload_data), overwrite=True)

        # Act
        blob_previous = await snapshot.download_blob()
        blob_previous_bytes = await blob_previous.readall()
        blob_latest = await blob.download_blob()
        blob_latest_bytes = await blob_latest.readall()

        # Assert
        assert blob_previous_bytes == self.byte_data
        assert blob_latest_bytes == b'hello world again'

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_get_blob_with_range(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        blob_name = await self._create_block_blob()

        # Act
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        stream = await blob.download_blob(offset=0, length=5)
        content = await stream.readall()

        # Assert
        assert content == self.byte_data[:5]

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_get_blob_with_lease(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        blob_name = await self._create_block_blob()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        lease = await blob.acquire_lease(lease_id='00000000-1111-2222-3333-444444444444')

        # Act
        stream = await blob.download_blob(lease=lease)
        content = await stream.readall()
        await lease.release()

        # Assert
        assert content == self.byte_data

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_get_blob_with_non_existing_blob(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        blob_name = self._get_blob_reference()

        # Act
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        with pytest.raises(ResourceNotFoundError):
            await blob.download_blob()

        # Assert

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_set_blob_properties_with_existing_blob(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        blob_name = await self._create_block_blob()

        # Act
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        await blob.set_http_headers(
            content_settings=ContentSettings(
                content_language='spanish',
                content_disposition='inline'),
        )

        # Assert
        props = await blob.get_blob_properties()
        assert props.content_settings.content_language == 'spanish'
        assert props.content_settings.content_disposition == 'inline'

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_set_blob_properties_with_if_tags(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        await self._setup(storage_account_name, storage_account_key)
        tags = {"tag1 name": "my tag", "tag2": "secondtag", "tag3": "thirdtag"}
        blob_name = await self._create_block_blob(tags=tags, overwrite=True)

        # Act
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        with pytest.raises(ResourceModifiedError):
            await blob.set_http_headers(content_settings=ContentSettings(
                content_language='spanish',
                content_disposition='inline'),
                if_tags_match_condition="\"tag1\"='first tag'")
        await blob.set_http_headers(
            content_settings=ContentSettings(
                content_language='spanish',
                content_disposition='inline'),
            if_tags_match_condition="\"tag1 name\"='my tag' AND \"tag2\"='secondtag'"
        )

        # Assert
        props = await blob.get_blob_properties()
        assert props.content_settings.content_language == 'spanish'
        assert props.content_settings.content_disposition == 'inline'

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_set_blob_properties_with_blob_settings_param(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        blob_name = await self._create_block_blob()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        props = await blob.get_blob_properties()

        # Act
        props.content_settings.content_language = 'spanish'
        props.content_settings.content_disposition = 'inline'
        await blob.set_http_headers(content_settings=props.content_settings)

        # Assert
        props = await blob.get_blob_properties()
        assert props.content_settings.content_language == 'spanish'
        assert props.content_settings.content_disposition == 'inline'

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_get_blob_properties(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        blob_name = await self._create_block_blob()

        # Act
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        props = await blob.get_blob_properties()

        # Assert
        assert isinstance(props, BlobProperties)
        assert props.blob_type == BlobType.BlockBlob
        assert props.size == len(self.byte_data)
        assert props.lease.status == 'unlocked'
        assert props.creation_time is not None

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_get_blob_properties_returns_rehydrate_priority(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        blob_name = await self._create_block_blob(standard_blob_tier=StandardBlobTier.Archive)

        # Act
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        await blob.set_standard_blob_tier(StandardBlobTier.Hot, rehydrate_priority=RehydratePriority.high)
        props = await blob.get_blob_properties()

        # Assert
        assert isinstance(props, BlobProperties)
        assert props.blob_type == BlobType.BlockBlob
        assert props.size == len(self.byte_data)
        assert props.rehydrate_priority == 'High'

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_get_blob_properties_fail(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        blob_name = await self._create_block_blob()

        # Act
        blob = self.bsc.get_blob_client(self.container_name, blob_name, snapshot=1)

        with pytest.raises(HttpResponseError) as e:
            await blob.get_blob_properties()  # Invalid snapshot value of 1

        # Assert
        # TODO: No error code returned
        # assert StorageErrorCode.invalid_query_parameter_value == e.exception.error_code

    # This test is to validate that the ErrorCode is retrieved from the header during a
    # GET request. This is preferred to relying on the ErrorCode in the body.
    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_get_blob_metadata_fail(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        blob_name = await self._create_block_blob()

        # Act
        blob = self.bsc.get_blob_client(self.container_name, blob_name, snapshot=1)
        with pytest.raises(HttpResponseError) as e:
            (await blob.get_blob_properties()).metadata  # Invalid snapshot value of 1

        # Assert
        # TODO: No error code returned
        # assert StorageErrorCode.invalid_query_parameter_value == e.exception.error_code

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_get_blob_server_encryption(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        blob_name = await self._create_block_blob()

        # Act
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        data = await blob.download_blob()

        # Assert
        assert data.properties.server_encrypted

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_get_blob_properties_server_encryption(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        blob_name = await self._create_block_blob()

        # Act
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        props = await blob.get_blob_properties()

        # Assert
        assert props.server_encrypted

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_list_blobs_server_encryption(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        await self._create_block_blob()
        container = self.bsc.get_container_client(self.container_name)
        blob_list = []
        async for b in container.list_blobs():
            blob_list.append(b)

        # Act

        # Assert
        for blob in blob_list:
            assert blob.server_encrypted

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_no_server_encryption(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        self.bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=storage_account_key)
        self.container_name = self.get_resource_name('utcontainer')
        self.source_container_name = self.get_resource_name('utcontainersource')
        self.byte_data = self.get_random_bytes(1024)
        await self.bsc.create_container(self.container_name)
        blob_name = await self._create_block_blob()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)

        # Act
        def callback(response):
            response.http_response.headers['x-ms-server-encrypted'] = 'false'

        props = await blob.get_blob_properties(raw_response_hook=callback)

        # Assert
        assert not props.server_encrypted

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_get_blob_properties_with_snapshot(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        blob_name = await self._create_block_blob()
        container = self.bsc.get_container_client(self.container_name)
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        res = await blob.create_snapshot()
        blobs = []
        async for b in container.list_blobs(include='snapshots'):
            blobs.append(b)

        assert len(blobs) == 2

        # Act
        snapshot = self.bsc.get_blob_client(self.container_name, blob_name, snapshot=res)
        props = await snapshot.get_blob_properties()

        # Assert
        assert blob is not None
        assert props.blob_type == BlobType.BlockBlob
        assert props.size == len(self.byte_data)

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_get_blob_properties_with_leased_blob(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        blob_name = await self._create_block_blob()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        lease = await blob.acquire_lease(lease_id='00000000-1111-2222-3333-444444444444')

        # Act
        props = await blob.get_blob_properties()

        # Assert
        assert isinstance(props, BlobProperties)
        assert props.blob_type == BlobType.BlockBlob
        assert props.size == len(self.byte_data)
        assert props.lease.status == 'locked'
        assert props.lease.state == 'leased'
        assert props.lease.duration == 'infinite'

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_get_blob_metadata(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        blob_name = await self._create_block_blob()

        # Act
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        md = (await blob.get_blob_properties()).metadata

        # Assert
        assert md is not None

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_set_blob_metadata_with_upper_case(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        metadata = {'hello': ' world ', ' number ': '42', 'UP': 'UPval'}
        blob_name = await self._create_block_blob()

        # Act
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        await blob.set_blob_metadata(metadata)

        # Assert
        md = (await blob.get_blob_properties()).metadata
        assert 3 == len(md)
        assert md['hello'] == 'world'
        assert md['number'] == '42'
        assert md['UP'] == 'UPval'
        assert not 'up' in md

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_set_blob_metadata_with_if_tags(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        tags = {"tag1 name": "my tag", "tag2": "secondtag", "tag3": "thirdtag"}
        metadata = {'hello': ' world ', ' number ': '42', 'UP': 'UPval'}
        blob_name = await self._create_block_blob(tags=tags, overwrite=True)

        # Act
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        with pytest.raises(ResourceModifiedError):
            await blob.set_blob_metadata(metadata, if_tags_match_condition="\"tag1\"='first tag'")
        await blob.set_blob_metadata(metadata, if_tags_match_condition="\"tag1 name\"='my tag' AND \"tag2\"='secondtag'")

        # Assert
        md = (await blob.get_blob_properties()).metadata
        assert 3 == len(md)
        assert md['hello'] == 'world'
        assert md['number'] == '42'
        assert md['UP'] == 'UPval'
        assert not 'up' in md

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_set_blob_metadata_returns_vid(self, **kwargs):
        versioned_storage_account_name = kwargs.pop("versioned_storage_account_name")
        versioned_storage_account_key = kwargs.pop("versioned_storage_account_key")

        # Arrange
        await self._setup(versioned_storage_account_name, versioned_storage_account_key)
        metadata = {'hello': 'world', 'number': '42', 'UP': 'UPval'}
        blob_name = await self._create_block_blob()

        # Act
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        resp = await blob.set_blob_metadata(metadata)

        # Assert
        assert resp['version_id'] is not None
        md = (await blob.get_blob_properties()).metadata
        assert 3 == len(md)
        assert md['hello'] == 'world'
        assert md['number'] == '42'
        assert md['UP'] == 'UPval'
        assert not 'up' in md

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_delete_blob_with_existing_blob(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        blob_name = await self._create_block_blob()

        # Act
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        resp = await blob.delete_blob()

        # Assert
        assert resp is None

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_delete_blob_with_if_tags(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        await self._setup(storage_account_name, storage_account_key)
        tags = {"tag1 name": "my tag", "tag2": "secondtag", "tag3": "thirdtag"}

        blob_name = await self._create_block_blob(tags=tags, overwrite=True)

        # Act
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        prop = await blob.get_blob_properties()

        with pytest.raises(ResourceModifiedError):
            await blob.delete_blob(if_tags_match_condition="\"tag1\"='first tag'")
        resp = await blob.delete_blob(etag=prop.etag, match_condition=MatchConditions.IfNotModified, if_tags_match_condition="\"tag1 name\"='my tag' AND \"tag2\"='secondtag'")

        # Assert
        assert resp is None

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_delete_specific_blob_version(self, **kwargs):
        versioned_storage_account_name = kwargs.pop("versioned_storage_account_name")
        versioned_storage_account_key = kwargs.pop("versioned_storage_account_key")

        # Arrange
        await self._setup(versioned_storage_account_name, versioned_storage_account_key)
        blob_name = self.get_resource_name("blobtodelete")

        # Act
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        resp = await blob.upload_blob(b'abc', overwrite=True)

        # Assert
        assert resp['version_id'] is not None

        # upload to override the previous version
        await blob.upload_blob(b'abc', overwrite=True)

        # Act
        resp = await blob.delete_blob(version_id=resp['version_id'])
        blob_list = []
        async for blob in self.bsc.get_container_client(self.container_name).list_blobs(include="versions"):
            blob_list.append(blob)
        # Assert
        assert resp is None
        assert len(blob_list) > 0

    @pytest.mark.live_test_only
    @BlobPreparer()
    async def test_delete_blob_version_with_blob_sas(self, **kwargs):
        versioned_storage_account_name = kwargs.pop("versioned_storage_account_name")
        versioned_storage_account_key = kwargs.pop("versioned_storage_account_key")

        await self._setup(versioned_storage_account_name, versioned_storage_account_key)
        blob_name = await self._create_block_blob()
        blob_client = self.bsc.get_blob_client(self.container_name, blob_name)
        resp = await blob_client.upload_blob(b'abcde', overwrite=True)

        version_id = resp['version_id']
        assert version_id is not None
        await blob_client.upload_blob(b'abc', overwrite=True)

        token = self.generate_sas(
            generate_blob_sas,
            blob_client.account_name,
            blob_client.container_name,
            blob_client.blob_name,
            version_id=version_id,
            account_key=versioned_storage_account_key,
            permission=BlobSasPermissions(delete=True, delete_previous_version=True),
            expiry=datetime.utcnow() + timedelta(hours=1),
        )

        # Act
        blob_client_using_sas = BlobClient.from_blob_url(blob_client.url, credential=token)
        resp = await blob_client_using_sas.delete_blob(version_id=version_id)

        # Assert
        assert resp is None
        async for blob in self.bsc.get_container_client(self.container_name).list_blobs(include="versions"):
            assert blob.version_id != version_id

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_delete_blob_with_non_existing_blob(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        blob_name = self._get_blob_reference()

        # Act
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        with pytest.raises(ResourceNotFoundError):
            await blob.delete_blob()

        # Assert

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_delete_blob_snapshot(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        blob_name = await self._create_block_blob()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        snap = await blob.create_snapshot()
        snapshot = self.bsc.get_blob_client(
            self.container_name, blob_name, snapshot=snap)

        # Act
        await snapshot.delete_blob()

        # Assert
        container = self.bsc.get_container_client(self.container_name)
        blobs = []
        async for b in container.list_blobs(include='snapshots'):
            blobs.append(b)
        assert len(blobs) == 1
        assert blobs[0].name == blob_name
        assert blobs[0].snapshot is None

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_delete_blob_snapshots(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        blob_name = await self._create_block_blob()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        await blob.create_snapshot()

        # Act
        await blob.delete_blob(delete_snapshots='only')

        # Assert
        container = self.bsc.get_container_client(self.container_name)
        blobs = []
        async for b in container.list_blobs(include='snapshots'):
            blobs.append(b)
        assert len(blobs) == 1
        assert blobs[0].snapshot is None

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_create_blob_snapshot_returns_vid(self, **kwargs):
        versioned_storage_account_name = kwargs.pop("versioned_storage_account_name")
        versioned_storage_account_key = kwargs.pop("versioned_storage_account_key")

        # Arrange
        await self._setup(versioned_storage_account_name, versioned_storage_account_key)
        container = self.bsc.get_container_client(self.container_name)

        blob_name = await self._create_block_blob()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        resp = await blob.create_snapshot()
        blobs = []
        async for b in container.list_blobs(include='snapshots'):
            blobs.append(b)

        # Assert
        assert resp['version_id'] is not None
        # Both create blob and create snapshot will create a new version
        assert len(blobs) >= 2

        # Act
        await blob.delete_blob(delete_snapshots='only')

        # Assert
        blobs = []
        async for b in container.list_blobs(include=['snapshots', 'versions']):
            blobs.append(b)
        assert len(blobs) > 0
        assert blobs[0].snapshot is None

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_delete_blob_with_snapshots(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        blob_name = await self._create_block_blob()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        await blob.create_snapshot()

        # Act
        # with pytest.raises(HttpResponseError):
        #    blob.delete_blob()

        await blob.delete_blob(delete_snapshots='include')

        # Assert
        container = self.bsc.get_container_client(self.container_name)
        blobs = []
        async for b in container.list_blobs(include='snapshots'):
            blobs.append(b)
        assert len(blobs) == 0

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_soft_delete_blob_without_snapshots(self, **kwargs):
        storage_account_name = kwargs.pop("soft_delete_storage_account_name")
        storage_account_key = kwargs.pop("soft_delete_storage_account_key")

        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        blob_name = await self._create_block_blob()

        container = self.bsc.get_container_client(self.container_name)
        blob = container.get_blob_client(blob_name)

        # Soft delete the blob
        await blob.delete_blob()
        blob_list = []
        async for b in container.list_blobs(include='deleted'):
            blob_list.append(b)

        # Assert
        assert len(blob_list) == 1
        self._assert_blob_is_soft_deleted(blob_list[0])


        # list_blobs should not list soft deleted blobs if Include(deleted=True) is not specified
        blob_list = []
        async for b in container.list_blobs():
            blob_list.append(b)

        # Assert
        assert len(blob_list) == 0

        # Restore blob with undelete
        await blob.undelete_blob()
        blob_list = []
        async for b in container.list_blobs(include='deleted'):
            blob_list.append(b)

        # Assert
        assert len(blob_list) == 1
        self._assert_blob_not_soft_deleted(blob_list[0])

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_soft_delete_single_blob_snapshot(self, **kwargs):
        storage_account_name = kwargs.pop("soft_delete_storage_account_name")
        storage_account_key = kwargs.pop("soft_delete_storage_account_key")

        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        blob_name = await self._create_block_blob()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        blob_snapshot_1 = await blob.create_snapshot()
        blob_snapshot_2 = await blob.create_snapshot()

        # Soft delete blob_snapshot_1
        snapshot_1 = self.bsc.get_blob_client(
            self.container_name, blob_name, snapshot=blob_snapshot_1)
        await snapshot_1.delete_blob()

        with pytest.raises(ValueError):
            await snapshot_1.delete_blob(delete_snapshots='only')

        container = self.bsc.get_container_client(self.container_name)
        blob_list = []
        async for b in container.list_blobs(include=["snapshots", "deleted"]):
            blob_list.append(b)

        # Assert
        assert len(blob_list) == 3
        for listedblob in blob_list:
            if listedblob.snapshot == blob_snapshot_1['snapshot']:
                self._assert_blob_is_soft_deleted(listedblob)
            else:
                self._assert_blob_not_soft_deleted(listedblob)

        # list_blobs should not list soft deleted blob snapshots if Include(deleted=True) is not specified
        blob_list = []
        async for b in container.list_blobs(include='snapshots'):
            blob_list.append(b)

        # Assert
        assert len(blob_list) == 2

        # Restore snapshot with undelete
        await blob.undelete_blob()
        blob_list = []
        async for b in container.list_blobs(include=["snapshots", "deleted"]):
            blob_list.append(b)

        # Assert
        assert len(blob_list) == 3
        for blob in blob_list:
            self._assert_blob_not_soft_deleted(blob)

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_soft_delete_only_snapshots_of_blob(self, **kwargs):
        storage_account_name = kwargs.pop("soft_delete_storage_account_name")
        storage_account_key = kwargs.pop("soft_delete_storage_account_key")

        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        blob_name = await self._create_block_blob()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        blob_snapshot_1 = await blob.create_snapshot()
        blob_snapshot_2 = await blob.create_snapshot()

        # Soft delete all snapshots
        await blob.delete_blob(delete_snapshots='only')
        container = self.bsc.get_container_client(self.container_name)
        blob_list = []
        async for b in container.list_blobs(include=["snapshots", "deleted"]):
            blob_list.append(b)

        # Assert
        assert len(blob_list) == 3
        for listedblob in blob_list:
            if listedblob.snapshot == blob_snapshot_1['snapshot']:
                self._assert_blob_is_soft_deleted(listedblob)
            elif listedblob.snapshot == blob_snapshot_2['snapshot']:
                self._assert_blob_is_soft_deleted(listedblob)
            else:
                self._assert_blob_not_soft_deleted(listedblob)

        # list_blobs should not list soft deleted blob snapshots if Include(deleted=True) is not specified
        blob_list = []
        async for b in container.list_blobs(include="snapshots"):
            blob_list.append(b)

        # Assert
        assert len(blob_list) == 1

        # Restore snapshots with undelete
        await blob.undelete_blob()
        blob_list = []
        async for b in container.list_blobs(include=["snapshots", "deleted"]):
            blob_list.append(b)

        # Assert
        assert len(blob_list) == 3
        for blob in blob_list:
            self._assert_blob_not_soft_deleted(blob)

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_soft_delete_blob_including_all_snapshots(self, **kwargs):
        storage_account_name = kwargs.pop("soft_delete_storage_account_name")
        storage_account_key = kwargs.pop("soft_delete_storage_account_key")

        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        blob_name = await self._create_block_blob()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        blob_snapshot_1 = await blob.create_snapshot()
        blob_snapshot_2 = await blob.create_snapshot()

        # Soft delete blob and all snapshots
        await blob.delete_blob(delete_snapshots='include')
        container = self.bsc.get_container_client(self.container_name)
        blob_list = []
        async for b in container.list_blobs(include=["snapshots", "deleted"]):
            blob_list.append(b)

        # Assert
        assert len(blob_list) == 3
        for listedblob in blob_list:
            self._assert_blob_is_soft_deleted(listedblob)

        # list_blobs should not list soft deleted blob snapshots if Include(deleted=True) is not specified
        blob_list = []
        async for b in container.list_blobs(include=["snapshots"]):
            blob_list.append(b)

        # Assert
        assert len(blob_list) == 0

        # Restore blob and snapshots with undelete
        await blob.undelete_blob()
        blob_list = []
        async for b in container.list_blobs(include=["snapshots", "deleted"]):
            blob_list.append(b)

        # Assert
        assert len(blob_list) == 3
        for blob in blob_list:
            self._assert_blob_not_soft_deleted(blob)

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_soft_delete_with_leased_blob(self, **kwargs):
        storage_account_name = kwargs.pop("soft_delete_storage_account_name")
        storage_account_key = kwargs.pop("soft_delete_storage_account_key")

        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        blob_name = await self._create_block_blob()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        lease = await blob.acquire_lease(lease_id='00000000-1111-2222-3333-444444444444')

        # Soft delete the blob without lease_id should fail
        with pytest.raises(HttpResponseError):
            await blob.delete_blob()

        # Soft delete the blob
        await blob.delete_blob(lease=lease)
        container = self.bsc.get_container_client(self.container_name)
        blob_list = []
        async for b in container.list_blobs(include="deleted"):
            blob_list.append(b)

        # Assert
        assert len(blob_list) == 1
        self._assert_blob_is_soft_deleted(blob_list[0])

        # list_blobs should not list soft deleted blobs if Include(deleted=True) is not specified
        blob_list = []
        async for b in container.list_blobs():
            blob_list.append(b)

        # Assert
        assert len(blob_list) == 0

        # Restore blob with undelete, this also gets rid of the lease
        await blob.undelete_blob()
        blob_list = []
        async for b in container.list_blobs(include="deleted"):
            blob_list.append(b)

        # Assert
        assert len(blob_list) == 1
        self._assert_blob_not_soft_deleted(blob_list[0])

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_async_copy_blob_with_if_tags(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        await self._setup(storage_account_name, storage_account_key)
        source_tags = {"source": "source tag"}
        blob_name = await self._create_block_blob(overwrite=True, tags=source_tags)
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        tags1 = {"tag1 name": "my tag", "tag2": "secondtag", "tag3": "thirdtag"}

        # Act
        sourceblob = '{0}/{1}/{2}'.format(
            self.account_url(storage_account_name, "blob"), self.container_name, blob_name)

        copyblob = self.bsc.get_blob_client(self.container_name, 'blob1copy')
        await copyblob.upload_blob("abc", overwrite=True)
        await copyblob.set_blob_tags(tags=tags1)

        tags = {"tag1": "first tag", "tag2": "secondtag", "tag3": "thirdtag"}
        with pytest.raises(ResourceModifiedError):
            await copyblob.set_blob_tags(tags, if_tags_match_condition="\"tag1\"='first tag'")
        await copyblob.set_blob_tags(tags, if_tags_match_condition="\"tag1 name\"='my tag' AND \"tag2\"='secondtag'")

        with pytest.raises(ResourceModifiedError):
            await copyblob.get_blob_tags(if_tags_match_condition="\"tag1\"='first taga'")
        dest_tags = await copyblob.get_blob_tags(if_tags_match_condition="\"tag1\"='first tag'")

        assert len(dest_tags) == len(tags)

        with pytest.raises(ResourceModifiedError):
            await copyblob.start_copy_from_url(sourceblob, tags=tags, source_if_tags_match_condition="\"source\"='sourcetag'")
        await copyblob.start_copy_from_url(sourceblob, tags=tags, source_if_tags_match_condition="\"source\"='source tag'")

        with pytest.raises(ResourceModifiedError):
            await copyblob.start_copy_from_url(sourceblob, tags={"tag1": "abc"}, if_tags_match_condition="\"tag1\"='abc'")
        copy = await copyblob.start_copy_from_url(sourceblob, tags={"tag1": "abc"}, if_tags_match_condition="\"tag1\"='first tag'")

        # Assert
        assert copy is not None
        assert copy['copy_status'] == 'success'
        assert not isinstance(copy['copy_status'], Enum)
        assert copy['copy_id'] is not None

        with pytest.raises(ResourceModifiedError):
            await (await copyblob.download_blob(if_tags_match_condition="\"tag1\"='abc1'")).readall()
        copy_content = await (await copyblob.download_blob(if_tags_match_condition="\"tag1\"='abc'")).readall()
        assert copy_content == self.byte_data

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_copy_blob_returns_vid(self, **kwargs):
        versioned_storage_account_name = kwargs.pop("versioned_storage_account_name")
        versioned_storage_account_key = kwargs.pop("versioned_storage_account_key")

        # Arrange
        await self._setup(versioned_storage_account_name, versioned_storage_account_key)
        blob_name = await self._create_block_blob()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)

        # Act
        sourceblob = '{0}/{1}/{2}'.format(
            self.account_url(versioned_storage_account_name, "blob"), self.container_name, blob_name)

        copyblob = self.bsc.get_blob_client(self.container_name, 'blob1copy')
        copy = await copyblob.start_copy_from_url(sourceblob)

        # Assert
        assert copy is not None
        assert copy['version_id'] is not None
        assert copy['copy_status'] == 'success'
        assert not isinstance(copy['copy_status'], Enum)
        assert copy['copy_id'] is not None

        copy_content = await (await copyblob.download_blob()).readall()
        assert copy_content == self.byte_data

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_copy_blob_with_existing_blob(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        blob_name = await self._create_block_blob()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)

        # Act
        sourceblob = '{0}/{1}/{2}'.format(
            self.account_url(storage_account_name, "blob"), self.container_name, blob_name)

        copyblob = self.bsc.get_blob_client(self.container_name, 'blob1copy')
        copy = await copyblob.start_copy_from_url(sourceblob)

        # Assert
        assert copy is not None
        assert copy['copy_status'] == 'success'
        assert not isinstance(copy['copy_status'], Enum)
        assert copy['copy_id'] is not None

        copy_content = await (await copyblob.download_blob()).readall()
        assert copy_content == self.byte_data

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_copy_blob_with_immutability_policy(self, **kwargs):
        versioned_storage_account_name = kwargs.pop("versioned_storage_account_name")
        versioned_storage_account_key = kwargs.pop("versioned_storage_account_key")
        storage_resource_group_name = kwargs.pop("storage_resource_group_name")
        variables = kwargs.pop("variables", {})

        await self._setup(versioned_storage_account_name, versioned_storage_account_key)

        container_name = self.get_resource_name('vlwcontainer')
        if self.is_live:
            token_credential = self.get_credential(BlobServiceClient, is_async=True)
            subscription_id = self.get_settings_value("SUBSCRIPTION_ID")
            mgmt_client = StorageManagementClient(token_credential, subscription_id, '2021-04-01')
            property = mgmt_client.models().BlobContainer(
                immutable_storage_with_versioning=mgmt_client.models().ImmutableStorageWithVersioning(enabled=True))
            await mgmt_client.blob_containers.create(storage_resource_group_name, versioned_storage_account_name, container_name, blob_container=property)

        blob_name = await self._create_block_blob()
        # Act
        sourceblob = '{0}/{1}/{2}'.format(
            self.account_url(versioned_storage_account_name, "blob"), self.container_name, blob_name)

        copyblob = self.bsc.get_blob_client(container_name, 'blob1copy')
        expiry_time = self.get_datetime_variable(variables, 'expiry_time', datetime.utcnow() + timedelta(seconds=5))
        immutability_policy = ImmutabilityPolicy(expiry_time=expiry_time,
                                                 policy_mode=BlobImmutabilityPolicyMode.Unlocked)

        copy = await copyblob.start_copy_from_url(sourceblob, immutability_policy=immutability_policy,
                                                  legal_hold=True)

        download_resp = await copyblob.download_blob()
        assert await download_resp.readall() == self.byte_data

        assert download_resp.properties['has_legal_hold']
        assert download_resp.properties['immutability_policy']['expiry_time'] is not None
        assert download_resp.properties['immutability_policy']['policy_mode'] is not None
        assert copy is not None
        assert copy['copy_status'] == 'success'
        assert not isinstance(copy['copy_status'], Enum)

        if self.is_live:
            await copyblob.delete_immutability_policy()
            await copyblob.set_legal_hold(False)
            await copyblob.delete_blob()
            await mgmt_client.blob_containers.delete(storage_resource_group_name, versioned_storage_account_name, container_name)

        return variables

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_copy_blob_async_private_blob_no_sas(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")
        secondary_storage_account_name = kwargs.pop("secondary_storage_account_name")
        secondary_storage_account_key = kwargs.pop("secondary_storage_account_key")

        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        await self._setup_remote(secondary_storage_account_name, secondary_storage_account_key)
        await self._create_remote_container()
        source_blob = await self._create_remote_block_blob()

        # Act
        target_blob_name = 'targetblob'
        target_blob = self.bsc.get_blob_client(self.container_name, target_blob_name)

        # Assert
        with pytest.raises(ClientAuthenticationError):
            await target_blob.start_copy_from_url(source_blob.url)

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_copy_blob_async_private_blob_with_sas(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")
        secondary_storage_account_name = kwargs.pop("secondary_storage_account_name")
        secondary_storage_account_key = kwargs.pop("secondary_storage_account_key")

        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        data = b'12345678' * 1024 * 1024
        await self._setup_remote(secondary_storage_account_name, secondary_storage_account_key)
        await self._create_remote_container()
        source_blob = await self._create_remote_block_blob(blob_data=data)
        sas_token = self.generate_sas(
            generate_blob_sas,
            source_blob.account_name,
            source_blob.container_name,
            source_blob.blob_name,
            snapshot=source_blob.snapshot,
            account_key=source_blob.credential.account_key,
            permission=BlobSasPermissions(read=True),
            expiry=datetime.utcnow() + timedelta(hours=1),
        )
        blob = BlobClient.from_blob_url(source_blob.url, credential=sas_token)

        # Act
        target_blob_name = 'targetblob'
        target_blob = self.bsc.get_blob_client(self.container_name, target_blob_name)
        copy_resp = await target_blob.start_copy_from_url(blob.url)

        # Assert
        props = await self._wait_for_async_copy(target_blob)
        assert props.copy.status == 'success'
        actual_data = await (await target_blob.download_blob()).readall()
        assert actual_data == data

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_abort_copy_blob(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        source_blob = "https://www.gutenberg.org/files/59466/59466-0.txt"
        copied_blob = self.bsc.get_blob_client(self.container_name, '59466-0.txt')

        # Act
        copy = await copied_blob.start_copy_from_url(source_blob)
        assert copy['copy_status'] == 'pending'

        try:
            await copied_blob.abort_copy(copy)
            props = await self._wait_for_async_copy(copied_blob)
            assert props.copy.status == 'aborted'

            # Assert
            actual_data = await copied_blob.download_blob()
            bytes_data = await (await copied_blob.download_blob()).readall()
            assert bytes_data == b""
            assert actual_data.properties.copy.status == 'aborted'

        # In the Live test pipeline, the copy occasionally finishes before it can be aborted.
        # Catch and assert on error code to prevent this test from failing.
        except HttpResponseError as e:
            assert e.error_code == StorageErrorCode.NO_PENDING_COPY_OPERATION

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_abort_copy_blob_with_synchronous_copy_fails(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        source_blob_name = await self._create_block_blob()
        source_blob = self.bsc.get_blob_client(self.container_name, source_blob_name)

        # Act
        target_blob_name = 'targetblob'
        target_blob = self.bsc.get_blob_client(self.container_name, target_blob_name)
        copy_resp = await target_blob.start_copy_from_url(source_blob.url)

        with pytest.raises(HttpResponseError):
            await target_blob.abort_copy(copy_resp)

        # Assert
        assert copy_resp['copy_status'] == 'success'

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_snapshot_blob(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        blob_name = await self._create_block_blob()

        # Act
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        resp = await blob.create_snapshot()

        # Assert
        assert resp is not None
        assert resp['snapshot'] is not None

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_lease_blob_acquire_and_release(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        blob_name = await self._create_block_blob()

        # Act
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        lease = await blob.acquire_lease(lease_id='00000000-1111-2222-3333-444444444444')
        await lease.release()
        lease2 = await blob.acquire_lease(lease_id='00000000-1111-2222-3333-444444444444')

        # Assert
        assert lease is not None
        assert lease2 is not None

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_lease_blob_with_duration(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        blob_name = await self._create_block_blob()

        # Act
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        lease = await blob.acquire_lease(lease_id='00000000-1111-2222-3333-444444444444', lease_duration=15)
        resp = await blob.upload_blob(b'hello 2', length=7, lease=lease)
        self.sleep(20)

        # Assert
        with pytest.raises(HttpResponseError):
            await blob.upload_blob(b'hello 3', length=7, lease=lease)

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_lease_blob_with_proposed_lease_id(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        blob_name = await self._create_block_blob()

        # Act
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        lease_id = 'a0e6c241-96ea-45a3-a44b-6ae868bc14d0'
        lease = await blob.acquire_lease(lease_id=lease_id)

        # Assert
        assert lease.id == lease_id

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_lease_blob_change_lease_id(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        blob_name = await self._create_block_blob()

        # Act
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        lease_id = 'a0e6c241-96ea-45a3-a44b-6ae868bc14d0'
        lease = await blob.acquire_lease(lease_id='00000000-1111-2222-3333-444444444444')
        first_lease_id = lease.id
        await lease.change(lease_id)
        await lease.renew()

        # Assert
        assert first_lease_id != lease.id
        assert lease.id == lease_id

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_lease_blob_break_period(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        blob_name = await self._create_block_blob()

        # Act
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        lease = await blob.acquire_lease(lease_id='00000000-1111-2222-3333-444444444444', lease_duration=15)
        lease_time = await lease.break_lease(lease_break_period=5)

        resp = await blob.upload_blob(b'hello 2', length=7, lease=lease)
        self.sleep(5)

        with pytest.raises(HttpResponseError):
            await blob.upload_blob(b'hello 3', length=7, lease=lease)

        # Assert
        assert lease.id is not None
        assert lease_time is not None
        assert resp.get('etag') is not None

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_lease_blob_acquire_and_renew(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        blob_name = await self._create_block_blob()

        # Act
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        lease = await blob.acquire_lease(lease_id='00000000-1111-2222-3333-444444444444')
        first_id = lease.id
        await lease.renew()

        # Assert
        assert first_id == lease.id

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_lease_blob_acquire_twice_fails(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        blob_name = await self._create_block_blob()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        lease = await blob.acquire_lease(lease_id='00000000-1111-2222-3333-444444444444')

        # Act
        with pytest.raises(HttpResponseError):
            await blob.acquire_lease(lease_id='00000000-1111-2222-3333-555555555555')

        # Assert
        assert lease.id is not None

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_unicode_get_blob_unicode_name(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        blob_name = '啊齄丂狛狜'
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        await blob.upload_blob(b'hello world')

        # Act
        stream = await blob.download_blob()
        content = await stream.readall()

        # Assert
        assert content == b'hello world'

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_create_blob_blob_unicode_data(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)

        # Act
        data = u'hello world啊齄丂狛狜'
        resp = await blob.upload_blob(data)

        # Assert
        assert resp.get('etag') is not None

    @pytest.mark.live_test_only
    @BlobPreparer()
    async def test_sas_access_blob(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        blob_name = await self._create_block_blob()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)

        permission = BlobSasPermissions(read=True, write=True, delete=True, delete_previous_version=True,
                                        permanent_delete=True, list=True, add=True, create=True, update=True)
        assert 'y' in str(permission)

        token = self.generate_sas(
            generate_blob_sas,
            blob.account_name,
            blob.container_name,
            blob.blob_name,
            snapshot=blob.snapshot,
            account_key=blob.credential.account_key,
            permission=permission,
            expiry=datetime.utcnow() + timedelta(hours=1),
        )

        # Act
        service = BlobClient.from_blob_url(blob.url, credential=token)
        content = await (await service.download_blob()).readall()

        # Assert
        assert self.byte_data == content

    @pytest.mark.live_test_only
    @BlobPreparer()
    async def test_sas_signed_identifier(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")
        variables = kwargs.pop("variables", {})

        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        blob_name = await self._create_block_blob()
        container = self.bsc.get_container_client(self.container_name)
        blob = self.bsc.get_blob_client(self.container_name, blob_name)

        start = self.get_datetime_variable(variables, 'start', datetime.utcnow() - timedelta(hours=1))
        expiry = self.get_datetime_variable(variables, 'expiry', datetime.utcnow() + timedelta(hours=1))

        access_policy = AccessPolicy()
        access_policy.start = start
        access_policy.expiry = expiry
        access_policy.permission = BlobSasPermissions(read=True)
        identifiers = {'testid': access_policy}

        await container.set_container_access_policy(identifiers)

        token = self.generate_sas(
            generate_blob_sas,
            blob.account_name,
            blob.container_name,
            blob.blob_name,
            snapshot=blob.snapshot,
            account_key=blob.credential.account_key,
            policy_id='testid')

        # Act
        service = BlobClient.from_blob_url(blob.url, credential=token)
        result = await (await service.download_blob()).readall()

        # Assert
        assert self.byte_data == result

        return variables

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_account_sas(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        blob_name = await self._create_block_blob()

        account_sas_permission = AccountSasPermissions(read=True, write=True, delete=True, add=True,
                                                       permanent_delete=True, list=True)
        assert 'y' in str(account_sas_permission)

        token = self.generate_sas(
            generate_account_sas,
            self.bsc.account_name,
            self.bsc.credential.account_key,
            ResourceTypes(container=True, object=True),
            account_sas_permission,
            datetime.utcnow() + timedelta(hours=1),
        )

        # Act
        blob = BlobClient(
            self.bsc.url, container_name=self.container_name, blob_name=blob_name, credential=token)
        container = ContainerClient(
            self.bsc.url, container_name=self.container_name, credential=token)

        container_props = await container.get_container_properties()
        blob_props = await blob.get_blob_properties()

        # Assert
        assert container_props is not None
        assert blob_props is not None

    @pytest.mark.live_test_only
    @BlobPreparer()
    async def test_account_sas_credential(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        await self._setup(storage_account_name, storage_account_key)
        blob_name = await self._create_block_blob()

        token = self.generate_sas(
            generate_account_sas,
            self.bsc.account_name,
            self.bsc.credential.account_key,
            ResourceTypes(container=True, object=True),
            AccountSasPermissions(read=True),
            datetime.utcnow() + timedelta(hours=1),
        )

        # Act
        blob = BlobClient(
            self.bsc.url, container_name=self.container_name, blob_name=blob_name, credential=AzureSasCredential(token))
        container = ContainerClient(
            self.bsc.url, container_name=self.container_name, credential=AzureSasCredential(token))
        blob_properties = await blob.get_blob_properties()
        container_properties = await container.get_container_properties()

        # Assert
        assert blob_name == blob_properties.name
        assert self.container_name == container_properties.name

    @BlobPreparer()
    async def test_multiple_services_sas(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Act
        token = self.generate_sas(
            generate_account_sas,
            storage_account_name,
            storage_account_key,
            ResourceTypes(container=True, object=True, service=True),
            AccountSasPermissions(read=True, list=True),
            datetime.utcnow() + timedelta(hours=1),
            services=Services(blob=True, fileshare=True)
        )

        # Assert
        assert 'ss=bf' in token

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_azure_named_key_credential_access(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        named_key = AzureNamedKeyCredential(storage_account_name, storage_account_key)
        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), named_key)
        container_name = self._get_container_reference()

        # Act
        container = bsc.get_container_client(container_name)
        created = await container.create_container()

        # Assert
        assert created

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_token_credential(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        await self._setup(storage_account_name, storage_account_key)
        token_credential = self.get_credential(BlobServiceClient, is_async=True)

        # Action 1: make sure token works
        service = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=token_credential)
        result = await service.get_service_properties()
        assert result is not None

        # Action 2: change token value to make request fail
        fake_credential = AsyncFakeCredential()
        service = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=fake_credential)
        with pytest.raises(ClientAuthenticationError):
            await service.get_service_properties()

        # Action 3: update token to make it working again
        service = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=token_credential)
        result = await service.get_service_properties()
        assert result is not None

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_token_credential_blob(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")

        # Setup
        container_name = self._get_container_reference()
        blob_name = self._get_blob_reference()
        blob_data = b'Helloworld'
        token_credential = self.get_credential(BlobServiceClient, is_async=True)

        service = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=token_credential)
        container = service.get_container_client(container_name)

        # Act / Assert
        try:
            await container.create_container()
            blob = await container.upload_blob(blob_name, blob_data)

            data = await (await blob.download_blob()).readall()
            assert blob_data == data

            await blob.delete_blob()
        finally:
            await container.delete_container()

    @pytest.mark.live_test_only
    @BlobPreparer()
    async def test_token_credential_with_batch_operation(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")

        # Setup
        container_name = self._get_container_reference()
        blob_name = self._get_blob_reference()
        token_credential = self.get_credential(BlobServiceClient, is_async=True)
        async with BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=token_credential) as service:
            container = service.get_container_client(container_name)
            try:
                await container.create_container()
                await container.upload_blob(blob_name + '1', b'HelloWorld')
                await container.upload_blob(blob_name + '2', b'HelloWorld')
                await container.upload_blob(blob_name + '3', b'HelloWorld')

                delete_batch = []
                blob_list = container.list_blobs(name_starts_with=blob_name)
                async for blob in blob_list:
                    delete_batch.append(blob.name)

                await container.delete_blobs(*delete_batch)
            finally:
                await container.delete_container()

    @pytest.mark.live_test_only
    @BlobPreparer()
    async def test_shared_read_access_blob(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        await self._setup(storage_account_name, storage_account_key)
        # Arrange
        blob_name = await self._create_block_blob()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)

        token = self.generate_sas(
            generate_blob_sas,
            blob.account_name,
            blob.container_name,
            blob.blob_name,
            snapshot=blob.snapshot,
            account_key=blob.credential.account_key,
            permission=BlobSasPermissions(read=True),
            expiry=datetime.utcnow() + timedelta(hours=1),
        )

        # Act
        sas_blob = BlobClient.from_blob_url(blob.url, credential=token)
        response = requests.get(sas_blob.url)

        # Assert
        response.raise_for_status()
        assert response.ok
        assert self.byte_data == response.content

    @pytest.mark.live_test_only
    @BlobPreparer()
    async def test_shared_read_access_blob_with_content_query_params(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        blob_name = await self._create_block_blob()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)

        token = self.generate_sas(
            generate_blob_sas,
            blob.account_name,
            blob.container_name,
            blob.blob_name,
            snapshot=blob.snapshot,
            account_key=blob.credential.account_key,
            permission=BlobSasPermissions(read=True),
            expiry=datetime.utcnow() + timedelta(hours=1),
            cache_control='no-cache',
            content_disposition='inline',
            content_encoding='utf-8',
            content_language='fr',
            content_type='text',
        )
        sas_blob = BlobClient.from_blob_url(blob.url, credential=token)

        # Act
        response = requests.get(sas_blob.url)

        # Assert
        response.raise_for_status()
        assert self.byte_data == response.content
        assert response.headers['cache-control'] == 'no-cache'
        assert response.headers['content-disposition'] == 'inline'
        assert response.headers['content-encoding'] == 'utf-8'
        assert response.headers['content-language'] == 'fr'
        assert response.headers['content-type'] == 'text'

    @pytest.mark.live_test_only
    @BlobPreparer()
    async def test_shared_write_access_blob(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        updated_data = b'updated blob data'
        blob_name = await self._create_block_blob()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)

        token = self.generate_sas(
            generate_blob_sas,
            blob.account_name,
            blob.container_name,
            blob.blob_name,
            snapshot=blob.snapshot,
            account_key=blob.credential.account_key,
            permission=BlobSasPermissions(write=True),
            expiry=datetime.utcnow() + timedelta(hours=1),
        )
        sas_blob = BlobClient.from_blob_url(blob.url, credential=token)

        # Act
        headers = {'x-ms-blob-type': 'BlockBlob'}
        response = requests.put(sas_blob.url, headers=headers, data=updated_data)

        # Assert
        response.raise_for_status()
        assert response.ok
        data = await (await blob.download_blob()).readall()
        assert updated_data == data

    @pytest.mark.live_test_only
    @BlobPreparer()
    async def test_shared_delete_access_blob(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        blob_name = await self._create_block_blob()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)

        token = self.generate_sas(
            generate_blob_sas,
            blob.account_name,
            blob.container_name,
            blob.blob_name,
            snapshot=blob.snapshot,
            account_key=blob.credential.account_key,
            permission=BlobSasPermissions(delete=True),
            expiry=datetime.utcnow() + timedelta(hours=1),
        )
        sas_blob = BlobClient.from_blob_url(blob.url, credential=token)

        # Act
        response = requests.delete(sas_blob.url)

        # Assert
        response.raise_for_status()
        assert response.ok
        with pytest.raises(HttpResponseError):
            await sas_blob.download_blob()

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_get_account_information(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Act
        await self._setup(storage_account_name, storage_account_key)
        bsc_info = await self.bsc.get_account_information()
        container_client = self.bsc.get_container_client(self.container_name)
        cc_info = await container_client.get_account_information()
        blob_client = await self._create_blob()
        bc_info = await blob_client.get_account_information()

        # Assert
        assert bsc_info.get('sku_name') is not None
        assert bsc_info.get('account_kind') is not None
        assert not bsc_info.get('is_hns_enabled')
        assert cc_info.get('sku_name') is not None
        assert cc_info.get('account_kind') is not None
        assert not cc_info.get('is_hns_enabled')
        assert bc_info.get('sku_name') is not None
        assert bc_info.get('account_kind') is not None
        assert not bc_info.get('is_hns_enabled')

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_get_account_information_sas(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")
        await self._setup(storage_account_name, storage_account_key)

        account_token = self.generate_sas(
            generate_account_sas,
            account_name=storage_account_name,
            account_key=storage_account_key,
            resource_types=ResourceTypes(service=True),
            permission=AccountSasPermissions(read=True),
            expiry=datetime.utcnow() + timedelta(hours=1),
        )

        container_token = self.generate_sas(
            generate_container_sas,
            account_name=storage_account_name,
            container_name=self.container_name,
            account_key=storage_account_key,
            permission=ContainerSasPermissions(read=True),
            expiry=datetime.utcnow() + timedelta(hours=1),
        )

        blob_token = self.generate_sas(
            generate_blob_sas,
            account_name=storage_account_name,
            container_name=self.container_name,
            blob_name=self._get_blob_reference(),
            account_key=storage_account_key,
            permission=BlobSasPermissions(read=True),
            expiry=datetime.utcnow() + timedelta(hours=1),
        )

        # Act
        bsc = BlobServiceClient(
            self.account_url(storage_account_name, "blob"),
            credential=account_token)
        bsc_info = await bsc.get_account_information()
        container_client = ContainerClient(
            self.account_url(storage_account_name, "blob"),
            self.container_name,
            credential=container_token)
        cc_info = await container_client.get_account_information()
        blob_client = BlobClient(
            self.account_url(storage_account_name, "blob"),
            self.container_name,
            self._get_blob_reference(),
            credential=blob_token)
        bc_info = await blob_client.get_account_information()

        # Assert
        assert bsc_info.get('sku_name') is not None
        assert bsc_info.get('account_kind') is not None
        assert not bsc_info.get('is_hns_enabled')
        assert cc_info.get('sku_name') is not None
        assert cc_info.get('account_kind') is not None
        assert not cc_info.get('is_hns_enabled')
        assert bc_info.get('sku_name') is not None
        assert bc_info.get('account_kind') is not None
        assert not bc_info.get('is_hns_enabled')

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_get_account_information_with_container_name(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Act
        # Container name gets ignored
        await self._setup(storage_account_name, storage_account_key)
        container = self.bsc.get_container_client("missing")
        info = await container.get_account_information()

        # Assert
        assert info.get('sku_name') is not None
        assert info.get('account_kind') is not None

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_get_account_information_with_blob_name(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Act
        # Both container and blob names get ignored
        await self._setup(storage_account_name, storage_account_key)
        blob = self.bsc.get_blob_client("missing", "missing")
        info = await blob.get_account_information()

        # Assert
        assert info.get('sku_name') is not None
        assert info.get('account_kind') is not None

    @pytest.mark.live_test_only
    @BlobPreparer()
    async def test_get_account_information_with_container_sas(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        container = self.bsc.get_container_client(self.container_name)
        permission = ContainerSasPermissions(read=True, write=True, delete=True, delete_previous_version=True,
                                             list=True, tag=True, set_immutability_policy=True,
                                             permanent_delete=True)
        assert 'y' in str(permission)
        token = self.generate_sas(
            generate_container_sas,
            container.account_name,
            container.container_name,
            account_key=container.credential.account_key,
            permission=permission,
            expiry=datetime.utcnow() + timedelta(hours=1),
        )
        sas_container = ContainerClient.from_container_url(container.url, credential=token)

        # Act
        info = await sas_container.get_account_information()

        # Assert
        assert info.get('sku_name') is not None
        assert info.get('account_kind') is not None

    @pytest.mark.live_test_only
    @BlobPreparer()
    async def test_get_account_information_with_blob_sas(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        blob_name = await self._create_block_blob()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)

        token = self.generate_sas(
            generate_blob_sas,
            blob.account_name,
            blob.container_name,
            blob.blob_name,
            snapshot=blob.snapshot,
            account_key=blob.credential.account_key,
            permission=BlobSasPermissions(read=True),
            expiry=datetime.utcnow() + timedelta(hours=1),
        )
        sas_blob = BlobClient.from_blob_url(blob.url, credential=token)

        # Act
        info = await sas_blob.get_account_information()

        # Assert
        assert info.get('sku_name') is not None
        assert info.get('account_kind') is not None

    @pytest.mark.live_test_only
    @BlobPreparer()
    async def test_download_to_file_with_sas(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        await self._setup(storage_account_name, storage_account_key)
        data = b'123' * 1024
        source_blob = await self._create_blob(data=data)

        sas_token = self.generate_sas(
            generate_blob_sas,
            source_blob.account_name,
            source_blob.container_name,
            source_blob.blob_name,
            snapshot=source_blob.snapshot,
            account_key=source_blob.credential.account_key,
            permission=BlobSasPermissions(read=True),
            expiry=datetime.utcnow() + timedelta(hours=1),
        )
        blob = BlobClient.from_blob_url(source_blob.url, credential=sas_token)

        # Act
        with tempfile.TemporaryFile() as temp_file:
            await download_blob_from_url(blob.url, temp_file)
            temp_file.seek(0)
            # Assert
            actual = temp_file.read()
            assert data == actual

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_download_to_file_with_credential(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        await self._setup(storage_account_name, storage_account_key)
        data = b'123' * 1024
        source_blob = await self._create_blob(data=data)

        # Act
        with tempfile.TemporaryFile() as temp_file:
            await download_blob_from_url(source_blob.url, temp_file, credential=storage_account_key)
            temp_file.seek(0)
            actual = temp_file.read()
            assert data == actual

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_download_to_stream_with_credential(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        await self._setup(storage_account_name, storage_account_key)
        data = b'123' * 1024
        source_blob = await self._create_blob(data=data)

        # Act
        with tempfile.TemporaryFile() as temp_file:
            await download_blob_from_url(source_blob.url, temp_file, credential=storage_account_key)
            temp_file.seek(0)
            # Assert
            actual = temp_file.read()
            assert data == actual

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_download_to_file_with_existing_file(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        await self._setup(storage_account_name, storage_account_key)
        data = b'123' * 1024
        source_blob = await self._create_blob(data=data)

        # Act
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            await download_blob_from_url(source_blob.url, temp_file.name, credential=storage_account_key, overwrite=True)

            with pytest.raises(ValueError):
                await download_blob_from_url(source_blob.url, temp_file.name)

            # Assert
            temp_file.seek(0)
            actual = temp_file.read()
            assert data == actual

            temp_file.close()
            os.unlink(temp_file.name)

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_download_to_file_with_existing_file_overwrite(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        await self._setup(storage_account_name, storage_account_key)
        data = b'123' * 1024
        source_blob = await self._create_blob(data=data)
        file_path = 'file_with_existing_file_overwrite.temp.{}.dat'.format(str(uuid.uuid4()))

        # Act
        await download_blob_from_url(
            source_blob.url, file_path,
            credential=storage_account_key)

        data2 = b'ABC' * 1024
        source_blob = await self._create_blob(data=data2)
        await download_blob_from_url(
            source_blob.url, file_path, overwrite=True,
            credential=storage_account_key)

        # Assert
        with open(file_path, 'rb') as stream:
            actual = stream.read()
            assert data2 == actual
        self._teardown(file_path)

    @pytest.mark.live_test_only
    @BlobPreparer()
    async def test_upload_to_url_bytes_with_sas(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        data = b'123' * 1024
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)

        token = self.generate_sas(
            generate_blob_sas,
            blob.account_name,
            blob.container_name,
            blob.blob_name,
            snapshot=blob.snapshot,
            account_key=blob.credential.account_key,
            permission=BlobSasPermissions(write=True),
            expiry=datetime.utcnow() + timedelta(hours=1),
        )
        sas_blob = BlobClient.from_blob_url(blob.url, credential=token)

        # Act
        uploaded = await upload_blob_to_url(sas_blob.url, data)

        # Assert
        assert uploaded is not None
        content = await (await blob.download_blob()).readall()
        assert data == content

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_upload_to_url_bytes_with_credential(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        data = b'123' * 1024
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)

        # Act
        uploaded = await upload_blob_to_url(
            blob.url, data, credential=storage_account_key)

        # Assert
        assert uploaded is not None
        content = await (await blob.download_blob()).readall()
        assert data == content

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_upload_to_url_bytes_with_existing_blob(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        data = b'123' * 1024
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        await blob.upload_blob(b"existing_data")

        # Act
        with pytest.raises(ResourceExistsError):
            await upload_blob_to_url(
                blob.url, data, credential=storage_account_key)

        # Assert
        content = await (await blob.download_blob()).readall()
        assert b"existing_data" == content

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_upload_to_url_bytes_with_existing_blob_overwrite(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        data = b'123' * 1024
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        await blob.upload_blob(b"existing_data")

        # Act
        uploaded = await upload_blob_to_url(
            blob.url, data,
            overwrite=True,
            credential=storage_account_key)

        # Assert
        assert uploaded is not None
        content = await (await blob.download_blob()).readall()
        assert data == content

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_upload_to_url_text_with_credential(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        data = '123' * 1024
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)

        # Act
        uploaded = await upload_blob_to_url(
            blob.url, data, credential=storage_account_key)

        # Assert
        assert uploaded is not None
        stream = await blob.download_blob(encoding='UTF-8')
        content = await stream.readall()
        assert data == content

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_upload_to_url_file_with_credential(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        data = b'123' * 1024
        blob_name = self._get_blob_reference()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)

        # Act
        with tempfile.TemporaryFile() as temp_file:
            temp_file.write(data)
            temp_file.seek(0)
            uploaded = await upload_blob_to_url(blob.url, data, credential=storage_account_key)

            # Assert
            assert uploaded is not None
            content = await (await blob.download_blob()).readall()
            assert data == content

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_transport_closed_only_once(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        container_name = self.get_resource_name('utcontainerasync')
        transport = AioHttpTransport()
        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=storage_account_key, transport=transport)
        blob_name = self._get_blob_reference()
        async with bsc:
            await bsc.get_service_properties()
            assert transport.session is not None
            async with bsc.get_blob_client(container_name, blob_name) as bc:
                assert transport.session is not None
            await bsc.get_service_properties()
            assert transport.session is not None

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_blob_immutability_policy(self, **kwargs):
        versioned_storage_account_name = kwargs.pop("versioned_storage_account_name")
        versioned_storage_account_key = kwargs.pop("versioned_storage_account_key")
        storage_resource_group_name = kwargs.pop("storage_resource_group_name")
        variables = kwargs.pop("variables", {})

        await self._setup(versioned_storage_account_name, versioned_storage_account_key)

        container_name = self.get_resource_name('vlwcontainer')
        if self.is_live:
            token_credential = self.get_credential(BlobServiceClient, is_async=True)
            subscription_id = self.get_settings_value("SUBSCRIPTION_ID")
            mgmt_client = StorageManagementClient(token_credential, subscription_id, '2021-04-01')
            property = mgmt_client.models().BlobContainer(
                immutable_storage_with_versioning=mgmt_client.models().ImmutableStorageWithVersioning(enabled=True))
            await mgmt_client.blob_containers.create(storage_resource_group_name, versioned_storage_account_name, container_name, blob_container=property)

        # Act
        blob_name = self.get_resource_name('vlwblob')
        blob = self.bsc.get_blob_client(container_name, blob_name)
        await blob.upload_blob(b"abc", overwrite=True)

        expiry_time = self.get_datetime_variable(variables, 'expiry_time', datetime.utcnow() + timedelta(seconds=5))
        immutability_policy = ImmutabilityPolicy(expiry_time=expiry_time,
                                                 policy_mode=BlobImmutabilityPolicyMode.Unlocked)
        resp = await blob.set_immutability_policy(
            immutability_policy=immutability_policy)

        # Assert
        # check immutability policy after set_immutability_policy()
        props = await blob.get_blob_properties()
        assert resp['immutability_policy_until_date'] is not None
        assert resp['immutability_policy_mode'] is not None
        assert props['immutability_policy']['expiry_time'] is not None
        assert props['immutability_policy']['policy_mode'] is not None
        assert props['immutability_policy']['policy_mode'] == "unlocked"

        # check immutability policy after delete_immutability_policy()
        await blob.delete_immutability_policy()
        props = await blob.get_blob_properties()
        assert props['immutability_policy']['policy_mode'] is None
        assert props['immutability_policy']['policy_mode'] is None

        if self.is_live:
            await blob.delete_immutability_policy()
            await blob.set_legal_hold(False)
            await blob.delete_blob()
            await mgmt_client.blob_containers.delete(storage_resource_group_name, versioned_storage_account_name, container_name)

        return variables

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_blob_legal_hold(self, **kwargs):
        versioned_storage_account_name = kwargs.pop("versioned_storage_account_name")
        versioned_storage_account_key = kwargs.pop("versioned_storage_account_key")
        storage_resource_group_name = kwargs.pop("storage_resource_group_name")

        await self._setup(versioned_storage_account_name, versioned_storage_account_key)

        container_name = self.get_resource_name('vlwcontainer')
        if self.is_live:
            token_credential = self.get_credential(BlobServiceClient, is_async=True)
            subscription_id = self.get_settings_value("SUBSCRIPTION_ID")
            mgmt_client = StorageManagementClient(token_credential, subscription_id, '2021-04-01')
            property = mgmt_client.models().BlobContainer(
                immutable_storage_with_versioning=mgmt_client.models().ImmutableStorageWithVersioning(enabled=True))
            await mgmt_client.blob_containers.create(storage_resource_group_name, versioned_storage_account_name, container_name, blob_container=property)

        # Act
        blob_name = self.get_resource_name('vlwblob')
        blob = self.bsc.get_blob_client(container_name, blob_name)
        await blob.upload_blob(b"abc", overwrite=True)
        resp = await blob.set_legal_hold(True)
        props = await blob.get_blob_properties()

        with pytest.raises(HttpResponseError):
            await blob.delete_blob()

        assert resp['legal_hold']
        assert props['has_legal_hold']

        resp2 = await blob.set_legal_hold(False)
        props2 = await blob.get_blob_properties()

        assert not resp2['legal_hold']
        assert not props2['has_legal_hold']

        if self.is_live:
            await blob.delete_immutability_policy()
            await blob.set_legal_hold(False)
            await blob.delete_blob()
            await mgmt_client.blob_containers.delete(storage_resource_group_name, versioned_storage_account_name, container_name)

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_download_blob_with_immutability_policy(self, **kwargs):
        versioned_storage_account_name = kwargs.pop("versioned_storage_account_name")
        versioned_storage_account_key = kwargs.pop("versioned_storage_account_key")
        storage_resource_group_name = kwargs.pop("storage_resource_group_name")
        variables = kwargs.pop("variables", {})

        await self._setup(versioned_storage_account_name, versioned_storage_account_key)
        container_name = self.get_resource_name('vlwcontainer')
        if self.is_live:
            token_credential = self.get_credential(BlobServiceClient, is_async=True)
            subscription_id = self.get_settings_value("SUBSCRIPTION_ID")
            mgmt_client = StorageManagementClient(token_credential, subscription_id, '2021-04-01')
            property = mgmt_client.models().BlobContainer(
                immutable_storage_with_versioning=mgmt_client.models().ImmutableStorageWithVersioning(enabled=True))
            await mgmt_client.blob_containers.create(storage_resource_group_name, versioned_storage_account_name, container_name, blob_container=property)

        # Act
        blob_name = self.get_resource_name('vlwblob')
        blob = self.bsc.get_blob_client(container_name, blob_name)
        content = b"abcedfg"

        expiry_time = self.get_datetime_variable(variables, 'expiry_time', datetime.utcnow() + timedelta(seconds=5))
        immutability_policy = ImmutabilityPolicy(expiry_time=expiry_time,
                                                 policy_mode=BlobImmutabilityPolicyMode.Unlocked)
        await blob.upload_blob(content,
                               immutability_policy=immutability_policy,
                               legal_hold=True,
                               overwrite=True)

        download_resp = await blob.download_blob()

        with pytest.raises(HttpResponseError):
            await blob.delete_blob()

        assert download_resp.properties['has_legal_hold']
        assert download_resp.properties['immutability_policy']['expiry_time'] is not None
        assert download_resp.properties['immutability_policy']['policy_mode'] is not None

        # Cleanup
        await blob.set_legal_hold(False)
        await blob.delete_immutability_policy()

        if self.is_live:
            await blob.delete_immutability_policy()
            await blob.set_legal_hold(False)
            await blob.delete_blob()
            await mgmt_client.blob_containers.delete(storage_resource_group_name, versioned_storage_account_name, container_name)

        return variables

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_list_blobs_with_immutability_policy(self, **kwargs):
        versioned_storage_account_name = kwargs.pop("versioned_storage_account_name")
        versioned_storage_account_key = kwargs.pop("versioned_storage_account_key")
        storage_resource_group_name = kwargs.pop("storage_resource_group_name")
        variables = kwargs.pop("variables", {})

        await self._setup(versioned_storage_account_name, versioned_storage_account_key)
        container_name = self.get_resource_name('vlwcontainer')
        if self.is_live:
            token_credential = self.get_credential(BlobServiceClient, is_async=True)
            subscription_id = self.get_settings_value("SUBSCRIPTION_ID")
            mgmt_client = StorageManagementClient(token_credential, subscription_id, '2021-04-01')
            property = mgmt_client.models().BlobContainer(
                immutable_storage_with_versioning=mgmt_client.models().ImmutableStorageWithVersioning(enabled=True))
            await mgmt_client.blob_containers.create(storage_resource_group_name, versioned_storage_account_name, container_name, blob_container=property)

        # Act
        blob_name = self.get_resource_name('vlwblob')
        container_client = self.bsc.get_container_client(container_name)
        blob = self.bsc.get_blob_client(container_name, blob_name)
        content = b"abcedfg"

        expiry_time = self.get_datetime_variable(variables, 'expiry_time', datetime.utcnow() + timedelta(seconds=5))
        immutability_policy = ImmutabilityPolicy(expiry_time=expiry_time,
                                                 policy_mode=BlobImmutabilityPolicyMode.Unlocked)
        await blob.upload_blob(content,
                               immutability_policy=immutability_policy,
                               legal_hold=True,
                               overwrite=True)

        blob_list = list()
        async for blob_prop in container_client.list_blobs(include=['immutabilitypolicy', 'legalhold']):
            blob_list.append(blob_prop)

        assert blob_list[0]['has_legal_hold']
        assert blob_list[0]['immutability_policy']['expiry_time'] is not None
        assert blob_list[0]['immutability_policy']['policy_mode'] is not None

        if self.is_live:
            await blob.delete_immutability_policy()
            await blob.set_legal_hold(False)
            await blob.delete_blob()
            await mgmt_client.blob_containers.delete(storage_resource_group_name, versioned_storage_account_name, container_name)

        return variables

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_validate_empty_blob(self, **kwargs):
        """Test that we can upload an empty blob with validate=True."""
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        await self._setup(storage_account_name, storage_account_key)

        blob_name = self.get_resource_name("utcontainer")
        container_client = self.bsc.get_container_client(self.container_name)
        await container_client.upload_blob(blob_name, b"", validate_content=True)

        blob_client = container_client.get_blob_client(blob_name)

        assert await blob_client.exists()
        assert (await blob_client.get_blob_properties()).size == 0

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_download_properties(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        await self._setup(storage_account_name, storage_account_key)

        blob_name = self.get_resource_name("utcontainer")
        blob_data = 'abc'

        # Act
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        await blob.upload_blob(blob_data)

        # Assert
        stream = await blob.download_blob(encoding='utf-8')
        props = stream.properties
        data = await stream.readall()

        assert data is not None
        assert data == blob_data
        assert props['creation_time'] is not None
        assert props['content_settings'] is not None
        assert props['size'] == len(blob_data)

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_blob_version_id_operations(self, **kwargs):
        versioned_storage_account_name = kwargs.pop("versioned_storage_account_name")
        versioned_storage_account_key = kwargs.pop("versioned_storage_account_key")

        await self._setup(versioned_storage_account_name, versioned_storage_account_key)
        container = self.bsc.get_container_client(self.container_name)
        blob_name = self.get_resource_name("utcontainer")
        blob_data = b'abc'
        blob_client = container.get_blob_client(blob_name)
        tags_a = {"color": "red"}
        tags_b = {"color": "yellow"}
        tags_c = {"color": "orange"}

        await blob_client.upload_blob(blob_data, overwrite=True)
        v1_props = await blob_client.get_blob_properties()
        v1_blob = BlobClient(self.bsc.url, container_name=self.container_name, blob_name=blob_name,
                             version_id=v1_props['version_id'], credential=versioned_storage_account_key)
        await blob_client.upload_blob(blob_data * 2, overwrite=True)
        v2_props = await blob_client.get_blob_properties()
        v2_blob = container.get_blob_client(v2_props, version_id=v2_props['version_id'])
        await blob_client.upload_blob(blob_data * 3, overwrite=True)
        v3_props = await blob_client.get_blob_properties()

        await v1_blob.set_standard_blob_tier(StandardBlobTier.Cool)
        await v1_blob.set_blob_tags(tags_a)
        await v2_blob.set_standard_blob_tier(StandardBlobTier.Cool, version_id=v3_props['version_id'])
        await v1_blob.set_blob_tags(tags_c, version_id=v3_props['version_id'])
        await v2_blob.set_standard_blob_tier(StandardBlobTier.Hot)
        await v2_blob.set_blob_tags(tags_b)

        # Assert
        assert await (await v1_blob.download_blob()).readall() == blob_data
        assert await (await v2_blob.download_blob()).readall() == blob_data * 2
        assert await (await v1_blob.download_blob(version_id=v3_props['version_id'])).readall() == blob_data * 3
        assert await v1_blob.get_blob_tags() == tags_a
        assert await v2_blob.get_blob_tags() == tags_b
        assert await v2_blob.get_blob_tags(version_id=v3_props['version_id']) == tags_c
        await v1_blob.delete_blob(version_id=v2_props['version_id'])
        assert await v1_blob.exists() is True
        assert await v1_blob.exists(version_id=v2_props['version_id']) is False
        assert await blob_client.exists() is True

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_storage_account_audience_blob_service_client(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        self.bsc.list_containers()

        # Act
        token_credential = self.get_credential(BlobServiceClient, is_async=True)
        bsc = BlobServiceClient(
            self.account_url(storage_account_name, "blob"), credential=token_credential,
            audience=f'https://{storage_account_name}.blob.core.windows.net'
        )

        # Assert
        response = bsc.list_containers()
        assert response is not None

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_storage_account_audience_blob_client(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        blob_name = await self._create_block_blob()
        blob = self.bsc.get_blob_client(self.container_name, blob_name)
        await blob.exists()

        # Act
        token_credential = self.get_credential(BlobClient, is_async=True)
        blob = BlobClient(
            self.bsc.url, container_name=self.container_name, blob_name=blob_name,
            credential=token_credential, audience=f'https://{storage_account_name}.blob.core.windows.net'
        )

        # Assert
        response = await blob.exists()
        assert response is not None

    @pytest.mark.live_test_only
    @BlobPreparer()
    async def test_oauth_error_handling(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")

        # Arrange
        from azure.identity.aio import ClientSecretCredential

        # Generate an invalid credential
        creds = ClientSecretCredential(
            "00000000-0000-0000-0000-000000000000",
            "00000000-0000-0000-0000-000000000000",
            "00000000-0000-0000-0000-000000000000" + 'a'
        )

        bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=creds, retry_total=0)
        container = bsc.get_container_client('testing')

        # Act
        with pytest.raises(ClientAuthenticationError):
            await container.exists()

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_upload_blob_partial_stream(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        blob = self.bsc.get_container_client(self.container_name).get_blob_client(self._get_blob_reference())
        data = b'abcde' * 100
        stream = BytesIO(data)
        length = 207

        # Act
        await blob.upload_blob(stream, length=length, overwrite=True)

        # Assert
        result = await (await blob.download_blob()).readall()
        assert result == data[:length]

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_upload_blob_partial_stream_chunked(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        # Arrange
        await self._setup(storage_account_name, storage_account_key)
        self.bsc._config.max_single_put_size = 1024
        self.bsc._config.max_block_size = 1024

        blob = self.bsc.get_container_client(self.container_name).get_blob_client(self._get_blob_reference())
        data = b'abcde' * 1024
        stream = BytesIO(data)
        length = 3000

        # Act
        await blob.upload_blob(stream, length=length, overwrite=True)

        # Assert
        result = await (await blob.download_blob()).readall()
        assert result == data[:length]
# ------------------------------------------------------------------------------