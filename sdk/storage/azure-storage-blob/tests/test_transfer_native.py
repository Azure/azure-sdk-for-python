# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""Tests for the native transfer acceleration dispatch module."""

import unittest
from types import ModuleType
from unittest.mock import MagicMock, patch

from azure.storage.blob._transfer_native import (
    _build_token_provider,
    _can_use_native_download,
    _can_use_native_upload,
    _is_native_available,
    try_native_upload,
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


class TestBuildTokenProvider(unittest.TestCase):
    """Tests for the on-demand token provider used by the native extension."""

    def test_returns_none_for_none_credential(self):
        self.assertIsNone(_build_token_provider(None))

    def test_returns_none_without_get_token(self):
        cred = MagicMock(spec=[])
        self.assertIsNone(_build_token_provider(cred))

    def test_provider_returns_token_and_int_expiry(self):
        cred = MagicMock()
        token_result = MagicMock()
        token_result.token = "test-access-token"
        token_result.expires_on = 1_700_000_000.9  # float -> coerced to int
        cred.get_token.return_value = token_result

        provider = _build_token_provider(cred)
        self.assertIsNotNone(provider)
        token, expires_on = provider(["https://storage.azure.com/.default"])
        self.assertEqual(token, "test-access-token")
        self.assertEqual(expires_on, 1_700_000_000)
        self.assertIsInstance(expires_on, int)

    def test_provider_calls_get_token_fresh_each_time(self):
        """The provider must not cache; each call fetches a fresh token."""
        cred = MagicMock()
        tokens = [MagicMock(token="tok-1", expires_on=1), MagicMock(token="tok-2", expires_on=2)]
        cred.get_token.side_effect = tokens

        provider = _build_token_provider(cred)
        first = provider(["scope"])
        second = provider(["scope"])

        self.assertEqual(cred.get_token.call_count, 2)
        self.assertEqual(first, ("tok-1", 1))
        self.assertEqual(second, ("tok-2", 2))

    def test_provider_defaults_scope_when_empty(self):
        cred = MagicMock()
        cred.get_token.return_value = MagicMock(token="t", expires_on=1)
        provider = _build_token_provider(cred)
        provider([])
        cred.get_token.assert_called_once_with("https://storage.azure.com/.default")

    def test_provider_is_thread_safe(self):
        """Concurrent invocations are serialized and all succeed."""
        import threading

        counter = {"value": 0}
        state_lock = threading.Lock()

        cred = MagicMock()

        def _get_token(*_scopes, **_kwargs):
            with state_lock:
                counter["value"] += 1
                current = counter["value"]
            return MagicMock(token=f"tok-{current}", expires_on=current)

        cred.get_token.side_effect = _get_token
        provider = _build_token_provider(cred)

        results = []
        results_lock = threading.Lock()

        def _worker():
            token, expires_on = provider(["scope"])
            with results_lock:
                results.append((token, expires_on))

        threads = [threading.Thread(target=_worker) for _ in range(20)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        self.assertEqual(len(results), 20)
        self.assertEqual(cred.get_token.call_count, 20)
        for token, expires_on in results:
            self.assertTrue(token.startswith("tok-"))
            self.assertIsInstance(expires_on, int)


class TestNativeCredentialIdentity(unittest.TestCase):
    """Tests that native transfers identify the credential behind each provider closure."""

    def test_upload_forwards_stable_distinct_credential_ids(self):
        native_upload = MagicMock(return_value={"etag": "etag"})
        native_module = ModuleType("azure.storage.extensions.transfer")
        native_module.upload_blob = native_upload

        first_credential = MagicMock()
        second_credential = MagicMock()
        first_client = MagicMock(
            credential=first_credential,
            url="https://account.blob.core.windows.net/container/first",
        )
        second_client = MagicMock(
            credential=second_credential,
            url="https://account.blob.core.windows.net/container/second",
        )
        config = MagicMock(max_single_put_size=64, max_block_size=32)

        with patch(
            "azure.storage.blob._transfer_native._is_native_available",
            return_value=True,
        ), patch.dict("sys.modules", {"azure.storage.extensions.transfer": native_module}):
            try_native_upload(first_client, b"first", "BlockBlob", {}, None, config)
            try_native_upload(first_client, b"again", "BlockBlob", {}, None, config)
            try_native_upload(second_client, b"second", "BlockBlob", {}, None, config)

        credential_ids = [call.kwargs["credential_id"] for call in native_upload.call_args_list]
        self.assertEqual(credential_ids, [id(first_credential), id(first_credential), id(second_credential)])
        self.assertNotEqual(credential_ids[0], credential_ids[2])


class _FakeNativeStream:
    """Minimal stand-in for the native windowed download stream.

    Yields the provided windows and exposes ``size``/``etag``/``last_modified`` like the real
    native object. Single-pass, matching the native stream's semantics.
    """

    def __init__(self, windows, size=None):
        self._windows = iter(windows)
        self.size = size if size is not None else sum(len(w) for w in windows)
        self.etag = None
        self.last_modified = None

    def __iter__(self):
        return self

    def __next__(self):
        return next(self._windows)


class TestNativeStorageStreamDownloader(unittest.TestCase):
    """Tests for the lightweight NativeStorageStreamDownloader wrapper."""

    def setUp(self):
        from azure.storage.blob._transfer_native import NativeStorageStreamDownloader
        self.data = b"hello world blob content"
        self._make = lambda windows=None: NativeStorageStreamDownloader(
            stream=_FakeNativeStream(windows if windows is not None else [self.data], size=len(self.data)),
            name="myblob.txt",
            container="mycontainer",
        )
        self.downloader = self._make()

    def test_attributes(self):
        self.assertEqual(self.downloader.name, "myblob.txt")
        self.assertEqual(self.downloader.container, "mycontainer")
        self.assertEqual(self.downloader.size, len(self.data))
        self.assertIsNone(self.downloader.properties)

    def test_len(self):
        self.assertEqual(len(self.downloader), len(self.data))

    def test_readall(self):
        self.assertEqual(self.downloader.readall(), self.data)

    def test_readall_multiple_windows(self):
        downloader = self._make([b"hello ", b"world ", b"blob content"])
        self.assertEqual(downloader.readall(), self.data)

    def test_read_all_at_once(self):
        self.assertEqual(self.downloader.read(), self.data)
        # Second read returns empty
        self.assertEqual(self.downloader.read(), b"")

    def test_read_with_size(self):
        self.assertEqual(self.downloader.read(5), b"hello")
        self.assertEqual(self.downloader.read(6), b" world")
        self.assertEqual(self.downloader.read(), b" blob content")

    def test_read_with_size_across_windows(self):
        downloader = self._make([b"hello ", b"world ", b"blob content"])
        self.assertEqual(downloader.read(8), b"hello wo")
        self.assertEqual(downloader.read(), b"rld blob content")

    def test_readinto(self):
        from io import BytesIO
        stream = BytesIO()
        written = self.downloader.readinto(stream)
        self.assertEqual(written, len(self.data))
        self.assertEqual(stream.getvalue(), self.data)

    def test_readinto_multiple_windows(self):
        from io import BytesIO
        downloader = self._make([b"hello ", b"world ", b"blob content"])
        stream = BytesIO()
        written = downloader.readinto(stream)
        self.assertEqual(written, len(self.data))
        self.assertEqual(stream.getvalue(), self.data)

    def test_chunks(self):
        chunks = list(self.downloader.chunks())
        self.assertEqual(chunks, [self.data])

    def test_chunks_multiple_windows(self):
        windows = [b"hello ", b"world ", b"blob content"]
        downloader = self._make(windows)
        self.assertEqual(list(downloader.chunks()), windows)

    def test_iter(self):
        chunks = list(self.downloader)
        self.assertEqual(chunks, [self.data])


if __name__ == "__main__":
    unittest.main()
