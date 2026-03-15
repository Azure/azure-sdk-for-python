# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from unittest import mock

import pytest
from azure.core.exceptions import HttpResponseError, ResourceNotFoundError
from azure.storage.blob import BlobClient
from azure.storage.blob._encryption import _ERROR_UNSUPPORTED_METHOD_FOR_ENCRYPTION

from devtools_testutils.storage import StorageRecordedTestCase
from settings.testcase import BlobPreparer


class TestStorageBlobClientPageBlobGapBranches(StorageRecordedTestCase):

    def _create_blob_client(self, storage_account_name, credential, protocol="https"):
        account_url = self.account_url(storage_account_name, "blob")
        if protocol == "http":
            account_url = account_url.replace("https", "http")
        return BlobClient(
            account_url,
            container_name="container",
            blob_name="blob",
            credential=credential,
        )

    @BlobPreparer()
    def test_resize_blob_when_generated_client_raises_http_error_propagates_processed_error(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        client = self._create_blob_client(storage_account_name, storage_account_key.secret)
        client._client.page_blob.resize = mock.Mock(side_effect=HttpResponseError(message="boom"))
        processed_error = ResourceNotFoundError("processed resize failure")

        # Tests defensive branch — requires mock.
        with mock.patch("azure.storage.blob._blob_client.process_storage_error", side_effect=processed_error):
            with pytest.raises(ResourceNotFoundError) as error:
                client.resize_blob(512)

        assert error.value is processed_error
        client._client.page_blob.resize.assert_called_once()

    @BlobPreparer()
    def test_upload_page_when_http_and_cpk_raises_value_error(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        client = self._create_blob_client(storage_account_name, storage_account_key.secret, protocol="http")

        with pytest.raises(ValueError) as error:
            client.upload_page(b"0" * 512, offset=0, length=512, cpk=object())

        assert str(error.value) == "Customer provided encryption key must be used over HTTPS."

    @BlobPreparer()
    def test_upload_pages_from_url_when_encryption_required_raises_value_error(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        client = self._create_blob_client(storage_account_name, storage_account_key.secret)
        client.require_encryption = True

        with pytest.raises(ValueError) as error:
            client.upload_pages_from_url(
                "https://sourceaccount.blob.core.windows.net/sourcecontainer/sourceblob",
                offset=0,
                length=512,
                source_offset=0,
            )

        assert str(error.value) == _ERROR_UNSUPPORTED_METHOD_FOR_ENCRYPTION

    @BlobPreparer()
    def test_upload_pages_from_url_when_http_and_source_cpk_raises_value_error(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        client = self._create_blob_client(storage_account_name, storage_account_key.secret, protocol="http")

        with pytest.raises(ValueError) as error:
            client.upload_pages_from_url(
                "https://sourceaccount.blob.core.windows.net/sourcecontainer/sourceblob",
                offset=0,
                length=512,
                source_offset=0,
                source_cpk=object(),
            )

        assert str(error.value) == "Customer provided encryption key must be used over HTTPS."

    @BlobPreparer()
    def test_clear_page_when_encryption_required_raises_value_error(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        client = self._create_blob_client(storage_account_name, storage_account_key.secret)
        client.require_encryption = True

        with pytest.raises(ValueError) as error:
            client.clear_page(offset=0, length=512)

        assert str(error.value) == _ERROR_UNSUPPORTED_METHOD_FOR_ENCRYPTION
