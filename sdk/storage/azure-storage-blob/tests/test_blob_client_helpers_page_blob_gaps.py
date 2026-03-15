# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import pytest
from azure.core.exceptions import HttpResponseError
from azure.storage.blob import BlobClient, BlobServiceClient, CustomerProvidedEncryptionKey
from azure.storage.blob._blob_client_helpers import _resize_blob_options

from devtools_testutils import recorded_by_proxy
from devtools_testutils.storage import StorageRecordedTestCase
from fake_credentials import CPK_KEY_HASH, CPK_KEY_VALUE
from settings.testcase import BlobPreparer


TEST_ENCRYPTION_KEY = CustomerProvidedEncryptionKey(key_value=CPK_KEY_VALUE, key_hash=CPK_KEY_HASH)


class TestStorageBlobClientHelperPageBlobGaps(StorageRecordedTestCase):

    def _setup(self, storage_account_name, key):
        self.bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=key.secret)
        self.container_name = self.get_resource_name('utcontainer')
        if self.is_live:
            try:
                self.bsc.create_container(self.container_name)
            except:
                pass

    def _get_blob_client(self):
        return self.bsc.get_blob_client(self.container_name, self.get_resource_name('blob'))

    def test_set_sequence_number_when_action_is_none_raises_value_error(self):
        blob_client = BlobClient(
            "https://foo.blob.core.windows.net/account",
            container_name='container',
            blob_name='blob',
            credential='fake_key')

        with pytest.raises(ValueError) as error:
            blob_client.set_sequence_number(None)

        assert str(error.value) == "A sequence number action must be specified"

    def test_resize_blob_when_size_is_none_raises_value_error(self):
        blob_client = BlobClient(
            "https://foo.blob.core.windows.net/account",
            container_name='container',
            blob_name='blob',
            credential='fake_key')

        with pytest.raises(ValueError) as error:
            blob_client.resize_blob(None)

        assert str(error.value) == "A content length must be specified for a Page Blob."

    def test_resize_blob_when_cpk_is_provided_resizes_encrypted_page_blob(self):
        options = _resize_blob_options(1024, cpk=TEST_ENCRYPTION_KEY)

        assert options['blob_content_length'] == 1024
        assert options['cpk_info'].encryption_key == CPK_KEY_VALUE
        assert options['cpk_info'].encryption_key_sha256 == CPK_KEY_HASH
        assert options['cpk_info'].encryption_algorithm == TEST_ENCRYPTION_KEY.algorithm

    def test_upload_page_when_offset_is_not_page_aligned_raises_value_error(self):
        blob_client = BlobClient(
            "https://foo.blob.core.windows.net/account",
            container_name='container',
            blob_name='blob',
            credential='fake_key')

        with pytest.raises(ValueError) as error:
            blob_client.upload_page(b'a' * 512, offset=1, length=512)

        assert str(error.value) == "offset must be an integer that aligns with 512 page size"

    def test_upload_pages_from_url_when_length_is_not_page_aligned_raises_value_error(self):
        blob_client = BlobClient(
            "https://foo.blob.core.windows.net/account",
            container_name='container',
            blob_name='blob',
            credential='fake_key')

        with pytest.raises(ValueError) as error:
            blob_client.upload_pages_from_url(
                "https://src.blob.core.windows.net/container/blob",
                offset=0,
                length=513,
                source_offset=0)

        assert str(error.value) == "length must be an integer that aligns with 512 page size"
