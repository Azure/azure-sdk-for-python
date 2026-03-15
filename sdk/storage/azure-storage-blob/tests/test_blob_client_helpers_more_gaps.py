# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from unittest import mock

import pytest
from azure.storage.blob import BlobClient

from devtools_testutils.storage import StorageRecordedTestCase


class TestBlobClientHelperMoreGaps(StorageRecordedTestCase):

    def _create_blob_client(self):
        return BlobClient(
            "https://fakestorage.blob.core.windows.net",
            container_name="container",
            blob_name="blob",
            credential="fake_key"
        )

    def test_append_block_when_appendpos_condition_is_zero_sets_append_conditions(self):
        blob_client = self._create_blob_client()

        with mock.patch.object(blob_client._client.append_blob, "append_block", side_effect=lambda **kwargs: kwargs):
            resp = blob_client.append_block(b"abc", appendpos_condition=0)

        assert resp["content_length"] == 3
        assert resp["append_position_access_conditions"].append_position == 0
        assert resp["append_position_access_conditions"].max_size is None

    def test_append_block_from_url_when_only_source_offset_is_provided_uses_open_ended_source_range(self):
        blob_client = self._create_blob_client()
        source_url = "https://fakestorage.blob.core.windows.net/sourcecontainer/sourceblob"

        with mock.patch.object(blob_client._client.append_blob, "append_block_from_url", side_effect=lambda **kwargs: kwargs):
            resp = blob_client.append_block_from_url(source_url, source_offset=512)

        assert resp["source_url"] == source_url
        assert resp["source_range"] == "bytes=512-"
        assert resp["content_length"] == 0

    def test_from_blob_url_when_url_has_no_scheme_prefixes_https(self):
        blob_client = BlobClient.from_blob_url(
            "fakestorage.blob.core.windows.net/container/blob",
            credential="fake_key"
        )

        assert blob_client.scheme == "https"
        assert blob_client.url == "https://fakestorage.blob.core.windows.net/container/blob"
        assert blob_client.account_name == "fakestorage"

    def test_from_blob_url_when_blob_url_is_none_raises_value_error(self):
        with pytest.raises(ValueError) as error:
            BlobClient.from_blob_url(None, credential="fake_key")

        assert str(error.value) == "Blob URL must be a string."

    def test_from_blob_url_when_blob_url_is_not_string_preserves_attribute_error_cause(self):
        with pytest.raises(ValueError) as error:
            BlobClient.from_blob_url(1, credential="fake_key")

        assert str(error.value) == "Blob URL must be a string."
        assert isinstance(error.value.__cause__, AttributeError)
