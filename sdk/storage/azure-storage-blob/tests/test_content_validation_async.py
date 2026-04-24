# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from io import BytesIO

import pytest
from azure.core.exceptions import ResourceExistsError
from azure.storage.blob import BlobBlock, BlobType, ContainerClient as SyncContainerClient
from azure.storage.blob.aio import (
    BlobClient,
    BlobServiceClient,
    ContainerClient
)
from devtools_testutils import is_live
from devtools_testutils.aio import recorded_by_proxy_async
from devtools_testutils.storage.aio import (
    AsyncStorageRecordedTestCase,
    GenericTestProxyParametrize1,
    GenericTestProxyParametrize2
)
from encryption_test_helper import KeyWrapper
from settings.testcase import BlobPreparer

from test_content_validation import (
    assert_content_crc64,
    assert_content_md5,
    assert_content_md5_get,
    assert_structured_message,
    assert_structured_message_get,
    TestIter
)


class TestStorageContentValidationAsync(AsyncStorageRecordedTestCase):
    bsc: BlobServiceClient
    container: ContainerClient

    async def _setup(self, account_name):
        token_credential = self.get_credential(BlobServiceClient, is_async=True)
        self.bsc = BlobServiceClient(self.account_url(account_name, "blob"), token_credential, logging_enable=True)
        self.container = self.bsc.get_container_client(self.get_resource_name('utcontainer'))
        try:
            await self.container.create_container()
        except ResourceExistsError:
            pass

    def teardown_method(self, _):
        if not is_live():
            return
        # Use sync client as teardown_method must be sync
        if self.container:
            sync_credential = self.get_credential(SyncContainerClient, is_async=False)
            sync_container = SyncContainerClient.from_container_url(
                self.container.url,
                credential=sync_credential)

            try:
                sync_container.delete_container()
            except:
                pass

    def _get_blob_reference(self):
        return self.get_resource_name('blob')

    @BlobPreparer()
    async def test_encryption_blocked_crc64(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")

        kek = KeyWrapper('key1')
        blob = BlobClient(
            self.account_url(storage_account_name, "blob"),
            "testing",
            "testing",
            credential=self.get_credential(BlobServiceClient, is_async=True),
            require_encryption=True,
            encryption_version='2.0',
            key_encryption_key=kek)

        with pytest.raises(ValueError):
            await blob.upload_blob(b'123', validate_content='crc64')

        # Needed for teardown
        self.container = None

    @BlobPreparer()
    @pytest.mark.parametrize('a', [BlobType.BLOCKBLOB, BlobType.PAGEBLOB, BlobType.APPENDBLOB])  # a: blob_type
    @pytest.mark.parametrize('b', [True, "auto", 'md5', 'crc64'])  # b: validate_content
    @GenericTestProxyParametrize2()
    @recorded_by_proxy_async
    async def test_upload_blob(self, a, b, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")

        await self._setup(storage_account_name)
        blob = self.container.get_blob_client(self._get_blob_reference())
        assert_method = assert_content_crc64 if b in ('auto', 'crc64') else assert_content_md5

        # Test supported data types
        byte_data = b'abc' * 512
        str_data = "你好世界abcd" * 32
        str_data_encoded = str_data.encode('utf-8')
        byte_stream = BytesIO(byte_data)
        byte_iter = TestIter(byte_data)
        str_iter = TestIter(str_data)

        # Act / Assert
        await blob.upload_blob(byte_data, blob_type=a, validate_content=b, overwrite=True, raw_request_hook=assert_method)
        assert await (await blob.download_blob()).read() == byte_data
        await blob.upload_blob(str_data, blob_type=a, encoding='utf-8', validate_content=b, overwrite=True, raw_request_hook=assert_method)
        assert await (await blob.download_blob()).read() == str_data_encoded
        await blob.upload_blob(byte_stream, blob_type=a, validate_content=b, overwrite=True, raw_request_hook=assert_method)
        assert await (await blob.download_blob()).read() == byte_data
        await blob.upload_blob(byte_iter, blob_type=a, validate_content=b, overwrite=True, raw_request_hook=assert_method)
        assert await (await blob.download_blob()).read() == byte_data
        await blob.upload_blob(str_iter, blob_type=a, length=len(str_data_encoded), encoding='utf-8', validate_content=b, overwrite=True, raw_request_hook=assert_method)
        assert await (await blob.download_blob()).read() == str_data_encoded

    @BlobPreparer()
    @pytest.mark.parametrize('a', [BlobType.BLOCKBLOB, BlobType.PAGEBLOB, BlobType.APPENDBLOB])  # a: blob_type
    @pytest.mark.parametrize('b', [True, 'md5', 'crc64'])  # b: validate_content
    @GenericTestProxyParametrize2()
    @recorded_by_proxy_async
    async def test_upload_blob_chunks(self, a, b, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")

        await self._setup(storage_account_name)
        self.container._config.max_single_put_size = 512
        self.container._config.max_block_size = 512
        self.container._config.max_page_size = 512
        blob = self.container.get_blob_client(self._get_blob_reference())
        assert_method = assert_content_crc64 if b == 'crc64' else assert_content_md5

        # Test supported data types
        byte_data = b'abc' * 512
        str_data = "你好世界abcd" * 32
        str_data_encoded = str_data.encode('utf-8')
        byte_stream = BytesIO(byte_data)
        byte_iter = TestIter(byte_data)
        str_iter = TestIter(str_data)

        # Act / Assert
        await blob.upload_blob(byte_data, blob_type=a, validate_content=b, overwrite=True, raw_request_hook=assert_method)
        assert await (await blob.download_blob()).read() == byte_data
        await blob.upload_blob(str_data, blob_type=a, encoding='utf-8', validate_content=b, overwrite=True, raw_request_hook=assert_method)
        assert await (await blob.download_blob()).read() == str_data_encoded
        await blob.upload_blob(byte_stream, blob_type=a, validate_content=b, overwrite=True, raw_request_hook=assert_method)
        assert await (await blob.download_blob()).read() == byte_data
        await blob.upload_blob(byte_iter, blob_type=a, validate_content=b, overwrite=True, raw_request_hook=assert_method)
        assert await (await blob.download_blob()).read() == byte_data
        await blob.upload_blob(str_iter, blob_type=a, length=len(str_data_encoded), encoding='utf-8', validate_content=b, overwrite=True, raw_request_hook=assert_method)
        assert await (await blob.download_blob()).read() == str_data_encoded

    @BlobPreparer()
    @pytest.mark.parametrize('a', [True, 'md5', 'crc64'])  # a: validate_content
    @GenericTestProxyParametrize1()
    @recorded_by_proxy_async
    async def test_upload_blob_substream(self, a, **kwargs):
        # Substream is disabled when using content validation so this will behave like regular upload (buffer)
        storage_account_name = kwargs.pop("storage_account_name")

        await self._setup(storage_account_name)
        self.container._config.max_single_put_size = 512
        self.container._config.max_block_size = 512
        self.container._config.min_large_block_upload_threshold = 1  # Set less than block size to enable substream
        blob = self.container.get_blob_client(self._get_blob_reference())
        assert_method = assert_content_crc64 if a == 'crc64' else assert_content_md5

        data = b'abc' * 512 + b'abcde'
        io = BytesIO(data)

        # Act
        await blob.upload_blob(io, validate_content=a, raw_request_hook=assert_method)

        # Assert
        content = await blob.download_blob()
        assert await content.read() == data

    @BlobPreparer()
    @pytest.mark.parametrize('a', [True, 'auto', 'md5', 'crc64'])  # a: validate_content
    @GenericTestProxyParametrize1()
    @recorded_by_proxy_async
    async def test_stage_block(self, a, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")

        await self._setup(storage_account_name)
        blob = self.container.get_blob_client(self._get_blob_reference())
        data1 = b'abc' * 512
        data2 = '你好世界' * 10

        # An iterable with no length will be read into bytes and therefore will behave like
        # bytes when it comes to testing content validation.
        def generator():
            for i in range(0, len(data1), 500):
                yield data1[i: i + 500]

        assert_method = assert_content_crc64 if a in ('auto', 'crc64') else assert_content_md5

        # Act
        await blob.stage_block('1', data1, validate_content=a, raw_request_hook=assert_method)
        await blob.stage_block('2', data2, encoding='utf-8-sig', validate_content=a, raw_request_hook=assert_method)
        await blob.stage_block('3', generator(), validate_content=a, raw_request_hook=assert_method)
        await blob.commit_block_list([BlobBlock('1'), BlobBlock('2'), BlobBlock('3')])

        # Assert
        content = await blob.download_blob()
        assert await content.read() == data1 + data2.encode('utf-8-sig') + data1

    @BlobPreparer()
    @pytest.mark.parametrize('a', [True, 'md5', 'crc64'])  # a: validate_content
    @GenericTestProxyParametrize1()
    @recorded_by_proxy_async
    async def test_stage_block_streaming(self, a, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")

        await self._setup(storage_account_name)
        blob = self.container.get_blob_client(self._get_blob_reference())

        content = b'abcde' * 1030  # 5 KiB + 30
        assert_method = assert_structured_message if a == 'crc64' else assert_content_md5

        await blob.stage_block('1', BytesIO(content), validate_content=a, raw_request_hook=assert_method)
        await blob.commit_block_list([BlobBlock('1')])

        # Assert
        result = await blob.download_blob()
        assert await result.read() == content

    @BlobPreparer()
    @pytest.mark.parametrize('a', [True, 'md5', 'crc64'])  # a: validate_content
    @pytest.mark.live_test_only
    async def test_stage_block_streaming_large(self, a, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")

        await self._setup(storage_account_name)
        blob = self.container.get_blob_client(self._get_blob_reference())

        data1 = b'abcde' * 1024 * 1024  # 5 MiB
        data2 = b'12345' * 2 * 1024 * 1024 + b'abcdefg'  # 10 MiB + 7
        data3 = b'12345678' * 8 * 1024 * 1024  # 64 MiB
        assert_method = assert_structured_message if a == 'crc64' else assert_content_md5

        await blob.stage_block('1', BytesIO(data1), validate_content=a, raw_request_hook=assert_method)
        await blob.stage_block('2', BytesIO(data2), validate_content=a, raw_request_hook=assert_method)
        await blob.stage_block('3', BytesIO(data3), validate_content=a, raw_request_hook=assert_method)
        await blob.commit_block_list([BlobBlock('1'), BlobBlock('2'), BlobBlock('3')])

        result = await blob.download_blob()
        assert await result.read() == data1 + data2 + data3

    @BlobPreparer()
    @pytest.mark.parametrize('a', [True, 'auto', 'md5', 'crc64'])  # a: validate_content
    @GenericTestProxyParametrize1()
    @recorded_by_proxy_async
    async def test_append_block(self, a, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")

        await self._setup(storage_account_name)
        blob = self.container.get_blob_client(self._get_blob_reference())
        data1 = b'abc' * 512
        data2 = '你好世界' * 10

        # An iterable with no length will be read into bytes and therefore will behave like
        # bytes when it comes to testing content validation.
        def generator():
            for i in range(0, len(data1), 500):
                yield data1[i: i + 500]

        assert_method = assert_content_crc64 if a in ('auto', 'crc64') else assert_content_md5

        # Act
        await blob.create_append_blob()
        await blob.append_block(data1, validate_content=a, raw_request_hook=assert_method)
        await blob.append_block(data2, encoding='utf-16', validate_content=a, raw_request_hook=assert_method)
        await blob.append_block(generator(), validate_content=a, raw_request_hook=assert_method)

        # Assert
        content = await blob.download_blob()
        assert await content.readall() == data1 + data2.encode('utf-16') + data1

    @BlobPreparer()
    @pytest.mark.parametrize('a', [True, 'md5', 'crc64'])  # a: validate_content
    @GenericTestProxyParametrize1()
    @recorded_by_proxy_async
    async def test_append_block_streaming(self, a, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")

        await self._setup(storage_account_name)
        blob = self.container.get_blob_client(self._get_blob_reference())

        content = b'abcde' * 1030  # 5 KiB + 30
        assert_method = assert_structured_message if a == 'crc64' else assert_content_md5

        await blob.create_append_blob()
        await blob.append_block(BytesIO(content), validate_content=a, raw_request_hook=assert_method)

        result = await blob.download_blob()
        assert await result.read() == content

    @BlobPreparer()
    @pytest.mark.parametrize('a', [True, 'md5', 'crc64'])  # a: validate_content
    @pytest.mark.live_test_only
    async def test_append_block_streaming_large(self, a, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")

        await self._setup(storage_account_name)
        blob = self.container.get_blob_client(self._get_blob_reference())

        data1 = b'abcde' * 1024 * 1024  # 5 MiB
        data2 = b'12345' * 2 * 1024 * 1024 + b'abcdefg'  # 10 MiB + 7
        data3 = b'12345678' * 8 * 1024 * 1024  # 64 MiB
        assert_method = assert_structured_message if a == 'crc64' else assert_content_md5

        await blob.create_append_blob()
        await blob.append_block(BytesIO(data1), validate_content=a, raw_request_hook=assert_method)
        await blob.append_block(BytesIO(data2), validate_content=a, raw_request_hook=assert_method)
        await blob.append_block(BytesIO(data3), validate_content=a, raw_request_hook=assert_method)

        result = await blob.download_blob()
        assert await result.read() == data1 + data2 + data3

    @BlobPreparer()
    @pytest.mark.parametrize('a', [True, 'auto', 'md5', 'crc64'])  # a: validate_content
    @GenericTestProxyParametrize1()
    @recorded_by_proxy_async
    async def test_upload_page(self, a, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")

        await self._setup(storage_account_name)
        blob = self.container.get_blob_client(self._get_blob_reference())
        data1 = b'abc' * 512
        data2 = "你好世界abcd" * 32
        data2_encoded = data2.encode('utf-8')
        assert_method = assert_content_crc64 if a in ('auto', 'crc64') else assert_content_md5

        # Act
        await blob.create_page_blob(5 * 1024)
        await blob.upload_page(data1, offset=0, length=len(data1), validate_content=a, raw_request_hook=assert_method)
        await blob.upload_page(data2, offset=len(data1), length=len(data2_encoded), encoding='utf-8', validate_content=a, raw_request_hook=assert_method)

        # Assert
        content = await blob.download_blob(offset=0, length=len(data1) + len(data2_encoded))
        assert await content.read() == data1 + data2_encoded

    @BlobPreparer()
    @pytest.mark.parametrize('a', [True, 'auto', 'md5', 'crc64'])  # a: validate_content
    @GenericTestProxyParametrize1()
    @recorded_by_proxy_async
    async def test_download_blob(self, a, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")

        await self._setup(storage_account_name)
        blob = self.container.get_blob_client(self._get_blob_reference())
        data = b'abc' * 512
        await blob.upload_blob(data, overwrite=True)
        assert_method = assert_structured_message_get if a in ('auto', 'crc64') else assert_content_md5_get

        # Act
        downloader = await blob.download_blob(validate_content=a, raw_response_hook=assert_method)
        content = await downloader.read()

        stream = BytesIO()
        downloader = await blob.download_blob(validate_content=a, raw_response_hook=assert_method)
        await downloader.readinto(stream)
        stream.seek(0)

        # Assert
        assert content == data
        assert stream.read() == data

    @BlobPreparer()
    @pytest.mark.parametrize('a', [True, 'md5', 'crc64'])  # a: validate_content
    @GenericTestProxyParametrize1()
    @recorded_by_proxy_async
    async def test_download_blob_chunks(self, a, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")

        await self._setup(storage_account_name)
        self.container._config.max_single_get_size = 512
        self.container._config.max_chunk_get_size = 512
        blob = self.container.get_blob_client(self._get_blob_reference())
        data = b'abc' * 512 + b'abcde'
        await blob.upload_blob(data, overwrite=True)
        assert_method = assert_structured_message_get if a == 'crc64' else assert_content_md5_get

        # Act
        downloader = await blob.download_blob(validate_content=a, raw_response_hook=assert_method)
        content = await downloader.read()

        stream = BytesIO()
        downloader = await blob.download_blob(validate_content=a, raw_response_hook=assert_method)
        await downloader.readinto(stream)
        stream.seek(0)

        read_content = b''
        downloader = await blob.download_blob(validate_content=a, raw_response_hook=assert_method)
        for _ in range(len(data) // 100 + 1):
            read_content += await downloader.read(100)

        # Assert
        assert content == data
        assert stream.read() == data
        assert read_content == data

    @BlobPreparer()
    @pytest.mark.parametrize('a', [True, 'md5', 'crc64'])  # a: validate_content
    @GenericTestProxyParametrize1()
    @recorded_by_proxy_async
    async def test_download_blob_chunks_partial(self, a, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")

        await self._setup(storage_account_name)
        self.container._config.max_single_get_size = 512
        self.container._config.max_chunk_get_size = 512
        blob = self.container.get_blob_client(self._get_blob_reference())
        data = b'abc' * 512 + b'abcde'
        await blob.upload_blob(data, overwrite=True)
        assert_method = assert_structured_message_get if a == 'crc64' else assert_content_md5_get

        # Act
        downloader = await blob.download_blob(offset=10, length=1000, validate_content=a, raw_response_hook=assert_method)
        content = await downloader.read()

        stream = BytesIO()
        downloader = await blob.download_blob(offset=10, length=1000, validate_content=a, raw_response_hook=assert_method)
        await downloader.readinto(stream)
        stream.seek(0)

        # Assert
        assert content == data[10:1010]
        assert stream.read() == data[10:1010]

    @BlobPreparer()
    @pytest.mark.live_test_only
    async def test_download_blob_large_chunks(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")

        await self._setup(storage_account_name)
        blob = self.container.get_blob_client(self._get_blob_reference())
        # The service will use 4 MiB for structured message chunk size, so make chunk size larger
        self.container._config.max_chunk_get_size = 10 * 1024 * 1024
        data = b'abcde' * 30 * 1024 * 1024 + b'abcde'  # 150 MiB + 5
        await blob.upload_blob(data, overwrite=True, max_concurrency=5)

        # Act
        downloader = await blob.download_blob(validate_content='crc64', max_concurrency=5)
        content = await downloader.read()

        downloader = await blob.download_blob(offset=5 * 1024 * 1024, length=25 * 1024 * 1024, validate_content='crc64')
        partial = await downloader.read()

        # Assert
        assert content == data
        assert partial == data[5 * 1024 * 1024: 30 * 1024 * 1024]

    @BlobPreparer()
    @pytest.mark.parametrize('a', [True, 'md5', 'crc64'])  # a: validate_content
    @GenericTestProxyParametrize1()
    @recorded_by_proxy_async
    async def test_download_blob_chars(self, a, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")

        await self._setup(storage_account_name)
        self.container._config.max_single_get_size = 512
        self.container._config.max_chunk_get_size = 512

        data = '你好世界' * 256  # 3 KiB
        blob = self.container.get_blob_client(self._get_blob_reference())
        await blob.upload_blob(data, encoding='utf-8', overwrite=True)

        stream = await blob.download_blob(encoding='utf-8', validate_content=a)
        assert await stream.read() == data

        stream = await blob.download_blob(encoding='utf-8', validate_content=a)
        assert await stream.read(chars=100000) == data

        result = ''
        stream = await blob.download_blob(encoding='utf-8', validate_content=a)
        for _ in range(4):
            chunk = await stream.read(chars=100)
            result += chunk
            assert len(chunk) == 100

        result += await stream.readall()
        assert result == data

    @BlobPreparer()
    @pytest.mark.parametrize('a', [True, 'md5', 'crc64'])  # a: validate_content
    @GenericTestProxyParametrize1()
    @recorded_by_proxy_async
    async def test_content_validation_with_retry(self, a, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")

        # Setup with retry enabled
        token_credential = self.get_credential(BlobServiceClient, is_async=True)
        self.bsc = BlobServiceClient(
            self.account_url(storage_account_name, "blob"),
            token_credential,
            retry_total=1,
            initial_backoff=0.1,
            increment_base=0.1,
            logging_enable=True
        )
        self.container = self.bsc.get_container_client(self.get_resource_name('utcontainer'))
        try:
            await self.container.create_container()
        except ResourceExistsError:
            pass
        blob = self.container.get_blob_client(self._get_blob_reference())
        data = b'abc' * 512

        # Determine the appropriate assert methods based on validation mode
        upload_assert_method = assert_content_crc64 if a == 'crc64' else assert_content_md5
        download_assert_method = assert_structured_message_get if a == 'crc64' else assert_content_md5_get

        # Test upload with retry
        upload_call_count = 0
        def upload_hook_fail_once(response):
            nonlocal upload_call_count
            upload_call_count += 1
            # Assert content validation headers are present on both attempts
            upload_assert_method(response)
            if upload_call_count == 1:
                response.http_response.status_code = 408  # Request Timeout - triggers retry

        await blob.upload_blob(data, validate_content=a, overwrite=True, raw_response_hook=upload_hook_fail_once)
        assert upload_call_count == 2  # Original + retry
        assert await (await blob.download_blob()).read() == data

        # Test download with retry
        download_call_count = 0
        def download_hook_fail_once(response):
            nonlocal download_call_count
            download_call_count += 1
            # Assert content validation headers are present on both attempts
            download_assert_method(response)
            if download_call_count == 1:
                response.http_response.status_code = 408  # Request Timeout - triggers retry

        downloader = await blob.download_blob(validate_content=a, raw_response_hook=download_hook_fail_once)
        content = await downloader.read()
        assert download_call_count == 2  # Original + retry
        assert content == data
