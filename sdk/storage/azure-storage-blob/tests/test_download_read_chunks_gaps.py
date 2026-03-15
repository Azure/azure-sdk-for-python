# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from types import SimpleNamespace
from unittest import mock

import pytest
from azure.storage.blob import BlobClient


class _IterResponse(object):
    def __init__(self, body, content_range, blob_type="BlockBlob", etag="etag"):
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
        max_single_get_size=4,
        max_chunk_get_size=4,
        retry_total=0,
    )


def _download_side_effect(data):
    def _download(**kwargs):
        range_header = kwargs.get("range")
        assert range_header is not None
        start, end = [int(value) for value in range_header.replace("bytes=", "").split("-")]
        body = data[start:end + 1]
        return None, _IterResponse(body, f"bytes {start}-{end}/{len(data)}")

    return _download


def test_chunks_when_first_chunk_already_consumed_redownloads_from_start():
    data = b"abcdefgh"
    blob_client = _create_blob_client()
    blob_client._client.blob.download = mock.Mock(side_effect=_download_side_effect(data))

    stream = blob_client.download_blob()

    assert stream.read(5) == b"abcde"
    assert list(stream.chunks()) == [b"abcd", b"efgh"]


def test_chunks_when_first_chunk_false_sets_current_progress_to_zero():
    data = b"abcdefgh"
    blob_client = _create_blob_client()
    blob_client._client.blob.download = mock.Mock(side_effect=_download_side_effect(data))

    stream = blob_client.download_blob()
    assert stream.read(5) == b"abcde"

    captured = {}

    class FakeChunkDownloader(object):
        def __init__(self, **kwargs):
            captured.update(kwargs)

        def get_chunk_offsets(self):
            return iter(())

        def yield_chunk(self, chunk_start):
            return b"", 0

    # Tests defensive branch — requires mock.
    with mock.patch("azure.storage.blob._download._ChunkDownloader", FakeChunkDownloader):
        chunks = stream.chunks()

    assert captured["current_progress"] == 0
    assert captured["start_range"] == 0
    assert list(chunks) == []


def test_read_when_size_and_chars_specified_raises_value_error():
    blob_client = _create_blob_client()
    blob_client._client.blob.download = mock.Mock(return_value=(None, _IterResponse(b"data", "bytes 0-3/4")))

    stream = blob_client.download_blob()

    with pytest.raises(ValueError) as error:
        stream.read(1, chars=1)

    assert str(error.value) == "Cannot specify both size and chars."


def test_read_when_partially_read_in_bytes_mode_then_chars_raises_value_error():
    blob_client = _create_blob_client()
    blob_client._client.blob.download = mock.Mock(return_value=(None, _IterResponse(b"data", "bytes 0-3/4")))

    stream = blob_client.download_blob(encoding="utf-8")

    with pytest.warns(UserWarning, match="Size parameter specified with text encoding enabled."):
        assert stream.read(1) == "d"

    with pytest.raises(ValueError) as error:
        stream.read(chars=1)

    assert str(error.value) == "Stream has been partially read in bytes mode. Please use size."


def test_readall_when_parallel_and_multiple_chunks_remaining_uses_thread_pool_executor():
    data = b"abcdefghijkl"
    blob_client = _create_blob_client()
    blob_client._client.blob.download = mock.Mock(side_effect=_download_side_effect(data))
    captured = {}

    class FakeExecutor(object):
        def __init__(self, max_workers):
            captured["max_workers"] = max_workers

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return None

        def map(self, fn, iterable):
            items = list(iterable)
            captured["offsets"] = items
            return [fn(item) for item in items]

    with mock.patch("azure.storage.blob._download.with_current_context", new=lambda fn: fn), \
         mock.patch("concurrent.futures.ThreadPoolExecutor", FakeExecutor):
        stream = blob_client.download_blob(max_concurrency=2)
        content = stream.readall()

    assert content == data
    assert captured["max_workers"] == 2
    assert captured["offsets"] == [4, 8]
