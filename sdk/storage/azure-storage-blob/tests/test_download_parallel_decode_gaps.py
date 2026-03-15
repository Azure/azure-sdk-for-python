# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from types import SimpleNamespace

import pytest

import azure.storage.blob._download as download_module
from azure.storage.blob._download import StorageStreamDownloader


class _FakeResponse(object):
    def __init__(self, body, total_size, start=0):
        self._body = body
        self.response = SimpleNamespace(headers={})
        self.properties = SimpleNamespace(
            content_range="bytes {}-{}/{}".format(start, start + len(body) - 1, total_size),
            blob_type='BlockBlob',
            etag='etag-value'
        )
        self.content_length = len(body)

    def __iter__(self):
        return iter([self._body])


class _FakeBlobClient(object):
    def __init__(self, response):
        self._response = response
        self.calls = []

    def download(self, **kwargs):
        self.calls.append(kwargs)
        return None, self._response


def _build_stream_downloader(body, total_size, *, max_chunk_get_size=4, max_single_get_size=4, max_concurrency=1, encoding=None):
    response = _FakeResponse(body, total_size)
    clients = SimpleNamespace(
        blob=_FakeBlobClient(response),
        page_blob=SimpleNamespace(get_page_ranges=lambda: None)
    )
    config = SimpleNamespace(
        max_single_get_size=max_single_get_size,
        max_chunk_get_size=max_chunk_get_size
    )
    return StorageStreamDownloader(
        clients=clients,
        config=config,
        start_range=None,
        end_range=None,
        validate_content=False,
        encryption_options={},
        max_concurrency=max_concurrency,
        name='blob',
        container='container',
        encoding=encoding,
        download_cls=None
    )


def test_readall_when_parallel_and_multiple_chunks_remaining_enters_thread_pool_executor(monkeypatch):
    # Tests defensive branch — requires mock.
    downloader = _build_stream_downloader(b'AAAA', 12, max_concurrency=2)

    executor_state = {'entered': False, 'max_workers': None}

    class FakeChunkDownloader(object):
        def __init__(self, **kwargs):
            self.stream = kwargs['stream']
            self.start_range = kwargs['start_range']
            self.chunk_size = kwargs['chunk_size']

        def get_chunk_offsets(self):
            return iter([self.start_range, self.start_range + self.chunk_size])

        def process_chunk(self, chunk_start):
            self.stream.write({4: b'BBBB', 8: b'CCCC'}[chunk_start])

    class FakeExecutor(object):
        def __init__(self, max_workers):
            executor_state['max_workers'] = max_workers

        def __enter__(self):
            executor_state['entered'] = True
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def map(self, func, iterable):
            return [func(item) for item in iterable]

    import concurrent.futures

    monkeypatch.setattr(download_module, '_ChunkDownloader', FakeChunkDownloader)
    monkeypatch.setattr(concurrent.futures, 'ThreadPoolExecutor', FakeExecutor)

    data = downloader.readall()

    assert executor_state['entered'] is True
    assert executor_state['max_workers'] == 2
    assert data == b'AAAABBBBCCCC'


def test_readall_when_parallel_and_multiple_chunks_remaining_maps_wrapped_process_chunk(monkeypatch):
    # Tests defensive branch — requires mock.
    downloader = _build_stream_downloader(b'AAAA', 12, max_concurrency=2)

    map_state = {'func': None, 'offsets': None}

    class FakeChunkDownloader(object):
        def __init__(self, **kwargs):
            self.stream = kwargs['stream']
            self.start_range = kwargs['start_range']
            self.chunk_size = kwargs['chunk_size']

        def get_chunk_offsets(self):
            return iter([self.start_range, self.start_range + self.chunk_size])

        def process_chunk(self, chunk_start):
            self.stream.write({4: b'BBBB', 8: b'CCCC'}[chunk_start])

    class FakeExecutor(object):
        def __init__(self, max_workers):
            self.max_workers = max_workers

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def map(self, func, iterable):
            offsets = list(iterable)
            map_state['func'] = func
            map_state['offsets'] = offsets
            return [func(item) for item in offsets]

    def fake_with_current_context(func):
        def wrapped(*args, **kwargs):
            return func(*args, **kwargs)
        wrapped.__name__ = 'wrapped_process_chunk'
        wrapped._original = func
        return wrapped

    import concurrent.futures

    monkeypatch.setattr(download_module, '_ChunkDownloader', FakeChunkDownloader)
    monkeypatch.setattr(download_module, 'with_current_context', fake_with_current_context)
    monkeypatch.setattr(concurrent.futures, 'ThreadPoolExecutor', FakeExecutor)

    data = downloader.readall()

    assert map_state['offsets'] == [4, 8]
    assert map_state['func'].__name__ == 'wrapped_process_chunk'
    assert data == b'AAAABBBBCCCC'


def test_read_when_partial_utf8_bytes_with_encoding_raises_unicode_decode_error():
    downloader = _build_stream_downloader(b'\xe2\x82\xac', 3, encoding='utf-8')

    with pytest.raises(UnicodeDecodeError) as error:
        downloader.read(1)

    assert str(error.value) == "'utf-8' codec can't decode byte 0xe2 in position 0: unexpected end of data"


def test_read_when_partial_utf8_bytes_with_encoding_warns_before_reraising_decode_error():
    downloader = _build_stream_downloader(b'\xe2\x82\xac', 3, encoding='utf-8')

    with pytest.raises(UnicodeDecodeError):
        with pytest.warns(UserWarning) as warnings_record:
            downloader.read(1)

    warning_messages = [str(w.message) for w in warnings_record]
    assert warning_messages == [
        "Size parameter specified with text encoding enabled. It is recommended to use chars to read a specific number of characters instead.",
        "Encountered a decoding error while decoding blob data from a partial read. Try using the `chars` keyword instead to read in text mode."
    ]


def test_read_when_partial_utf8_bytes_with_encoding_reraises_original_unicode_decode_error_details():
    downloader = _build_stream_downloader(b'\xe2\x82\xac', 3, encoding='utf-8')

    with pytest.raises(UnicodeDecodeError) as error:
        downloader.read(1)

    assert error.value.object == b'\xe2'
    assert error.value.start == 0
    assert error.value.end == 1
