# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import sys
import threading
from io import BytesIO

from azure.core.exceptions import HttpResponseError
from azure.core.tracing.context import tracing_context

from .request_handlers import validate_and_format_range_headers
from .response_handlers import process_storage_error, parse_length_from_content_range
from .encryption import decrypt_blob


def process_range_and_offset(start_range, end_range, length, encryption):
    start_offset, end_offset = 0, 0
    if encryption.get("key") is not None or encryption.get("resolver") is not None:
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


def process_content(data, start_offset, end_offset, encryption):
    if data is None:
        raise ValueError("Response cannot be None.")
    content = b"".join(list(data))
    if content and encryption.get("key") is not None or encryption.get("resolver") is not None:
        try:
            return decrypt_blob(
                encryption.get("required"),
                encryption.get("key"),
                encryption.get("resolver"),
                content,
                start_offset,
                end_offset,
                data.response.headers,
            )
        except Exception as error:
            raise HttpResponseError(message="Decryption failed.", response=data.response, error=error)
    return content


class _ChunkDownloader(object):
    def __init__(
        self,
        service=None,
        total_size=None,
        chunk_size=None,
        current_progress=None,
        start_range=None,
        end_range=None,
        stream=None,
        validate_content=None,
        encryption_options=None,
        **kwargs
    ):

        self.service = service

        # information on the download range/chunk size
        self.chunk_size = chunk_size
        self.total_size = total_size
        self.start_index = start_range
        self.end_index = end_range

        # the destination that we will write to
        self.stream = stream

        # download progress so far
        self.progress_total = current_progress

        # encryption
        self.encryption_options = encryption_options

        # parameters for each get operation
        self.validate_content = validate_content
        self.request_options = kwargs

    def _calculate_range(self, chunk_start):
        if chunk_start + self.chunk_size > self.end_index:
            chunk_end = self.end_index
        else:
            chunk_end = chunk_start + self.chunk_size
        return chunk_start, chunk_end

    def get_chunk_offsets(self):
        index = self.start_index
        while index < self.end_index:
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
            chunk_start, chunk_end, chunk_end, self.encryption_options
        )
        range_header, range_validation = validate_and_format_range_headers(
            download_range[0], download_range[1] - 1, check_content_md5=self.validate_content
        )

        try:
            _, response = self.service.download(
                range=range_header,
                range_get_content_md5=range_validation,
                validate_content=self.validate_content,
                data_stream_total=self.total_size,
                download_stream_current=self.progress_total,
                **self.request_options
            )
        except HttpResponseError as error:
            process_storage_error(error)

        chunk_data = process_content(response, offset[0], offset[1], self.encryption_options)

        # This makes sure that if_match is set so that we can validate
        # that subsequent downloads are to an unmodified blob
        if self.request_options.get("modified_access_conditions"):
            self.request_options["modified_access_conditions"].if_match = response.properties.etag
        return chunk_data


class ParallelChunkDownloader(_ChunkDownloader):
    def __init__(
        self,
        service=None,
        total_size=None,
        chunk_size=None,
        current_progress=None,
        start_range=None,
        end_range=None,
        stream=None,
        validate_content=None,
        encryption_options=None,
        **kwargs
    ):
        super(ParallelChunkDownloader, self).__init__(
            service=service,
            total_size=total_size,
            chunk_size=chunk_size,
            current_progress=current_progress,
            start_range=start_range,
            end_range=end_range,
            stream=stream,
            validate_content=validate_content,
            encryption_options=encryption_options,
            **kwargs
        )

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


class SequentialChunkDownloader(_ChunkDownloader):
    def _update_progress(self, length):
        self.progress_total += length

    def _write_to_stream(self, chunk_data, chunk_start):
        # chunk_start is ignored in the case of sequential download since we cannot seek the destination stream
        self.stream.write(chunk_data)


class StorageStreamDownloader(object):  # pylint: disable=too-many-instance-attributes
    """A streaming object to download from Azure Storage.

    The stream downloader can iterated, or download to open file or stream
    over multiple threads.
    """

    def __init__(
        self,
        service=None,
        config=None,
        offset=None,
        length=None,
        validate_content=None,
        encryption_options=None,
        extra_properties=None,
        **kwargs
    ):
        self.service = service
        self.config = config
        self.offset = offset
        self.length = length
        self.validate_content = validate_content
        self.encryption_options = encryption_options or {}
        self.request_options = kwargs
        self.location_mode = None
        self._download_complete = False

        # The service only provides transactional MD5s for chunks under 4MB.
        # If validate_content is on, get only self.MAX_CHUNK_GET_SIZE for the first
        # chunk so a transactional MD5 can be retrieved.
        self.first_get_size = (
            self.config.max_single_get_size if not self.validate_content else self.config.max_chunk_get_size
        )
        initial_request_start = self.offset if self.offset is not None else 0
        if self.length is not None and self.length - self.offset < self.first_get_size:
            initial_request_end = self.length
        else:
            initial_request_end = initial_request_start + self.first_get_size - 1

        self.initial_range, self.initial_offset = process_range_and_offset(
            initial_request_start, initial_request_end, self.length, self.encryption_options
        )

        self.download_size = None
        self.file_size = None
        self.response = self._initial_request()
        self.properties = self.response.properties

        # Set the content length to the download size instead of the size of
        # the last range
        self.properties.size = self.download_size

        # Overwrite the content range to the user requested range
        self.properties.content_range = "bytes {0}-{1}/{2}".format(self.offset, self.length, self.file_size)

        # Set additional properties according to download type
        if extra_properties:
            for prop, value in extra_properties.items():
                setattr(self.properties, prop, value)

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
            content = process_content(
                self.response, self.initial_offset[0], self.initial_offset[1], self.encryption_options
            )

        if content is not None:
            yield content
        if self._download_complete:
            return

        data_end = self.file_size
        if self.length is not None:
            # Use the length unless it is over the end of the file
            data_end = min(self.file_size, self.length + 1)

        downloader = SequentialChunkDownloader(
            service=self.service,
            total_size=self.download_size,
            chunk_size=self.config.max_chunk_get_size,
            current_progress=self.first_get_size,
            start_range=self.initial_range[1] + 1,  # start where the first download ended
            end_range=data_end,
            stream=None,
            validate_content=self.validate_content,
            encryption_options=self.encryption_options,
            use_location=self.location_mode,
            **self.request_options
        )

        for chunk in downloader.get_chunk_offsets():
            yield downloader.yield_chunk(chunk)

    def _initial_request(self):
        range_header, range_validation = validate_and_format_range_headers(
            self.initial_range[0],
            self.initial_range[1],
            start_range_required=False,
            end_range_required=False,
            check_content_md5=self.validate_content
        )

        try:
            location_mode, response = self.service.download(
                range=range_header,
                range_get_content_md5=range_validation,
                validate_content=self.validate_content,
                data_stream_total=None,
                download_stream_current=0,
                **self.request_options
            )

            # Check the location we read from to ensure we use the same one
            # for subsequent requests.
            self.location_mode = location_mode

            # Parse the total file size and adjust the download size if ranges
            # were specified
            self.file_size = parse_length_from_content_range(response.properties.content_range)
            if self.length is not None:
                # Use the length unless it is over the end of the file
                self.download_size = min(self.file_size, self.length - self.offset + 1)
            elif self.offset is not None:
                self.download_size = self.file_size - self.offset
            else:
                self.download_size = self.file_size

        except HttpResponseError as error:
            if self.offset is None and error.response.status_code == 416:
                # Get range will fail on an empty file. If the user did not
                # request a range, do a regular get request in order to get
                # any properties.
                try:
                    _, response = self.service.download(
                        validate_content=self.validate_content,
                        data_stream_total=0,
                        download_stream_current=0,
                        **self.request_options
                    )
                except HttpResponseError as error:
                    process_storage_error(error)

                # Set the download size to empty
                self.download_size = 0
                self.file_size = 0
            else:
                process_storage_error(error)

        # If the file is small, the download is complete at this point.
        # If file size is large, download the rest of the file in chunks.
        if response.properties.size != self.download_size:
            # Lock on the etag. This can be overriden by the user by specifying '*'
            if self.request_options.get("modified_access_conditions"):
                if not self.request_options["modified_access_conditions"].if_match:
                    self.request_options["modified_access_conditions"].if_match = response.properties.etag
        else:
            self._download_complete = True

        return response

    def content_as_bytes(self, max_connections=1):
        """Download the contents of this file.

        This operation is blocking until all data is downloaded.

        :param int max_connections:
            The number of parallel connections with which to download.
        :rtype: bytes
        """
        stream = BytesIO()
        self.download_to_stream(stream, max_connections=max_connections)
        return stream.getvalue()

    def content_as_text(self, max_connections=1, encoding="UTF-8"):
        """Download the contents of this file, and decode as text.

        This operation is blocking until all data is downloaded.

        :param int max_connections:
            The number of parallel connections with which to download.
        :rtype: str
        """
        content = self.content_as_bytes(max_connections=max_connections)
        return content.decode(encoding)

    def download_to_stream(self, stream, max_connections=1):
        """Download the contents of this file to a stream.

        :param stream:
            The stream to download to. This can be an open file-handle,
            or any writable stream. The stream must be seekable if the download
            uses more than one parallel connection.
        :returns: The properties of the downloaded file.
        :rtype: Any
        """
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
            content = process_content(
                self.response, self.initial_offset[0], self.initial_offset[1], self.encryption_options
            )

        # Write the content to the user stream
        if content is not None:
            stream.write(content)
        if self._download_complete:
            return self.properties

        data_end = self.file_size
        if self.length is not None:
            # Use the length unless it is over the end of the file
            data_end = min(self.file_size, self.length + 1)

        downloader_class = ParallelChunkDownloader if max_connections > 1 else SequentialChunkDownloader
        downloader = downloader_class(
            service=self.service,
            total_size=self.download_size,
            chunk_size=self.config.max_chunk_get_size,
            current_progress=self.first_get_size,
            start_range=self.initial_range[1] + 1,  # start where the first download ended
            end_range=data_end,
            stream=stream,
            validate_content=self.validate_content,
            encryption_options=self.encryption_options,
            use_location=self.location_mode,
            **self.request_options
        )

        if max_connections > 1:
            import concurrent.futures
            executor = concurrent.futures.ThreadPoolExecutor(max_connections)
            list(executor.map(
                    tracing_context.with_current_context(downloader.process_chunk),
                    downloader.get_chunk_offsets()
                ))
        else:
            for chunk in downloader.get_chunk_offsets():
                downloader.process_chunk(chunk)

        return self.properties
