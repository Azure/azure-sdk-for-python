# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from io import BytesIO
from types import SimpleNamespace
from unittest import mock

import pytest
from azure.core.exceptions import HttpResponseError, ServiceResponseError
from azure.core.exceptions import DecodeError
from azure.storage.blob import BlobClient
from azure.storage.blob._deserialize import deserialize_blob_properties
from azure.storage.blob._download import _ChunkDownloader, process_content
from azure.storage.blob._download import _ChunkIterator, StorageStreamDownloader
from devtools_testutils.storage import StorageRecordedTestCase
from settings.testcase import BlobPreparer
from test_helpers import MockLegacyTransport


class _LockRecorder(object):
    def __init__(self):
        self.enter_count = 0

    def __enter__(self):
        self.enter_count += 1
        return self

    def __exit__(self, *args):
        return None


class TestStorageDownloadGaps(StorageRecordedTestCase):

    def _create_downloader(
        self,
        stream,
        parallel=None,
        total_size=8,
        chunk_size=4,
        current_progress=0,
        start_range=0,
        end_range=8,
        progress_hook=None,
    ):
        return _ChunkDownloader(
            client=mock.Mock(),
            total_size=total_size,
            chunk_size=chunk_size,
            current_progress=current_progress,
            start_range=start_range,
            end_range=end_range,
            validate_content=False,
            encryption_options={},
            stream=stream,
            parallel=parallel,
            progress_hook=progress_hook,
        )

    def test_process_content_when_response_is_none_raises_value_error(self):
        with pytest.raises(ValueError) as error:
            process_content(None, 0, 0, {})

        assert str(error.value) == "Response cannot be None."

    def test_process_chunk_when_downloaded_length_positive_writes_and_updates_progress(self):
        stream = BytesIO()
        downloader = self._create_downloader(
            stream=stream,
            total_size=4,
            chunk_size=10,
            current_progress=0,
            start_range=0,
            end_range=4,
        )

        # Tests defensive branch — requires mock.
        downloader._download_chunk = mock.Mock(return_value=(b"DATA", 4))

        downloader.process_chunk(0)

        assert stream.getvalue() == b"DATA"
        assert downloader.progress_total == 4
        downloader._download_chunk.assert_called_once_with(0, 3)

    def test_update_progress_when_parallel_enabled_calls_progress_hook_with_locked_total(self):
        stream = BytesIO()
        progress_hook = mock.Mock()
        downloader = self._create_downloader(
            stream=stream,
            parallel=2,
            total_size=10,
            current_progress=0,
            progress_hook=progress_hook,
        )
        lock = _LockRecorder()
        downloader.progress_lock = lock

        downloader._update_progress(3)

        assert lock.enter_count == 1
        progress_hook.assert_called_once_with(3, 10)

    def test_update_progress_when_parallel_enabled_increments_progress_total_inside_lock(self):
        stream = BytesIO()
        downloader = self._create_downloader(
            stream=stream,
            parallel=2,
            total_size=20,
            current_progress=5,
        )
        lock = _LockRecorder()
        downloader.progress_lock = lock

        downloader._update_progress(7)

        assert lock.enter_count == 1
        assert downloader.progress_total == 12

    def test_write_to_stream_when_parallel_enabled_seeks_before_writing(self):
        stream = BytesIO(b"0123456789")
        stream.seek(4)
        downloader = self._create_downloader(
            stream=stream,
            parallel=2,
            start_range=10,
            end_range=20,
        )
        lock = _LockRecorder()
        downloader.stream_lock = lock

        downloader._write_to_stream(b"AB", 12)

        assert lock.enter_count == 1
        assert stream.getvalue() == b"012345AB89"

    def _create_chunk_downloader(self, **kwargs):
        options = {
            "client": mock.Mock(),
            "total_size": 8,
            "chunk_size": 2,
            "current_progress": 0,
            "start_range": 0,
            "end_range": 8,
            "validate_content": False,
            "encryption_options": {},
        }
        options.update(kwargs)
        return _ChunkDownloader(**options)

    def _create_download_response(self, content_length=2):
        return SimpleNamespace(
            content_length=content_length,
            properties=SimpleNamespace(etag="etag", content_range="bytes 0-1/8"),
            response=SimpleNamespace(headers={}),
        )

    def test_write_to_stream_when_parallel_enabled_seeks_to_stream_start_plus_chunk_offset(self):
        stream = BytesIO(b"abcdefghij")
        stream.seek(len(b"abcdefghij"))
        downloader = self._create_chunk_downloader(
            stream=stream,
            parallel=2,
            start_range=1,
        )

        downloader._write_to_stream(b"Z", 4)

        assert stream.tell() == 14
        assert stream.getvalue().endswith(b"Z")

    def test_write_to_stream_when_parallel_enabled_writes_chunk_data_at_seeked_position(self):
        stream = BytesIO(b"prefix")
        stream.seek(len(b"prefix"))
        downloader = self._create_chunk_downloader(
            stream=stream,
            parallel=2,
            start_range=2,
        )

        downloader._write_to_stream(b"cd", 4)

        assert stream.getvalue() == b"prefix\x00\x00cd"

    def test_download_chunk_when_encryption_options_missing_raises_value_error(self):
        # Tests defensive branch — requires direct construction with invalid state.
        downloader = self._create_chunk_downloader(encryption_options=None)

        with pytest.raises(ValueError) as error:
            downloader._download_chunk(0, 1)

        assert str(error.value) == "Required argument is missing: encryption_options"

    def test_download_chunk_when_process_content_fails_once_retries_and_returns_chunk(self):
        # Tests defensive branch — requires mock.
        client = mock.Mock()
        response = self._create_download_response(content_length=2)
        client.download.return_value = (None, response)
        downloader = self._create_chunk_downloader(client=client)

        with mock.patch(
            "azure.storage.blob._download.process_content",
            side_effect=[ServiceResponseError("boom"), b"ok"],
        ), mock.patch("azure.storage.blob._download.time.sleep") as sleep_mock:
            chunk_data, content_length = downloader._download_chunk(0, 1)

        assert chunk_data == b"ok"
        assert content_length == 2
        assert client.download.call_count == 2
        assert sleep_mock.call_count == 1

    def test_download_chunk_when_process_content_keeps_failing_raises_after_three_attempts(self):
        # Tests defensive branch — requires mock.
        client = mock.Mock()
        response = self._create_download_response(content_length=2)
        client.download.return_value = (None, response)
        downloader = self._create_chunk_downloader(client=client)

        with mock.patch(
            "azure.storage.blob._download.process_content",
            side_effect=ServiceResponseError("boom"),
        ), mock.patch("azure.storage.blob._download.time.sleep") as sleep_mock:
            with pytest.raises(HttpResponseError) as error:
                downloader._download_chunk(0, 1)

        assert error.value.args[0] == "boom"
        assert client.download.call_count == 3
        assert sleep_mock.call_count == 2


class _FakeDownloadClient(object):
    def __init__(self, response):
        self.response = response
        self.calls = 0
        self.last_kwargs = None

    def download(self, **kwargs):
        self.calls += 1
        self.last_kwargs = kwargs
        return None, self.response


class _FakeBlobGetPropertiesClient(object):
    def __init__(self):
        self.kwargs = None

    def get_properties(self, **kwargs):
        self.kwargs = kwargs
        return SimpleNamespace(metadata={"encryptiondata": "value"})


class TestDownloadGaps(StorageRecordedTestCase):

    def test_download_chunk_when_process_content_keeps_failing_with_decode_error_raises_wrapped_http_response_error(self):
        response = SimpleNamespace(
            content_length=2,
            properties=SimpleNamespace(etag="etag-value"),
            response=SimpleNamespace(headers={})
        )
        client = _FakeDownloadClient(response)
        downloader = _ChunkDownloader(
            client=client,
            total_size=2,
            chunk_size=2,
            current_progress=0,
            start_range=0,
            end_range=2,
            validate_content=False,
            encryption_options={}
        )
        decode_error = DecodeError(message="bad decode")

        with mock.patch("azure.storage.blob._download.process_content", side_effect=decode_error), \
             mock.patch("azure.storage.blob._download.time.sleep", return_value=None):
            with pytest.raises(HttpResponseError) as error:
                downloader._download_chunk(0, 1)

        assert error.value.__cause__ is decode_error
        assert client.calls == 3

    def test_download_chunk_when_modified_access_conditions_present_sets_if_match_to_response_etag(self):
        response = SimpleNamespace(
            content_length=2,
            properties=SimpleNamespace(etag="etag-123"),
            response=SimpleNamespace(headers={})
        )
        client = _FakeDownloadClient(response)
        modified_access_conditions = SimpleNamespace(if_match=None)
        downloader = _ChunkDownloader(
            client=client,
            total_size=2,
            chunk_size=2,
            current_progress=0,
            start_range=0,
            end_range=2,
            validate_content=False,
            encryption_options={},
            modified_access_conditions=modified_access_conditions
        )

        with mock.patch("azure.storage.blob._download.process_content", return_value=b"ab"):
            chunk_data, content_length = downloader._download_chunk(0, 1)

        assert chunk_data == b"ab"
        assert content_length == 2
        assert modified_access_conditions.if_match == "etag-123"

    def test_next_when_no_downloader_and_current_content_exceeds_chunk_size_returns_first_chunk(self):
        iterator = _ChunkIterator(size=6, content=b"abcdef", downloader=None, chunk_size=4)

        first_chunk = next(iterator)
        second_chunk = next(iterator)

        assert first_chunk == b"abcd"
        assert second_chunk == b"ef"
        with pytest.raises(StopIteration, match="Download complete"):
            next(iterator)

    def test_get_encryption_data_request_when_decompress_provided_restores_request_option(self):
        download_cls = object()
        get_properties_client = _FakeBlobGetPropertiesClient()
        clients = SimpleNamespace(blob=get_properties_client)
        config = SimpleNamespace(max_single_get_size=4, max_chunk_get_size=2)

        def _fake_initial_request(self):
            self.size = 4
            self._file_size = 4
            self._current_content = b"data"
            return SimpleNamespace(
                properties=SimpleNamespace(
                    size=4,
                    content_range="bytes 0-3/4",
                    content_md5=None
                )
            )

        with mock.patch("azure.storage.blob._download.parse_encryption_data", return_value="parsed"), \
             mock.patch("azure.storage.blob._download.process_range_and_offset", return_value=((0, 3), (0, 0))), \
             mock.patch.object(StorageStreamDownloader, "_initial_request", _fake_initial_request):
            downloader = StorageStreamDownloader(
                clients=clients,
                config=config,
                encryption_options={"key": object()},
                name="blob",
                container="container",
                download_cls=download_cls,
                decompress=False
            )

        assert get_properties_client.kwargs["cls"] is deserialize_blob_properties
        assert "decompress" not in get_properties_client.kwargs
        assert downloader._request_options["decompress"] is False
        assert downloader._request_options["cls"] is download_cls

    @BlobPreparer()
    def test_initial_request_when_content_range_missing_raises_value_error(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        blob_client = BlobClient(
            self.account_url(storage_account_name, "blob"),
            container_name="container",
            blob_name="blob",
            credential=storage_account_key.secret,
            transport=MockLegacyTransport(),
            retry_total=0
        )

        with mock.patch("azure.storage.blob._download.parse_length_from_content_range", return_value=None):
            with pytest.raises(ValueError) as error:
                blob_client.download_blob()

        assert str(error.value) == "Required Content-Range response header is missing or malformed."


class _IterResponse(object):
    def __init__(self, body, content_range="bytes 0-3/4", blob_type="BlockBlob", etag="etag"):
        self._body = body
        self.content_length = len(body)
        self.properties = SimpleNamespace(content_range=content_range, blob_type=blob_type, etag=etag)
        self.response = SimpleNamespace(headers={})

    def __iter__(self):
        yield self._body


def _create_blob_client():
    return BlobClient(
        "https://fakename.blob.core.windows.net/account",
        container_name="container",
        blob_name="blob",
        credential="fake_key",
        max_single_get_size=32,
        max_chunk_get_size=4,
        retry_total=0,
    )


def _create_http_response(status_code, reason):
    return SimpleNamespace(status_code=status_code, reason=reason, headers={})


def _raise_http_response_error(error):
    raise error


def test_initial_request_when_empty_blob_fallback_download_raises_http_response_error():
    blob_client = _create_blob_client()
    initial_error = HttpResponseError(
        message="initial range request failed",
        response=_create_http_response(416, "Requested Range Not Satisfiable"),
    )
    fallback_error = HttpResponseError(
        message="fallback request failed",
        response=_create_http_response(500, "Internal Server Error"),
    )
    blob_client._client.blob.download = mock.Mock(side_effect=[initial_error, fallback_error])

    # Tests defensive branch — requires mock.
    with mock.patch("azure.storage.blob._download.process_storage_error", side_effect=_raise_http_response_error):
        with pytest.raises(HttpResponseError) as exc:
            blob_client.download_blob()

    assert exc.value is fallback_error
    assert blob_client._client.blob.download.call_count == 2
    assert "range" not in blob_client._client.blob.download.call_args_list[1].kwargs
    assert blob_client._client.blob.download.call_args_list[1].kwargs["data_stream_total"] == 0


def test_initial_request_when_empty_blob_fallback_download_fails_processes_storage_error():
    blob_client = _create_blob_client()
    initial_error = HttpResponseError(
        message="initial range request failed",
        response=_create_http_response(416, "Requested Range Not Satisfiable"),
    )
    fallback_error = HttpResponseError(
        message="fallback request failed",
        response=_create_http_response(500, "Internal Server Error"),
    )
    blob_client._client.blob.download = mock.Mock(side_effect=[initial_error, fallback_error])

    # Tests defensive branch — requires mock.
    with mock.patch(
        "azure.storage.blob._download.process_storage_error",
        side_effect=RuntimeError("processed storage error"),
    ) as process_storage_error:
        with pytest.raises(RuntimeError, match="processed storage error"):
            blob_client.download_blob()

    assert process_storage_error.call_count == 1
    assert process_storage_error.call_args.args[0] is fallback_error


def test_initial_request_when_page_blob_get_page_ranges_raises_http_response_error_returns_content():
    blob_client = _create_blob_client()
    blob_client._client.blob.download = mock.Mock(
        return_value=(None, _IterResponse(b"data", blob_type="PageBlob"))
    )
    blob_client._client.page_blob.get_page_ranges = mock.Mock(
        side_effect=HttpResponseError(
            message="page ranges failed",
            response=_create_http_response(500, "Internal Server Error"),
        )
    )

    stream = blob_client.download_blob()

    assert stream.readall() == b"data"
    assert blob_client._client.page_blob.get_page_ranges.call_count == 1


def test_initial_request_when_page_blob_get_page_ranges_raises_keeps_non_empty_ranges_unset():
    blob_client = _create_blob_client()
    blob_client._client.blob.download = mock.Mock(
        return_value=(None, _IterResponse(b"data", blob_type="PageBlob"))
    )
    blob_client._client.page_blob.get_page_ranges = mock.Mock(
        side_effect=HttpResponseError(
            message="page ranges failed",
            response=_create_http_response(500, "Internal Server Error"),
        )
    )

    stream = blob_client.download_blob()

    assert stream._non_empty_ranges is None
    assert stream.properties.size == 4


def test_chunks_when_encoding_specified_warns_and_returns_bytes_chunks():
    blob_client = _create_blob_client()
    blob_client._client.blob.download = mock.Mock(
        return_value=(None, _IterResponse(b"data", blob_type="BlockBlob"))
    )

    stream = blob_client.download_blob(encoding="utf-8")

    with pytest.warns(UserWarning, match="Encoding is ignored with chunks as only bytes are supported."):
        chunks = list(stream.chunks())

    assert chunks == [b"data"]
