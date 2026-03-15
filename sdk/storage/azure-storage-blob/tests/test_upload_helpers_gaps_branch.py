# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from io import BytesIO
from unittest import mock

import pytest
from azure.core.exceptions import HttpResponseError, ResourceExistsError, ResourceModifiedError
from azure.storage.blob import BlobClient, BlobServiceClient, BlobType, PremiumPageBlobTier, StorageErrorCode

from devtools_testutils.storage import StorageRecordedTestCase
from settings.testcase import BlobPreparer
from test_helpers import MockLegacyTransport


class TestUploadHelpersGaps(StorageRecordedTestCase):
    def _setup(self, storage_account_name, key, **kwargs):
        self.bsc = BlobServiceClient(
            self.account_url(storage_account_name, "blob"),
            credential=key.secret,
            **kwargs
        )
        self.container_name = self.get_resource_name('utcontainer')
        if self.is_live:
            try:
                self.bsc.create_container(self.container_name)
            except ResourceExistsError:
                pass

    def _get_blob_client(self, blob_name=None):
        return self.bsc.get_blob_client(self.container_name, blob_name or self.get_resource_name('blob'))

    @BlobPreparer()
    def test_upload_block_blob_when_stream_is_seekable_uses_substream_blocks(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        blob_client = BlobClient(
            self.account_url(storage_account_name, "blob"),
            container_name='container',
            blob_name='blob',
            credential=storage_account_key.secret,
            transport=MockLegacyTransport(),
            retry_total=0,
            max_single_put_size=4,
            max_block_size=4,
            min_large_block_upload_threshold=4
        )
        expected = {'etag': 'etag'}

        # Tests defensive branch — requires mock.
        with mock.patch(
            'azure.storage.blob._upload_helpers.upload_substream_blocks',
            return_value=['block1', 'block2']
        ) as substream_upload, mock.patch(
            'azure.storage.blob._upload_helpers.upload_data_chunks'
        ) as data_chunks_upload, mock.patch.object(
            blob_client._client.block_blob,
            'commit_block_list',
            return_value=expected
        ):
            response = blob_client.upload_blob(BytesIO(b'abcdefgh'), overwrite=True, length=8)

        assert response == expected
        assert substream_upload.call_count == 1
        assert data_chunks_upload.call_count == 0

    @BlobPreparer()
    def test_upload_block_blob_when_v2_encryption_metadata_has_no_cek_raises_value_error(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        blob_client = BlobClient(
            self.account_url(storage_account_name, "blob"),
            container_name='container',
            blob_name='blob',
            credential=storage_account_key.secret,
            transport=MockLegacyTransport(),
            retry_total=0,
            max_single_put_size=4,
            max_block_size=4,
            min_large_block_upload_threshold=4,
            require_encryption=True,
            encryption_version='2.0',
            key_encryption_key=object()
        )

        # Tests defensive branch — requires mock.
        with mock.patch(
            'azure.storage.blob._upload_helpers.generate_blob_encryption_data',
            return_value=(None, b'iv', 'metadata')
        ):
            with pytest.raises(ValueError) as exc:
                blob_client.upload_blob(BytesIO(b'abcdefgh'), overwrite=True, length=8)

        assert str(exc.value) == "Generate encryption metadata failed. 'cek' is None."

    @BlobPreparer()
    def test_upload_block_blob_when_overwrite_false_on_existing_blob_raises_resource_exists_error(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        blob = BlobClient(
            self.account_url(storage_account_name, "blob"),
            container_name='container',
            blob_name='blob',
            credential=storage_account_key.secret,
            transport=MockLegacyTransport(),
            retry_total=0,
            max_single_put_size=4,
            max_block_size=4,
            min_large_block_upload_threshold=4
        )
        http_error = HttpResponseError(message='condition not met', response=mock.Mock())
        modified_error = ResourceModifiedError(
            message='The condition specified using HTTP conditional header(s) is not met. ConditionNotMet',
            response=mock.Mock()
        )

        with mock.patch.object(blob._client.block_blob, 'upload', side_effect=http_error), mock.patch(
            'azure.storage.blob._upload_helpers.process_storage_error',
            side_effect=modified_error
        ):
            with pytest.raises(ResourceExistsError) as exc:
                blob.upload_blob(b'abcd', overwrite=False, length=4)

        assert exc.value.error_code == StorageErrorCode.blob_already_exists
        assert "The specified blob already exists." in str(exc.value)

    @BlobPreparer()
    def test_upload_page_blob_when_length_is_negative_raises_value_error(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        blob = BlobClient(
            self.account_url(storage_account_name, "blob"),
            container_name='container',
            blob_name='blob',
            credential=storage_account_key.secret,
            transport=MockLegacyTransport(),
            retry_total=0,
            max_page_size=512
        )

        with pytest.raises(ValueError) as exc:
            blob.upload_blob(b'a' * 512, blob_type=BlobType.PAGEBLOB, overwrite=True, length=-1)

        assert str(exc.value) == "A content length must be specified for a Page Blob."

    @BlobPreparer()
    def test_upload_page_blob_when_premium_tier_is_string_sets_page_blob_tier(self, **kwargs):
        premium_storage_account_name = kwargs.pop("premium_storage_account_name")
        premium_storage_account_key = kwargs.pop("premium_storage_account_key")

        blob = BlobClient(
            self.account_url(premium_storage_account_name, "blob"),
            container_name='container',
            blob_name='blob',
            credential=premium_storage_account_key.secret,
            transport=MockLegacyTransport(),
            retry_total=0,
            max_page_size=512
        )
        expected = {'etag': 'etag'}

        with mock.patch.object(blob._client.page_blob, 'create', return_value={'etag': 'etag'}) as create_page_blob, mock.patch(
            'azure.storage.blob._upload_helpers.upload_data_chunks',
            return_value=expected
        ) as upload_chunks:
            response = blob.upload_blob(
                b'a' * 512,
                blob_type=BlobType.PAGEBLOB,
                overwrite=True,
                length=512,
                premium_page_blob_tier='P4'
            )

        assert response == expected
        assert create_page_blob.call_count == 1
        assert create_page_blob.call_args.kwargs['tier'] == PremiumPageBlobTier.P4.value
        assert upload_chunks.call_count == 1
