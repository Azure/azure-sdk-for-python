# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""Pure unit tests for the Python native-transfer bridge, without the extension."""

import os
import unittest
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from io import BytesIO
from threading import Event, Lock
from types import ModuleType, SimpleNamespace
from unittest.mock import Mock, patch

from azure.core import MatchConditions
from azure.core.credentials import AccessToken, AzureSasCredential
from azure.core.exceptions import (
    AzureError,
    ClientAuthenticationError,
    DecodeError,
    HttpResponseError,
    IncompleteReadError,
    ResourceExistsError,
    ResourceModifiedError,
    ResourceNotFoundError,
    ServiceRequestError,
    ServiceResponseError,
)
from azure.storage.blob import (
    BlobImmutabilityPolicyMode,
    BlobType,
    ContentSettings,
    CustomerProvidedEncryptionKey,
    ImmutabilityPolicy,
    StandardBlobTier,
)
from azure.storage.blob._transfer_native import (
    _build_token_provider,
    _is_native_available,
    NativeStorageStreamDownloader,
    try_native_download_eager,
    try_native_upload,
)


_MODULE = "azure.storage.blob._transfer_native"
_EXTENSION = "azure.storage.extensions.transfer"
_DISABLE_ENV = "AZURE_STORAGE_DISABLE_NATIVE_TRANSFER"
_SCOPE = "https://storage.azure.com/.default"


class _FakeNativeTransferError(Exception):
    def __init__(
        self,
        message="native failure",
        *,
        kind="http",
        status_code=404,
        error_code=None,
        headers=None,
        body=None,
        request_id=None,
        additional_info=None,
        normalization_error=None,
    ):
        super().__init__(message)
        self.message = message
        self.kind = kind
        self.status_code = status_code
        self.error_code = error_code
        self.headers = headers or {}
        self.body = body
        self.request_id = request_id
        self.additional_info = additional_info or {}
        self.normalization_error = normalization_error


class _FakeNativeStream:
    """Single-pass native stream stand-in that records yielded windows."""

    def __init__(self, windows):
        self.size = sum(len(window) for window in windows)
        self._windows = iter(windows)
        self.events = []

    def __iter__(self):
        return self

    def __next__(self):
        window = next(self._windows)
        self.events.append(("next", window))
        return window


class _FakeNativeReadallStream(_FakeNativeStream):
    """Native stream stand-in that also implements the native ``readall`` fast path."""

    def __init__(self, windows, readall_error=None):
        super().__init__(windows)
        self.readall_error = readall_error

    def readall(self):
        self.events.append(("readall",))
        if self.readall_error is not None:
            raise self.readall_error
        return b"".join(self._windows)


class _NativeTransferTestCase(unittest.TestCase):
    def setUp(self):
        self.extension = ModuleType(_EXTENSION)
        self.extension.is_available = Mock(return_value=True)
        self.extension.NativeTransferError = _FakeNativeTransferError
        self.extension.upload_blob = Mock(return_value={"etag": '"etag"'})
        self.extension.download_blob = Mock(side_effect=lambda **kwargs: _FakeNativeStream([b"data"]))
        for patcher in (
            patch.dict("sys.modules", {_EXTENSION: self.extension}),
            patch.dict(os.environ),
        ):
            patcher.start()
            self.addCleanup(patcher.stop)
        os.environ.pop(_DISABLE_ENV, None)
        self.client = SimpleNamespace(
            credential=None,
            url="https://account.blob.core.windows.net/container/blob?sig=test",
            blob_name="blob",
            container_name="container",
            version_id=None,
            _config=SimpleNamespace(max_chunk_get_size=8),
        )
        self.config = SimpleNamespace(max_block_size=4)

    def upload(
        self,
        data=b"data",
        blob_type="BlockBlob",
        encryption_options=None,
        validate_content=None,
        **kwargs,
    ):
        return try_native_upload(
            self.client,
            data,
            blob_type,
            {} if encryption_options is None else encryption_options,
            validate_content,
            self.config,
            **kwargs,
        )

    def download(
        self,
        offset=None,
        length=None,
        encryption_options=None,
        validate_content=None,
        **kwargs,
    ):
        return try_native_download_eager(
            self.client,
            offset,
            length,
            {} if encryption_options is None else encryption_options,
            validate_content,
            **kwargs,
        )


class TestNativeAvailability(_NativeTransferTestCase):
    def test_missing_extension(self):
        with patch.dict("sys.modules", {_EXTENSION: None}):
            self.assertFalse(_is_native_available())

    def test_extension_availability_result(self):
        for available in (True, False):
            with self.subTest(available=available):
                self.extension.is_available.return_value = available
                self.assertIs(_is_native_available(), available)
        self.assertEqual(self.extension.is_available.call_count, 2)

    def test_disable_environment_values(self):
        for value in ("1", "true", "yes", "on", "  TrUe  "):
            with self.subTest(value=value):
                os.environ[_DISABLE_ENV] = value
                self.assertFalse(_is_native_available())
        self.extension.is_available.assert_not_called()

        for value in (None, "", "false"):
            with self.subTest(value=value):
                if value is None:
                    os.environ.pop(_DISABLE_ENV, None)
                else:
                    os.environ[_DISABLE_ENV] = value
                self.assertTrue(_is_native_available())
        self.assertEqual(self.extension.is_available.call_count, 3)

    def test_unavailable_short_circuits_validation_and_execution(self):
        for unavailable in ("missing", "unavailable", "disabled"):
            with self.subTest(unavailable=unavailable):
                self.extension.is_available.return_value = False
                os.environ[_DISABLE_ENV] = "true" if unavailable == "disabled" else ""
                module = None if unavailable == "missing" else self.extension
                with patch.dict("sys.modules", {_EXTENSION: module}):
                    self.client.credential = object()
                    self.assertIsNone(self.upload(data=BytesIO(), blob_type="PageBlob"))
                    self.assertIsNone(self.download(encoding="utf-8"))
        self.extension.upload_blob.assert_not_called()
        self.extension.download_blob.assert_not_called()


class TestNativeEligibility(_NativeTransferTestCase):
    def test_upload_supported_data_and_blob_types(self):
        for data in (b"data", "data", b"", ""):
            with self.subTest(data=data):
                self.assertIsNotNone(self.upload(data=data, validate_content=False))
        for blob_type in (BlobType.BLOCKBLOB, BlobType.BlockBlob, "BlockBlob"):
            with self.subTest(blob_type=blob_type):
                self.assertIsNotNone(self.upload(blob_type=blob_type))

    def test_upload_rejects_unsupported_inputs(self):
        cases = [
            ("page blob", {"blob_type": "PageBlob"}, "only block blobs"),
            ("append blob", {"blob_type": "AppendBlob"}, "only block blobs"),
            ("stream", {"data": BytesIO(b"data")}, "immutable bytes or str"),
            ("mutable buffer", {"data": bytearray(b"data")}, "immutable bytes or str"),
            ("buffer view", {"data": memoryview(b"data")}, "immutable bytes or str"),
            ("iterator", {"data": iter([b"data"])}, "immutable bytes or str"),
            (
                "encryption key",
                {"encryption_options": {"key": "key"}},
                "client-side encryption",
            ),
            (
                "encryption required",
                {"encryption_options": {"required": True}},
                "client-side encryption",
            ),
            ("validation", {"validate_content": True}, "content validation"),
            ("validation algorithm", {"validate_content": "md5"}, "content validation"),
            ("progress", {"progress_hook": Mock()}, "progress hooks"),
        ]
        for name, kwargs, reason in cases:
            with self.subTest(name=name), self.assertRaisesRegex(ValueError, reason):
                self.upload(**kwargs)
        self.extension.upload_blob.assert_not_called()

    def test_download_rejects_unsupported_options(self):
        cases = [
            (
                "encryption key",
                {"encryption_options": {"key": "key"}},
                "client-side encryption",
            ),
            (
                "encryption required",
                {"encryption_options": {"required": True}},
                "client-side encryption",
            ),
            (
                "encryption resolver",
                {"encryption_options": {"resolver": Mock()}},
                "client-side encryption",
            ),
            ("validation", {"validate_content": True}, "content validation"),
            (
                "validation algorithm",
                {"validate_content": "crc64"},
                "content validation",
            ),
            ("decompression", {"decompress": True}, "decompression"),
            ("encoding", {"encoding": "utf-8"}, "text encoding"),
            ("progress", {"progress_hook": Mock()}, "progress hooks"),
        ]
        for name, kwargs, reason in cases:
            with self.subTest(name=name), self.assertRaisesRegex(ValueError, reason):
                self.download(**kwargs)
        self.extension.download_blob.assert_not_called()

    def test_download_accepts_disabled_optional_features(self):
        self.assertIsInstance(
            self.download(
                validate_content=False,
                decompress=False,
                encoding=None,
                progress_hook=None,
            ),
            NativeStorageStreamDownloader,
        )

    def test_unsupported_credential_never_reaches_native_calls(self):
        self.client.credential = object()
        for transfer in (self.upload, self.download):
            with self.subTest(transfer=transfer.__name__), self.assertRaisesRegex(
                ValueError, "token credential or SAS credential"
            ):
                transfer()
        self.extension.upload_blob.assert_not_called()
        self.extension.download_blob.assert_not_called()


class TestNativeDispatch(_NativeTransferTestCase):
    def test_upload_defaults_and_result_passthrough(self):
        for response in ({"etag": '"etag"'}, {}):
            with self.subTest(response=response):
                self.extension.upload_blob.reset_mock()
                self.extension.upload_blob.return_value = response
                data = b"data"
                self.assertIs(self.upload(data=data), response)
                self.extension.upload_blob.assert_called_once()
                forwarded = self.extension.upload_blob.call_args.kwargs
                self.assertEqual(forwarded["url"], self.client.url)
                self.assertIs(forwarded["data"], data)
                self.assertIs(forwarded["overwrite"], False)
                self.assertEqual(forwarded["max_block_size"], 4)
                for key, value in forwarded.items():
                    if key not in ("url", "data", "overwrite", "max_block_size"):
                        self.assertIsNone(value, key)

    def test_upload_encodes_text_and_accepts_empty_bytes(self):
        for data, kwargs, expected in (
            (b"", {}, b""),
            ("caf\u00e9", {}, b"caf\xc3\xa9"),
            ("caf\u00e9", {"encoding": "latin-1"}, b"caf\xe9"),
        ):
            with self.subTest(data=data, kwargs=kwargs):
                self.upload(data=data, **kwargs)
                self.assertEqual(self.extension.upload_blob.call_args.kwargs["data"], expected)

    def test_invalid_upload_encoding_does_not_call_native(self):
        with self.assertRaises(LookupError):
            self.upload(data="text", encoding="not-a-real-encoding")
        self.extension.upload_blob.assert_not_called()

    def test_upload_forwards_supported_options(self):
        modified = datetime(2024, 1, 2, 3, 4, 5, tzinfo=timezone.utc)
        unmodified = datetime(2024, 2, 3, 4, 5, 6, tzinfo=timezone.utc)
        expiry = datetime(2025, 1, 1, tzinfo=timezone.utc)
        settings = ContentSettings(
            content_type="text/plain",
            content_encoding="gzip",
            content_language="en-US",
            content_disposition="attachment",
            cache_control="no-cache",
            content_md5=bytearray(b"digest"),
        )
        self.upload(
            overwrite=True,
            content_settings=settings,
            metadata={"meta": "value"},
            tags={"tag": "value"},
            lease=SimpleNamespace(id="lease-id"),
            cpk=CustomerProvidedEncryptionKey("key", "hash"),
            encryption_scope="scope",
            etag='"etag"',
            match_condition=MatchConditions.IfNotModified,
            if_modified_since=modified,
            if_unmodified_since=unmodified,
            if_tags_match_condition="\"tag\" = 'value'",
            immutability_policy=ImmutabilityPolicy(
                expiry_time=expiry,
                policy_mode=BlobImmutabilityPolicyMode.Locked,
            ),
            legal_hold=True,
            standard_blob_tier=StandardBlobTier.Cool,
            timeout=30,
            max_concurrency=4,
        )
        self.extension.upload_blob.assert_called_once()
        forwarded = self.extension.upload_blob.call_args.kwargs
        expected = {
            "url": self.client.url,
            "data": b"data",
            "token_provider": None,
            "credential_id": None,
            "overwrite": True,
            "content_type": "text/plain",
            "content_encoding": "gzip",
            "content_language": "en-US",
            "content_disposition": "attachment",
            "cache_control": "no-cache",
            "content_md5": b"digest",
            "metadata": {"meta": "value"},
            "tags": {"tag": "value"},
            "lease_id": "lease-id",
            "encryption_key": "key",
            "encryption_key_sha256": "hash",
            "encryption_algorithm": "AES256",
            "encryption_scope": "scope",
            "if_match": '"etag"',
            "if_none_match": None,
            "if_modified_since": int(modified.timestamp()),
            "if_unmodified_since": int(unmodified.timestamp()),
            "if_tags": "\"tag\" = 'value'",
            "immutability_policy_expiry": int(expiry.timestamp()),
            "immutability_policy_mode": BlobImmutabilityPolicyMode.Locked.value,
            "legal_hold": True,
            "tier": "Cool",
            "timeout": 30,
            "max_concurrency": 4,
            "max_block_size": 4,
        }
        self.assertEqual(forwarded, expected)
        self.assertIsInstance(forwarded["content_md5"], bytes)
        self.assertIs(type(forwarded["immutability_policy_mode"]), str)
        self.assertIs(type(forwarded["tier"]), str)

    def test_upload_plain_string_policy_and_tier(self):
        self.upload(
            immutability_policy=ImmutabilityPolicy(policy_mode="Locked"),
            standard_blob_tier="Cool",
        )
        forwarded = self.extension.upload_blob.call_args.kwargs
        self.assertEqual(forwarded["immutability_policy_mode"], "Locked")
        self.assertIsNone(forwarded["immutability_policy_expiry"])
        self.assertEqual(forwarded["tier"], "Cool")

    def test_download_defaults_and_returned_wrapper(self):
        result = self.download()
        self.extension.download_blob.assert_called_once()
        forwarded = self.extension.download_blob.call_args.kwargs
        self.assertEqual(forwarded["url"], self.client.url)
        self.assertEqual(forwarded["max_chunk_size"], 8)
        for key, value in forwarded.items():
            if key not in ("url", "max_chunk_size"):
                self.assertIsNone(value, key)
        self.assertIsInstance(result, NativeStorageStreamDownloader)
        self.assertEqual((result.name, result.container, result.size), ("blob", "container", 4))
        self.assertIsNone(result.properties)
        self.assertEqual(result.readall(), b"data")

    def test_download_forwards_supported_options(self):
        modified = datetime(2024, 1, 2, 3, 4, 5, tzinfo=timezone.utc)
        unmodified = datetime(2024, 2, 3, 4, 5, 6, tzinfo=timezone.utc)
        self.download(
            offset=10,
            length=20,
            lease="lease-id",
            cpk=CustomerProvidedEncryptionKey("key", "hash"),
            etag='"etag"',
            match_condition=MatchConditions.IfNotModified,
            if_modified_since=modified,
            if_unmodified_since=unmodified,
            if_tags_match_condition="\"tag\" = 'value'",
            version_id="requested-version",
            timeout=30,
            max_concurrency=4,
        )
        self.extension.download_blob.assert_called_once_with(
            url=self.client.url,
            token_provider=None,
            credential_id=None,
            offset=10,
            length=20,
            lease_id="lease-id",
            encryption_key="key",
            encryption_key_sha256="hash",
            encryption_algorithm="AES256",
            if_match='"etag"',
            if_none_match=None,
            if_modified_since=int(modified.timestamp()),
            if_unmodified_since=int(unmodified.timestamp()),
            if_tags="\"tag\" = 'value'",
            version_id="requested-version",
            timeout=30,
            max_concurrency=4,
            max_chunk_size=8,
        )

    def test_download_version_selection_and_zero_range(self):
        self.client.version_id = "client-version"
        for kwargs, expected in (
            ({}, "client-version"),
            ({"version_id": "requested-version"}, "requested-version"),
            ({"version_id": None}, None),
        ):
            with self.subTest(kwargs=kwargs):
                self.download(offset=0, length=0, **kwargs)
                forwarded = self.extension.download_blob.call_args.kwargs
                self.assertEqual(forwarded["version_id"], expected)
                self.assertEqual(forwarded["offset"], 0)
                self.assertEqual(forwarded["length"], 0)

    def test_conditions_and_timestamp_conversion(self):
        naive = datetime(2024, 1, 1)
        aware = datetime(2024, 1, 1, 2, tzinfo=timezone(timedelta(hours=2)))
        expected_timestamp = int(datetime(2024, 1, 1, tzinfo=timezone.utc).timestamp())
        for transfer, native in (
            (self.upload, self.extension.upload_blob),
            (self.download, self.extension.download_blob),
        ):
            with self.subTest(transfer=transfer.__name__):
                transfer(
                    etag='"other"',
                    match_condition=MatchConditions.IfModified,
                    if_modified_since=naive,
                    if_unmodified_since=aware,
                )
                forwarded = native.call_args.kwargs
                self.assertIsNone(forwarded["if_match"])
                self.assertEqual(forwarded["if_none_match"], '"other"')
                self.assertEqual(forwarded["if_modified_since"], expected_timestamp)
                self.assertEqual(forwarded["if_unmodified_since"], expected_timestamp)

    def test_supported_credentials_and_callback_wiring(self):
        token_credential = Mock(spec=["get_token"])
        token_credential.get_token.return_value = AccessToken("token", 123)
        for credential in (
            None,
            "sig=test",
            AzureSasCredential("sig=test"),
            token_credential,
        ):
            self.client.credential = credential
            for transfer, native in (
                (self.upload, self.extension.upload_blob),
                (self.download, self.extension.download_blob),
            ):
                with self.subTest(credential=type(credential).__name__, transfer=transfer.__name__):
                    transfer()
                    forwarded = native.call_args.kwargs
                    if credential is token_credential:
                        self.assertEqual(forwarded["credential_id"], id(credential))
                        self.assertTrue(callable(forwarded["token_provider"]))
                        self.assertEqual(forwarded["token_provider"](["scope"]), ("token", 123))
                    else:
                        self.assertIsNone(forwarded["credential_id"])
                        self.assertIsNone(forwarded["token_provider"])
        self.assertEqual(token_credential.get_token.call_count, 2)
        token_credential.get_token.assert_called_with("scope")

    def test_credential_identity_is_stable_and_distinct(self):
        first, second = Mock(spec=["get_token"]), Mock(spec=["get_token"])
        for transfer, native in (
            (self.upload, self.extension.upload_blob),
            (self.download, self.extension.download_blob),
        ):
            with self.subTest(transfer=transfer.__name__):
                for credential in (first, first, second):
                    self.client.credential = credential
                    transfer()
                self.assertEqual(
                    [call.kwargs["credential_id"] for call in native.call_args_list],
                    [id(first), id(first), id(second)],
                )

    def test_native_errors_propagate_without_fallback(self):
        for transfer, native in (
            (self.upload, self.extension.upload_blob),
            (self.download, self.extension.download_blob),
        ):
            with self.subTest(transfer=transfer.__name__):
                failure = ValueError("native failure")
                native.side_effect = failure
                with self.assertRaises(ValueError) as caught:
                    transfer()
                self.assertIs(caught.exception, failure)
                native.assert_called_once()


class TestBuildTokenProvider(unittest.TestCase):
    def test_non_token_credentials_have_no_provider(self):
        for credential in (None, "sig=test", AzureSasCredential("sig=test"), object()):
            with self.subTest(credential=type(credential).__name__):
                self.assertIsNone(_build_token_provider(credential))

    def test_requested_scopes_and_fresh_tokens(self):
        credential = Mock(spec=["get_token"])
        credential.get_token.side_effect = [
            SimpleNamespace(token="first", expires_on=123.9),
            AccessToken("second", 456),
        ]
        provider = _build_token_provider(credential)
        token, expiry = provider(["scope-a", "scope-b"])
        self.assertEqual((token, expiry), ("first", 123))
        self.assertIsInstance(expiry, int)
        self.assertEqual(provider(["scope-a", "scope-b"]), ("second", 456))
        self.assertEqual(credential.get_token.call_count, 2)
        for call in credential.get_token.call_args_list:
            self.assertEqual(call.args, ("scope-a", "scope-b"))
            self.assertEqual(call.kwargs, {})

    def test_default_scope(self):
        for scopes in ([], None):
            with self.subTest(scopes=scopes):
                credential = Mock(spec=["get_token"])
                credential.get_token.return_value = AccessToken("token", 123)
                self.assertEqual(_build_token_provider(credential)(scopes), ("token", 123))
                credential.get_token.assert_called_once_with(_SCOPE)

    def test_credential_failure_propagates_and_releases_lock(self):
        failure = RuntimeError("credential failure")
        credential = Mock(spec=["get_token"])
        credential.get_token.side_effect = [failure, AccessToken("recovered", 123)]
        lock = Lock()
        with patch(f"{_MODULE}.threading.Lock", return_value=lock):
            provider = _build_token_provider(credential)
        with self.assertRaises(RuntimeError) as caught:
            provider(["scope"])
        self.assertIs(caught.exception, failure)
        self.assertTrue(lock.acquire(blocking=False), "Credential failure left the provider locked")
        lock.release()
        self.assertEqual(provider(["scope"]), ("recovered", 123))

    def test_concurrent_callbacks_are_serialized(self):
        first_entered, release_first, second_attempted = Event(), Event(), Event()
        lock = Lock()
        calls = []

        class ObservedLock:
            def __enter__(self):
                if first_entered.is_set():
                    second_attempted.set()
                return lock.__enter__()

            def __exit__(self, *args):
                return lock.__exit__(*args)

        def get_token(*scopes):
            calls.append(scopes)
            if len(calls) == 1:
                first_entered.set()
                if not release_first.wait(timeout=5):
                    raise AssertionError("First callback was not released")
            return AccessToken("token", 123)

        credential = SimpleNamespace(get_token=get_token)
        with patch(f"{_MODULE}.threading.Lock", return_value=ObservedLock()):
            provider = _build_token_provider(credential)

        with ThreadPoolExecutor(max_workers=2) as executor:
            first = executor.submit(provider, ["first"])
            try:
                self.assertTrue(first_entered.wait(timeout=5))
                second = executor.submit(provider, ["second"])
                self.assertTrue(second_attempted.wait(timeout=5))
                self.assertEqual(calls, [("first",)])
            finally:
                release_first.set()
            self.assertEqual(first.result(timeout=5), ("token", 123))
            self.assertEqual(second.result(timeout=5), ("token", 123))
        self.assertEqual(calls, [("first",), ("second",)])


class TestNativeStorageStreamDownloader(_NativeTransferTestCase):
    def make_downloader(self, windows):
        stream = _FakeNativeStream(windows)
        return NativeStorageStreamDownloader(stream, "blob", "container"), stream

    def test_metadata_and_length(self):
        downloader, _ = self.make_downloader([b"ab", b"c"])
        self.assertEqual((downloader.name, downloader.container), ("blob", "container"))
        self.assertEqual(downloader.size, 3)
        self.assertEqual(len(downloader), 3)
        self.assertIsNone(downloader.properties)

    def test_consumption_and_eof(self):
        for windows in ([], [b"abcde"], [b"ab", b"c", b"de"]):
            for method in ("readall", "chunks", "iter", "readinto"):
                with self.subTest(windows=windows, method=method):
                    downloader, _ = self.make_downloader(windows)
                    expected = b"".join(windows)
                    if method == "readinto":
                        destination = BytesIO()
                        self.assertEqual(downloader.readinto(destination), len(expected))
                        self.assertEqual(destination.getvalue(), expected)
                        self.assertEqual(downloader.readinto(BytesIO()), 0)
                    elif method in ("chunks", "iter"):
                        chunks = list(downloader if method == "iter" else downloader.chunks())
                        self.assertEqual(chunks, windows)
                        self.assertEqual(list(downloader.chunks()), [])
                    else:
                        self.assertEqual(downloader.readall(), expected)
                        self.assertEqual(downloader.readall(), b"")
                    self.assertEqual(downloader.read(1), b"")

    def test_sized_reads_and_lazy_window_consumption(self):
        downloader, stream = self.make_downloader([b"ab", b"cde", b"fg"])
        self.assertEqual(stream.events, [])
        self.assertEqual(downloader.read(0), b"")
        self.assertEqual(stream.events, [])
        self.assertEqual(downloader.read(2), b"ab")
        self.assertEqual(stream.events, [("next", b"ab")])
        self.assertEqual(downloader.read(4), b"cdef")
        self.assertEqual(len(stream.events), 3)
        self.assertEqual(downloader.read(0), b"")
        self.assertEqual(downloader.read(10), b"g")
        self.assertEqual(downloader.read(1), b"")
        self.assertEqual(downloader.read(1), b"")

    def test_unbounded_reads_consume_buffer_and_remaining_windows(self):
        for args in ((), (None,), (-1,), (-2,)):
            with self.subTest(args=args):
                downloader, _ = self.make_downloader([b"ab", b"cde"])
                self.assertEqual(downloader.read(1), b"a")
                self.assertEqual(downloader.read(*args), b"bcde")
                self.assertEqual(downloader.read(*args), b"")

    def test_partial_read_then_other_consumption_methods(self):
        for method in ("readall", "chunks", "readinto"):
            with self.subTest(method=method):
                downloader, _ = self.make_downloader([b"ab", b"cde", b"f"])
                self.assertEqual(downloader.read(1), b"a")
                if method == "chunks":
                    self.assertEqual(list(downloader.chunks()), [b"b", b"cde", b"f"])
                elif method == "readinto":
                    destination = BytesIO()
                    self.assertEqual(downloader.readinto(destination), 5)
                    self.assertEqual(destination.getvalue(), b"bcdef")
                else:
                    self.assertEqual(downloader.readall(), b"bcdef")
                self.assertEqual(downloader.readall(), b"")
                self.assertEqual(list(downloader.chunks()), [])

    def test_chunks_are_lazy(self):
        downloader, stream = self.make_downloader([b"ab", b"cde"])
        chunks = downloader.chunks()
        self.assertEqual(stream.events, [])
        self.assertEqual(next(chunks), b"ab")
        self.assertEqual(stream.events, [("next", b"ab")])
        self.assertEqual(next(chunks), b"cde")
        self.assertEqual(list(chunks), [])

    def test_readinto_writes_each_window_before_fetching_next(self):
        downloader, stream = self.make_downloader([b"ab", b"cde", b"f"])
        self.assertEqual(downloader.read(1), b"a")
        stream.events.clear()

        def write(data):
            stream.events.append(("write", bytes(data)))
            return len(data)

        self.assertEqual(downloader.readinto(SimpleNamespace(write=write)), 5)
        self.assertEqual(
            stream.events,
            [
                ("write", b"b"),
                ("next", b"cde"),
                ("write", b"cde"),
                ("next", b"f"),
                ("write", b"f"),
            ],
        )

    def test_stream_errors_propagate_from_consumption_methods(self):
        for method in ("readall", "read", "chunks", "readinto"):
            with self.subTest(method=method):
                failure = ValueError("incomplete native download")

                def windows():
                    yield b"first"
                    raise failure

                stream = Mock(size=10, spec=["size", "__iter__"])
                # A generator models a one-shot failure without implementing Rust error state.
                stream.__iter__ = Mock(return_value=windows())
                downloader = NativeStorageStreamDownloader(stream, "blob", "container")
                self.assertEqual(downloader.read(2), b"fi")
                destination = BytesIO()
                with self.assertRaises(ValueError) as caught:
                    if method == "chunks":
                        list(downloader.chunks())
                    elif method == "readinto":
                        downloader.readinto(destination)
                    else:
                        getattr(downloader, method)()
                self.assertIs(caught.exception, failure)
                if method == "readinto":
                    self.assertEqual(destination.getvalue(), b"rst")

    def test_destination_write_error_propagates(self):
        downloader, _ = self.make_downloader([b"data"])
        failure = OSError("destination failed")
        destination = Mock(spec=["write"])
        destination.write.side_effect = failure
        with self.assertRaises(OSError) as caught:
            downloader.readinto(destination)
        self.assertIs(caught.exception, failure)
        destination.write.assert_called_once_with(b"data")

    def test_readall_uses_native_readall_when_available(self):
        stream = _FakeNativeReadallStream([b"ab", b"cde"])
        downloader = NativeStorageStreamDownloader(stream, "blob", "container")
        self.assertEqual(downloader.readall(), b"abcde")
        self.assertEqual(stream.events, [("readall",)])
        self.assertEqual(downloader.readall(), b"")
        self.assertEqual(downloader.read(1), b"")
        self.assertEqual(list(downloader.chunks()), [])

    def test_native_readall_after_partial_read_prepends_buffered_bytes(self):
        stream = _FakeNativeReadallStream([b"ab", b"cde", b"f"])
        downloader = NativeStorageStreamDownloader(stream, "blob", "container")
        self.assertEqual(downloader.read(1), b"a")
        self.assertEqual(downloader.readall(), b"bcdef")
        self.assertEqual(stream.events, [("next", b"ab"), ("readall",)])
        self.assertEqual(downloader.readall(), b"")
        self.assertEqual(downloader.read(1), b"")

    def test_native_readall_non_native_errors_propagate(self):
        failure = ValueError("unexpected failure")
        stream = _FakeNativeReadallStream([b"data"], readall_error=failure)
        downloader = NativeStorageStreamDownloader(stream, "blob", "container")
        with self.assertRaises(ValueError) as caught:
            downloader.readall()
        self.assertIs(caught.exception, failure)


class TestNativeErrorMapping(_NativeTransferTestCase):
    def test_http_diagnostics_remain_on_native_cause_without_response(self):
        body = b'{"error":{"code":"InternalError","message":"service failure"}}'
        failure = _FakeNativeTransferError(
            "original native message",
            status_code=500,
            error_code="InternalError",
            headers={"content-type": "application/json", "x-ms-request-id": "request-id"},
            body=body,
            request_id="request-id",
            normalization_error="Could not parse XML",
        )
        self.extension.download_blob.side_effect = failure
        with self.assertRaises(HttpResponseError) as caught:
            self.download()
        error = caught.exception
        self.assertIsNone(error.response)
        self.assertIsNone(error.inner_exception)
        self.assertIs(error.__cause__, failure)
        self.assertEqual(error.message, "original native message")
        self.assertEqual(error.request_id, "request-id")
        self.assertEqual(error.__cause__.body, body)
        self.assertEqual(error.__cause__.headers["x-ms-request-id"], "request-id")
        self.assertEqual(error.__cause__.normalization_error, "Could not parse XML")

    def test_http_mapping_uses_normalized_fields(self):
        cases = [
            (401, None, ClientAuthenticationError),
            (403, "AuthenticationFailed", ClientAuthenticationError),
            (403, "InvalidAuthenticationInfo", ClientAuthenticationError),
            (403, "AuthorizationPermissionMismatch", HttpResponseError),
            (404, "BlobNotFound", ResourceNotFoundError),
            (404, "ContainerNotFound", ResourceNotFoundError),
            (500, "ResourceNotFound", ResourceNotFoundError),
            (500, "CannotVerifyCopySource", ResourceNotFoundError),
            (409, "BlobAlreadyExists", ResourceExistsError),
            (409, "ContainerAlreadyExists", ResourceExistsError),
            (409, "AccountAlreadyExists", ResourceExistsError),
            (409, "AccountBeingCreated", ResourceExistsError),
            (409, "ResourceAlreadyExists", ResourceExistsError),
            (409, "ResourceTypeMismatch", ResourceExistsError),
            (409, "ContainerBeingDeleted", ResourceExistsError),
            (409, "LeaseAlreadyPresent", HttpResponseError),
            (409, None, HttpResponseError),
            (412, "ConditionNotMet", ResourceModifiedError),
            (412, "BlobOverwritten", ResourceModifiedError),
            (412, "LeaseIdMismatchWithBlobOperation", HttpResponseError),
            (416, "InvalidRange", HttpResponseError),
            (429, "TooManyRequests", HttpResponseError),
            (500, "InternalError", HttpResponseError),
            (599, "FutureServiceCode", HttpResponseError),
            (404, "ConditionNotMet", ResourceModifiedError),
            (409, "AuthenticationFailed", ClientAuthenticationError),
        ]
        for status, code, expected in cases:
            for operation in (self.upload, self.download):
                with self.subTest(status=status, code=code, operation=operation):
                    failure = _FakeNativeTransferError(
                        "service message",
                        status_code=status,
                        error_code=code,
                        additional_info={"Detail": "extra info", "reason": "reason"},
                        request_id="request-id",
                    )
                    self.extension.upload_blob.side_effect = failure
                    self.extension.download_blob.side_effect = failure
                    with self.assertRaises(expected) as caught:
                        operation()
                    error = caught.exception
                    self.assertIs(type(error), expected)
                    self.assertIsNone(error.response)
                    self.assertEqual(error.status_code, status)
                    self.assertEqual(error.error_code, code)
                    self.assertEqual(error.message, "service message")
                    self.assertEqual(error.additional_info, failure.additional_info)
                    self.assertEqual(error.request_id, "request-id")
                    self.assertIsNone(error.inner_exception)
                    self.assertIs(error.__cause__, failure)

    def test_missing_or_unparseable_http_details(self):
        for body in (None, b"", b"not xml", b"\xff"):
            for code in (None, "UnknownCode"):
                for status, expected in (
                    (404, ResourceNotFoundError),
                    (500, HttpResponseError),
                ):
                    with self.subTest(body=body, code=code, status=status):
                        self.extension.download_blob.side_effect = _FakeNativeTransferError(
                            status_code=status,
                            error_code=code,
                            body=body,
                            normalization_error="parse failure" if body else None,
                        )
                        with self.assertRaises(expected) as caught:
                            self.download()
                        self.assertIs(type(caught.exception), expected)
                        self.assertEqual(caught.exception.status_code, status)
                        self.assertEqual(caught.exception.error_code, code)
                        self.assertIsNone(caught.exception.response)
                        self.assertIsNone(caught.exception.inner_exception)
                        self.assertIsNone(caught.exception.request_id)
                        self.assertEqual(caught.exception.__cause__.body, body)

    def test_python_does_not_reparse_raw_diagnostics(self):
        self.extension.download_blob.side_effect = _FakeNativeTransferError(
            status_code=412,
            error_code="ConditionNotMet",
            headers={
                "content-type": "application/xml",
                "x-ms-error-code": "LeaseIdMismatchWithBlobOperation",
            },
            body=b"<Error><Code>LeaseIdMismatchWithBlobOperation</Code><Message>lease failure</Message></Error>",
        )
        with self.assertRaises(ResourceModifiedError) as caught:
            self.download()
        self.assertEqual(caught.exception.error_code, "ConditionNotMet")
        self.assertEqual(caught.exception.message, "native failure")

    def test_conditions_are_not_rewritten_based_on_overwrite(self):
        for overwrite in (False, True):
            for conditions in (
                {},
                {"etag": '"etag"', "match_condition": MatchConditions.IfNotModified},
            ):
                with self.subTest(overwrite=overwrite, conditions=conditions):
                    self.extension.upload_blob.side_effect = _FakeNativeTransferError(
                        status_code=412,
                        error_code="ConditionNotMet",
                    )
                    with self.assertRaises(ResourceModifiedError) as caught:
                        self.upload(overwrite=overwrite, **conditions)
                    self.assertEqual(caught.exception.status_code, 412)
                    self.assertEqual(caught.exception.error_code, "ConditionNotMet")

    def test_non_http_categories(self):
        for kind, expected in (
            ("connection", ServiceRequestError),
            ("io", ServiceResponseError),
            ("incomplete_read", IncompleteReadError),
            ("data_conversion", DecodeError),
            ("credential", ClientAuthenticationError),
            ("other", AzureError),
            ("future_kind", AzureError),
        ):
            for operation in (self.upload, self.download):
                with self.subTest(kind=kind, operation=operation):
                    failure = _FakeNativeTransferError(
                        kind=kind,
                        status_code=None,
                    )
                    self.extension.upload_blob.side_effect = failure
                    self.extension.download_blob.side_effect = failure
                    with self.assertRaises(expected) as caught:
                        operation()
                    self.assertIs(type(caught.exception), expected)
                    self.assertIsNone(caught.exception.inner_exception)
                    self.assertIs(caught.exception.__cause__, failure)

    def test_later_stream_failures_are_terminal_for_all_consumers(self):
        for method in ("read", "readall", "readinto", "chunks", "iter"):
            with self.subTest(method=method):
                failure = _FakeNativeTransferError(
                    "short response",
                    kind="incomplete_read",
                )
                advances = []

                def windows():
                    advances.append("first")
                    yield b"first"
                    advances.append("failure")
                    raise failure

                stream = Mock(size=10, spec=["size", "__iter__"])
                stream.__iter__ = Mock(return_value=windows())
                self.extension.download_blob.side_effect = None
                self.extension.download_blob.return_value = stream
                downloader = self.download()
                self.assertEqual(downloader.read(2), b"fi")
                destination = BytesIO()
                with self.assertRaises(IncompleteReadError) as caught:
                    if method == "readinto":
                        downloader.readinto(destination)
                    elif method == "chunks":
                        list(downloader.chunks())
                    elif method == "iter":
                        list(downloader)
                    else:
                        getattr(downloader, method)()
                if method == "readinto":
                    self.assertEqual(destination.getvalue(), b"rst")
                for consume in (
                    downloader.readall,
                    lambda: downloader.read(1),
                    lambda: list(downloader.chunks()),
                    lambda: list(downloader),
                    lambda: downloader.readinto(BytesIO()),
                ):
                    with self.assertRaises(IncompleteReadError) as repeated:
                        consume()
                    self.assertIs(repeated.exception, caught.exception)
                self.assertEqual(advances, ["first", "failure"])

    def test_native_readall_failures_are_mapped_and_terminal(self):
        for partial in (False, True):
            with self.subTest(partial=partial):
                failure = _FakeNativeTransferError("short response", kind="incomplete_read")
                stream = _FakeNativeReadallStream([b"first", b"second"], readall_error=failure)
                self.extension.download_blob.side_effect = None
                self.extension.download_blob.return_value = stream
                downloader = self.download()
                if partial:
                    self.assertEqual(downloader.read(2), b"fi")
                with self.assertRaises(IncompleteReadError) as caught:
                    downloader.readall()
                self.assertIs(caught.exception.__cause__, failure)
                for consume in (
                    downloader.readall,
                    lambda: downloader.read(1),
                    lambda: list(downloader.chunks()),
                    lambda: list(downloader),
                    lambda: downloader.readinto(BytesIO()),
                ):
                    with self.assertRaises(IncompleteReadError) as repeated:
                        consume()
                    self.assertIs(repeated.exception, caught.exception)
                self.assertEqual(stream.events.count(("readall",)), 1)

    def test_destination_native_shaped_error_is_not_translated(self):
        downloader = self.download()
        failure = _FakeNativeTransferError()
        destination = Mock()
        destination.write.side_effect = failure
        with self.assertRaises(_FakeNativeTransferError) as caught:
            downloader.readinto(destination)
        self.assertIs(caught.exception, failure)

    def test_incompatible_extension_is_explicit(self):
        del self.extension.NativeTransferError
        for operation in (self.upload, self.download):
            with self.subTest(operation=operation):
                with self.assertRaisesRegex(RuntimeError, "compatible"):
                    operation()
        self.extension.upload_blob.assert_not_called()
        self.extension.download_blob.assert_not_called()


if __name__ == "__main__":
    unittest.main()
