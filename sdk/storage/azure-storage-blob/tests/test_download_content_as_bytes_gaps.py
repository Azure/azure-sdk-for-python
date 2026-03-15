# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from io import BytesIO
from types import SimpleNamespace
from unittest import mock

import pytest

from azure.storage.blob import BlobClient
from azure.storage.blob._download import StorageStreamDownloader

from devtools_testutils.storage import StorageRecordedTestCase
from settings.testcase import BlobPreparer
from test_helpers import MockLegacyTransport


class _RangeResponse(object):
    def __init__(self, data):
        self._data = data
        self.content_length = len(data)
        self.properties = SimpleNamespace(etag='etag')
        self.headers = {}

    def __iter__(self):
        return iter([self._data])


class _RangeDownloadClient(object):
    def __init__(self, data):
        self.data = data
        self.requested_ranges = []

    def download(self, **kwargs):
        range_header = kwargs['range']
        self.requested_ranges.append(range_header)
        start, end = [int(x) for x in range_header.split('=')[1].split('-')]
        return None, _RangeResponse(self.data[start:end + 1])


class TestStorageDownloadContentAsBytesGaps(StorageRecordedTestCase):
    def _build_parallel_downloader(self):
        range_client = _RangeDownloadClient(b'abcdefghijkl')
        downloader = StorageStreamDownloader.__new__(StorageStreamDownloader)
        downloader.size = 12
        downloader._text_mode = False
        downloader._encoding = None
        downloader._max_concurrency = 2
        downloader._read_offset = 0
        downloader._current_content = b'abcd'
        downloader._current_content_offset = 0
        downloader._progress_hook = None
        downloader._download_start = 0
        downloader._download_offset = 4
        downloader._raw_download_offset = 4
        downloader._encryption_data = None
        downloader._clients = SimpleNamespace(blob=range_client)
        downloader._non_empty_ranges = None
        downloader._config = SimpleNamespace(max_chunk_get_size=4)
        downloader._validate_content = False
        downloader._encryption_options = {}
        downloader._location_mode = None
        downloader._request_options = {}
        return downloader, range_client

    @BlobPreparer()
    def test_readinto_when_parallel_and_remaining_data_downloads_all_bytes(self, **kwargs):
        # Tests defensive branch — requires mock.
        downloader, range_client = self._build_parallel_downloader()
        stream = BytesIO()

        class InlineExecutor(object):
            def __init__(self, max_workers):
                self.max_workers = max_workers

            def __enter__(self):
                return self

            def __exit__(self, *args):
                return None

            def map(self, func, iterable):
                return [func(item) for item in iterable]

        with mock.patch('concurrent.futures.ThreadPoolExecutor', InlineExecutor):
            count = downloader.readinto(stream)

        assert count == 12
        assert stream.getvalue() == b'abcdefghijkl'
        assert range_client.requested_ranges == ['bytes=4-7', 'bytes=8-11']

    @BlobPreparer()
    def test_readinto_when_parallel_and_remaining_data_enters_thread_pool_executor(self, **kwargs):
        # Tests defensive branch — requires mock.
        downloader, _ = self._build_parallel_downloader()
        stream = BytesIO()
        state = {'max_workers': None, 'entered': False}

        class RecordingExecutor(object):
            def __init__(self, max_workers):
                state['max_workers'] = max_workers

            def __enter__(self):
                state['entered'] = True
                return self

            def __exit__(self, *args):
                return None

            def map(self, func, iterable):
                return [func(item) for item in iterable]

        with mock.patch('concurrent.futures.ThreadPoolExecutor', RecordingExecutor):
            count = downloader.readinto(stream)

        assert count == 12
        assert state['max_workers'] == 2
        assert state['entered'] is True

    @BlobPreparer()
    def test_readinto_when_parallel_and_remaining_data_maps_wrapped_process_chunk(self, **kwargs):
        # Tests defensive branch — requires mock.
        downloader, _ = self._build_parallel_downloader()
        stream = BytesIO()
        state = {'func': None, 'offsets': None}
        wrapped = mock.Mock(side_effect=lambda chunk_start: state['original'](chunk_start))

        class RecordingExecutor(object):
            def __init__(self, max_workers):
                self.max_workers = max_workers

            def __enter__(self):
                return self

            def __exit__(self, *args):
                return None

            def map(self, func, iterable):
                state['func'] = func
                state['offsets'] = list(iterable)
                return [func(item) for item in state['offsets']]

        with mock.patch('azure.storage.blob._download.with_current_context', side_effect=lambda fn: wrapped) as wrap_current_context:
            with mock.patch('concurrent.futures.ThreadPoolExecutor', RecordingExecutor):
                with mock.patch('azure.storage.blob._download._ChunkDownloader.process_chunk', autospec=True) as process_chunk:
                    state['original'] = lambda chunk_start: process_chunk(mock.ANY, chunk_start)
                    downloader.readinto(stream)

        assert wrap_current_context.call_count == 1
        assert state['func'] is wrapped
        assert state['offsets'] == [4, 8]
        assert wrapped.call_count == 2
        assert process_chunk.call_args_list == [mock.call(mock.ANY, 4), mock.call(mock.ANY, 8)]

    @BlobPreparer()
    def test_content_as_bytes_when_called_warns_and_returns_bytes(self, **kwargs):
        storage_account_name = kwargs.pop('storage_account_name')
        storage_account_key = kwargs.pop('storage_account_key')

        blob_client = BlobClient(
            self.account_url(storage_account_name, 'blob'),
            container_name='container',
            blob_name='blob',
            credential=storage_account_key.secret,
            transport=MockLegacyTransport(),
            retry_total=0
        )

        stream = blob_client.download_blob()

        with pytest.warns(DeprecationWarning, match='content_as_bytes is deprecated, use readall instead'):
            data = stream.content_as_bytes(max_concurrency=2)

        assert data == b'Hello World!'
        assert stream._max_concurrency == 2

    @BlobPreparer()
    def test_content_as_bytes_when_partially_read_in_text_mode_raises_value_error(self, **kwargs):
        storage_account_name = kwargs.pop('storage_account_name')
        storage_account_key = kwargs.pop('storage_account_key')

        blob_client = BlobClient(
            self.account_url(storage_account_name, 'blob'),
            container_name='container',
            blob_name='blob',
            credential=storage_account_key.secret,
            transport=MockLegacyTransport(),
            retry_total=0
        )

        stream = blob_client.download_blob(encoding='utf-8')
        first_char = stream.read(chars=1)

        with pytest.warns(DeprecationWarning, match='content_as_bytes is deprecated, use readall instead'):
            with pytest.raises(ValueError, match='Stream has been partially read in text mode. content_as_bytes is not supported in text mode.'):
                stream.content_as_bytes()

        assert first_char == 'H'
