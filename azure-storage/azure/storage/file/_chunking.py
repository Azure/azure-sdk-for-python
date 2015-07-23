#-------------------------------------------------------------------------
# Copyright (c) Microsoft.  All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#--------------------------------------------------------------------------
import sys
import threading

from time import sleep
from .._common_conversion import _encode_base64
from .._common_serialization import url_quote


class _FileChunkDownloader(object):
    def __init__(self, file_service, share_name, directory_name, file_name, 
                 file_size, chunk_size, stream, parallel, max_retries, retry_wait,
                 progress_callback):
        self.file_service = file_service
        self.share_name = share_name
        self.directory_name = directory_name
        self.file_name = file_name
        self.file_size = file_size
        self.chunk_size = chunk_size
        self.stream = stream
        self.stream_start = stream.tell() if parallel else None
        self.stream_lock = threading.Lock() if parallel else None
        self.progress_callback = progress_callback
        self.progress_total = 0
        self.progress_lock = threading.Lock() if parallel else None
        self.max_retries = max_retries
        self.retry_wait = retry_wait

    def get_chunk_offsets(self):
        index = 0
        while index < self.file_size:
            yield index
            index += self.chunk_size

    def process_chunk(self, chunk_offset):
        chunk_data = self._download_chunk_with_retries(chunk_offset)
        length = len(chunk_data)
        if length > 0:
            self._write_to_stream(chunk_data, chunk_offset)
            self._update_progress(length)

    def _update_progress(self, length):
        if self.progress_callback is not None:
            if self.progress_lock is not None:
                with self.progress_lock:
                    self.progress_total += length
                    total = self.progress_total
            else:
                self.progress_total += length
                total = self.progress_total
            self.progress_callback(total, self.file_size)

    def _write_to_stream(self, chunk_data, chunk_offset):
        if self.stream_lock is not None:
            with self.stream_lock:
                self.stream.seek(self.stream_start + chunk_offset)
                self.stream.write(chunk_data)
        else:
            self.stream.write(chunk_data)

    def _download_chunk_with_retries(self, chunk_offset):
        range_id = 'bytes={0}-{1}'.format(chunk_offset, chunk_offset + self.chunk_size - 1)
        retries = self.max_retries
        while True:
            try:
                return self.file_service.get_file(
                    self.share_name,
                    self.directory_name,
                    self.file_name,
                    x_ms_range=range_id
                )
            except Exception:
                if retries > 0:
                    retries -= 1
                    sleep(self.retry_wait)
                else:
                    raise


class _FileChunkUploader(object):
    def __init__(self, file_service, share_name, directory_name, file_name, 
                 file_size, chunk_size, stream, parallel, max_retries, retry_wait,
                 progress_callback):
        self.file_service = file_service
        self.share_name = share_name
        self.directory_name = directory_name
        self.file_name = file_name
        self.file_size = file_size
        self.chunk_size = chunk_size
        self.stream = stream
        self.stream_start = stream.tell() if parallel else None
        self.stream_lock = threading.Lock() if parallel else None
        self.progress_callback = progress_callback
        self.progress_total = 0
        self.progress_lock = threading.Lock() if parallel else None
        self.max_retries = max_retries
        self.retry_wait = retry_wait

    def get_chunk_offsets(self):
        index = 0
        if self.file_size is None:
            # we don't know the size of the stream, so we have no
            # choice but to seek
            while True:
                data = self._read_from_stream(index, 1)
                if not data:
                    break
                yield index
                index += self.chunk_size
        else:
            while index < self.file_size:
                yield index
                index += self.chunk_size

    def process_chunk(self, chunk_offset):
        size = self.chunk_size
        if self.file_size is not None:
            size = min(size, self.file_size - chunk_offset)
        chunk_data = self._read_from_stream(chunk_offset, size)
        return self._upload_chunk_with_retries(chunk_offset, chunk_data)

    def process_all_unknown_size(self):
        assert self.stream_lock is None
        range_ids = []
        index = 0
        while True:
            data = self._read_from_stream(None, self.chunk_size)
            if data:
                index += len(data)
                range_id = self._upload_chunk_with_retries(index, data)
                range_ids.append(range_id)
            else:
                break

        return range_ids

    def _read_from_stream(self, offset, count):
        if self.stream_lock is not None:
            with self.stream_lock:
                self.stream.seek(self.stream_start + offset)
                data = self.stream.read(count)
        else:
            data = self.stream.read(count)
        return data

    def _update_progress(self, length):
        if self.progress_callback is not None:
            if self.progress_lock is not None:
                with self.progress_lock:
                    self.progress_total += length
                    total = self.progress_total
            else:
                self.progress_total += length
                total = self.progress_total
            self.progress_callback(total, self.file_size)

    def _upload_chunk_with_retries(self, chunk_offset, chunk_data):
        retries = self.max_retries
        while True:
            try:
                range_id = self._upload_chunk(chunk_offset, chunk_data) 
                self._update_progress(len(chunk_data))
                return range_id
            except Exception:
                if retries > 0:
                    retries -= 1
                    sleep(self.retry_wait)
                else:
                    raise

    def _upload_chunk(self, chunk_offset, chunk_data):
        range_id = 'bytes={0}-{1}'.format(chunk_offset, chunk_offset + len(chunk_data) - 1)
        self.file_service.update_range(
            self.share_name,
            self.directory_name,
            self.file_name,
            chunk_data,
            range_id,
        )
        return range_id


def _download_file_chunks(file_service, share_name, directory_name, file_name,
                          file_size, block_size, stream, max_connections,
                          max_retries, retry_wait, progress_callback):
    downloader = _FileChunkDownloader(
        file_service,
        share_name,
        directory_name, 
        file_name,
        file_size,
        block_size,
        stream,
        max_connections > 1,
        max_retries,
        retry_wait,
        progress_callback,
    )

    if progress_callback is not None:
        progress_callback(0, file_size)

    if max_connections > 1:
        import concurrent.futures
        executor = concurrent.futures.ThreadPoolExecutor(max_connections)
        result = list(executor.map(downloader.process_chunk, downloader.get_chunk_offsets()))
    else:
        for range_start in downloader.get_chunk_offsets():
            downloader.process_chunk(range_start)


def _upload_file_chunks(file_service, share_name, directory_name, file_name,
                        file_size, block_size, stream, max_connections,
                        max_retries, retry_wait, progress_callback):
    uploader = _FileChunkUploader(
        file_service,
        share_name,
        directory_name,
        file_name,
        file_size,
        block_size,
        stream,
        max_connections > 1,
        max_retries,
        retry_wait,
        progress_callback,
    )

    if progress_callback is not None:
        progress_callback(0, file_size)

    if max_connections > 1:
        import concurrent.futures
        executor = concurrent.futures.ThreadPoolExecutor(max_connections)
        range_ids = list(executor.map(uploader.process_chunk, uploader.get_chunk_offsets()))
    else:
        if file_size is not None:
            range_ids = [uploader.process_chunk(start) for start in uploader.get_chunk_offsets()]
        else:
            range_ids = uploader.process_all_unknown_size()

    return range_ids
