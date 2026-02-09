# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from io import BytesIO

import pytest
from azure.core.exceptions import ResourceExistsError
from azure.storage.blob import BlobBlock, BlobType
from azure.storage.blob.aio import (
    BlobServiceClient,
    ContainerClient
)
from devtools_testutils.aio import recorded_by_proxy_async
from devtools_testutils.storage.aio import (
    AsyncStorageRecordedTestCase,
    GenericTestProxyParametrize1,
    GenericTestProxyParametrize2
)
from settings.testcase import BlobPreparer

from test_content_validation import (
    assert_content_crc64,
    assert_content_md5,
    assert_structured_message,
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

    # TODO: Figure out how to get this to run automatically
    async def _teardown(self):
        if self.container:
            try:
                await self.container.delete_container()
            except:
                pass

    def _get_blob_reference(self):
        return self.get_resource_name('blob')

    # TODO: This test coming later
    # @BlobPreparer()
    # async def test_encryption_blocked_crc64(self, **kwargs):
    #     storage_account_name = kwargs.pop("storage_account_name")
    #     storage_account_key = kwargs.pop("storage_account_key")

    #     kek = KeyWrapper('key1')
    #     blob = BlobClient(
    #         self.account_url(storage_account_name, "blob"),
    #         "testing",
    #         "testing",
    #         credential=storage_account_key,
    #         require_encryption=True,
    #         encryption_version='2.0',
    #         key_encryption_key=kek)

    #     with pytest.raises(ValueError):
    #         await blob.upload_blob(b'123', validate_content='crc64')

    @BlobPreparer()
    @pytest.mark.parametrize('a', [BlobType.BLOCKBLOB, BlobType.PAGEBLOB, BlobType.APPENDBLOB])  # a: blob_type
    @pytest.mark.parametrize('b', [True, 'md5', 'crc64'])  # b: validate_content
    @GenericTestProxyParametrize2()
    @recorded_by_proxy_async
    async def test_upload_blob(self, a, b, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")

        await self._setup(storage_account_name)
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

        await self._teardown()

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

        await self._teardown()

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
        await self._teardown()

    @BlobPreparer()
    @pytest.mark.parametrize('a', [True, 'md5', 'crc64'])  # a: validate_content
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

        assert_method = assert_content_crc64 if a == 'crc64' else assert_content_md5

        # Act
        await blob.stage_block('1', data1, validate_content=a, raw_request_hook=assert_method)
        await blob.stage_block('2', data2, encoding='utf-8-sig', validate_content=a, raw_request_hook=assert_method)
        await blob.stage_block('3', generator(), validate_content=a, raw_request_hook=assert_method)
        await blob.commit_block_list([BlobBlock('1'), BlobBlock('2'), BlobBlock('3')])

        # Assert
        content = await blob.download_blob()
        assert await content.read() == data1 + data2.encode('utf-8-sig') + data1
        await self._teardown()

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
        await self._teardown()

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
    @pytest.mark.parametrize('a', [True, 'md5', 'crc64'])  # a: validate_content
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

        assert_method = assert_content_crc64 if a == 'crc64' else assert_content_md5

        # Act
        await blob.create_append_blob()
        await blob.append_block(data1, validate_content=a, raw_request_hook=assert_method)
        await blob.append_block(data2, encoding='utf-16', validate_content=a, raw_request_hook=assert_method)
        await blob.append_block(generator(), validate_content=a, raw_request_hook=assert_method)

        # Assert
        content = await blob.download_blob()
        assert await content.readall() == data1 + data2.encode('utf-16') + data1
        await self._teardown()

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
        await self._teardown()

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
        await self._teardown()

    @BlobPreparer()
    @pytest.mark.parametrize('a', [True, 'md5', 'crc64'])  # a: validate_content
    @GenericTestProxyParametrize1()
    @recorded_by_proxy_async
    async def test_upload_page(self, a, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")

        await self._setup(storage_account_name)
        blob = self.container.get_blob_client(self._get_blob_reference())
        data1 = b'abc' * 512
        data2 = "你好世界abcd" * 32
        data2_encoded = data2.encode('utf-8')
        assert_method = assert_content_crc64 if a == 'crc64' else assert_content_md5

        # Act
        await blob.create_page_blob(5 * 1024)
        await blob.upload_page(data1, offset=0, length=len(data1), validate_content=a, raw_request_hook=assert_method)
        await blob.upload_page(data2, offset=len(data1), length=len(data2_encoded), encoding='utf-8', validate_content=a, raw_request_hook=assert_method)

        # Assert
        content = await blob.download_blob(offset=0, length=len(data1) + len(data2_encoded))
        assert await content.read() == data1 + data2_encoded
        await self._teardown()
