# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from unittest import mock

import pytest
from azure.storage.blob import BlobClient
from azure.storage.blob._shared.constants import DEFAULT_MAX_CONCURRENCY

from devtools_testutils.storage import StorageRecordedTestCase
from settings.testcase import BlobPreparer
from test_helpers import MockLegacyTransport


class TestStorageDownloadDeprecatedMethods(StorageRecordedTestCase):
    def _get_legacy_download_stream(self, storage_account_name, storage_account_key):
        transport = MockLegacyTransport()
        blob_client = BlobClient(
            self.account_url(storage_account_name, "blob"),
            container_name='container',
            blob_name='blob',
            credential=storage_account_key.secret,
            transport=transport,
            retry_total=0
        )
        return blob_client.download_blob()

    @BlobPreparer()
    def test_content_as_bytes_when_called_with_max_concurrency_delegates_to_readall(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        stream = self._get_legacy_download_stream(storage_account_name, storage_account_key)

        with mock.patch.object(stream, 'readall', return_value=b'delegated-bytes') as patched:
            with pytest.warns(DeprecationWarning, match="content_as_bytes is deprecated, use readall instead"):
                data = stream.content_as_bytes(max_concurrency=4)

        assert data == b'delegated-bytes'
        assert stream._max_concurrency == 4
        patched.assert_called_once_with()

    @BlobPreparer()
    def test_content_as_text_when_called_emits_deprecation_warning(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        stream = self._get_legacy_download_stream(storage_account_name, storage_account_key)

        with pytest.warns(DeprecationWarning) as warning:
            data = stream.content_as_text()

        assert str(warning[0].message) == "content_as_text is deprecated, use readall instead"
        assert data == "Hello World!"

    @BlobPreparer()
    def test_content_as_text_when_not_in_text_mode_uses_default_max_concurrency(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        stream = self._get_legacy_download_stream(storage_account_name, storage_account_key)
        stream._text_mode = False
        stream._max_concurrency = 9

        with mock.patch.object(stream, 'readall', return_value='branch-ok') as patched:
            with pytest.warns(DeprecationWarning, match="content_as_text is deprecated, use readall instead"):
                data = stream.content_as_text()

        assert data == 'branch-ok'
        assert stream._max_concurrency == DEFAULT_MAX_CONCURRENCY
        patched.assert_called_once_with()

    @BlobPreparer()
    def test_content_as_text_when_encoding_provided_sets_encoding_before_readall(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        stream = self._get_legacy_download_stream(storage_account_name, storage_account_key)

        with mock.patch.object(stream, 'readall', return_value='encoded-text'):
            with pytest.warns(DeprecationWarning, match="content_as_text is deprecated, use readall instead"):
                data = stream.content_as_text(encoding='ascii')

        assert stream._encoding == 'ascii'
        assert data == 'encoded-text'

    @BlobPreparer()
    def test_content_as_text_when_called_returns_readall_value(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        stream = self._get_legacy_download_stream(storage_account_name, storage_account_key)

        with mock.patch.object(stream, 'readall', return_value='delegated-text') as patched:
            with pytest.warns(DeprecationWarning, match="content_as_text is deprecated, use readall instead"):
                data = stream.content_as_text(max_concurrency=5, encoding='utf-8')

        assert data == 'delegated-text'
        assert stream._max_concurrency == 5
        patched.assert_called_once_with()
