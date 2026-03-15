# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from unittest import mock

import pytest
from azure.core.exceptions import HttpResponseError, ResourceNotFoundError
from azure.storage.blob import BlobClient


class TestBlobClientGapRemainingBranches:

    def test_get_page_range_diff_for_managed_disk_when_error_processor_swallows_error_raises_unboundlocalerror(self):
        blob_client = BlobClient(
            "https://foo.blob.core.windows.net",
            container_name="container",
            blob_name="blob",
            credential="fake_key"
        )
        error = HttpResponseError(message="boom")
        blob_client._client.page_blob.get_page_ranges_diff = mock.Mock(side_effect=error)

        # Tests defensive branch — requires mock.
        with mock.patch("azure.storage.blob._blob_client.process_storage_error") as process_storage_error:
            process_storage_error.return_value = None

            with pytest.raises(UnboundLocalError) as exc:
                blob_client.get_page_range_diff_for_managed_disk("https://foo.blob.core.windows.net/container/blob?snapshot=abc")

            assert "ranges" in str(exc.value)
            process_storage_error.assert_called_once_with(error)

    def test_set_sequence_number_when_generated_client_raises_http_error_returns_none_after_error_processing(self):
        blob_client = BlobClient(
            "https://foo.blob.core.windows.net",
            container_name="container",
            blob_name="blob",
            credential="fake_key"
        )
        error = HttpResponseError(message="boom")
        blob_client._client.page_blob.update_sequence_number = mock.Mock(side_effect=error)

        # Tests defensive branch — requires mock.
        with mock.patch("azure.storage.blob._blob_client.process_storage_error") as process_storage_error:
            process_storage_error.return_value = None

            result = blob_client.set_sequence_number("increment")

            assert result is None
            process_storage_error.assert_called_once_with(error)

    def test_set_sequence_number_when_error_processor_raises_processed_error_propagates_exception(self):
        blob_client = BlobClient(
            "https://foo.blob.core.windows.net",
            container_name="container",
            blob_name="blob",
            credential="fake_key"
        )
        error = HttpResponseError(message="boom")
        processed_error = ResourceNotFoundError(message="processed")
        blob_client._client.page_blob.update_sequence_number = mock.Mock(side_effect=error)

        # Tests defensive branch — requires mock.
        with mock.patch("azure.storage.blob._blob_client.process_storage_error", side_effect=processed_error) as process_storage_error:
            with pytest.raises(ResourceNotFoundError) as exc:
                blob_client.set_sequence_number("increment")

            assert exc.value is processed_error
            process_storage_error.assert_called_once_with(error)

    def test_resize_blob_when_http_and_cpk_raises_value_error(self):
        blob_client = BlobClient(
            "http://foo.blob.core.windows.net",
            container_name="container",
            blob_name="blob",
            credential="fake_key"
        )

        with pytest.raises(ValueError) as exc:
            blob_client.resize_blob(512, cpk=object())

        assert str(exc.value) == "Customer provided encryption key must be used over HTTPS."

    def test_resize_blob_when_generated_client_raises_http_error_returns_none_after_error_processing(self):
        blob_client = BlobClient(
            "https://foo.blob.core.windows.net",
            container_name="container",
            blob_name="blob",
            credential="fake_key"
        )
        error = HttpResponseError(message="boom")
        blob_client._client.page_blob.resize = mock.Mock(side_effect=error)

        # Tests defensive branch — requires mock.
        with mock.patch("azure.storage.blob._blob_client.process_storage_error") as process_storage_error:
            process_storage_error.return_value = None

            result = blob_client.resize_blob(512)

            assert result is None
            process_storage_error.assert_called_once_with(error)
