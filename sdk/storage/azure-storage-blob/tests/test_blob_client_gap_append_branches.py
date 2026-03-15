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


class TestStorageBlobClientGapAppendBranches(StorageRecordedTestCase):

    @BlobPreparer()
    def test_clear_page_when_generated_client_raises_http_error_calls_error_processor(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        blob = BlobClient(
            self.account_url(storage_account_name, "blob"),
            container_name='container',
            blob_name='blob',
            credential=storage_account_key.secret,
        )
        error = HttpResponseError(message="boom")

        # Tests defensive branch — requires mock.
        with mock.patch.object(blob._client.page_blob, 'clear_pages', side_effect=error), mock.patch(
            'azure.storage.blob._blob_client.process_storage_error'
        ) as error_processor:
            result = blob.clear_page(offset=0, length=512)

        assert result is None
        assert error_processor.call_count == 1
        assert error_processor.call_args[0][0] is error

    @BlobPreparer()
    def test_clear_page_when_error_processor_raises_processed_error_propagates_exception(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        blob = BlobClient(
            self.account_url(storage_account_name, "blob"),
            container_name='container',
            blob_name='blob',
            credential=storage_account_key.secret,
        )
        error = HttpResponseError(message="boom")

        # Tests defensive branch — requires mock.
        with mock.patch.object(blob._client.page_blob, 'clear_pages', side_effect=error), mock.patch(
            'azure.storage.blob._blob_client.process_storage_error',
            side_effect=ResourceNotFoundError("processed")
        ):
            with pytest.raises(ResourceNotFoundError) as exc:
                blob.clear_page(offset=0, length=512)

        assert str(exc.value) == "processed"

    @BlobPreparer()
    def test_append_block_when_http_and_cpk_raises_value_error(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        blob = BlobClient(
            self.account_url(storage_account_name, "blob").replace('https', 'http'),
            container_name='container',
            blob_name='blob',
            credential=storage_account_key.secret,
        )

        with pytest.raises(ValueError) as exc:
            blob.append_block(b"data", cpk=object())

        assert str(exc.value) == "Customer provided encryption key must be used over HTTPS."

    @BlobPreparer()
    def test_append_block_from_url_when_encryption_required_raises_value_error(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        blob = BlobClient(
            self.account_url(storage_account_name, "blob"),
            container_name='container',
            blob_name='blob',
            credential=storage_account_key.secret,
            require_encryption=True,
        )

        with pytest.raises(ValueError) as exc:
            blob.append_block_from_url("https://source.blob.core.windows.net/container/source")

        assert str(exc.value) == _ERROR_UNSUPPORTED_METHOD_FOR_ENCRYPTION

    @BlobPreparer()
    def test_append_block_from_url_when_http_and_source_cpk_raises_value_error(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        blob = BlobClient(
            self.account_url(storage_account_name, "blob").replace('https', 'http'),
            container_name='container',
            blob_name='blob',
            credential=storage_account_key.secret,
        )

        with pytest.raises(ValueError) as exc:
            blob.append_block_from_url(
                "https://source.blob.core.windows.net/container/source",
                source_cpk=object(),
            )

        assert str(exc.value) == "Customer provided encryption key must be used over HTTPS."
