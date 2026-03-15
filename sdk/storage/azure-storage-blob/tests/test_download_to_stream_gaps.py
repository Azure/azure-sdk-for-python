# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from io import BytesIO

import pytest
from azure.storage.blob import BlobClient

from devtools_testutils.storage import StorageRecordedTestCase
from settings.testcase import BlobPreparer
from test_helpers import MockLegacyTransport


class TestStorageDownloadToStreamGaps(StorageRecordedTestCase):
    def _get_legacy_download_stream(self, storage_account_name, storage_account_key):
        blob_client = BlobClient(
            self.account_url(storage_account_name, "blob"),
            container_name="container",
            blob_name="blob",
            credential=storage_account_key.secret,
            transport=MockLegacyTransport(),
            retry_total=0,
        )
        return blob_client.download_blob(encoding="utf-8")

    @BlobPreparer()
    def test_download_to_stream_when_partially_read_in_text_mode_raises_value_error(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        stream = self._get_legacy_download_stream(storage_account_name, storage_account_key)
        partial_text = stream.read(chars=1)

        assert partial_text == "H"

        with pytest.warns(DeprecationWarning, match="download_to_stream is deprecated, use readinto instead"):
            with pytest.raises(ValueError) as exc:
                stream.download_to_stream(BytesIO())

        assert str(exc.value) == "Stream has been partially read in text mode. download_to_stream is not supported in text mode."
