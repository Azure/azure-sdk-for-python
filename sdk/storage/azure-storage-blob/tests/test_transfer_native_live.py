# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint: disable=attribute-defined-outside-init

"""Live OAuth integration tests requiring the native transfer extension."""

import os
from io import BytesIO

import pytest

from devtools_testutils.storage import StorageRecordedTestCase
from settings.testcase import BlobPreparer

from azure.core.exceptions import ResourceExistsError
from azure.storage.blob import BlobServiceClient, ContentSettings
from azure.storage.blob._transfer_native import _is_native_available, NativeStorageStreamDownloader


SMALL_BLOB_SIZE = 1024 * 1024 + 17
LARGE_BLOB_SIZE = 65 * 1024 * 1024 + 17
BLOB_SIZES = [
    pytest.param(SMALL_BLOB_SIZE, id="single-shot"),
    pytest.param(LARGE_BLOB_SIZE, id="partitioned"),
]


@pytest.mark.live_test_only
class TestStorageNativeTransfer(StorageRecordedTestCase):
    @pytest.fixture(autouse=True)
    def require_native_transfer(self, caplog):
        if not self.is_live:
            pytest.skip("Native transfer integration tests are live only.")
        pytest.importorskip("azure.storage.extensions.transfer")
        if not _is_native_available():
            pytest.skip("The native transfer extension must be available and enabled.")
        caplog.set_level("INFO", logger="azure.storage.blob._transfer_native")

    def _setup(self, storage_account_name, request):
        self.bsc = BlobServiceClient(
            self.account_url(storage_account_name, "blob"),
            credential=self.get_credential(BlobServiceClient),
        )
        request.addfinalizer(self.bsc.close)
        self.container_name = self.get_resource_name("utnative")
        container = self.bsc.create_container(self.container_name)
        request.addfinalizer(container.delete_container)
        return container.get_blob_client(self.get_resource_name("blob"))

    @pytest.mark.parametrize("size", BLOB_SIZES)
    @BlobPreparer()
    def test_upload_blob_with_options(self, size, request, caplog, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")

        # Arrange
        blob = self._setup(storage_account_name, request)
        data = os.urandom(size)
        metadata = {"source": "native"}
        tags = {"transfer": "rust"}
        content_settings = ContentSettings(
            content_type="application/octet-stream",
            content_language="en",
            content_disposition="attachment",
            cache_control="no-cache",
        )

        # Act
        response = blob.upload_blob(
            data,
            metadata=metadata,
            tags=tags,
            content_settings=content_settings,
            max_concurrency=4,
        )

        # Assert
        assert "Used native Rust extension for blob upload." in caplog.text
        properties = blob.get_blob_properties()
        assert response["etag"] == properties.etag
        assert properties.size == size
        assert properties.metadata == metadata
        assert properties.content_settings.content_type == content_settings.content_type
        assert properties.content_settings.content_language == content_settings.content_language
        assert properties.content_settings.content_disposition == content_settings.content_disposition
        assert properties.content_settings.cache_control == content_settings.cache_control
        assert blob.get_blob_tags() == tags
        committed_blocks, _ = blob.get_block_list()
        if size == SMALL_BLOB_SIZE:
            assert len(committed_blocks) == 0
        else:
            assert len(committed_blocks) > 1
            assert sum(block.size for block in committed_blocks) == size
        downloader = blob.download_blob()
        assert isinstance(downloader, NativeStorageStreamDownloader)
        assert downloader.readall() == data

    @BlobPreparer()
    def test_upload_blob_overwrite(self, request, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")

        # Arrange
        blob = self._setup(storage_account_name, request)
        original_data = os.urandom(SMALL_BLOB_SIZE)
        replacement_data = os.urandom(SMALL_BLOB_SIZE + 1)
        blob.upload_blob(original_data)

        # Act
        with pytest.raises(ResourceExistsError):
            blob.upload_blob(replacement_data)
        assert blob.download_blob().readall() == original_data
        blob.upload_blob(replacement_data, overwrite=True)

        # Assert
        assert blob.download_blob().readall() == replacement_data

    @pytest.mark.parametrize("size", BLOB_SIZES)
    @BlobPreparer()
    def test_download_blob_readall(self, size, request, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")

        # Arrange
        blob = self._setup(storage_account_name, request)
        data = os.urandom(size)
        blob.upload_blob(data)

        # Act
        downloader = blob.download_blob(max_concurrency=4)

        # Assert
        assert isinstance(downloader, NativeStorageStreamDownloader)
        assert downloader.size == size
        assert downloader.readall() == data

    @pytest.mark.parametrize("size", BLOB_SIZES)
    @BlobPreparer()
    def test_download_blob_read(self, size, request, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")

        # Arrange
        blob = self._setup(storage_account_name, request)
        data = os.urandom(size)
        blob.upload_blob(data)

        # Act
        downloader = blob.download_blob(max_concurrency=4)

        # Assert
        assert isinstance(downloader, NativeStorageStreamDownloader)
        offset = 0
        while chunk := downloader.read(1024 * 1024 + 3):
            assert chunk == data[offset : offset + len(chunk)]
            offset += len(chunk)
        assert offset == size
        assert downloader.read(1) == b""

    @pytest.mark.parametrize("size", BLOB_SIZES)
    @BlobPreparer()
    def test_download_blob_readinto(self, size, request, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")

        # Arrange
        blob = self._setup(storage_account_name, request)
        data = os.urandom(size)
        blob.upload_blob(data)
        downloader = blob.download_blob(max_concurrency=4)
        assert isinstance(downloader, NativeStorageStreamDownloader)

        # Act
        with BytesIO() as stream:
            bytes_written = downloader.readinto(stream)

            # Assert
            assert bytes_written == size
            assert stream.getvalue() == data

    @pytest.mark.parametrize("size", BLOB_SIZES)
    @BlobPreparer()
    def test_download_blob_chunks(self, size, request, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")

        # Arrange
        blob = self._setup(storage_account_name, request)
        data = os.urandom(size)
        blob.upload_blob(data)
        downloader = blob.download_blob(max_concurrency=4)
        assert isinstance(downloader, NativeStorageStreamDownloader)

        # Act
        chunks = list(downloader.chunks())

        # Assert
        assert b"".join(chunks) == data
        if size == SMALL_BLOB_SIZE:
            assert len(chunks) == 1
        else:
            assert len(chunks) > 1

    @BlobPreparer()
    def test_download_blob_range(self, request, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")

        # Arrange
        blob = self._setup(storage_account_name, request)
        data = os.urandom(LARGE_BLOB_SIZE)
        blob.upload_blob(data)
        offset = 1024 * 1024 + 3
        length = 8 * 1024 * 1024 + 17

        # Act
        downloader = blob.download_blob(offset=offset, length=length, max_concurrency=4)

        # Assert
        assert isinstance(downloader, NativeStorageStreamDownloader)
        assert downloader.size == length
        assert downloader.readall() == data[offset : offset + length]
