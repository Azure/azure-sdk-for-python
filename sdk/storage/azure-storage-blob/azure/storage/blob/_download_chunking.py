# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import threading
import sys
if sys.version_info >= (3,):
    from io import BytesIO
else:
    from cStringIO import StringIO as BytesIO

from azure.core.exceptions import HttpResponseError

from ._utils import (
    validate_and_format_range_headers,
    parse_length_from_content_range,
    process_storage_error)
from .common import LocationMode
from ._generated.models import ModifiedAccessConditions, StorageErrorException
from ._deserialize import deserialize_blob_stream
from ._encryption import _decrypt_blob


def _process_range_and_offset(start_range, end_range, length, key_encryption_key, key_resolver_function):
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


def _process_content(blob, start_offset, end_offset, require_encryption, key_encryption_key, key_resolver_function):
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


class StorageStreamDownloader(object):

    def __init__(
            self, name, container, service, config, offset, length, validate_content,
            access_conditions, mod_conditions, timeout,
            require_encryption, key_encryption_key, key_resolver_function, **kwargs
    ):
        self.service = service
        self.config = config
        self.offset = offset
        self.length = length
        self.timeout = timeout
        self.validate_content = validate_content
        self.access_conditions = access_conditions
        self.mod_conditions = mod_conditions
        self.require_encryption = require_encryption
        self.key_encryption_key = key_encryption_key
        self.key_resolver_function = key_resolver_function
        self.request_options = kwargs
        self.location_mode = None
        self._download_complete = False

        # The service only provides transactional MD5s for chunks under 4MB.
        # If validate_content is on, get only self.MAX_CHUNK_GET_SIZE for the first
        # chunk so a transactional MD5 can be retrieved.
        self.first_get_size = self.config.max_single_get_size if not self.validate_content \
            else self.config.max_chunk_get_size
        initial_request_start = self.offset if self.offset is not None else 0
        if self.length is not None and self.length - self.offset < self.first_get_size:
            initial_request_end = self.length
        else:
            initial_request_end = initial_request_start + self.first_get_size - 1

        self.initial_range, self.initial_offset = _process_range_and_offset(
            initial_request_start,
            initial_request_end,
            self.length,
            self.key_encryption_key,
            self.key_resolver_function)

        self.download_size = None
        self.blob_size = None
        self.blob = self._initial_request()
        self.properties = self.blob.properties
        self.properties.name = name
        self.properties.container = container
        # Set the content length to the download size instead of the size of
        # the last range
        self.properties.size = self.download_size

        # Overwrite the content range to the user requested range
        self.properties.content_range = 'bytes {0}-{1}/{2}'.format(self.offset, self.length, self.blob_size)

        # Overwrite the content MD5 as it is the MD5 for the last range instead
        # of the stored MD5
        # TODO: Set to the stored MD5 when the service returns this
        self.properties.content_md5 = None

    def __len__(self):
        return self.download_size

    def __iter__(self):
        if self.download_size == 0:
            content = b""
        else:
            content = _process_content(
                self.blob,
                self.initial_offset[0],
                self.initial_offset[1],
                self.require_encryption,
                self.key_encryption_key,
                self.key_resolver_function)

        if content is not None:
            yield content
        if self._download_complete:
            return

        end_blob = self.blob_size
        if self.length is not None:
            # Use the length unless it is over the end of the blob
            end_blob = min(self.blob_size, self.length + 1)

        downloader = _SequentialBlobChunkDownloader(
            blob_service=self.service,
            download_size=self.download_size,
            chunk_size=self.config.max_chunk_get_size,
            progress=self.first_get_size,
            start_range=self.initial_range[1] + 1,  # start where the first download ended
            end_range=end_blob,
            stream=stream,
            validate_content=self.validate_content,
            access_conditions=self.access_conditions,
            mod_conditions=self.mod_conditions,
            timeout=self.timeout,
            require_encryption=self.require_encryption,
            key_encryption_key=self.key_encryption_key,
            key_resolver_function=self.key_resolver_function,
            use_location=self.location_mode,
            cls=deserialize_blob_stream,
            **self.request_options)

        for chunk in downloader.get_chunk_offsets():
            yield downloader.yield_chunk(chunk)

    def _initial_request(self):
        range_header, range_validation = validate_and_format_range_headers(
            self.initial_range[0],
            self.initial_range[1],
            start_range_required=False,
            end_range_required=False,
            check_content_md5=self.validate_content)

        try:
            location_mode, blob = self.service.download(
                timeout=self.timeout,
                range=range_header,
                range_get_content_md5=range_validation,
                lease_access_conditions=self.access_conditions,
                modified_access_conditions=self.mod_conditions,
                validate_content=self.validate_content,
                cls=deserialize_blob_stream,
                data_stream_total=None,
                download_stream_current=0,
                **self.request_options)

            # Check the location we read from to ensure we use the same one
            # for subsequent requests.
            self.location_mode = location_mode

            # Parse the total blob size and adjust the download size if ranges
            # were specified
            self.blob_size = parse_length_from_content_range(blob.properties.content_range)
            if self.length is not None:
                # Use the length unless it is over the end of the blob
                self.download_size = min(self.blob_size, self.length - self.offset + 1)
            elif self.offset is not None:
                self.download_size = self.blob_size - self.offset
            else:
                self.download_size = self.blob_size

        except StorageErrorException as error:
            if self.offset is None and error.response.status_code == 416:
                # Get range will fail on an empty blob. If the user did not
                # request a range, do a regular get request in order to get
                # any properties.
                try:
                    _, blob = self.service.download(
                        timeout=self.timeout,
                        lease_access_conditions=self.access_conditions,
                        modified_access_conditions=self.mod_conditions,
                        validate_content=self.validate_content,
                        cls=deserialize_blob_stream,
                        data_stream_total=0,
                        download_stream_current=0,
                        **self.request_options)
                except StorageErrorException as error:
                    process_storage_error(error)

                # Set the download size to empty
                self.download_size = 0
                self.blob_size = 0
            else:
                process_storage_error(error)
    
        # If the blob is small, the download is complete at this point.
        # If blob size is large, download the rest of the blob in chunks.
        if blob.properties.size != self.download_size:
            # Lock on the etag. This can be overriden by the user by specifying '*'
            if not self.mod_conditions:
                self.mod_conditions = ModifiedAccessConditions()
            if not self.mod_conditions.if_match:
                self.mod_conditions.if_match = blob.properties.etag
        else:
            self._download_complete = True

        return blob


    def content_as_bytes(self, max_connections=1):
        stream = BytesIO()
        self.download_to_stream(stream, max_connections=max_connections)
        return stream.getvalue()

    def content_as_text(self, max_connections=1, encoding='UTF-8'):
        content = self.content_as_bytes(max_connections=max_connections)
        return content.decode(encoding)

    def download_to_stream(self, stream, max_connections=1):
        # the stream must be seekable if parallel download is required
        if max_connections > 1:
            error_message = "Target stream handle must be seekable."
            if sys.version_info >= (3,) and not stream.seekable():
                raise ValueError(error_message)

            try:
                stream.seek(stream.tell())
            except (NotImplementedError, AttributeError):
                raise ValueError(error_message)

        if self.download_size == 0:
            content = b""
        else:
            content = _process_content(
                self.blob,
                self.initial_offset[0],
                self.initial_offset[1],
                self.require_encryption,
                self.key_encryption_key,
                self.key_resolver_function)
        # Write the content to the user stream
        # Clear blob content since output has been written to user stream
        if content is not None:
            stream.write(content)
        if self._download_complete:
            return self.properties

        end_blob = self.blob_size
        if self.length is not None:
            # Use the length unless it is over the end of the blob
            end_blob = min(self.blob_size, self.length + 1)

        downloader_class = _ParallelBlobChunkDownloader if max_connections > 1 else _SequentialBlobChunkDownloader
        downloader = downloader_class(
            blob_service=self.service,
            download_size=self.download_size,
            chunk_size=self.config.max_chunk_get_size,
            progress=self.first_get_size,
            start_range=self.initial_range[1] + 1,  # start where the first download ended
            end_range=end_blob,
            stream=stream,
            validate_content=self.validate_content,
            access_conditions=self.access_conditions,
            mod_conditions=self.mod_conditions,
            timeout=self.timeout,
            require_encryption=self.require_encryption,
            key_encryption_key=self.key_encryption_key,
            key_resolver_function=self.key_resolver_function,
            use_location=self.location_mode,
            cls=deserialize_blob_stream,
            **self.request_options)

        if max_connections > 1:
            import concurrent.futures
            executor = concurrent.futures.ThreadPoolExecutor(max_connections)
            list(executor.map(downloader.process_chunk, downloader.get_chunk_offsets()))
        else:
            for chunk in downloader.get_chunk_offsets():
                downloader.process_chunk(chunk)

        return self.properties


class _BlobChunkDownloader(object):

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
        download_range, offset = _process_range_and_offset(
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
        except StorageErrorException as error:
            process_storage_error(error)

        chunk_data = _process_content(
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


class _ParallelBlobChunkDownloader(_BlobChunkDownloader):
    def __init__(
        self, blob_service, download_size, chunk_size, progress, start_range, end_range,
        stream, validate_content, access_conditions, mod_conditions, timeout,
        require_encryption, key_encryption_key, key_resolver_function, **kwargs):

        super(_ParallelBlobChunkDownloader, self).__init__(
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


class _SequentialBlobChunkDownloader(_BlobChunkDownloader):

    def _update_progress(self, length):
        self.progress_total += length

    def _write_to_stream(self, chunk_data, chunk_start):
        # chunk_start is ignored in the case of sequential download since we cannot seek the destination stream
        self.stream.write(chunk_data)
