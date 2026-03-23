# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import pytest

from azure.storage.blob.aio import BlobClient, BlobServiceClient
from azure.core.exceptions import ResourceExistsError
from azure.core.pipeline.transport import AioHttpTransport, AsyncioRequestsTransport

from devtools_testutils.aio import recorded_by_proxy_async
from devtools_testutils.storage.aio import AsyncStorageRecordedTestCase
from settings.testcase import BlobPreparer
from test_helpers_async import AsyncStream, MockLegacyTransport


class TestStorageTransportsAsync(AsyncStorageRecordedTestCase):
    async def _setup(self, storage_account_name, key):
        self.bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=key.secret)
        self.container_name = self.get_resource_name('utcontainer')
        self.byte_data = self.get_random_bytes(1024)
        if self.is_live:
            try:
                await self.bsc.create_container(self.container_name)
            except ResourceExistsError:
                pass

    @BlobPreparer()
    async def test_legacy_transport_old_response(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        transport = MockLegacyTransport()
        blob_client = BlobClient(
            self.account_url(storage_account_name, "blob"),
            container_name='container',
            blob_name='blob',
            credential=storage_account_key.secret,
            transport=transport,
            retry_total=0
        )

        data = b"Hello Async World!"
        stream = AsyncStream(data)
        resp = await blob_client.upload_blob(stream, overwrite=True)
        assert resp is not None

        blob_data = await (await blob_client.download_blob()).read()
        assert blob_data == b"Hello Async World!"  # data is fixed by mock transport

        resp = await blob_client.delete_blob()
        assert resp is None

    @BlobPreparer()
    async def test_legacy_transport_old_response_content_validation(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        transport = MockLegacyTransport()
        blob_client = BlobClient(
            self.account_url(storage_account_name, "blob"),
            container_name='container',
            blob_name='blob',
            credential=storage_account_key.secret,
            transport=transport,
            retry_total=0
        )

        data = b"Hello Async World!"
        stream = AsyncStream(data)
        resp = await blob_client.upload_blob(stream, overwrite=True, validate_content=True)
        assert resp is not None

        blob_data = await (await blob_client.download_blob(validate_content=True)).read()
        assert blob_data == b"Hello Async World!"  # data is fixed by mock transport

        resp = await blob_client.delete_blob()
        assert resp is None

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_legacy_transport(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        await self._setup(storage_account_name, storage_account_key)

        transport = AioHttpTransport()
        blob_client = BlobClient(
            self.account_url(storage_account_name, "blob"),
            container_name=self.container_name,
            blob_name=self.get_resource_name('blob'),
            credential=storage_account_key.secret,
            transport=transport
        )

        data = b"Hello Async World!"
        stream = AsyncStream(data)
        resp = await blob_client.upload_blob(stream, overwrite=True)
        assert resp is not None

        blob_data = await (await blob_client.download_blob()).read()
        assert blob_data == b"Hello Async World!"

        resp = await blob_client.delete_blob()
        assert resp is None

    @BlobPreparer()
    @recorded_by_proxy_async
    async def test_legacy_transport_content_validation(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        await self._setup(storage_account_name, storage_account_key)

        transport = AioHttpTransport()
        blob_client = BlobClient(
            self.account_url(storage_account_name, "blob"),
            container_name=self.container_name,
            blob_name=self.get_resource_name('blob'),
            credential=storage_account_key.secret,
            transport=transport
        )

        data = b"Hello Async World!"
        stream = AsyncStream(data)
        resp = await blob_client.upload_blob(stream, overwrite=True, validate_content=True)
        assert resp is not None

        blob_data = await (await blob_client.download_blob(validate_content=True)).read()
        assert blob_data == b"Hello Async World!"

        resp = await blob_client.delete_blob()
        assert resp is None

    @pytest.mark.live_test_only
    @BlobPreparer()
    async def test_asyncio_transport(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        await self._setup(storage_account_name, storage_account_key)

        transport = AsyncioRequestsTransport()
        blob_client = BlobClient(
            self.account_url(storage_account_name, "blob"),
            container_name=self.container_name,
            blob_name=self.get_resource_name('blob'),
            credential=storage_account_key.secret,
            transport=transport
        )

        data = b"Hello Async World!"
        stream = AsyncStream(data)
        resp = await blob_client.upload_blob(stream, overwrite=True)
        assert resp is not None

        blob_data = await (await blob_client.download_blob()).read()
        assert blob_data == b"Hello Async World!"

        resp = await blob_client.delete_blob()
        assert resp is None

    @pytest.mark.live_test_only
    @BlobPreparer()
    async def test_asyncio_transport_content_validation(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        await self._setup(storage_account_name, storage_account_key)

        transport = AsyncioRequestsTransport()
        blob_client = BlobClient(
            self.account_url(storage_account_name, "blob"),
            container_name=self.container_name,
            blob_name=self.get_resource_name('blob'),
            credential=storage_account_key.secret,
            transport=transport
        )

        data = b"Hello Async World!"
        stream = AsyncStream(data)
        resp = await blob_client.upload_blob(stream, overwrite=True, validate_content=True)
        assert resp is not None

        blob_data = await (await blob_client.download_blob(validate_content=True)).read()
        assert blob_data == b"Hello Async World!"

        resp = await blob_client.delete_blob()
        assert resp is None
