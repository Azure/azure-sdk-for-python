# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from io import BytesIO

import pytest
from azure.storage.fileshare import ShareClient as SyncShareClient
from azure.storage.fileshare.aio import ShareServiceClient

from devtools_testutils.aio import recorded_by_proxy_async
from devtools_testutils.storage.aio import AsyncStorageRecordedTestCase, GenericTestProxyParametrize1
from settings.testcase import FileSharePreparer
from test_content_validation import (
    assert_content_md5,
    assert_content_md5_get,
    assert_structured_message,
    assert_structured_message_get
)


class TestStorageContentValidationAsync(AsyncStorageRecordedTestCase):
    async def _setup(self, account_name):
        token_credential = self.get_credential(ShareServiceClient, is_async=True)
        self.ssc = ShareServiceClient(self.account_url(account_name, "file"), credential=token_credential, token_intent="backup", logging_enable=True)
        self.share_client = self.ssc.get_share_client(self.get_resource_name('utshare'))
        await self.share_client.create_share()

    def teardown_method(self, _):
        if self.share_client:
            sync_credential = self.get_credential(SyncShareClient, is_async=False)
            sync_share_client = SyncShareClient(
                self.account_url(self.share_client.account_name, "file"),
                self.share_client.share_name,
                credential=sync_credential,
                token_intent="backup")
            try:
                sync_share_client.delete_share()
            except:
                pass

    def _get_file_reference(self):
        return self.get_resource_name('file')

    @FileSharePreparer()
    @pytest.mark.parametrize('a', ['auto', 'md5', 'crc64'])  # a: validate_content
    @GenericTestProxyParametrize1()
    @recorded_by_proxy_async
    async def test_create_file_with_data(self, a, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")

        await self._setup(storage_account_name)
        file = self.share_client.get_file_client(self._get_file_reference())
        data = b'abc' * 512
        assert_method = assert_structured_message if a in ('auto', 'crc64') else assert_content_md5

        # Act
        await file.create_file(len(data), data=data, validate_content=a, raw_request_hook=assert_method)

        # Assert
        content = await file.download_file()
        assert await content.readall() == data

    @FileSharePreparer()
    @pytest.mark.parametrize('a', [True, 'auto', 'md5', 'crc64'])  # a: validate_content
    @GenericTestProxyParametrize1()
    @recorded_by_proxy_async
    async def test_upload_file(self, a, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")

        await self._setup(storage_account_name)
        file = self.share_client.get_file_client(self._get_file_reference())
        data = b'abc' * 512
        assert_method = assert_structured_message if a in ('auto', 'crc64') else assert_content_md5

        # Act
        await file.upload_file(data, validate_content=a, raw_request_hook=assert_method)

        # Assert
        content = await file.download_file()
        assert await content.readall() == data

    @FileSharePreparer()
    @pytest.mark.parametrize('a', [True, 'md5', 'crc64'])  # a: validate_content
    @GenericTestProxyParametrize1()
    @recorded_by_proxy_async
    async def test_upload_file_chunks(self, a, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")

        await self._setup(storage_account_name)
        self.share_client._config.max_range_size = 1024
        file = self.share_client.get_file_client(self._get_file_reference())
        data = b'abcde' * 512
        assert_method = assert_structured_message if a == 'crc64' else assert_content_md5

        # Act
        await file.upload_file(data, validate_content=a, raw_request_hook=assert_method)

        # Assert
        content = await file.download_file()
        assert await content.readall() == data

    @FileSharePreparer()
    @pytest.mark.parametrize('a', [True, 'auto', 'md5', 'crc64'])  # a: validate_content
    @GenericTestProxyParametrize1()
    @recorded_by_proxy_async
    async def test_upload_range(self, a, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")

        await self._setup(storage_account_name)
        file = self.share_client.get_file_client(self._get_file_reference())
        data1 = b'abcde' * 512
        data2 = '你好世界' * 10
        encoded2 = data2.encode('utf-16')

        assert_method = assert_structured_message if a in ('auto', 'crc64') else assert_content_md5

        # Act
        await file.create_file(len(data1) + len(encoded2))
        await file.upload_range(data1, 0, len(data1), validate_content=a, raw_request_hook=assert_method)
        await file.upload_range(data2, len(data1), len(encoded2), encoding='utf-16', validate_content=a, raw_request_hook=assert_method)

        # Assert
        content = await file.download_file()
        assert await content.readall() == data1 + encoded2

    @FileSharePreparer()
    @pytest.mark.parametrize('a', [True, 'md5', 'crc64'])  # a: validate_content
    @GenericTestProxyParametrize1()
    @recorded_by_proxy_async
    async def test_upload_range_streaming(self, a, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")

        await self._setup(storage_account_name)
        file = self.share_client.get_file_client(self._get_file_reference())

        data = b'abcd' * 1030  # 4 KiB + 24
        assert_method = assert_structured_message if a == 'crc64' else assert_content_md5

        # Act
        await file.create_file(len(data))
        # This is not an officially supported data type for upload_range, but we should still be able to handle it
        # as there are probably users out there using it.
        await file.upload_range(BytesIO(data), 0, len(data), validate_content=a, raw_request_hook=assert_method)

        # Assert
        content = await file.download_file()
        assert await content.readall() == data

    @FileSharePreparer()
    @pytest.mark.parametrize('a', [True, 'auto', 'md5', 'crc64'])  # a: validate_content
    @GenericTestProxyParametrize1()
    @recorded_by_proxy_async
    async def test_download_file(self, a, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")

        await self._setup(storage_account_name)
        file = self.share_client.get_file_client(self._get_file_reference())
        data = b'abc' * 512
        await file.upload_file(data)
        assert_method = assert_structured_message_get if a in ('auto', 'crc64') else assert_content_md5_get

        # Act
        downloader = await file.download_file(validate_content=a, raw_response_hook=assert_method)
        content = await downloader.readall()

        stream = BytesIO()
        downloader = await file.download_file(validate_content=a, raw_response_hook=assert_method)
        await downloader.readinto(stream)
        stream.seek(0)

        # Assert
        assert content == data
        assert stream.read() == data

    @FileSharePreparer()
    @pytest.mark.parametrize('a', [True, 'md5', 'crc64'])  # a: validate_content
    @GenericTestProxyParametrize1()
    @recorded_by_proxy_async
    async def test_download_file_chunks(self, a, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")

        await self._setup(storage_account_name)
        self.share_client._config.max_single_get_size = 512
        self.share_client._config.max_chunk_get_size = 512
        file = self.share_client.get_file_client(self._get_file_reference())
        data = b'abc' * 512 + b'abcde'
        await file.upload_file(data)
        assert_method = assert_structured_message_get if a == 'crc64' else assert_content_md5_get

        # Act
        downloader = await file.download_file(validate_content=a, raw_response_hook=assert_method)
        content = await downloader.readall()

        stream = BytesIO()
        downloader = await file.download_file(validate_content=a, raw_response_hook=assert_method)
        await downloader.readinto(stream)
        stream.seek(0)

        read_content = bytearray()
        downloader = await file.download_file(validate_content=a, raw_response_hook=assert_method)
        async for chunk in downloader.chunks():
            read_content.extend(chunk)

        # Assert
        assert content == data
        assert stream.read() == data
        assert read_content == data

    @FileSharePreparer()
    @pytest.mark.parametrize('a', [True, 'md5', 'crc64'])  # a: validate_content
    @GenericTestProxyParametrize1()
    @recorded_by_proxy_async
    async def test_download_file_chunks_partial(self, a, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")

        await self._setup(storage_account_name)
        self.share_client._config.max_single_get_size = 512
        self.share_client._config.max_chunk_get_size = 512
        file = self.share_client.get_file_client(self._get_file_reference())
        data = b'abc' * 512 + b'abcde'
        await file.upload_file(data)
        assert_method = assert_structured_message_get if a == 'crc64' else assert_content_md5_get

        # Act
        downloader = await file.download_file(offset=10, length=1000, validate_content=a, raw_response_hook=assert_method)
        content = await downloader.readall()

        stream = BytesIO()
        downloader = await file.download_file(offset=512, length=1024, validate_content=a, raw_response_hook=assert_method)
        await downloader.readinto(stream)
        stream.seek(0)

        # Assert
        assert content == data[10:1010]
        assert stream.read() == data[512:1536]

    @FileSharePreparer()
    @pytest.mark.live_test_only
    async def test_download_file_large_chunks(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")

        await self._setup(storage_account_name)
        # The service will use 4 MiB for structured message chunk size, so make chunk size larger
        self.share_client._config.max_chunk_get_size = 5 * 1024 * 1024  # 5 MiB
        file = self.share_client.get_file_client(self._get_file_reference())
        data = b'abcde' * 30 * 1024 * 1024 + b'abcde'  # 150 MiB + 5
        await file.upload_file(data, max_concurrency=5)

        # Act
        downloader = await file.download_file(validate_content='crc64', max_concurrency=5)
        content = await downloader.readall()

        downloader = await file.download_file(offset=5 * 1024 * 1024, length=25 * 1024 * 1024, validate_content='crc64')
        partial = await downloader.readall()

        # Assert
        assert content == data
        assert partial == data[5 * 1024 * 1024:30 * 1024 * 1024]
