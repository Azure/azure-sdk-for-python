# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""Tests for the native transfer acceleration dispatch module."""

import unittest
from datetime import datetime, timezone
from types import ModuleType
from unittest.mock import MagicMock, patch

from azure.core import MatchConditions

from azure.storage.blob._transfer_native import (
    _build_token_provider,
    _can_use_native_download,
    _can_use_native_upload,
    _is_native_available,
    try_native_download_eager,
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
        with patch(
            "azure.storage.blob._transfer_native._is_native_available",
            return_value=True,
        ), self.assertRaisesRegex(ValueError, "only block blobs"):
            _can_use_native_upload(
                blob_type="PageBlob",
                encryption_options={},
                validate_content=None,
                data=b"test",
                credential=self._make_credential(),
            )

    def test_rejects_encryption(self):
        with patch(
            "azure.storage.blob._transfer_native._is_native_available",
            return_value=True,
        ), self.assertRaisesRegex(ValueError, "client-side encryption"):
            _can_use_native_upload(
                blob_type="BlockBlob",
                encryption_options={"key": "somekey"},
                validate_content=None,
                data=b"test",
                credential=self._make_credential(),
            )

    def test_rejects_content_validation(self):
        with patch(
            "azure.storage.blob._transfer_native._is_native_available",
            return_value=True,
        ), self.assertRaisesRegex(ValueError, "content validation"):
            _can_use_native_upload(
                blob_type="BlockBlob",
                encryption_options={},
                validate_content="md5",
                data=b"test",
                credential=self._make_credential(),
            )

    def test_rejects_progress_hook(self):
        with patch(
            "azure.storage.blob._transfer_native._is_native_available",
            return_value=True,
        ), self.assertRaisesRegex(ValueError, "progress hooks"):
            _can_use_native_upload(
                blob_type="BlockBlob",
                encryption_options={},
                validate_content=None,
                data=b"test",
                credential=self._make_credential(),
                progress_hook=lambda x, y: None,
            )

    def test_rejects_unsupported_credential(self):
        with patch(
            "azure.storage.blob._transfer_native._is_native_available",
            return_value=True,
        ), self.assertRaisesRegex(ValueError, "token credential or SAS credential"):
            _can_use_native_upload(
                blob_type="BlockBlob",
                encryption_options={},
                validate_content=None,
                data=b"test",
                credential=self._make_credential(has_get_token=False),
            )

    def test_accepts_supported_blob_options(self):
        with patch(
            "azure.storage.blob._transfer_native._is_native_available",
            return_value=True,
        ):
            result = _can_use_native_upload(
                blob_type="BlockBlob",
                encryption_options={},
                validate_content=None,
                data=b"test",
                credential=self._make_credential(),
                cpk=MagicMock(),
                lease="some-lease-id",
                tags={"key": "value"},
                if_modified_since=datetime(2021, 1, 1, tzinfo=timezone.utc),
                if_tags_match_condition="\"key\" = 'value'",
                immutability_policy=MagicMock(),
                legal_hold=True,
                standard_blob_tier="Cool",
            )
        self.assertTrue(result)

    def test_rejects_stream_input(self):
        """File-like stream inputs should fail when native upload is available."""
        import io

        with patch(
            "azure.storage.blob._transfer_native._is_native_available",
            return_value=True,
        ), self.assertRaisesRegex(ValueError, "received BytesIO"):
            _can_use_native_upload(
                blob_type="BlockBlob",
                encryption_options={},
                validate_content=None,
                data=io.BytesIO(b"test"),
                credential=self._make_credential(),
            )

    def test_accepts_immutable_in_memory_data(self):
        """bytes/str payloads should be eligible for zero-copy native upload."""
        with patch(
            "azure.storage.blob._transfer_native._is_native_available",
            return_value=True,
        ):
            for data in (b"test", "test"):
                result = _can_use_native_upload(
                    blob_type="BlockBlob",
                    encryption_options={},
                    validate_content=None,
                    data=data,
                    credential=self._make_credential(),
                )
                self.assertTrue(
                    result, f"expected {type(data).__name__} to be eligible"
                )

    def test_rejects_mutable_buffers_and_buffer_views(self):
        """Mutable buffers and potentially aliased views must fail native upload."""
        with patch(
            "azure.storage.blob._transfer_native._is_native_available",
            return_value=True,
        ):
            for data in (bytearray(b"test"), memoryview(b"test")):
                with self.subTest(data_type=type(data).__name__), self.assertRaises(
                    ValueError
                ):
                    _can_use_native_upload(
                        blob_type="BlockBlob",
                        encryption_options={},
                        validate_content=None,
                        data=data,
                        credential=self._make_credential(),
                    )


class TestCanUseNativeDownload(unittest.TestCase):
    """Tests for download acceleration eligibility checks."""

    def _make_credential(self, has_get_token=True):
        cred = MagicMock()
        if not has_get_token:
            del cred.get_token
        return cred

    def test_rejects_encryption(self):
        with patch(
            "azure.storage.blob._transfer_native._is_native_available",
            return_value=True,
        ), self.assertRaisesRegex(ValueError, "client-side encryption"):
            _can_use_native_download(
                encryption_options={"key": "somekey"},
                validate_content=None,
                credential=self._make_credential(),
            )

    def test_rejects_content_validation(self):
        with patch(
            "azure.storage.blob._transfer_native._is_native_available",
            return_value=True,
        ), self.assertRaisesRegex(ValueError, "content validation"):
            _can_use_native_download(
                encryption_options={},
                validate_content="crc64",
                credential=self._make_credential(),
            )

    def test_rejects_decompression(self):
        with patch(
            "azure.storage.blob._transfer_native._is_native_available",
            return_value=True,
        ), self.assertRaisesRegex(ValueError, "decompression"):
            _can_use_native_download(
                encryption_options={},
                validate_content=None,
                credential=self._make_credential(),
                decompress=True,
            )

    def test_rejects_encoding(self):
        with patch(
            "azure.storage.blob._transfer_native._is_native_available",
            return_value=True,
        ), self.assertRaisesRegex(ValueError, "text encoding"):
            _can_use_native_download(
                encryption_options={},
                validate_content=None,
                credential=self._make_credential(),
                encoding="utf-8",
            )

    def test_rejects_progress_hook(self):
        with patch(
            "azure.storage.blob._transfer_native._is_native_available",
            return_value=True,
        ), self.assertRaisesRegex(ValueError, "progress hooks"):
            _can_use_native_download(
                encryption_options={},
                validate_content=None,
                credential=self._make_credential(),
                progress_hook=lambda x, y: None,
            )

    def test_rejects_unsupported_credential(self):
        with patch(
            "azure.storage.blob._transfer_native._is_native_available",
            return_value=True,
        ), self.assertRaisesRegex(ValueError, "token credential or SAS credential"):
            _can_use_native_download(
                encryption_options={},
                validate_content=None,
                credential=self._make_credential(has_get_token=False),
            )

    def test_accepts_supported_blob_options(self):
        with patch(
            "azure.storage.blob._transfer_native._is_native_available",
            return_value=True,
        ):
            result = _can_use_native_download(
                encryption_options={},
                validate_content=None,
                credential=self._make_credential(),
                cpk=MagicMock(),
                lease="lease-id",
                etag='"etag"',
                match_condition=MatchConditions.IfNotModified,
                if_modified_since=datetime(2024, 1, 1, tzinfo=timezone.utc),
                if_unmodified_since=datetime(2024, 2, 1, tzinfo=timezone.utc),
                if_tags_match_condition="\"tag\" = 'value'",
                version_id="version",
                timeout=30,
            )
        self.assertTrue(result)


class TestNativeDownloadDispatch(unittest.TestCase):
    """Tests for native download dispatch and option forwarding."""

    def test_download_returns_none_only_when_extension_is_unavailable(self):
        client = MagicMock()

        with patch(
            "azure.storage.blob._transfer_native._is_native_available",
            return_value=False,
        ):
            result = try_native_download_eager(client, None, None, {}, None)

        self.assertIsNone(result)

    def test_download_propagates_native_extension_failure(self):
        native_download = MagicMock(side_effect=ValueError("native failure"))
        native_module = ModuleType("azure.storage.extensions.transfer")
        native_module.download_blob = native_download
        client = MagicMock(
            credential=MagicMock(),
            url="https://account.blob.core.windows.net/container/blob",
        )

        with patch(
            "azure.storage.blob._transfer_native._is_native_available",
            return_value=True,
        ), patch.dict(
            "sys.modules", {"azure.storage.extensions.transfer": native_module}
        ), self.assertRaisesRegex(
            ValueError, "native failure"
        ):
            try_native_download_eager(client, None, None, {}, None)

        native_download.assert_called_once()

    def test_download_forwards_supported_blob_options(self):
        stream = MagicMock(size=4)
        stream.__iter__.return_value = iter([b"data"])
        native_download = MagicMock(return_value=stream)
        native_module = ModuleType("azure.storage.extensions.transfer")
        native_module.download_blob = native_download

        credential = MagicMock()
        client = MagicMock(
            credential=credential,
            url="https://account.blob.core.windows.net/container/blob",
            blob_name="blob",
            container_name="container",
            version_id="client-version",
        )
        cpk = MagicMock(key_value="key", key_hash="hash", algorithm="AES256")
        lease = MagicMock(id="lease-id")
        modified_since = datetime(2024, 1, 2, 3, 4, 5, tzinfo=timezone.utc)
        unmodified_since = datetime(2024, 2, 3, 4, 5, 6, tzinfo=timezone.utc)

        with patch(
            "azure.storage.blob._transfer_native._is_native_available",
            return_value=True,
        ), patch.dict(
            "sys.modules", {"azure.storage.extensions.transfer": native_module}
        ):
            result = try_native_download_eager(
                client,
                10,
                20,
                {},
                None,
                cpk=cpk,
                lease=lease,
                etag='"etag"',
                match_condition=MatchConditions.IfNotModified,
                if_modified_since=modified_since,
                if_unmodified_since=unmodified_since,
                if_tags_match_condition="\"tag\" = 'value'",
                version_id="requested-version",
                timeout=30,
                max_concurrency=4,
            )

        self.assertIsNotNone(result)
        native_download.assert_called_once()
        forwarded = native_download.call_args.kwargs
        self.assertEqual(forwarded["offset"], 10)
        self.assertEqual(forwarded["length"], 20)
        self.assertEqual(forwarded["lease_id"], "lease-id")
        self.assertEqual(forwarded["encryption_key"], "key")
        self.assertEqual(forwarded["encryption_key_sha256"], "hash")
        self.assertEqual(forwarded["encryption_algorithm"], "AES256")
        self.assertEqual(forwarded["if_match"], '"etag"')
        self.assertIsNone(forwarded["if_none_match"])
        self.assertEqual(
            forwarded["if_modified_since"], int(modified_since.timestamp())
        )
        self.assertEqual(
            forwarded["if_unmodified_since"], int(unmodified_since.timestamp())
        )
        self.assertEqual(forwarded["if_tags"], "\"tag\" = 'value'")
        self.assertEqual(forwarded["version_id"], "requested-version")
        self.assertEqual(forwarded["timeout"], 30)
        self.assertEqual(forwarded["max_concurrency"], 4)


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
        tokens = [
            MagicMock(token="tok-1", expires_on=1),
            MagicMock(token="tok-2", expires_on=2),
        ]
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

    def test_upload_returns_none_only_when_extension_is_unavailable(self):
        client = MagicMock()
        config = MagicMock()

        with patch(
            "azure.storage.blob._transfer_native._is_native_available",
            return_value=False,
        ):
            result = try_native_upload(client, b"data", "BlockBlob", {}, None, config)

        self.assertIsNone(result)

    def test_upload_propagates_native_extension_failure(self):
        native_upload = MagicMock(side_effect=ValueError("native failure"))
        native_module = ModuleType("azure.storage.extensions.transfer")
        native_module.upload_blob = native_upload
        client = MagicMock(
            credential=MagicMock(),
            url="https://account.blob.core.windows.net/container/blob",
        )
        config = MagicMock(max_block_size=32)

        with patch(
            "azure.storage.blob._transfer_native._is_native_available",
            return_value=True,
        ), patch.dict(
            "sys.modules", {"azure.storage.extensions.transfer": native_module}
        ), self.assertRaisesRegex(
            ValueError, "native failure"
        ):
            try_native_upload(client, b"data", "BlockBlob", {}, None, config)

        native_upload.assert_called_once()

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
        ), patch.dict(
            "sys.modules", {"azure.storage.extensions.transfer": native_module}
        ):
            try_native_upload(first_client, b"first", "BlockBlob", {}, None, config)
            try_native_upload(first_client, b"again", "BlockBlob", {}, None, config)
            try_native_upload(second_client, b"second", "BlockBlob", {}, None, config)

        credential_ids = [
            call.kwargs["credential_id"] for call in native_upload.call_args_list
        ]
        self.assertEqual(
            credential_ids,
            [id(first_credential), id(first_credential), id(second_credential)],
        )
        self.assertNotEqual(credential_ids[0], credential_ids[2])

    def test_upload_forwards_supported_blob_options(self):
        native_upload = MagicMock(return_value={"etag": "etag"})
        native_module = ModuleType("azure.storage.extensions.transfer")
        native_module.upload_blob = native_upload

        credential = MagicMock()
        client = MagicMock(
            credential=credential,
            url="https://account.blob.core.windows.net/container/blob",
        )
        config = MagicMock(max_block_size=32)
        content_settings = MagicMock(
            content_type="text/plain",
            content_encoding="gzip",
            content_language="en-US",
            content_disposition="attachment",
            cache_control="no-cache",
            content_md5=bytearray(b"digest"),
        )
        cpk = MagicMock(key_value="key", key_hash="hash", algorithm="AES256")
        lease = MagicMock(id="lease-id")
        modified_since = datetime(2024, 1, 2, 3, 4, 5, tzinfo=timezone.utc)
        unmodified_since = datetime(2024, 2, 3, 4, 5, 6, tzinfo=timezone.utc)
        immutability_policy = MagicMock(
            expiry_time=datetime(2025, 1, 1, tzinfo=timezone.utc),
            policy_mode="Locked",
        )
        tier = MagicMock(value="Cool")

        with patch(
            "azure.storage.blob._transfer_native._is_native_available",
            return_value=True,
        ), patch.dict(
            "sys.modules", {"azure.storage.extensions.transfer": native_module}
        ):
            result = try_native_upload(
                client,
                b"data",
                "BlockBlob",
                {},
                None,
                config,
                overwrite=True,
                content_settings=content_settings,
                metadata={"meta": "value"},
                tags={"tag": "value"},
                lease=lease,
                cpk=cpk,
                encryption_scope="scope",
                etag='"etag"',
                match_condition=MatchConditions.IfNotModified,
                if_modified_since=modified_since,
                if_unmodified_since=unmodified_since,
                if_tags_match_condition="\"tag\" = 'value'",
                immutability_policy=immutability_policy,
                legal_hold=True,
                standard_blob_tier=tier,
                timeout=30,
                max_concurrency=4,
            )

        self.assertEqual(result, {"etag": "etag"})
        native_upload.assert_called_once()
        forwarded = native_upload.call_args.kwargs
        self.assertEqual(forwarded["content_type"], "text/plain")
        self.assertEqual(forwarded["content_encoding"], "gzip")
        self.assertEqual(forwarded["content_language"], "en-US")
        self.assertEqual(forwarded["content_disposition"], "attachment")
        self.assertEqual(forwarded["cache_control"], "no-cache")
        self.assertEqual(forwarded["content_md5"], b"digest")
        self.assertEqual(forwarded["metadata"], {"meta": "value"})
        self.assertEqual(forwarded["tags"], {"tag": "value"})
        self.assertEqual(forwarded["lease_id"], "lease-id")
        self.assertEqual(forwarded["encryption_key"], "key")
        self.assertEqual(forwarded["encryption_key_sha256"], "hash")
        self.assertEqual(forwarded["encryption_algorithm"], "AES256")
        self.assertEqual(forwarded["encryption_scope"], "scope")
        self.assertEqual(forwarded["if_match"], '"etag"')
        self.assertIsNone(forwarded["if_none_match"])
        self.assertEqual(
            forwarded["if_modified_since"], int(modified_since.timestamp())
        )
        self.assertEqual(
            forwarded["if_unmodified_since"], int(unmodified_since.timestamp())
        )
        self.assertEqual(forwarded["if_tags"], "\"tag\" = 'value'")
        self.assertEqual(
            forwarded["immutability_policy_expiry"],
            int(immutability_policy.expiry_time.timestamp()),
        )
        self.assertEqual(forwarded["immutability_policy_mode"], "Locked")
        self.assertTrue(forwarded["legal_hold"])
        self.assertEqual(forwarded["tier"], "Cool")
        self.assertEqual(forwarded["timeout"], 30)
        self.assertEqual(forwarded["max_concurrency"], 4)


class _FakeNativeStream:
    """Minimal stand-in for the native windowed download stream.

    Yields the provided windows and exposes ``size`` like the real native object. Single-pass,
    matching the native stream's semantics.
    """

    def __init__(self, windows, size=None):
        self._windows = iter(windows)
        self.size = size if size is not None else sum(len(w) for w in windows)

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
            stream=_FakeNativeStream(
                windows if windows is not None else [self.data], size=len(self.data)
            ),
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
