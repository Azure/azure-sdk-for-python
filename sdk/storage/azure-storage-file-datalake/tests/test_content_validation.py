# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from io import BytesIO

import pytest
from azure.storage.filedatalake import (
    DataLakeServiceClient
)

from devtools_testutils import recorded_by_proxy
from devtools_testutils.storage import GenericTestProxyParametrize1, StorageRecordedTestCase
from settings.testcase import DataLakePreparer


def assert_content_md5(request):
    if request.http_request.query.get('action') == 'append':
        assert request.http_request.headers.get('Content-MD5') is not None


def assert_content_md5_get(response):
    assert response.http_request.headers.get('x-ms-range-get-content-md5') == 'true'
    assert response.http_response.headers.get('Content-MD5') is not None


def assert_content_crc64(request):
    if request.http_request.query.get('action') == 'append':
        assert request.http_request.headers.get('x-ms-content-crc64') is not None


def assert_structured_message(request):
    if request.http_request.query.get('action') == 'append':
        assert request.http_request.headers.get('x-ms-structured-body') is not None


def assert_structured_message_get(response):
    assert response.http_request.headers.get('x-ms-structured-body') is not None
    assert response.http_response.headers.get('x-ms-structured-body') is not None


class TestStorageContentValidation(StorageRecordedTestCase):
    def _setup(self, account_name, account_key):
        credential = {"account_name": account_name, "account_key": account_key}
        self.dsc = DataLakeServiceClient(self.account_url(account_name, "dfs"), credential=credential, logging_enable=True)
        self.file_system = self.dsc.get_file_system_client(self.get_resource_name('filesystem'))
        self.file_system.create_file_system()

    def teardown_method(self, _):
        if self.file_system:
            try:
                self.file_system.delete_file_system()
            except:
                pass

    def _get_file_reference(self):
        return self.get_resource_name('file')

    @DataLakePreparer()
    @pytest.mark.parametrize('a', [True, 'md5', 'crc64'])  # a: validate_content
    @GenericTestProxyParametrize1()
    @recorded_by_proxy
    def test_upload_data(self, a, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        self._setup(datalake_storage_account_name, datalake_storage_account_key)
        file = self.file_system.get_file_client(self._get_file_reference())
        data = b'abc' * 512
        assert_method = assert_content_crc64 if a == 'crc64' else assert_content_md5

        # Act
        file.upload_data(data, overwrite=True, validate_content=a, raw_request_hook=assert_method)

        # Assert
        content = file.download_file()
        assert content.read() == data

    @DataLakePreparer()
    @pytest.mark.parametrize('a', [True, 'md5', 'crc64'])  # a: validate_content
    @GenericTestProxyParametrize1()
    @recorded_by_proxy
    def test_upload_data_chunks(self, a, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        self._setup(datalake_storage_account_name, datalake_storage_account_key)
        file = self.file_system.get_file_client(self._get_file_reference())
        data = b'abcde' * 512
        assert_method = assert_content_crc64 if a == 'crc64' else assert_content_md5

        # Act
        file.upload_data(data, overwrite=True, validate_content=a, chunk_size=1024, raw_request_hook=assert_method)

        # Assert
        content = file.download_file()
        assert content.read() == data

    @DataLakePreparer()
    @pytest.mark.parametrize('a', [True, 'md5', 'crc64'])  # a: validate_content
    @GenericTestProxyParametrize1()
    @recorded_by_proxy
    def test_upload_data_substream(self, a, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        self._setup(datalake_storage_account_name, datalake_storage_account_key)
        self.file_system._config.min_large_chunk_upload_threshold = 1  # Set less than chunk size to enable substream
        file = self.file_system.get_file_client(self._get_file_reference())
        assert_method = assert_structured_message if a == 'crc64' else assert_content_md5

        data = b'abc' * 512 + b'abcde'
        io = BytesIO(data)

        # Act
        file.upload_data(io, overwrite=True, validate_content=a, chunk_size=512, raw_request_hook=assert_method)

        # Assert
        content = file.download_file()
        assert content.read() == data

    @DataLakePreparer()
    @pytest.mark.parametrize('a', [True, 'md5', 'crc64'])  # a: validate_content
    @GenericTestProxyParametrize1()
    @recorded_by_proxy
    def test_append_data(self, a, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        self._setup(datalake_storage_account_name, datalake_storage_account_key)
        file = self.file_system.get_file_client(self._get_file_reference())
        data1 = b'abcde' * 512
        data2 = '你好世界' * 10
        encoded = data2.encode('utf-8')
        assert_method = assert_structured_message if a == 'crc64' else assert_content_md5

        # Act
        file.create_file()
        file.append_data(data1, 0, validate_content=a, raw_request_hook=assert_method)
        file.append_data(data2, len(data1), encoding='utf-8', validate_content=a, raw_request_hook=assert_method)
        file.flush_data(len(data1) + len(encoded))

        # Assert
        content = file.download_file()
        assert content.readall() == data1 + encoded

    @DataLakePreparer()
    @pytest.mark.parametrize('a', [True, 'md5', 'crc64'])  # a: validate_content
    @GenericTestProxyParametrize1()
    @recorded_by_proxy
    def test_append_data_data_types(self, a, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        self._setup(datalake_storage_account_name, datalake_storage_account_key)
        file = self.file_system.get_file_client(self._get_file_reference())
        assert_method = assert_structured_message if a == 'crc64' else assert_content_md5

        content = b'abcde' * 1030  # 5 KiB + 30
        byte_io = BytesIO(content)

        def generator():
            for i in range(0, len(content), 500):
                yield content[i: i + 500]

        data_list = [byte_io, generator()]

        # Act
        offset = 0
        file.create_file()
        for j in range(len(data_list)):
            file.append_data(data_list[j], offset, validate_content=a, raw_request_hook=assert_method)
            offset += len(content)
            file.flush_data(offset)

        # Assert
        result = file.download_file()
        assert result.readall() == content * len(data_list)

    @DataLakePreparer()
    @pytest.mark.parametrize('a', [True, 'md5', 'crc64'])  # a: validate_content
    @GenericTestProxyParametrize1()
    @recorded_by_proxy
    def test_download_file(self, a, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        self._setup(datalake_storage_account_name, datalake_storage_account_key)
        file = self.file_system.get_file_client(self._get_file_reference())
        data = b'abc' * 512
        file.upload_data(data, overwrite=True)
        assert_method = assert_structured_message_get if a == 'crc64' else assert_content_md5_get

        # Act
        downloader = file.download_file(validate_content=a, raw_response_hook=assert_method)
        content = downloader.read()

        # Assert
        assert content == data

    @DataLakePreparer()
    @pytest.mark.parametrize('a', [True, 'md5', 'crc64'])  # a: validate_content
    @GenericTestProxyParametrize1()
    @recorded_by_proxy
    def test_download_file_chunks(self, a, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        self._setup(datalake_storage_account_name, datalake_storage_account_key)
        self.file_system._config.max_single_get_size = 512
        self.file_system._config.max_chunk_get_size = 512
        file = self.file_system.get_file_client(self._get_file_reference())
        data = b'abc' * 512 + b'abcde'
        file.upload_data(data, overwrite=True)
        assert_method = assert_structured_message_get if a == 'crc64' else assert_content_md5_get

        # Act
        downloader = file.download_file(validate_content=a, raw_response_hook=assert_method)
        content = downloader.read()

        downloader2 = file.download_file(offset=10, length=1000, validate_content=a, raw_response_hook=assert_method)
        content2 = downloader2.read()

        # Assert
        assert content == data
        assert content2 == data[10:1010]

    @DataLakePreparer()
    @pytest.mark.live_test_only
    def test_download_file_large_chunks(self, **kwargs):
        datalake_storage_account_name = kwargs.pop("datalake_storage_account_name")
        datalake_storage_account_key = kwargs.pop("datalake_storage_account_key")

        self._setup(datalake_storage_account_name, datalake_storage_account_key)
        file = self.file_system.get_file_client(self._get_file_reference())
        # The service will use 4 MiB for structured message chunk size, so make chunk size larger
        self.file_system._config.max_chunk_get_size = 10 * 1024 * 1024
        data = b'abcde' * 30 * 1024 * 1024 + b'abcde'  # 150 MiB + 5
        file.upload_data(data, overwrite=True, max_concurrency=5)

        # Act
        downloader = file.download_file(validate_content='crc64', max_concurrency=3)
        content = downloader.read()

        # Assert
        assert content == data
