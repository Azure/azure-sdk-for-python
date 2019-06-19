# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import threading


def _download_file_chunks(file_service, share_name, directory_name, file_name,
                          download_size, block_size, progress, start_range, end_range,
                          stream, max_connections, progress_callback, validate_content,
                          timeout, operation_context, snapshot):

    downloader_class = _ParallelFileChunkDownloader if max_connections > 1 else _SequentialFileChunkDownloader

    downloader = downloader_class(
        file_service,
        share_name,
        directory_name,
        file_name,
        download_size,
        block_size,
        progress,
        start_range,
        end_range,
        stream,
        progress_callback,
        validate_content,
        timeout,
        operation_context,
        snapshot,
    )

    if max_connections > 1:
        import concurrent.futures
        executor = concurrent.futures.ThreadPoolExecutor(max_connections)
        list(executor.map(downloader.process_chunk, downloader.get_chunk_offsets()))
    else:
        for chunk in downloader.get_chunk_offsets():
            downloader.process_chunk(chunk)


class _FileChunkDownloader(object):
    def __init__(self, file_service, share_name, directory_name, file_name,
                 download_size, chunk_size, progress, start_range, end_range,
                 stream, progress_callback, validate_content, timeout, operation_context, snapshot):
        # identifiers for the file
        self.file_service = file_service
        self.share_name = share_name
        self.directory_name = directory_name
        self.file_name = file_name

        # information on the download range/chunk size
        self.chunk_size = chunk_size
        self.download_size = download_size
        self.start_index = start_range
        self.file_end = end_range

        # the destination that we will write to
        self.stream = stream

        # progress related
        self.progress_callback = progress_callback
        self.progress_total = progress

        # parameters for each get file operation
        self.validate_content = validate_content
        self.timeout = timeout
        self.operation_context = operation_context
        self.snapshot = snapshot

    def get_chunk_offsets(self):
        index = self.start_index
        while index < self.file_end:
            yield index
            index += self.chunk_size

    def process_chunk(self, chunk_start):
        if chunk_start + self.chunk_size > self.file_end:
            chunk_end = self.file_end
        else:
            chunk_end = chunk_start + self.chunk_size

        chunk_data = self._download_chunk(chunk_start, chunk_end).content
        length = chunk_end - chunk_start
        if length > 0:
            self._write_to_stream(chunk_data, chunk_start)
            self._update_progress(length)

    # should be provided by the subclass
    def _update_progress(self, length):
        pass

    # should be provided by the subclass
    def _write_to_stream(self, chunk_data, chunk_start):
        pass

    def _download_chunk(self, chunk_start, chunk_end):
        return self.file_service._get_file(
            self.share_name,
            self.directory_name,
            self.file_name,
            start_range=chunk_start,
            end_range=chunk_end - 1,
            validate_content=self.validate_content,
            timeout=self.timeout,
            _context=self.operation_context,
            snapshot=self.snapshot
        )


class _ParallelFileChunkDownloader(_FileChunkDownloader):
    def __init__(self, file_service, share_name, directory_name, file_name,
                 download_size, chunk_size, progress, start_range, end_range,
                 stream, progress_callback, validate_content, timeout, operation_context, snapshot):
        super(_ParallelFileChunkDownloader, self).__init__(file_service, share_name, directory_name, file_name,
                                                           download_size, chunk_size, progress, start_range, end_range,
                                                           stream, progress_callback, validate_content, timeout,
                                                           operation_context, snapshot)

        # for a parallel download, the stream is always seekable, so we note down the current position
        # in order to seek to the right place when out-of-order chunks come in
        self.stream_start = stream.tell()

        # since parallel operations are going on
        # it is essential to protect the writing and progress reporting operations
        self.stream_lock = threading.Lock()
        self.progress_lock = threading.Lock()

    def _update_progress(self, length):
        if self.progress_callback is not None:
            with self.progress_lock:
                self.progress_total += length
                total_so_far = self.progress_total
            self.progress_callback(total_so_far, self.download_size)

    def _write_to_stream(self, chunk_data, chunk_start):
        with self.stream_lock:
            self.stream.seek(self.stream_start + (chunk_start - self.start_index))
            self.stream.write(chunk_data)


class _SequentialFileChunkDownloader(_FileChunkDownloader):
    def __init__(self, file_service, share_name, directory_name, file_name, download_size, chunk_size, progress,
                 start_range, end_range, stream, progress_callback, validate_content, timeout, operation_context,
                 snapshot):
        super(_SequentialFileChunkDownloader, self).__init__(file_service, share_name, directory_name, file_name,
                                                             download_size, chunk_size, progress, start_range,
                                                             end_range, stream, progress_callback, validate_content,
                                                             timeout, operation_context, snapshot)

    def _update_progress(self, length):
        if self.progress_callback is not None:
            self.progress_total += length
            self.progress_callback(self.progress_total, self.download_size)

    def _write_to_stream(self, chunk_data, chunk_start):
        # chunk_start is ignored in the case of sequential download since we cannot seek the destination stream
        self.stream.write(chunk_data)
