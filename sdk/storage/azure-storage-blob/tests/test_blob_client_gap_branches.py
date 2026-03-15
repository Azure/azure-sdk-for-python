# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from unittest import mock

import pytest
from azure.core.exceptions import HttpResponseError, ResourceNotFoundError
from azure.storage.blob import BlobClient, CustomerProvidedEncryptionKey

from devtools_testutils.storage import StorageRecordedTestCase
from fake_credentials import CPK_KEY_HASH, CPK_KEY_VALUE


class TestStorageBlobClientGaps(StorageRecordedTestCase):

    def _create_blob_client(self, scheme="https"):
        return BlobClient(
            f"{scheme}://fakename.blob.core.windows.net",
            container_name="container",
            blob_name="blob",
            credential="fake_key",
        )

    def _get_cpk(self):
        return CustomerProvidedEncryptionKey(key_value=CPK_KEY_VALUE, key_hash=CPK_KEY_HASH)

    def test_create_page_blob_when_http_and_cpk_raises_value_error(self):
        blob_client = self._create_blob_client("http")

        with pytest.raises(ValueError) as error:
            blob_client.create_page_blob(512, cpk=self._get_cpk())

        assert str(error.value) == "Customer provided encryption key must be used over HTTPS."

    def test_create_append_blob_when_http_and_cpk_raises_value_error(self):
        blob_client = self._create_blob_client("http")

        with pytest.raises(ValueError) as error:
            blob_client.create_append_blob(cpk=self._get_cpk())

        assert str(error.value) == "Customer provided encryption key must be used over HTTPS."

    def test_create_append_blob_when_generated_client_raises_http_error_calls_error_processor(self):
        blob_client = self._create_blob_client()
        error = HttpResponseError(message="create failed")

        # Tests defensive branch — requires mock.
        with mock.patch.object(blob_client._client.append_blob, "create", side_effect=error), mock.patch(
            "azure.storage.blob._blob_client.process_storage_error"
        ) as process_storage_error:
            result = blob_client.create_append_blob()

        assert result is None
        process_storage_error.assert_called_once_with(error)

    def test_create_append_blob_when_error_processor_raises_processed_error(self):
        blob_client = self._create_blob_client()
        error = HttpResponseError(message="create failed")

        # Tests defensive branch — requires mock.
        with mock.patch.object(blob_client._client.append_blob, "create", side_effect=error), mock.patch(
            "azure.storage.blob._blob_client.process_storage_error",
            side_effect=ResourceNotFoundError("processed create failure"),
        ):
            with pytest.raises(ResourceNotFoundError) as processed_error:
                blob_client.create_append_blob()

        assert str(processed_error.value) == "processed create failure"

    def test_create_snapshot_when_http_and_cpk_raises_value_error(self):
        blob_client = self._create_blob_client("http")

        with pytest.raises(ValueError) as error:
            blob_client.create_snapshot(cpk=self._get_cpk())

        assert str(error.value) == "Customer provided encryption key must be used over HTTPS."
