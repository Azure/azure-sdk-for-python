# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from io import BytesIO

import pytest
from azure.storage.filedatalake.aio import (
    DataLakeServiceClient
)

from devtools_testutils.aio import recorded_by_proxy_async
from devtools_testutils.storage.aio import AsyncStorageRecordedTestCase, GenericTestProxyParametrize1
from settings.testcase import DataLakePreparer
from test_content_validation import (
    assert_content_crc64,
    assert_content_md5,
    assert_content_md5_get,
    assert_structured_message,
    assert_structured_message_get
)


class TestStorageContentValidationAsync(AsyncStorageRecordedTestCase):
    async def _setup(self, account_name):
        token_credential = self.get_credential(DataLakeServiceClient, is_async=True)
        self.dsc = DataLakeServiceClient(self.account_url(account_name, "dfs"), credential=token_credential, logging_enable=True)
        self.file_system = self.dsc.get_file_system_client(self.get_resource_name('filesystem'))
        await self.file_system.create_file_system()

    # TODO: Figure out how to get this to run automatically
    async def _teardown(self):
        if self.file_system:
            try:
                await self.file_system.delete_file_system()
            except:
                pass

    def _get_file_reference(self):
        return self.get_resource_name('file')
    
    @DataLakePreparer()
    @pytest.mark.parametrize('a', [True, 'auto', 'md5', 'crc64'])  # a: validate_content
    @GenericTestProxyParametrize1()
    @recorded_by_proxy_async
    async def test_upload_data(self, a, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")

        await self._setup(datalake_storage_account_name)
        file = self.file_system.get_file_client(self._get_file_reference())
        data = b'abc' * 512
        assert_method = assert_content_crc64 if a in ('auto', 'crc64') else assert_content_md5

        # Act
        await file.upload_data(data, overwrite=True, validate_content=a, raw_request_hook=assert_method)

        # Assert
        content = await file.download_file()
        assert await content.read() == data
        await self._teardown()

    @DataLakePreparer()
    @pytest.mark.parametrize('a', [True, 'md5', 'crc64'])  # a: validate_content
    @GenericTestProxyParametrize1()
    @recorded_by_proxy_async
    async def test_upload_data_chunks(self, a, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")

        await self._setup(datalake_storage_account_name)
        file = self.file_system.get_file_client(self._get_file_reference())
        data = b'abcde' * 512
        assert_method = assert_content_crc64 if a == 'crc64' else assert_content_md5

        # Act
        await file.upload_data(data, overwrite=True, validate_content=a, chunk_size=1024, raw_request_hook=assert_method)

        # Assert
        content = await file.download_file()
        assert await content.read() == data
        await self._teardown()

    @DataLakePreparer()
    @pytest.mark.parametrize('a', [True, 'md5', 'crc64'])  # a: validate_content
    @GenericTestProxyParametrize1()
    @recorded_by_proxy_async
    async def test_upload_data_substream(self, a, **kwargs):
        # Substream is disabled when using content validation so this will behave like regular upload (buffer)
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")

        await self._setup(datalake_storage_account_name)
        self.file_system._config.min_large_chunk_upload_threshold = 1  # Set less than chunk size to enable substream
        file = self.file_system.get_file_client(self._get_file_reference())
        assert_method = assert_content_crc64 if a == 'crc64' else assert_content_md5

        data = b'abc' * 512 + b'abcde'
        io = BytesIO(data)

        # Act
        await file.upload_data(io, overwrite=True, validate_content=a, chunk_size=512, raw_request_hook=assert_method)

        # Assert
        content = await file.download_file()
        assert await content.read() == data
        await self._teardown()

    @DataLakePreparer()
    @pytest.mark.parametrize('a', [True, 'auto', 'md5', 'crc64'])  # a: validate_content
    @GenericTestProxyParametrize1()
    @recorded_by_proxy_async
    async def test_append_data(self, a, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")

        await self._setup(datalake_storage_account_name)
        file = self.file_system.get_file_client(self._get_file_reference())
        data1 = b'abcde' * 512
        data2 = '你好世界' * 10
        encoded2 = data2.encode('utf-8-sig')

        # An iterable with no length will be read into bytes and therefore will behave like
        # bytes when it comes to testing content validation.
        def generator():
            for i in range(0, len(data1), 500):
                yield data1[i: i + 500]

        assert_method = assert_content_crc64 if a in ('auto', 'crc64') else assert_content_md5

        # Act
        await file.create_file()
        await file.append_data(data1, 0, validate_content=a, raw_request_hook=assert_method)
        await file.append_data(data2, len(data1), encoding='utf-8-sig', validate_content=a, raw_request_hook=assert_method)
        await file.append_data(generator(), len(data1) + len(encoded2), validate_content=a, raw_request_hook=assert_method)
        await file.flush_data(len(data1) + len(encoded2) + len(data1))

        # Assert
        content = await file.download_file()
        assert await content.read() == data1 + encoded2 + data1
        await self._teardown()

    @DataLakePreparer()
    @pytest.mark.parametrize('a', [True, 'md5', 'crc64'])  # a: validate_content
    @GenericTestProxyParametrize1()
    @recorded_by_proxy_async
    async def test_append_data_streaming(self, a, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")

        await self._setup(datalake_storage_account_name)
        file = self.file_system.get_file_client(self._get_file_reference())

        content = b'abcde' * 1030  # 5 KiB + 30
        assert_method = assert_structured_message if a == 'crc64' else assert_content_md5

        # Act
        await file.create_file()
        await file.append_data(BytesIO(content), 0, flush=True, validate_content=a, raw_request_hook=assert_method)

        # Assert
        result = await file.download_file()
        assert await result.read() == content
        await self._teardown()

    @DataLakePreparer()
    @pytest.mark.parametrize('a', [True, 'md5', 'crc64'])  # a: validate_content
    @pytest.mark.live_test_only
    async def test_append_data_streaming_large(self, a, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")

        await self._setup(datalake_storage_account_name)
        file = self.file_system.get_file_client(self._get_file_reference())

        data1 = b'abcde' * 1024 * 1024  # 5 MiB
        data2 = b'12345' * 2 * 1024 * 1024 + b'abcdefg'  # 10 MiB + 7
        data3 = b'12345678' * 8 * 1024 * 1024  # 64 MiB
        assert_method = assert_structured_message if a == 'crc64' else assert_content_md5

        # Act
        await file.create_file()
        await file.append_data(BytesIO(data1), 0, flush=True, validate_content=a, raw_request_hook=assert_method)
        await file.append_data(BytesIO(data2), len(data1), flush=True, validate_content=a, raw_request_hook=assert_method)
        await file.append_data(BytesIO(data3), len(data1) + len(data2), flush=True, validate_content=a, raw_request_hook=assert_method)
        await file.flush_data(len(data1) + len(data2) + len(data3))

        # Assert
        result = await file.download_file()
        assert await result.read() == data1 + data2 + data3
        await self._teardown()

    @DataLakePreparer()
    @pytest.mark.parametrize('a', [True, 'auto', 'md5', 'crc64'])  # a: validate_content
    @GenericTestProxyParametrize1()
    @recorded_by_proxy_async
    async def test_download_file(self, a, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")

        await self._setup(datalake_storage_account_name)
        file = self.file_system.get_file_client(self._get_file_reference())
        data = b'abc' * 512
        await file.upload_data(data, overwrite=True)
        assert_method = assert_structured_message_get if a in ('auto', 'crc64') else assert_content_md5_get

        # Act
        downloader = await file.download_file(validate_content=a, raw_response_hook=assert_method)
        content = await downloader.read()

        stream = BytesIO()
        downloader = await file.download_file(validate_content=a, raw_response_hook=assert_method)
        await downloader.readinto(stream)
        stream.seek(0)

        # Assert
        assert content == data
        assert stream.read() == data
        await self._teardown()

    @DataLakePreparer()
    @pytest.mark.parametrize('a', [True, 'md5', 'crc64'])  # a: validate_content
    @GenericTestProxyParametrize1()
    @recorded_by_proxy_async
    async def test_download_file_chunks(self, a, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")

        await self._setup(datalake_storage_account_name)
        self.file_system._config.max_single_get_size = 512
        self.file_system._config.max_chunk_get_size = 512
        file = self.file_system.get_file_client(self._get_file_reference())
        data = b'abc' * 512 + b'abcde'
        await file.upload_data(data, overwrite=True)
        assert_method = assert_structured_message_get if a == 'crc64' else assert_content_md5_get

        # Act
        downloader = await file.download_file(validate_content=a, raw_response_hook=assert_method)
        content = await downloader.read()

        stream = BytesIO()
        downloader = await file.download_file(validate_content=a, raw_response_hook=assert_method)
        await downloader.readinto(stream)
        stream.seek(0)

        read_content = bytearray()
        downloader = await file.download_file(validate_content=a, raw_response_hook=assert_method)
        for _ in range(len(data) // 100 + 1):
            read_content.extend(await downloader.read(100))

        # Assert
        assert content == data
        assert stream.read() == data
        assert read_content == data
        await self._teardown()

    @DataLakePreparer()
    @pytest.mark.parametrize('a', [True, 'md5', 'crc64'])  # a: validate_content
    @GenericTestProxyParametrize1()
    @recorded_by_proxy_async
    async def test_download_file_chunks_partial(self, a, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")

        await self._setup(datalake_storage_account_name)
        self.file_system._config.max_single_get_size = 512
        self.file_system._config.max_chunk_get_size = 512
        file = self.file_system.get_file_client(self._get_file_reference())
        data = b'abc' * 512 + b'abcde'
        await file.upload_data(data, overwrite=True)
        assert_method = assert_structured_message_get if a == 'crc64' else assert_content_md5_get

        # Act
        downloader = await file.download_file(offset=10, length=1000, validate_content=a, raw_response_hook=assert_method)
        content = await downloader.read()

        stream = BytesIO()
        downloader = await file.download_file(offset=512, length=1024, validate_content=a, raw_response_hook=assert_method)
        await downloader.readinto(stream)
        stream.seek(0)

        # Assert
        assert content == data[10:1010]
        assert stream.read() == data[512:1536]
        await self._teardown()

    @DataLakePreparer()
    @pytest.mark.live_test_only
    async def test_download_file_large_chunks(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")

        await self._setup(datalake_storage_account_name)
        file = self.file_system.get_file_client(self._get_file_reference())
        # The service will use 4 MiB for structured message chunk size, so make chunk size larger
        self.file_system._config.max_chunk_get_size = 10 * 1024 * 1024
        data = b'abcde' * 30 * 1024 * 1024 + b'abcde'  # 150 MiB + 5
        await file.upload_data(data, overwrite=True, max_concurrency=5)

        # Act
        downloader = await file.download_file(validate_content='crc64', max_concurrency=5)
        content = await downloader.read()

        downloader = await file.download_file(offset=5 * 1024 * 1024, length=25 * 1024 * 1024, validate_content='crc64')
        partial = await downloader.read()

        # Assert
        assert content == data
        assert partial == data[5 * 1024 * 1024:30 * 1024 * 1024]
        await self._teardown()
