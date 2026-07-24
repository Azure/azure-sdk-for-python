# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""Tests for the native transfer acceleration dispatch module."""

import unittest
from unittest.mock import MagicMock, patch

from azure.storage.blob._transfer_native import (
    _can_use_native_download,
    _can_use_native_upload,
    _extract_access_token,
    _extract_account_url,
    _is_native_available,
)


class TestNativeAvailability(unittest.TestCase):
    """Tests for the native availability check."""

    def test_not_available_when_not_installed(self):
        """The native extension should report unavailable when not installed."""
        with patch.dict("sys.modules", {"azure.storage.extensions.transfer": None}):
            result = _is_native_available()
            # Will be False since the module is not importable
            self.assertFalse(result)


class TestCanUseNativeUpload(unittest.TestCase):
    """Tests for upload acceleration eligibility checks."""

    def _make_credential(self, has_get_token=True):
        cred = MagicMock()
        if not has_get_token:
            del cred.get_token
        return cred

    def test_rejects_non_block_blob(self):
        result = _can_use_native_upload(
            blob_type="PageBlob",
            encryption_options={},
            validate_content=None,
            data=b"test",
            credential=self._make_credential(),
        )
        self.assertFalse(result)

    def test_rejects_encryption(self):
        result = _can_use_native_upload(
            blob_type="BlockBlob",
            encryption_options={"key": "somekey"},
            validate_content=None,
            data=b"test",
            credential=self._make_credential(),
        )
        self.assertFalse(result)

    def test_rejects_content_validation(self):
        result = _can_use_native_upload(
            blob_type="BlockBlob",
            encryption_options={},
            validate_content="md5",
            data=b"test",
            credential=self._make_credential(),
        )
        self.assertFalse(result)

    def test_rejects_progress_hook(self):
        result = _can_use_native_upload(
            blob_type="BlockBlob",
            encryption_options={},
            validate_content=None,
            data=b"test",
            credential=self._make_credential(),
            progress_hook=lambda x, y: None,
        )
        self.assertFalse(result)

    def test_rejects_lease(self):
        result = _can_use_native_upload(
            blob_type="BlockBlob",
            encryption_options={},
            validate_content=None,
            data=b"test",
            credential=self._make_credential(),
            lease="some-lease-id",
        )
        self.assertFalse(result)

    def test_rejects_conditional_access(self):
        result = _can_use_native_upload(
            blob_type="BlockBlob",
            encryption_options={},
            validate_content=None,
            data=b"test",
            credential=self._make_credential(),
            if_modified_since="2021-01-01",
        )
        self.assertFalse(result)

    def test_rejects_stream_input(self):
        """File-like stream inputs should fall back to the Python upload path."""
        import io

        with patch(
            "azure.storage.blob._transfer_native._is_native_available",
            return_value=True,
        ):
            result = _can_use_native_upload(
                blob_type="BlockBlob",
                encryption_options={},
                validate_content=None,
                data=io.BytesIO(b"test"),
                credential=self._make_credential(),
            )
        self.assertFalse(result)

    def test_accepts_in_memory_buffers(self):
        """bytes/bytearray/memoryview/str payloads should be eligible for native upload."""
        with patch(
            "azure.storage.blob._transfer_native._is_native_available",
            return_value=True,
        ):
            for data in (b"test", bytearray(b"test"), memoryview(b"test"), "test"):
                result = _can_use_native_upload(
                    blob_type="BlockBlob",
                    encryption_options={},
                    validate_content=None,
                    data=data,
                    credential=self._make_credential(),
                )
                self.assertTrue(result, f"expected {type(data).__name__} to be eligible")


class TestCanUseNativeDownload(unittest.TestCase):
    """Tests for download acceleration eligibility checks."""

    def _make_credential(self, has_get_token=True):
        cred = MagicMock()
        if not has_get_token:
            del cred.get_token
        return cred

    def test_rejects_encryption(self):
        result = _can_use_native_download(
            encryption_options={"key": "somekey"},
            validate_content=None,
            credential=self._make_credential(),
        )
        self.assertFalse(result)

    def test_rejects_content_validation(self):
        result = _can_use_native_download(
            encryption_options={},
            validate_content="crc64",
            credential=self._make_credential(),
        )
        self.assertFalse(result)

    def test_rejects_decompression(self):
        result = _can_use_native_download(
            encryption_options={},
            validate_content=None,
            credential=self._make_credential(),
            decompress=True,
        )
        self.assertFalse(result)

    def test_rejects_encoding(self):
        result = _can_use_native_download(
            encryption_options={},
            validate_content=None,
            credential=self._make_credential(),
            encoding="utf-8",
        )
        self.assertFalse(result)

    def test_rejects_progress_hook(self):
        result = _can_use_native_download(
            encryption_options={},
            validate_content=None,
            credential=self._make_credential(),
            progress_hook=lambda x, y: None,
        )
        self.assertFalse(result)


class TestExtractAccessToken(unittest.TestCase):
    """Tests for OAuth token extraction."""

    def test_returns_none_for_none_credential(self):
        self.assertIsNone(_extract_access_token(None))

    def test_returns_none_without_get_token(self):
        cred = MagicMock(spec=[])
        self.assertIsNone(_extract_access_token(cred))

    def test_extracts_token(self):
        cred = MagicMock()
        token_result = MagicMock()
        token_result.token = "test-access-token"
        cred.get_token.return_value = token_result
        result = _extract_access_token(cred)
        self.assertEqual(result, "test-access-token")

    def test_returns_none_on_exception(self):
        cred = MagicMock()
        cred.get_token.side_effect = Exception("auth failed")
        result = _extract_access_token(cred)
        self.assertIsNone(result)


class TestExtractAccountUrl(unittest.TestCase):
    """Tests for account URL extraction from BlobClient."""

    def test_basic_url(self):
        client = MagicMock()
        client.scheme = "https"
        client.primary_hostname = "myaccount.blob.core.windows.net"
        client._query_str = None
        result = _extract_account_url(client)
        self.assertEqual(result, "https://myaccount.blob.core.windows.net")

    def test_url_with_sas(self):
        client = MagicMock()
        client.scheme = "https"
        client.primary_hostname = "myaccount.blob.core.windows.net"
        client._query_str = "sv=2021-06-08&sig=abc"
        result = _extract_account_url(client)
        self.assertEqual(result, "https://myaccount.blob.core.windows.net?sv=2021-06-08&sig=abc")


class TestNativeStorageStreamDownloader(unittest.TestCase):
    """Tests for the lightweight NativeStorageStreamDownloader wrapper."""

    def setUp(self):
        from azure.storage.blob._transfer_native import NativeStorageStreamDownloader
        self.data = b"hello world blob content"
        self.downloader = NativeStorageStreamDownloader(
            data=self.data, name="myblob.txt", container="mycontainer"
        )

    def test_attributes(self):
        self.assertEqual(self.downloader.name, "myblob.txt")
        self.assertEqual(self.downloader.container, "mycontainer")
        self.assertEqual(self.downloader.size, len(self.data))
        self.assertIsNone(self.downloader.properties)

    def test_len(self):
        self.assertEqual(len(self.downloader), len(self.data))

    def test_readall(self):
        self.assertEqual(self.downloader.readall(), self.data)

    def test_read_all_at_once(self):
        self.assertEqual(self.downloader.read(), self.data)
        # Second read returns empty
        self.assertEqual(self.downloader.read(), b"")

    def test_read_with_size(self):
        self.assertEqual(self.downloader.read(5), b"hello")
        self.assertEqual(self.downloader.read(6), b" world")
        self.assertEqual(self.downloader.read(), b" blob content")

    def test_readinto(self):
        from io import BytesIO
        stream = BytesIO()
        written = self.downloader.readinto(stream)
        self.assertEqual(written, len(self.data))
        self.assertEqual(stream.getvalue(), self.data)

    def test_chunks(self):
        chunks = list(self.downloader.chunks())
        self.assertEqual(chunks, [self.data])

    def test_iter(self):
        chunks = list(self.downloader)
        self.assertEqual(chunks, [self.data])


if __name__ == "__main__":
    unittest.main()
