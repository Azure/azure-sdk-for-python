# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from io import BytesIO

import pytest
from azure.storage.blob import BlobBlock, BlobType
from azure.storage.blob.aio import (
    BlobClient,
    BlobServiceClient,
    ContainerClient
)
from devtools_testutils.aio import recorded_by_proxy_async
from devtools_testutils.storage.aio import AsyncStorageRecordedTestCase, GenericTestProxyParametrize1
from settings.testcase import BlobPreparer

from encryption_test_helper import KeyWrapper
from test_content_validation import assert_content_crc64, assert_content_md5, assert_structured_message


class TestStorageContentValidationAsync(AsyncStorageRecordedTestCase):
    bsc: BlobServiceClient = None
    container: ContainerClient = None

    async def _setup(self, account_name, account_key):
        self.bsc = BlobServiceClient(self.account_url(account_name, "blob"), credential=account_key, logging_enable=True)
        self.container = self.bsc.get_container_client(self.get_resource_name('utcontainer'))
        await self.container.create_container()

    # TODO: Figure out how to get this to run automatically
    async def _teardown(self):
        if self.container:
            try:
                await self.container.delete_container()
            except:
                pass

    def _get_blob_reference(self):
        return self.get_resource_name('blob')

    @BlobPreparer()
    async def test_encryption_blocked_crc64(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        kek = KeyWrapper('key1')
        blob = BlobClient(
            self.account_url(storage_account_name, "blob"),
            "testing",
            "testing",
            credential=storage_account_key,
            require_encryption=True,
            encryption_version='2.0',
            key_encryption_key=kek)

        with pytest.raises(ValueError):
            await blob.upload_blob(b'123', validate_content='crc64')

    @BlobPreparer()
    @pytest.mark.parametrize('a', [BlobType.BLOCKBLOB, BlobType.PAGEBLOB, BlobType.APPENDBLOB])  # a: blob_type
    @GenericTestProxyParametrize1()
    @recorded_by_proxy_async
    async def test_upload_blob_legacy_bool(self, a, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        await self._setup(storage_account_name, storage_account_key)
        blob = self.container.get_blob_client(self._get_blob_reference())
        data = b'abc' * 512

        # Act
        response = await blob.upload_blob(data, a, validate_content=True, raw_request_hook=assert_content_md5)

        # Assert
        assert response
        await self._teardown()

    @BlobPreparer()
    @pytest.mark.parametrize('a', [BlobType.BLOCKBLOB, BlobType.PAGEBLOB, BlobType.APPENDBLOB])  # a: blob_type
    @GenericTestProxyParametrize1()
    @recorded_by_proxy_async
    async def test_upload_blob_legacy_bool_chunks(self, a, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        await self._setup(storage_account_name, storage_account_key)
        blob = self.container.get_blob_client(self._get_blob_reference())
        self.container._config.max_single_put_size = 512
        self.container._config.max_block_size = 512
        data = b'abc' * 512

        # Act
        response = await blob.upload_blob(data, a, validate_content=True, raw_request_hook=assert_content_md5)

        # Assert
        assert response
        await self._teardown()

    @BlobPreparer()
    @pytest.mark.parametrize('a', [BlobType.BLOCKBLOB, BlobType.PAGEBLOB, BlobType.APPENDBLOB])  # a: blob_type
    @GenericTestProxyParametrize1()
    @recorded_by_proxy_async
    async def test_upload_blob_md5(self, a, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        await self._setup(storage_account_name, storage_account_key)
        blob = self.container.get_blob_client(self._get_blob_reference())
        data = b'abc' * 512

        # Act
        response = await blob.upload_blob(data, a, validate_content='md5', raw_request_hook=assert_content_md5)

        # Assert
        assert response
        await self._teardown()

    @BlobPreparer()
    @pytest.mark.parametrize('a', [BlobType.BLOCKBLOB, BlobType.PAGEBLOB, BlobType.APPENDBLOB])  # a: blob_type
    @GenericTestProxyParametrize1()
    @recorded_by_proxy_async
    async def test_upload_blob_md5_chunks(self, a, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        await self._setup(storage_account_name, storage_account_key)
        self.container._config.max_single_put_size = 512
        self.container._config.max_block_size = 512
        blob = self.container.get_blob_client(self._get_blob_reference())
        data = b'abc' * 512

        # Act
        response = await blob.upload_blob(data, a, validate_content='md5', raw_request_hook=assert_content_md5)

        # Assert
        assert response
        await self._teardown()

    @BlobPreparer()
    @pytest.mark.parametrize('a', [BlobType.BLOCKBLOB, BlobType.PAGEBLOB, BlobType.APPENDBLOB])  # a: blob_type
    @GenericTestProxyParametrize1()
    @recorded_by_proxy_async
    async def test_upload_blob_crc64(self, a, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        await self._setup(storage_account_name, storage_account_key)
        blob = self.container.get_blob_client(self._get_blob_reference())

        # Test different data types
        byte_data = b'abc' * 512
        str_data = "你好世界abcd" * 32
        stream = BytesIO(byte_data)

        # Act
        resp1 = await blob.upload_blob(byte_data, a, overwrite=True, validate_content='crc64',
                                 raw_request_hook=assert_content_crc64)
        resp2 = await blob.upload_blob(str_data, a, overwrite=True, validate_content='crc64',
                                 raw_request_hook=assert_content_crc64)
        resp3 = await blob.upload_blob(stream, a, overwrite=True, validate_content='crc64',
                                 raw_request_hook=assert_content_crc64)

        # Assert
        assert resp1
        assert resp2
        assert resp3
        await self._teardown()

    @BlobPreparer()
    @pytest.mark.parametrize('a', [BlobType.BLOCKBLOB, BlobType.PAGEBLOB, BlobType.APPENDBLOB])  # a: blob_type
    @GenericTestProxyParametrize1()
    @recorded_by_proxy_async
    async def test_upload_blob_crc64_chunks(self, a, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        await self._setup(storage_account_name, storage_account_key)
        self.container._config.max_single_put_size = 512
        self.container._config.max_block_size = 512
        blob = self.container.get_blob_client(self._get_blob_reference())

        # Test different data types
        byte_data = b'abc' * 512
        str_data = "你好世界abcd" * 32
        stream = BytesIO(byte_data)

        # Act
        resp1 = await blob.upload_blob(byte_data, a, overwrite=True, validate_content='crc64',
                                 raw_request_hook=assert_content_crc64)
        resp2 = await blob.upload_blob(str_data, a, overwrite=True, validate_content='crc64',
                                 raw_request_hook=assert_content_crc64)
        resp3 = await blob.upload_blob(stream, a, overwrite=True, validate_content='crc64',
                                 raw_request_hook=assert_content_crc64)

        # Assert
        assert resp1
        assert resp2
        assert resp3
        await self._teardown()

    @BlobPreparer()
    @pytest.mark.parametrize('a', [True, 'md5', 'crc64'])  # a: validate_content
    @GenericTestProxyParametrize1()
    @recorded_by_proxy_async
    async def test_stage_block(self, a, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        await self._setup(storage_account_name, storage_account_key)
        blob = self.container.get_blob_client(self._get_blob_reference())
        data1 = b'abc' * 512
        data2 = '你好世界' * 10
        assert_method = assert_structured_message if a == 'crc64' else assert_content_md5

        # Act
        await blob.stage_block('1', data1, validate_content=a, raw_request_hook=assert_method)
        await blob.stage_block('2', data2, encoding='utf-8-sig', validate_content=a, raw_request_hook=assert_method)
        await blob.commit_block_list([BlobBlock('1'), BlobBlock('2')])

        # Assert
        content = await blob.download_blob()
        assert await content.readall() == data1 + data2.encode('utf-8-sig')
        await self._teardown()

    @BlobPreparer()
    @pytest.mark.parametrize('a', [True, 'md5', 'crc64'])  # a: validate_content
    @pytest.mark.live_test_only
    async def test_stage_block_large(self, a, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        await self._setup(storage_account_name, storage_account_key)
        blob = self.container.get_blob_client(self._get_blob_reference())
        data1 = b'abcde' * 1024 * 1024  # 5 MiB
        data2 = b'12345' * 1024 * 1024 + b'abcdefg'  # 10 MiB + 7
        assert_method = assert_structured_message if a == 'crc64' else assert_content_md5

        # Act
        await blob.stage_block('1', data1, validate_content=a, raw_request_hook=assert_method)
        await blob.stage_block('2', data2, encoding='utf-8-sig', validate_content=a, raw_request_hook=assert_method)
        await blob.commit_block_list([BlobBlock('1'), BlobBlock('2')])

        # Assert
        content = await blob.download_blob()
        assert await content.readall() == data1 + data2
        await self._teardown()

    @BlobPreparer()
    @pytest.mark.parametrize('a', [True, 'md5', 'crc64'])  # a: validate_content
    @GenericTestProxyParametrize1()
    @recorded_by_proxy_async
    async def test_stage_block_data_types(self, a, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        await self._setup(storage_account_name, storage_account_key)
        blob = self.container.get_blob_client(self._get_blob_reference())

        content = b'abcde' * 1030  # 5 KiB + 30
        byte_io = BytesIO(content)

        def generator():
            for i in range(0, len(content), 500):
                yield content[i: i + 500]

        # TODO: Fix Iterable[str]? (Or just require length)
        # def text_generator():
        #     s_content = str(content, encoding='utf-8')
        #     for i in range(0, len(s_content), 500):
        #         yield s_content[i: i + 500]

        data_list = [byte_io, generator()]
        assert_method = assert_structured_message if a == 'crc64' else assert_content_md5

        blocks = []
        for j in range(len(data_list)):
            await blob.stage_block(str(j), data_list[j], validate_content=a, raw_request_hook=assert_method)
            blocks.append(BlobBlock(str(j)))
        await blob.commit_block_list(blocks)

        # Assert
        result = await blob.download_blob()
        assert await result.readall() == content * 2
        await self._teardown()

    @BlobPreparer()
    @pytest.mark.parametrize('a', [True, 'md5', 'crc64'])  # a: validate_content
    @GenericTestProxyParametrize1()
    @recorded_by_proxy_async
    async def test_append_block(self, a, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        await self._setup(storage_account_name, storage_account_key)
        blob = self.container.get_blob_client(self._get_blob_reference())
        data1 = b'abc' * 512
        data2 = '你好世界' * 10
        assert_method = assert_structured_message if a == 'crc64' else assert_content_md5

        # Act
        await blob.create_append_blob()
        await blob.append_block(data1, validate_content=a, raw_request_hook=assert_method)
        await blob.append_block(data2, encoding='utf-8-sig', validate_content=a, raw_request_hook=assert_method)

        # Assert
        content = await blob.download_blob()
        assert await content.readall() == data1 + data2.encode('utf-8-sig')
        await self._teardown()

    @BlobPreparer()
    @pytest.mark.parametrize('a', [True, 'md5', 'crc64'])  # a: validate_content
    @pytest.mark.live_test_only
    async def test_append_block_large(self, a, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        await self._setup(storage_account_name, storage_account_key)
        blob = self.container.get_blob_client(self._get_blob_reference())
        data1 = b'abcde' * 1024 * 1024  # 5 MiB
        data2 = b'12345' * 1024 * 1024 + b'abcdefg'  # 10 MiB + 7
        assert_method = assert_structured_message if a == 'crc64' else assert_content_md5

        # Act
        await blob.create_append_blob()
        await blob.append_block(data1, validate_content=a, raw_request_hook=assert_method)
        await blob.append_block(data2, encoding='utf-8-sig', validate_content=a, raw_request_hook=assert_method)

        # Assert
        content = await blob.download_blob()
        assert await content.readall() == data1 + data2
        await self._teardown()

    @BlobPreparer()
    @pytest.mark.parametrize('a', [True, 'md5', 'crc64'])  # a: validate_content
    @GenericTestProxyParametrize1()
    @recorded_by_proxy_async
    async def test_upload_page(self, a, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        await self._setup(storage_account_name, storage_account_key)
        blob = self.container.get_blob_client(self._get_blob_reference())
        data1 = b'abc' * 512
        data2 = "你好世界abcd" * 32
        data2_encoded_len = 512
        assert_method = assert_content_crc64 if a == 'crc64' else assert_content_md5

        # Act
        await blob.create_page_blob(5 * 1024)
        await blob.upload_page(data1, offset=0, length=len(data1), validate_content=a, raw_request_hook=assert_method)
        await blob.upload_page(data2, offset=len(data1), length=data2_encoded_len, encoding='utf-8', validate_content=a, raw_request_hook=assert_method)

        # Assert
        content = await blob.download_blob(offset=0, length=len(data1) + data2_encoded_len)
        assert await content.readall() == data1 + data2.encode('utf-8')
        await self._teardown()
