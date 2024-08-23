# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from io import BytesIO

import pytest
from azure.storage.blob import (
    BlobBlock,
    BlobClient,
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

from encryption_test_helper import KeyWrapper


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


def assert_structured_message_get(response):
    assert response.http_request.headers.get('x-ms-structured-body') is not None
    assert response.http_response.headers.get('x-ms-structured-body') is not None


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
    bsc: BlobServiceClient = None
    container: ContainerClient = None

    def _setup(self, account_name, account_key):
        credential = {'account_name': account_name, 'account_key': account_key}
        self.bsc = BlobServiceClient(self.account_url(account_name, "blob"), credential=credential, logging_enable=True)
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

    @BlobPreparer()
    def test_encryption_blocked_crc64(self, **kwargs):
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
            blob.upload_blob(b'123', validate_content='crc64')

    @BlobPreparer()
    @pytest.mark.parametrize('a', [BlobType.BLOCKBLOB, BlobType.PAGEBLOB, BlobType.APPENDBLOB])  # a: blob_type
    @pytest.mark.parametrize('b', [True, 'md5', 'crc64'])  # b: validate_content
    @GenericTestProxyParametrize2()
    @recorded_by_proxy
    def test_upload_blob(self, a, b, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
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
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
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
    @pytest.mark.parametrize('a', [True, 'md5', 'crc64'])  # a: validate_content
    @GenericTestProxyParametrize1()
    @recorded_by_proxy
    def test_stage_block(self, a, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        blob = self.container.get_blob_client(self._get_blob_reference())
        data1 = b'abc' * 512
        data2 = '你好世界' * 10
        assert_method = assert_structured_message if a == 'crc64' else assert_content_md5

        # Act
        blob.stage_block('1', data1, validate_content=a, raw_request_hook=assert_method)
        blob.stage_block('2', data2, encoding='utf-8-sig', validate_content=a, raw_request_hook=assert_method)
        blob.commit_block_list([BlobBlock('1'), BlobBlock('2')])

        # Assert
        content = blob.download_blob()
        assert content.readall() == data1 + data2.encode('utf-8-sig')

    @BlobPreparer()
    @pytest.mark.parametrize('a', [True, 'md5', 'crc64'])  # a: validate_content
    @pytest.mark.live_test_only
    def test_stage_block_large(self, a, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        blob = self.container.get_blob_client(self._get_blob_reference())
        data1 = b'abcde' * 1024 * 1024  # 5 MiB
        data2 = b'12345' * 1024 * 1024 + b'abcdefg'  # 10 MiB + 7
        assert_method = assert_structured_message if a == 'crc64' else assert_content_md5

        # Act
        blob.stage_block('1', data1, validate_content=a, raw_request_hook=assert_method)
        blob.stage_block('2', data2, encoding='utf-8-sig', validate_content=a, raw_request_hook=assert_method)
        blob.commit_block_list([BlobBlock('1'), BlobBlock('2')])

        # Assert
        content = blob.download_blob()
        assert content.readall() == data1 + data2

    @BlobPreparer()
    @pytest.mark.parametrize('a', [True, 'md5', 'crc64'])  # a: validate_content
    @GenericTestProxyParametrize1()
    @recorded_by_proxy
    def test_stage_block_data_types(self, a, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        blob = self.container.get_blob_client(self._get_blob_reference())

        content = b'abcde' * 1030  # 5 KiB + 30
        byte_io = BytesIO(content)

        def generator():
            for i in range(0, len(content), 500):
                yield content[i: i + 500]

        data_list = [byte_io, generator()]
        assert_method = assert_structured_message if a == 'crc64' else assert_content_md5

        blocks = []
        for j in range(len(data_list)):
            blob.stage_block(str(j), data_list[j], validate_content=a, raw_request_hook=assert_method)
            blocks.append(BlobBlock(str(j)))
        blob.commit_block_list(blocks)

        # Assert
        result = blob.download_blob()
        assert result.readall() == content * 2

    @BlobPreparer()
    @pytest.mark.parametrize('a', [True, 'md5', 'crc64'])  # a: validate_content
    @GenericTestProxyParametrize1()
    @recorded_by_proxy
    def test_append_block(self, a, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        blob = self.container.get_blob_client(self._get_blob_reference())
        data1 = b'abc' * 512
        data2 = '你好世界' * 10
        assert_method = assert_structured_message if a == 'crc64' else assert_content_md5

        # Act
        blob.create_append_blob()
        blob.append_block(data1, validate_content=a, raw_request_hook=assert_method)
        blob.append_block(data2, encoding='utf-8-sig', validate_content=a, raw_request_hook=assert_method)

        # Assert
        content = blob.download_blob()
        assert content.readall() == data1 + data2.encode('utf-8-sig')

    @BlobPreparer()
    @pytest.mark.parametrize('a', [True, 'md5', 'crc64'])  # a: validate_content
    @pytest.mark.live_test_only
    def test_append_block_large(self, a, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        blob = self.container.get_blob_client(self._get_blob_reference())
        data1 = b'abcde' * 1024 * 1024  # 5 MiB
        data2 = b'12345' * 1024 * 1024 + b'abcdefg'  # 10 MiB + 7
        assert_method = assert_structured_message if a == 'crc64' else assert_content_md5

        # Act
        blob.create_append_blob()
        blob.append_block(data1, validate_content=a, raw_request_hook=assert_method)
        blob.append_block(data2, encoding='utf-8-sig', validate_content=a, raw_request_hook=assert_method)

        # Assert
        content = blob.download_blob()
        assert content.readall() == data1 + data2

    @BlobPreparer()
    @pytest.mark.parametrize('a', [True, 'md5', 'crc64'])  # a: validate_content
    @GenericTestProxyParametrize1()
    @recorded_by_proxy
    def test_upload_page(self, a, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        blob = self.container.get_blob_client(self._get_blob_reference())
        data1 = b'abc' * 512
        data2 = "你好世界abcd" * 32
        data2_encoded_len = 512
        assert_method = assert_content_crc64 if a == 'crc64' else assert_content_md5

        # Act
        blob.create_page_blob(5 * 1024)
        blob.upload_page(data1, offset=0, length=len(data1), validate_content=a, raw_request_hook=assert_method)
        blob.upload_page(data2, offset=len(data1), length=data2_encoded_len, encoding='utf-8', validate_content=a, raw_request_hook=assert_method)

        # Assert
        content = blob.download_blob(offset=0, length=len(data1) + data2_encoded_len)
        assert content.readall() == data1 + data2.encode('utf-8')

    @BlobPreparer()
    @pytest.mark.parametrize('a', [True, 'md5', 'crc64'])  # a: validate_content
    @GenericTestProxyParametrize1()
    @recorded_by_proxy
    def test_get_blob(self, a, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        blob = self.container.get_blob_client(self._get_blob_reference())
        data = b'abc' * 512
        blob.upload_blob(data, overwrite=True)
        assert_method = assert_structured_message_get if a == 'crc64' else assert_content_md5_get

        # Act
        downloader = blob.download_blob(validate_content=a, raw_response_hook=assert_method)
        content = downloader.read()

        stream = BytesIO()
        downloader = blob.download_blob(validate_content=a, raw_response_hook=assert_method)
        downloader.readinto(stream)
        stream.seek(0)

        # Assert
        assert content == data
        assert stream.read() == data

    @BlobPreparer()
    @pytest.mark.parametrize('a', [True, 'md5', 'crc64'])  # a: validate_content
    @GenericTestProxyParametrize1()
    @recorded_by_proxy
    def test_get_blob_chunks(self, a, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        self.container._config.max_single_get_size = 512
        self.container._config.max_chunk_get_size = 512
        blob = self.container.get_blob_client(self._get_blob_reference())
        data = b'abc' * 512 + b'abcde'
        blob.upload_blob(data, overwrite=True)
        assert_method = assert_structured_message_get if a == 'crc64' else assert_content_md5_get

        # Act
        downloader = blob.download_blob(validate_content=a, raw_response_hook=assert_method)
        content = downloader.read()

        stream = BytesIO()
        downloader = blob.download_blob(validate_content=a, raw_response_hook=assert_method)
        downloader.readinto(stream)
        stream.seek(0)

        read_content = b''
        downloader = blob.download_blob(validate_content=a, raw_response_hook=assert_method)
        for _ in range(len(data) // 100 + 1):
            read_content += downloader.read(100)
            print(len(read_content))

        # Assert
        assert content == data
        assert stream.read() == data
        assert read_content == data

    @BlobPreparer()
    @pytest.mark.parametrize('a', [True, 'md5', 'crc64'])  # a: validate_content
    @GenericTestProxyParametrize1()
    @recorded_by_proxy
    def test_get_blob_chunks_partial(self, a, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        self.container._config.max_single_get_size = 512
        self.container._config.max_chunk_get_size = 512
        blob = self.container.get_blob_client(self._get_blob_reference())
        data = b'abc' * 512 + b'abcde'
        blob.upload_blob(data, overwrite=True)
        assert_method = assert_structured_message_get if a == 'crc64' else assert_content_md5_get

        # Act
        downloader = blob.download_blob(offset=10, length=1000, validate_content=a, raw_response_hook=assert_method)
        content = downloader.read()

        stream = BytesIO()
        downloader = blob.download_blob(offset=10, length=1000, validate_content=a, raw_response_hook=assert_method)
        downloader.readinto(stream)
        stream.seek(0)

        # Assert
        assert content == data[10:1010]
        assert stream.read() == data[10:1010]

    @BlobPreparer()
    @pytest.mark.live_test_only
    def test_get_blob_large_chunks(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        blob = self.container.get_blob_client(self._get_blob_reference())
        # The service will use 4 MiB for structured message chunk size, so make chunk size larger
        self.container._config.max_chunk_get_size = 10 * 1024 * 1024
        data = b'abcde' * 30 * 1024 * 1024 + b'abcde'  # 150 MiB + 5
        blob.upload_blob(data, overwrite=True, max_concurrency=5)

        # Act
        downloader = blob.download_blob(validate_content='crc64', max_concurrency=3)
        content = downloader.read()

        # Assert
        assert content == data
