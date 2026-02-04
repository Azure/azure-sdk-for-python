# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from io import BytesIO

import pytest
from azure.storage.blob import (
    BlobBlock,
    BlobServiceClient,
    BlobType,
    ContainerClient
)
from devtools_testutils import recorded_by_proxy
from devtools_testutils.storage import (
    GenericTestProxyParametrize1,
    GenericTestProxyParametrize2,
    StorageRecordedTestCase
)

from settings.testcase import BlobPreparer


def assert_content_md5(request):
    if request.http_request.query.get('comp') in ('block', 'page') or request.http_request.headers.get('x-ms-blob-type') == 'BlockBlob':
        assert request.http_request.headers.get('Content-MD5') is not None


def assert_content_md5_get(response):
    assert response.http_request.headers.get('x-ms-range-get-content-md5') == 'true'
    assert response.http_response.headers.get('Content-MD5') is not None


def assert_content_crc64(request):
    if request.http_request.query.get('comp') in ('block', 'page') or request.http_request.headers.get('x-ms-blob-type') == 'BlockBlob':
        assert request.http_request.headers.get('x-ms-content-crc64') is not None


def assert_structured_message(request):
    if request.http_request.query.get('comp') in ('block', 'page') or request.http_request.headers.get('x-ms-blob-type') == 'BlockBlob':
        assert request.http_request.headers.get('x-ms-structured-body') is not None


class TestIter:
    def __init__(self, data, *, chunk_size=100):
        self.data = data
        self.chunk_size = chunk_size
        self.length = len(data)
        self.offset = 0

    def __len__(self):
        return self.length

    def __iter__(self):
        return self

    def __next__(self):
        if self.offset >= self.length:
            raise StopIteration

        result = self.data[self.offset: self.offset + self.chunk_size]
        self.offset += len(result)
        return result


class TestStorageContentValidation(StorageRecordedTestCase):
    bsc: BlobServiceClient
    container: ContainerClient

    def _setup(self, account_name):
        token_credential = self.get_credential(BlobServiceClient)
        self.bsc = BlobServiceClient(self.account_url(account_name, "blob"), token_credential, logging_enable=True)
        self.container = self.bsc.get_container_client(self.get_resource_name('utcontainer'))
        self.container.create_container()

    def teardown_method(self, _):
        if self.container:
            try:
                self.container.delete_container()
            except:
                pass

    def _get_blob_reference(self):
        return self.get_resource_name('blob')

    # TODO: This test coming later
    # @BlobPreparer()
    # def test_encryption_blocked_crc64(self, **kwargs):
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
    #         blob.upload_blob(b'123', validate_content='crc64')

    @BlobPreparer()
    @pytest.mark.parametrize('a', [BlobType.BLOCKBLOB, BlobType.PAGEBLOB, BlobType.APPENDBLOB])  # a: blob_type
    @pytest.mark.parametrize('b', [True, 'md5', 'crc64'])  # b: validate_content
    @GenericTestProxyParametrize2()
    @recorded_by_proxy
    def test_upload_blob(self, a, b, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")

        self._setup(storage_account_name)
        blob = self.container.get_blob_client(self._get_blob_reference())
        assert_method = assert_content_crc64 if b == 'crc64' else assert_content_md5

        # Test supported data types
        byte_data = b'abc' * 512
        str_data = "你好世界abcd" * 32
        str_data_encoded = str_data.encode('utf-8')
        byte_stream = BytesIO(byte_data)
        byte_iter = TestIter(byte_data)
        str_iter = TestIter(str_data)

        blob.upload_blob(byte_data, blob_type=a, validate_content=b, overwrite=True, raw_request_hook=assert_method)
        assert blob.download_blob().read() == byte_data
        blob.upload_blob(str_data, blob_type=a, encoding='utf-8', validate_content=b, overwrite=True, raw_request_hook=assert_method)
        assert blob.download_blob().read() == str_data_encoded
        blob.upload_blob(byte_stream, blob_type=a, validate_content=b, overwrite=True, raw_request_hook=assert_method)
        assert blob.download_blob().read() == byte_data
        blob.upload_blob(byte_iter, blob_type=a, validate_content=b, overwrite=True, raw_request_hook=assert_method)
        assert blob.download_blob().read() == byte_data
        blob.upload_blob(str_iter, blob_type=a, length=len(str_data_encoded), encoding='utf-8', validate_content=b, overwrite=True, raw_request_hook=assert_method)
        assert blob.download_blob().read() == str_data_encoded

    @BlobPreparer()
    @pytest.mark.parametrize('a', [BlobType.BLOCKBLOB, BlobType.PAGEBLOB, BlobType.APPENDBLOB])  # a: blob_type
    @pytest.mark.parametrize('b', [True, 'md5', 'crc64'])  # b: validate_content
    @GenericTestProxyParametrize2()
    @recorded_by_proxy
    def test_upload_blob_chunks(self, a, b, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")

        self._setup(storage_account_name)
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

        blob.upload_blob(byte_data, blob_type=a, validate_content=b, overwrite=True, raw_request_hook=assert_method)
        assert blob.download_blob().read() == byte_data
        blob.upload_blob(str_data, blob_type=a, encoding='utf-8', validate_content=b, overwrite=True, raw_request_hook=assert_method)
        assert blob.download_blob().read() == str_data_encoded
        blob.upload_blob(byte_stream, blob_type=a, validate_content=b, overwrite=True, raw_request_hook=assert_method)
        assert blob.download_blob().read() == byte_data
        blob.upload_blob(byte_iter, blob_type=a, validate_content=b, overwrite=True, raw_request_hook=assert_method)
        assert blob.download_blob().read() == byte_data
        blob.upload_blob(str_iter, blob_type=a, length=len(str_data_encoded), encoding='utf-8', validate_content=b, overwrite=True, raw_request_hook=assert_method)
        assert blob.download_blob().read() == str_data_encoded

    # @BlobPreparer()
    # @pytest.mark.parametrize('a', [True, 'md5', 'crc64'])  # a: validate_content
    # @GenericTestProxyParametrize1()
    # @recorded_by_proxy
    # def test_upload_blob_substream(self, a, **kwargs):
    #     storage_account_name = kwargs.pop("storage_account_name")
    #     storage_account_key = kwargs.pop("storage_account_key")
    #
    #     self._setup(storage_account_name, storage_account_key)
    #     self.container._config.max_single_put_size = 512
    #     self.container._config.max_block_size = 512
    #     self.container._config.min_large_block_upload_threshold = 1  # Set less than block size to enable substream
    #     blob = self.container.get_blob_client(self._get_blob_reference())
    #     assert_method = assert_structured_message if a == 'crc64' else assert_content_md5
    #
    #     data = b'abc' * 512 + b'abcde'
    #     io = BytesIO(data)
    #
    #     # Act
    #     blob.upload_blob(io, validate_content=a, raw_request_hook=assert_method)
    #
    #     # Assert
    #     content = blob.download_blob()
    #     assert content.read() == data

    @BlobPreparer()
    @pytest.mark.parametrize('a', [True, 'md5', 'crc64'])  # a: validate_content
    @GenericTestProxyParametrize1()
    @recorded_by_proxy
    def test_stage_block(self, a, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")

        self._setup(storage_account_name)
        blob = self.container.get_blob_client(self._get_blob_reference())
        data1 = b'abc' * 512
        data2 = '你好世界' * 10

        # An iterable with no length will be read into bytes and therefore will behave like
        # bytes when it comes to testing content validation.
        def generator():
            for i in range(0, len(data1), 500):
                yield data1[i: i + 500]

        assert_method = assert_content_crc64 if a == 'crc64' else assert_content_md5

        blob.stage_block('1', data1, validate_content=a, raw_request_hook=assert_method)
        blob.stage_block('2', data2, encoding='utf-8-sig', validate_content=a, raw_request_hook=assert_method)
        blob.stage_block('3', generator(),  validate_content=a, raw_request_hook=assert_method)
        blob.commit_block_list([BlobBlock('1'), BlobBlock('2'), BlobBlock('3')])

        # Assert
        content = blob.download_blob()
        assert content.read() == data1 + data2.encode('utf-8-sig') + data1

    @BlobPreparer()
    @pytest.mark.parametrize('a', [True, 'md5', 'crc64'])  # a: validate_content
    @GenericTestProxyParametrize1()
    @recorded_by_proxy
    def test_stage_block_streaming(self, a, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")

        self._setup(storage_account_name)
        blob = self.container.get_blob_client(self._get_blob_reference())

        content = b'abcde' * 1030  # 5 KiB + 30
        assert_method = assert_structured_message if a == 'crc64' else assert_content_md5

        blob.stage_block('1', BytesIO(content), validate_content=a, raw_request_hook=assert_method)
        blob.commit_block_list([BlobBlock('1')])

        result = blob.download_blob()
        assert result.read() == content

    @BlobPreparer()
    @pytest.mark.parametrize('a', [True, 'md5', 'crc64'])  # a: validate_content
    @pytest.mark.live_test_only
    def test_stage_block_streaming_large(self, a, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")

        self._setup(storage_account_name)
        blob = self.container.get_blob_client(self._get_blob_reference())

        data1 = b'abcde' * 1024 * 1024  # 5 MiB
        data2 = b'12345' * 2 * 1024 * 1024 + b'abcdefg'  # 10 MiB + 7
        data3 = b'12345678' * 8 * 1024 * 1024  # 64 MiB
        assert_method = assert_structured_message if a == 'crc64' else assert_content_md5

        blob.stage_block('1', BytesIO(data1), validate_content=a, raw_request_hook=assert_method)
        blob.stage_block('2', BytesIO(data2), validate_content=a, raw_request_hook=assert_method)
        blob.stage_block('3', BytesIO(data3), validate_content=a, raw_request_hook=assert_method)
        blob.commit_block_list([BlobBlock('1'), BlobBlock('2'), BlobBlock('3')])

        result = blob.download_blob()
        assert result.read() == data1 + data2 + data3

    @BlobPreparer()
    @pytest.mark.parametrize('a', [True, 'md5', 'crc64'])  # a: validate_content
    @GenericTestProxyParametrize1()
    @recorded_by_proxy
    def test_append_block(self, a, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")

        self._setup(storage_account_name)
        blob = self.container.get_blob_client(self._get_blob_reference())
        data1 = b'abc' * 512
        data2 = '你好世界' * 10

        # An iterable with no length will be read into bytes and therefore will behave like
        # bytes when it comes to testing content validation.
        def generator():
            for i in range(0, len(data1), 500):
                yield data1[i: i + 500]

        assert_method = assert_content_crc64 if a == 'crc64' else assert_content_md5

        blob.create_append_blob()
        blob.append_block(data1, validate_content=a, raw_request_hook=assert_method)
        blob.append_block(data2, encoding='utf-16', validate_content=a, raw_request_hook=assert_method)
        blob.append_block(generator(), validate_content=a, raw_request_hook=assert_method)

        content = blob.download_blob()
        assert content.read() == data1 + data2.encode('utf-16') + data1

    @BlobPreparer()
    @pytest.mark.parametrize('a', [True, 'md5', 'crc64'])  # a: validate_content
    @GenericTestProxyParametrize1()
    @recorded_by_proxy
    def test_append_block_streaming(self, a, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")

        self._setup(storage_account_name)
        blob = self.container.get_blob_client(self._get_blob_reference())

        content = b'abcde' * 1030  # 5 KiB + 30
        assert_method = assert_structured_message if a == 'crc64' else assert_content_md5

        blob.create_append_blob()
        blob.append_block(BytesIO(content), validate_content=a, raw_request_hook=assert_method)

        result = blob.download_blob()
        assert result.read() == content

    @BlobPreparer()
    @pytest.mark.parametrize('a', [True, 'md5', 'crc64'])  # a: validate_content
    @pytest.mark.live_test_only
    def test_append_block_streaming_large(self, a, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")

        self._setup(storage_account_name)
        blob = self.container.get_blob_client(self._get_blob_reference())

        data1 = b'abcde' * 1024 * 1024  # 5 MiB
        data2 = b'12345' * 2 * 1024 * 1024 + b'abcdefg'  # 10 MiB + 7
        data3 = b'12345678' * 8 * 1024 * 1024  # 64 MiB
        assert_method = assert_structured_message if a == 'crc64' else assert_content_md5

        blob.create_append_blob()
        blob.append_block(BytesIO(data1), validate_content=a, raw_request_hook=assert_method)
        blob.append_block(BytesIO(data2), validate_content=a, raw_request_hook=assert_method)
        blob.append_block(BytesIO(data3), validate_content=a, raw_request_hook=assert_method)

        result = blob.download_blob()
        assert result.read() == data1 + data2 + data3

    @BlobPreparer()
    @pytest.mark.parametrize('a', [True, 'md5', 'crc64'])  # a: validate_content
    @GenericTestProxyParametrize1()
    @recorded_by_proxy
    def test_upload_page(self, a, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")

        self._setup(storage_account_name)
        blob = self.container.get_blob_client(self._get_blob_reference())
        data1 = b'abc' * 512
        data2 = "你好世界abcd" * 32
        data2_encoded = data2.encode('utf-8')
        assert_method = assert_content_crc64 if a == 'crc64' else assert_content_md5

        # Act
        blob.create_page_blob(5 * 1024)
        blob.upload_page(data1, offset=0, length=len(data1), validate_content=a, raw_request_hook=assert_method)
        blob.upload_page(data2, offset=len(data1), length=len(data2_encoded), encoding='utf-8', validate_content=a, raw_request_hook=assert_method)

        # Assert
        content = blob.download_blob(offset=0, length=len(data1) + len(data2_encoded))
        assert content.read() == data1 + data2_encoded
