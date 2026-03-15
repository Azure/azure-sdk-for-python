# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import pytest

from azure.core.exceptions import ResourceExistsError
from azure.storage.blob import BlobClient, BlobServiceClient, CustomerProvidedEncryptionKey
from azure.storage.blob._blob_client_helpers import _append_block_options, _clear_page_options

from devtools_testutils import recorded_by_proxy
from devtools_testutils.storage import StorageRecordedTestCase
from fake_credentials import CPK_KEY_HASH, CPK_KEY_VALUE
from settings.testcase import BlobPreparer


TEST_ENCRYPTION_KEY = CustomerProvidedEncryptionKey(key_value=CPK_KEY_VALUE, key_hash=CPK_KEY_HASH)


class TestStorageBlobClientHelperGaps(StorageRecordedTestCase):

    # --Helpers-----------------------------------------------------------------
    def _setup(self, storage_account_name, key):
        self.bsc = BlobServiceClient(self.account_url(storage_account_name, "blob"), credential=key.secret)
        self.container_name = self.get_resource_name('utcontainer')
        if self.is_live:
            try:
                self.bsc.create_container(self.container_name)
            except ResourceExistsError:
                pass

    def _create_page_blob(self, size=512, cpk=None):
        blob = self.bsc.get_blob_client(self.container_name, self.get_resource_name('pageblob'))
        blob.create_page_blob(size=size, cpk=cpk)
        return blob

    def _create_append_blob(self):
        blob = self.bsc.get_blob_client(self.container_name, self.get_resource_name('appendblob'))
        blob.create_append_blob()
        return blob

    # --Tests-------------------------------------------------------------------
    @BlobPreparer()
    def test_upload_pages_from_url_when_source_offset_is_none_raises_value_error(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        blob = BlobClient(
            self.account_url(storage_account_name, "blob"),
            container_name='container',
            blob_name='blob',
            credential=storage_account_key.secret)

        with pytest.raises(ValueError) as error:
            blob.upload_pages_from_url(
                "https://sourceaccount.blob.core.windows.net/source/sourceblob",
                offset=0,
                length=512,
                source_offset=None)

        assert str(error.value) == "source_offset must be an integer that aligns with 512 page size"

    @BlobPreparer()
    def test_clear_page_when_length_is_not_page_aligned_raises_value_error(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        blob = BlobClient(
            self.account_url(storage_account_name, "blob"),
            container_name='container',
            blob_name='blob',
            credential=storage_account_key.secret)

        with pytest.raises(ValueError) as error:
            blob.clear_page(offset=0, length=513)

        assert str(error.value) == "length must be an integer that aligns with 512 page size"

    def test_clear_page_when_cpk_is_provided_clears_encrypted_page_range(self):
        options = _clear_page_options(offset=0, length=512, cpk=TEST_ENCRYPTION_KEY)

        assert options['range'] == 'bytes=0-511'
        assert options['content_length'] == 0
        assert options['cpk_info'].encryption_key == CPK_KEY_VALUE
        assert options['cpk_info'].encryption_key_sha256 == CPK_KEY_HASH
        assert options['cpk_info'].encryption_algorithm == TEST_ENCRYPTION_KEY.algorithm

    def test_append_block_when_length_is_omitted_appends_entire_payload(self):
        options = _append_block_options(b'hello world')

        assert options['body'] == b'hello world'
        assert options['content_length'] == 11

    def test_append_block_when_length_is_zero_returns_empty_dict(self):
        assert _append_block_options(b'') == {}
