# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import pytest
from unittest import mock

from azure.core.exceptions import HttpResponseError, ResourceNotFoundError
from azure.storage.blob import BlobBlock, BlobClient, CustomerProvidedEncryptionKey, PremiumPageBlobTier

from devtools_testutils.storage import StorageRecordedTestCase
from settings.testcase import BlobPreparer
from fake_credentials import CPK_KEY_HASH, CPK_KEY_VALUE


TEST_ENCRYPTION_KEY = CustomerProvidedEncryptionKey(key_value=CPK_KEY_VALUE, key_hash=CPK_KEY_HASH)


class TestStorageBlobClientGapPageBlobBranches(StorageRecordedTestCase):

    @BlobPreparer()
    def test_commit_block_list_when_http_and_cpk_raises_value_error(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        blob_client = BlobClient(
            self.account_url(storage_account_name, "blob").replace("https", "http"),
            container_name='container',
            blob_name='blob',
            credential=storage_account_key.secret,
        )

        with pytest.raises(ValueError) as error:
            blob_client.commit_block_list([BlobBlock(block_id='1')], cpk=TEST_ENCRYPTION_KEY)

        assert str(error.value) == "Customer provided encryption key must be used over HTTPS."

    @BlobPreparer()
    def test_set_premium_page_blob_tier_when_tier_is_none_raises_value_error(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        blob_client = BlobClient(
            self.account_url(storage_account_name, "blob"),
            container_name='container',
            blob_name='blob',
            credential=storage_account_key.secret,
        )

        with pytest.raises(ValueError) as error:
            blob_client.set_premium_page_blob_tier(None)

        assert str(error.value) == "A PremiumPageBlobTier must be specified"

    @BlobPreparer()
    def test_set_premium_page_blob_tier_when_generated_client_raises_http_error_calls_error_processor(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        blob_client = BlobClient(
            self.account_url(storage_account_name, "blob"),
            container_name='container',
            blob_name='blob',
            credential=storage_account_key.secret,
        )

        # Tests defensive branch — requires mock.
        with mock.patch("azure.storage.blob._blob_client.process_storage_error") as error_handler:
            blob_client._client.blob.set_tier = mock.Mock(side_effect=HttpResponseError(message="boom"))

            result = blob_client.set_premium_page_blob_tier(PremiumPageBlobTier.P4)

        assert result is None
        error_handler.assert_called_once()
        assert isinstance(error_handler.call_args[0][0], HttpResponseError)
        assert str(error_handler.call_args[0][0]) == "boom"

    @BlobPreparer()
    def test_set_premium_page_blob_tier_when_error_processor_raises_processed_error(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        blob_client = BlobClient(
            self.account_url(storage_account_name, "blob"),
            container_name='container',
            blob_name='blob',
            credential=storage_account_key.secret,
        )

        # Tests defensive branch — requires mock.
        with mock.patch(
            "azure.storage.blob._blob_client.process_storage_error",
            side_effect=ResourceNotFoundError("processed"),
        ):
            blob_client._client.blob.set_tier = mock.Mock(side_effect=HttpResponseError(message="boom"))

            with pytest.raises(ResourceNotFoundError) as error:
                blob_client.set_premium_page_blob_tier(PremiumPageBlobTier.P4)

        assert str(error.value) == "processed"

    @BlobPreparer()
    def test_get_page_range_diff_for_managed_disk_when_generated_client_raises_http_error_raises_processed_error(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        blob_client = BlobClient(
            self.account_url(storage_account_name, "blob"),
            container_name='container',
            blob_name='blob',
            credential=storage_account_key.secret,
        )

        # Tests defensive branch — requires mock.
        with mock.patch(
            "azure.storage.blob._blob_client.process_storage_error",
            side_effect=ResourceNotFoundError("processed"),
        ):
            blob_client._client.page_blob.get_page_ranges_diff = mock.Mock(side_effect=HttpResponseError(message="boom"))

            with pytest.raises(ResourceNotFoundError) as error:
                blob_client.get_page_range_diff_for_managed_disk("https://example.com/snapshot")

        assert str(error.value) == "processed"
