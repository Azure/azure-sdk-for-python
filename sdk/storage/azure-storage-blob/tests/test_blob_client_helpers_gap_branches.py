# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from unittest.mock import patch

import pytest
from azure.storage.blob import BlobClient, BlobProperties

from devtools_testutils.storage import StorageRecordedTestCase
from settings.testcase import BlobPreparer


class UnknownLengthStream(object):
    def __init__(self, data):
        self._data = data
        self._offset = 0

    def read(self, size=-1):
        if size is None or size < 0:
            size = len(self._data) - self._offset
        start = self._offset
        end = min(start + size, len(self._data))
        self._offset = end
        return self._data[start:end]


class TestStorageBlobClientHelpers(StorageRecordedTestCase):

    @BlobPreparer()
    def test_start_copy_from_url_when_incremental_copy_has_source_authorization_raises_value_error(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        blob_client = BlobClient(
            self.account_url(storage_account_name, "blob"),
            container_name='container',
            blob_name='blob',
            credential=storage_account_key.secret,
        )

        with pytest.raises(ValueError) as error:
            blob_client.start_copy_from_url(
                "https://sourceaccount.blob.core.windows.net/source/sourceblob",
                incremental_copy=True,
                source_authorization="Bearer token",
            )

        assert str(error.value) == "Source authorization tokens are not applicable for incremental copying."

    @BlobPreparer()
    def test_start_copy_from_url_when_encryption_scope_without_sync_copy_raises_value_error(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        blob_client = BlobClient(
            self.account_url(storage_account_name, "blob"),
            container_name='container',
            blob_name='blob',
            credential=storage_account_key.secret,
        )

        with pytest.raises(ValueError) as error:
            blob_client.start_copy_from_url(
                "https://sourceaccount.blob.core.windows.net/source/sourceblob",
                encryption_scope="testscope",
            )

        assert str(error.value) == (
            "Encryption_scope is only supported for sync copy, please specify requires_sync=True"
        )

    @BlobPreparer()
    def test_start_copy_from_url_when_source_token_intent_without_sync_copy_raises_value_error(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        blob_client = BlobClient(
            self.account_url(storage_account_name, "blob"),
            container_name='container',
            blob_name='blob',
            credential=storage_account_key.secret,
        )

        with pytest.raises(ValueError) as error:
            blob_client.start_copy_from_url(
                "https://sourceaccount.file.core.windows.net/source/sourcefile",
                source_token_intent="backup",
            )

        assert str(error.value) == (
            "Source token intent is only supported for sync copy, please specify requires_sync=True"
        )

    @BlobPreparer()
    def test_abort_copy_when_copy_id_is_blob_properties_uses_nested_copy_id(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        blob_client = BlobClient(
            self.account_url(storage_account_name, "blob"),
            container_name='container',
            blob_name='blob',
            credential=storage_account_key.secret,
        )
        blob_properties = BlobProperties()
        blob_properties.copy = type("CopyProperties", (), {"id": "copy-id-from-properties"})()

        with patch.object(blob_client._client.blob, "abort_copy_from_url", return_value=None) as patched_abort:
            blob_client.abort_copy(blob_properties, timeout=12)

        assert patched_abort.call_count == 1
        assert patched_abort.call_args.kwargs["copy_id"] == "copy-id-from-properties"
        assert patched_abort.call_args.kwargs["timeout"] == 12

    @BlobPreparer()
    def test_stage_block_when_length_is_omitted_and_stream_length_is_unknown_reads_all_bytes(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        blob_client = BlobClient(
            self.account_url(storage_account_name, "blob"),
            container_name='container',
            blob_name='blob',
            credential=storage_account_key.secret,
        )
        stream = UnknownLengthStream(b"hello")

        with patch.object(blob_client._client.block_blob, "stage_block", return_value={"etag": "etag-value"}) as patched_stage:
            response = blob_client.stage_block("block1", stream)

        assert response == {"etag": "etag-value"}
        assert patched_stage.call_count == 1
        assert patched_stage.call_args.kwargs["content_length"] == 5
        assert patched_stage.call_args.kwargs["body"] == b"hello"
    