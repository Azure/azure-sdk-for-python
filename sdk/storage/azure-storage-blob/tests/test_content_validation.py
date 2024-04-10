# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from io import BytesIO

import pytest
from azure.storage.blob import (
    BlobClient,
    BlobServiceClient,
    ContainerClient
)
from devtools_testutils import recorded_by_proxy
from devtools_testutils.storage import StorageRecordedTestCase
from settings.testcase import BlobPreparer

from encryption_test_helper import KeyWrapper


def assert_content_md5(request):
    if 'comp=blocklist' not in request.http_request.url:
        assert request.http_request.headers['Content-MD5']


def assert_content_crc64(request):
    if 'comp=blocklist' not in request.http_request.url:
        assert request.http_request.headers['x-ms-content-crc64']


class TestStorageContentValidation(StorageRecordedTestCase):
    bsc: BlobServiceClient = None
    container: ContainerClient = None

    def _setup(self, account_name, account_key):
        self.bsc = BlobServiceClient(self.account_url(account_name, "blob"), credential=account_key, logging_enable=True)
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
    @recorded_by_proxy
    def test_upload_blob_legacy_bool(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        blob = self.container.get_blob_client(self._get_blob_reference())
        data = b'abc' * 512

        # Act
        response = blob.upload_blob(data, validate_content=True, raw_request_hook=assert_content_md5)

        # Assert
        assert response

    @BlobPreparer()
    @recorded_by_proxy
    def test_upload_blob_legacy_bool_chunks(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        blob = self.container.get_blob_client(self._get_blob_reference())
        self.container._config.max_single_put_size = 512
        self.container._config.max_block_size = 512
        data = b'abc' * 512

        # Act
        response = blob.upload_blob(data, validate_content=True, raw_request_hook=assert_content_md5)

        # Assert
        assert response

    @BlobPreparer()
    @recorded_by_proxy
    def test_upload_blob_md5(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        blob = self.container.get_blob_client(self._get_blob_reference())
        data = b'abc' * 512

        # Act
        response = blob.upload_blob(data, validate_content='md5', raw_request_hook=assert_content_md5)

        # Assert
        assert response

    @BlobPreparer()
    @recorded_by_proxy
    def test_upload_blob_md5_chunks(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        self.container._config.max_single_put_size = 512
        self.container._config.max_block_size = 512
        blob = self.container.get_blob_client(self._get_blob_reference())
        data = b'abc' * 512

        # Act
        response = blob.upload_blob(data, validate_content='md5', raw_request_hook=assert_content_md5)

        # Assert
        assert response

    @BlobPreparer()
    @recorded_by_proxy
    def test_upload_blob_crc64(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        blob = self.container.get_blob_client(self._get_blob_reference())

        # Test different data types
        byte_data = b'abc' * 512
        str_data = "你好世界" * 10
        stream = BytesIO(byte_data)

        # Act
        resp1 = blob.upload_blob(byte_data, overwrite=True, validate_content='crc64',
                                 raw_request_hook=assert_content_crc64)
        resp2 = blob.upload_blob(str_data, overwrite=True, validate_content='crc64',
                                 raw_request_hook=assert_content_crc64)
        resp3 = blob.upload_blob(stream, overwrite=True, validate_content='crc64',
                                 raw_request_hook=assert_content_crc64)

        # Assert
        assert resp1
        assert resp2
        assert resp3

    @BlobPreparer()
    @recorded_by_proxy
    def test_upload_blob_crc64_chunks(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        self._setup(storage_account_name, storage_account_key)
        self.container._config.max_single_put_size = 512
        self.container._config.max_block_size = 512
        blob = self.container.get_blob_client(self._get_blob_reference())

        # Test different data types
        byte_data = b'abc' * 512
        str_data = "你好世界" * 10
        stream = BytesIO(byte_data)

        # Act
        resp1 = blob.upload_blob(byte_data, overwrite=True, validate_content='crc64',
                                 raw_request_hook=assert_content_crc64)
        resp2 = blob.upload_blob(str_data, overwrite=True, validate_content='crc64',
                                 raw_request_hook=assert_content_crc64)
        resp3 = blob.upload_blob(stream, overwrite=True, validate_content='crc64',
                                 raw_request_hook=assert_content_crc64)

        # Assert
        assert resp1
        assert resp2
        assert resp3
