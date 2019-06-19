# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import threading


def _upload_file_chunks(file_service, share_name, directory_name, file_name,
                        file_size, block_size, stream, max_connections,
                        progress_callback, validate_content, timeout):
    uploader = _FileChunkUploader(
        file_service,
        share_name,
        directory_name,
        file_name,
        file_size,
        block_size,
        stream,
        max_connections > 1,
        progress_callback,
        validate_content,
        timeout
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


class _FileChunkUploader(object):
    def __init__(self, file_service, share_name, directory_name, file_name,
                 file_size, chunk_size, stream, parallel, progress_callback,
                 validate_content, timeout):
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
        self.validate_content = validate_content
        self.timeout = timeout

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
        return self._upload_chunk_with_progress(chunk_offset, chunk_data)

    def process_all_unknown_size(self):
        assert self.stream_lock is None
        range_ids = []
        index = 0
        while True:
            data = self._read_from_stream(None, self.chunk_size)
            if data:
                index += len(data)
                range_id = self._upload_chunk_with_progress(index, data)
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

    def _upload_chunk_with_progress(self, chunk_start, chunk_data):
        chunk_end = chunk_start + len(chunk_data) - 1
        self.file_service.update_range(
            self.share_name,
            self.directory_name,
            self.file_name,
            chunk_data,
            chunk_start,
            chunk_end,
            self.validate_content,
            timeout=self.timeout
        )
        range_id = 'bytes={0}-{1}'.format(chunk_start, chunk_end)
        self._update_progress(len(chunk_data))
        return range_id
