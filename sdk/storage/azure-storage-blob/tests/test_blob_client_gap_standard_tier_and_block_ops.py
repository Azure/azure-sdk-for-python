# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import pytest
from unittest import mock

from azure.core.exceptions import HttpResponseError, ResourceNotFoundError
from azure.storage.blob import BlobClient, CustomerProvidedEncryptionKey, StandardBlobTier

from devtools_testutils.storage import StorageRecordedTestCase
from fake_credentials import CPK_KEY_HASH, CPK_KEY_VALUE
from settings.testcase import BlobPreparer


TEST_ENCRYPTION_KEY = CustomerProvidedEncryptionKey(key_value=CPK_KEY_VALUE, key_hash=CPK_KEY_HASH)


class TestStorageBlobClientGapBranches(StorageRecordedTestCase):

    @BlobPreparer()
    def test_set_standard_blob_tier_when_tier_is_none_raises_value_error(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        blob_client = BlobClient(
            self.account_url(storage_account_name, "blob"),
            container_name="container",
            blob_name="blob",
            credential=storage_account_key.secret,
        )

        with pytest.raises(ValueError) as error:
            blob_client.set_standard_blob_tier(None)

        assert str(error.value) == "A StandardBlobTier must be specified"

    @BlobPreparer()
    def test_set_standard_blob_tier_when_snapshot_and_version_id_are_set_raises_value_error(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        blob_client = BlobClient(
            self.account_url(storage_account_name, "blob"),
            container_name="container",
            blob_name="blob",
            snapshot="2024-01-01T00:00:00.0000000Z",
            credential=storage_account_key.secret,
        )

        with mock.patch("azure.storage.blob._blob_client.get_version_id", return_value="2024-01-02T00:00:00.0000000Z"):
            with pytest.raises(ValueError) as error:
                blob_client.set_standard_blob_tier(StandardBlobTier.Hot, version_id="2024-01-02T00:00:00.0000000Z")

        assert str(error.value) == "Snapshot and version_id cannot be set at the same time"

    @BlobPreparer()
    def test_set_standard_blob_tier_when_generated_client_raises_http_error_raises_processed_error(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        blob_client = BlobClient(
            self.account_url(storage_account_name, "blob"),
            container_name="container",
            blob_name="blob",
            credential=storage_account_key.secret,
        )
        http_error = HttpResponseError(message="tier failure")

        # Tests defensive branch — requires mock.
        with mock.patch.object(blob_client._client.blob, "set_tier", side_effect=http_error), mock.patch(
            "azure.storage.blob._blob_client.process_storage_error",
            side_effect=ResourceNotFoundError("processed error"),
        ) as process_error:
            with pytest.raises(ResourceNotFoundError) as error:
                blob_client.set_standard_blob_tier(StandardBlobTier.Cool)

        assert str(error.value) == "processed error"
        process_error.assert_called_once_with(http_error)

    @BlobPreparer()
    def test_stage_block_when_http_and_cpk_raises_value_error(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        blob_client = BlobClient(
            self.account_url(storage_account_name, "blob").replace("https", "http"),
            container_name="container",
            blob_name="blob",
            credential=storage_account_key.secret,
        )

        with pytest.raises(ValueError) as error:
            blob_client.stage_block(block_id="block1", data=b"abc", cpk=TEST_ENCRYPTION_KEY)

        assert str(error.value) == "Customer provided encryption key must be used over HTTPS."

    @BlobPreparer()
    def test_stage_block_from_url_when_http_and_source_cpk_raises_value_error(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        blob_client = BlobClient(
            self.account_url(storage_account_name, "blob").replace("https", "http"),
            container_name="container",
            blob_name="blob",
            credential=storage_account_key.secret,
        )

        with pytest.raises(ValueError) as error:
            blob_client.stage_block_from_url(
                block_id="block1",
                source_url="https://sourceaccount.blob.core.windows.net/source/sourceblob",
                source_cpk=TEST_ENCRYPTION_KEY,
            )

        assert str(error.value) == "Customer provided encryption key must be used over HTTPS."
