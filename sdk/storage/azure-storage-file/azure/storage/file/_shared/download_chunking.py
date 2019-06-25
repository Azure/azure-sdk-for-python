# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import threading

from azure.core.exceptions import HttpResponseError

from .models import ModifiedAccessConditions
from .utils import validate_and_format_range_headers, process_storage_error
from .encryption import _decrypt_blob


def process_range_and_offset(start_range, end_range, length, key_encryption_key, key_resolver_function):
    start_offset, end_offset = 0, 0
    if key_encryption_key is not None or key_resolver_function is not None:
        if start_range is not None:
            # Align the start of the range along a 16 byte block
            start_offset = start_range % 16
            start_range -= start_offset

            # Include an extra 16 bytes for the IV if necessary
            # Because of the previous offsetting, start_range will always
            # be a multiple of 16.
            if start_range > 0:
                start_offset += 16
                start_range -= 16

        if length is not None:
            # Align the end of the range along a 16 byte block
            end_offset = 15 - (end_range % 16)
            end_range += end_offset

    return (start_range, end_range), (start_offset, end_offset)


def process_content(blob, start_offset, end_offset, require_encryption, key_encryption_key, key_resolver_function):
    if key_encryption_key is not None or key_resolver_function is not None:
        try:
            return _decrypt_blob(
                require_encryption,
                key_encryption_key,
                key_resolver_function,
                blob,
                start_offset,
                end_offset)
        except Exception as error:
            raise HttpResponseError(
                message="Decryption failed.",
                response=blob.response,
                error=error)
    else:
        return b"".join(list(blob))


class _BlobChunkDownloader(object):  # pylint: disable=too-many-instance-attributes

    def __init__(
            self, blob_service, download_size, chunk_size, progress, start_range, end_range, stream,
            validate_content, access_conditions, mod_conditions, timeout,
            require_encryption, key_encryption_key, key_resolver_function, **kwargs):
        # identifiers for the blob
        self.blob_service = blob_service

        # information on the download range/chunk size
        self.chunk_size = chunk_size
        self.download_size = download_size
        self.start_index = start_range
        self.blob_end = end_range

        # the destination that we will write to
        self.stream = stream

        # download progress so far
        self.progress_total = progress

        # encryption
        self.require_encryption = require_encryption
        self.key_encryption_key = key_encryption_key
        self.key_resolver_function = key_resolver_function

        # parameters for each get blob operation
        self.timeout = timeout
        self.validate_content = validate_content
        self.access_conditions = access_conditions
        self.mod_conditions = mod_conditions
        self.request_options = kwargs

    def _calculate_range(self, chunk_start):
        if chunk_start + self.chunk_size > self.blob_end:
            chunk_end = self.blob_end
        else:
            chunk_end = chunk_start + self.chunk_size
        return chunk_start, chunk_end

    def get_chunk_offsets(self):
        index = self.start_index
        while index < self.blob_end:
            yield index
            index += self.chunk_size

    def process_chunk(self, chunk_start):
        chunk_start, chunk_end = self._calculate_range(chunk_start)
        chunk_data = self._download_chunk(chunk_start, chunk_end)
        length = chunk_end - chunk_start
        if length > 0:
            self._write_to_stream(chunk_data, chunk_start)
            self._update_progress(length)

    def yield_chunk(self, chunk_start):
        chunk_start, chunk_end = self._calculate_range(chunk_start)
        return self._download_chunk(chunk_start, chunk_end)

    # should be provided by the subclass
    def _update_progress(self, length):
        pass

    # should be provided by the subclass
    def _write_to_stream(self, chunk_data, chunk_start):
        pass

    def _download_chunk(self, chunk_start, chunk_end):
        download_range, offset = process_range_and_offset(
            chunk_start,
            chunk_end,
            chunk_end,
            self.key_encryption_key,
            self.key_resolver_function,
        )
        range_header, range_validation = validate_and_format_range_headers(
            download_range[0],
            download_range[1] - 1,
            check_content_md5=self.validate_content)

        try:
            _, response = self.blob_service.download(
                timeout=self.timeout,
                range=range_header,
                range_get_content_md5=range_validation,
                lease_access_conditions=self.access_conditions,
                modified_access_conditions=self.mod_conditions,
                validate_content=self.validate_content,
                data_stream_total=self.download_size,
                download_stream_current=self.progress_total,
                **self.request_options)
        except HttpResponseError as error:
            process_storage_error(error)

        chunk_data = process_content(
            response,
            offset[0],
            offset[1],
            self.require_encryption,
            self.key_encryption_key,
            self.key_resolver_function)

        # This makes sure that if_match is set so that we can validate
        # that subsequent downloads are to an unmodified blob
        if not self.mod_conditions:
            self.mod_conditions = ModifiedAccessConditions()
        self.mod_conditions.if_match = response.properties.etag
        return chunk_data


class ParallelBlobChunkDownloader(_BlobChunkDownloader):
    def __init__(
            self, blob_service, download_size, chunk_size, progress, start_range, end_range,
            stream, validate_content, access_conditions, mod_conditions, timeout,
            require_encryption, key_encryption_key, key_resolver_function, **kwargs):

        super(ParallelBlobChunkDownloader, self).__init__(
            blob_service, download_size, chunk_size, progress, start_range, end_range,
            stream, validate_content, access_conditions, mod_conditions, timeout,
            require_encryption, key_encryption_key, key_resolver_function, **kwargs)

        # for a parallel download, the stream is always seekable, so we note down the current position
        # in order to seek to the right place when out-of-order chunks come in
        self.stream_start = stream.tell()

        # since parallel operations are going on
        # it is essential to protect the writing and progress reporting operations
        self.stream_lock = threading.Lock()
        self.progress_lock = threading.Lock()

    def _update_progress(self, length):
        with self.progress_lock:
            self.progress_total += length

    def _write_to_stream(self, chunk_data, chunk_start):
        with self.stream_lock:
            self.stream.seek(self.stream_start + (chunk_start - self.start_index))
            self.stream.write(chunk_data)


class SequentialBlobChunkDownloader(_BlobChunkDownloader):

    def _update_progress(self, length):
        self.progress_total += length

    def _write_to_stream(self, chunk_data, chunk_start):
        # chunk_start is ignored in the case of sequential download since we cannot seek the destination stream
        self.stream.write(chunk_data)


class _FileChunkDownloader(object):
    def __init__(self, file_service, download_size, chunk_size, progress,
                 start_range, end_range, stream, validate_content, timeout, **kwargs):
        # identifiers for the file
        self.file_service = file_service

        # information on the download range/chunk size
        self.chunk_size = chunk_size
        self.download_size = download_size
        self.start_index = start_range
        self.file_end = end_range

        # the destination that we will write to
        self.stream = stream

        # progress related
        self.progress_total = progress

        # parameters for each get file operation
        self.validate_content = validate_content
        self.timeout = timeout
        self.request_options = kwargs

    def _calculate_range(self, chunk_start):
        if chunk_start + self.chunk_size > self.file_end:
            chunk_end = self.file_end
        else:
            chunk_end = chunk_start + self.chunk_size
        return chunk_start, chunk_end

    def get_chunk_offsets(self):
        index = self.start_index
        while index < self.file_end:
            yield index
            index += self.chunk_size

    def process_chunk(self, chunk_start):
        chunk_start, chunk_end = self._calculate_range(chunk_start)
        chunk_data = self._download_chunk(chunk_start, chunk_end)
        length = chunk_end - chunk_start
        if length > 0:
            self._write_to_stream(chunk_data, chunk_start)
            self._update_progress(length)

    def yield_chunk(self, chunk_start):
        chunk_start, chunk_end = self._calculate_range(chunk_start)
        return self._download_chunk(chunk_start, chunk_end)

    # should be provided by the subclass
    def _update_progress(self, length):
        pass

    # should be provided by the subclass
    def _write_to_stream(self, chunk_data, chunk_start):
        pass

    def _download_chunk(self, chunk_start, chunk_end):
        download_range, offset = process_range_and_offset(
            chunk_start,
            chunk_end,
            chunk_end,
            None,
            None,
        )
        range_header, range_validation = validate_and_format_range_headers(
            download_range[0],
            download_range[1] - 1,
            check_content_md5=self.validate_content)
        try:
            _, response = self.file_service.download(
                timeout=self.timeout,
                range=range_header,
                range_get_content_md5=range_validation,
                validate_content=self.validate_content,
                data_stream_total=self.download_size,
                download_stream_current=self.progress_total,
                **self.request_options)
        except HttpResponseError as error:
            process_storage_error(error)

        chunk_data = process_content(response, offset[0], offset[1], False, None, None)
        return chunk_data


class ParallelFileChunkDownloader(_FileChunkDownloader):
    def __init__(
            self, file_service, download_size, chunk_size, progress,
            start_range, end_range, stream, validate_content, timeout, **kwargs):
        super(ParallelFileChunkDownloader, self).__init__(
            file_service, download_size, chunk_size, progress, start_range, end_range,
            stream, validate_content, timeout, **kwargs)

        # for a parallel download, the stream is always seekable, so we note down the current position
        # in order to seek to the right place when out-of-order chunks come in
        self.stream_start = stream.tell()

        # since parallel operations are going on
        # it is essential to protect the writing and progress reporting operations
        self.stream_lock = threading.Lock()
        self.progress_lock = threading.Lock()

    def _update_progress(self, length):
        with self.progress_lock:
            self.progress_total += length

    def _write_to_stream(self, chunk_data, chunk_start):
        with self.stream_lock:
            self.stream.seek(self.stream_start + (chunk_start - self.start_index))
            self.stream.write(chunk_data)


class SequentialFileChunkDownloader(_FileChunkDownloader):

    def _update_progress(self, length):
        self.progress_total += length

    def _write_to_stream(self, chunk_data, chunk_start):
        # chunk_start is ignored in the case of sequential download since we cannot seek the destination stream
        self.stream.write(chunk_data)
