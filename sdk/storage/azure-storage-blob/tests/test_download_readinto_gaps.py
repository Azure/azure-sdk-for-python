# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from io import BytesIO
from types import SimpleNamespace
from unittest import mock

import pytest

from azure.storage.blob._download import StorageStreamDownloader


class NonSeekableWriteStream(object):
    def __init__(self):
        self._buffer = BytesIO()

    def seekable(self):
        return False

    def write(self, data):
        return self._buffer.write(data)


class SeekNotImplementedWriteStream(object):
    def seekable(self):
        return True

    def tell(self):
        return 0

    def seek(self, *args, **kwargs):
        raise NotImplementedError("boom!")

    def write(self, data):
        return len(data)


class TellAttributeErrorWriteStream(object):
    def seekable(self):
        return True

    def tell(self):
        raise AttributeError("boom!")

    def seek(self, *args, **kwargs):
        return 0

    def write(self, data):
        return len(data)


def _create_downloader(
    *,
    encoding=None,
    max_concurrency=1,
    size=0,
    read_offset=0,
    current_content=b"",
    current_content_offset=0,
    progress_hook=None,
    download_offset=None,
    raw_download_offset=None,
):
    downloader = StorageStreamDownloader.__new__(StorageStreamDownloader)
    downloader.name = "blob"
    downloader.container = "container"
    downloader.size = size
    downloader._clients = SimpleNamespace(blob=mock.Mock())
    downloader._config = SimpleNamespace(max_chunk_get_size=4)
    downloader._start_range = None
    downloader._end_range = None
    downloader._max_concurrency = max_concurrency
    downloader._encoding = encoding
    downloader._validate_content = False
    downloader._encryption_options = {}
    downloader._progress_hook = progress_hook
    downloader._request_options = {}
    downloader._response = None
    downloader._location_mode = None
    downloader._current_content = current_content
    downloader._file_size = size
    downloader._non_empty_ranges = None
    downloader._encryption_data = None
    downloader._download_offset = size if download_offset is None else download_offset
    downloader._raw_download_offset = size if raw_download_offset is None else raw_download_offset
    downloader._read_offset = read_offset
    downloader._current_content_offset = current_content_offset
    downloader._text_mode = False
    downloader._decoder = None
    downloader._first_chunk = True
    downloader._download_start = 0
    return downloader


def test_readinto_when_encoding_specified_warns_and_returns_zero_for_empty_download():
    downloader = _create_downloader(encoding="utf-8", size=0)
    stream = BytesIO()

    with pytest.warns(UserWarning, match="Encoding is ignored with readinto as only byte streams are supported."):
        result = downloader.readinto(stream)

    assert result == 0
    assert stream.getvalue() == b""


def test_readinto_when_parallel_stream_not_seekable_raises_value_error():
    downloader = _create_downloader(max_concurrency=2)
    stream = NonSeekableWriteStream()

    with pytest.raises(ValueError, match="Target stream handle must be seekable."):
        downloader.readinto(stream)


def test_readinto_when_parallel_stream_seek_raises_not_implemented_raises_value_error():
    downloader = _create_downloader(max_concurrency=2)
    stream = SeekNotImplementedWriteStream()

    with pytest.raises(ValueError, match="Target stream handle must be seekable.") as exc:
        downloader.readinto(stream)

    assert isinstance(exc.value.__cause__, NotImplementedError)
    assert str(exc.value.__cause__) == "boom!"


def test_readinto_when_parallel_stream_tell_raises_attribute_error_raises_value_error():
    downloader = _create_downloader(max_concurrency=2)
    stream = TellAttributeErrorWriteStream()

    with pytest.raises(ValueError, match="Target stream handle must be seekable.") as exc:
        downloader.readinto(stream)

    assert isinstance(exc.value.__cause__, AttributeError)
    assert str(exc.value.__cause__) == "boom!"


def test_readinto_when_progress_hook_present_reports_current_buffer_progress():
    progress_hook = mock.Mock()
    downloader = _create_downloader(
        size=3,
        current_content=b"abc",
        progress_hook=progress_hook,
        download_offset=3,
        raw_download_offset=3,
    )
    stream = BytesIO()

    result = downloader.readinto(stream)

    assert result == 3
    assert stream.getvalue() == b"abc"
    progress_hook.assert_called_once_with(3, 3)
