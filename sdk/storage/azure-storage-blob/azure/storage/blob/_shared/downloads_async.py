# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import sys
import asyncio
from io import BytesIO
from itertools import islice

from azure.core.exceptions import HttpResponseError

from .request_handlers import validate_and_format_range_headers
from .response_handlers import process_storage_error, parse_length_from_content_range
from .encryption import decrypt_blob
from .downloads import process_range_and_offset


async def process_content(data, start_offset, end_offset, encryption):
    if data is None:
        raise ValueError("Response cannot be None.")
    content = data.response.body()
    if encryption.get('key') is not None or encryption.get('resolver') is not None:
        try:
            return decrypt_blob(
                encryption.get('required'),
                encryption.get('key'),
                encryption.get('resolver'),
                content,
                start_offset,
                end_offset,
                data.response.headers)
        except Exception as error:
            raise HttpResponseError(
                message="Decryption failed.",
                response=data.response,
                error=error)
    return content


class _AsyncChunkDownloader(object):  # pylint: disable=too-many-instance-attributes

    def __init__(
            self, service=None,
            total_size=None,
            chunk_size=None,
            current_progress=None,
            start_range=None,
            end_range=None,
            stream=None,
            parallel=None,
            validate_content=None,
            encryption_options=None,
            **kwargs):

        self.service = service

        # information on the download range/chunk size
        self.chunk_size = chunk_size
        self.total_size = total_size
        self.start_index = start_range
        self.end_index = end_range

        # the destination that we will write to
        self.stream = stream
        self.stream_lock = asyncio.Lock() if parallel else None
        self.progress_lock = asyncio.Lock() if parallel else None

        # for a parallel download, the stream is always seekable, so we note down the current position
        # in order to seek to the right place when out-of-order chunks come in
        self.stream_start = stream.tell() if parallel else None

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

    async def process_chunk(self, chunk_start):
        chunk_start, chunk_end = self._calculate_range(chunk_start)
        chunk_data = await self._download_chunk(chunk_start, chunk_end)
        length = chunk_end - chunk_start
        if length > 0:
            await self._write_to_stream(chunk_data, chunk_start)
            await self._update_progress(length)

    async def yield_chunk(self, chunk_start):
        chunk_start, chunk_end = self._calculate_range(chunk_start)
        return await self._download_chunk(chunk_start, chunk_end)

    async def _update_progress(self, length):
        if self.progress_lock:
            async with self.progress_lock:
                self.progress_total += length
        else:
            self.progress_total += length

    async def _write_to_stream(self, chunk_data, chunk_start):
        if self.stream_lock:
            async with self.stream_lock:
                self.stream.seek(self.stream_start + (chunk_start - self.start_index))
                self.stream.write(chunk_data)
        else:
            self.stream.write(chunk_data)

    async def _download_chunk(self, chunk_start, chunk_end):
        download_range, offset = process_range_and_offset(
            chunk_start, chunk_end, chunk_end, self.encryption_options)
        range_header, range_validation = validate_and_format_range_headers(
            download_range[0],
            download_range[1] - 1,
            check_content_md5=self.validate_content)

        try:
            _, response = await self.service.download(
                range=range_header,
                range_get_content_md5=range_validation,
                validate_content=self.validate_content,
                data_stream_total=self.total_size,
                download_stream_current=self.progress_total,
                **self.request_options)
        except HttpResponseError as error:
            process_storage_error(error)

        chunk_data = await process_content(response, offset[0], offset[1], self.encryption_options)

        # This makes sure that if_match is set so that we can validate
        # that subsequent downloads are to an unmodified blob
        if self.request_options.get('modified_access_conditions'):
            self.request_options['modified_access_conditions'].if_match = response.properties.etag

        return chunk_data

class StorageStreamDownloader(object):  # pylint: disable=too-many-instance-attributes
    """A streaming object to download from Azure Storage.

    The stream downloader can iterated, or download to open file or stream
    over multiple threads.
    """

    def __init__(
            self, service=None,
            config=None,
            offset=None,
            length=None,
            validate_content=None,
            encryption_options=None,
            **kwargs):
        self.service = service
        self.config = config
        self.offset = offset
        self.length = length
        self.validate_content = validate_content
        self.encryption_options = encryption_options or {}
        self.request_options = kwargs
        self.location_mode = None
        self._download_complete = False
        self._current_content = None
        self._iter_downloader = None
        self._iter_chunks = None

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

        self.initial_range, self.initial_offset = process_range_and_offset(
            initial_request_start, initial_request_end, self.length, self.encryption_options)
        self.download_size = None
        self.file_size = None
        self.response = None
        self.properties = None

    def __len__(self):
        return self.download_size

    def __iter__(self):
        raise TypeError("Async stream must be iterated asynchronously.")

    def __aiter__(self):
        return self

    async def __anext__(self):
        """Iterate through responses."""
        if self._current_content is None:
            if self.download_size == 0:
                self._current_content = b""
            else:
                self._current_content = await process_content(
                    self.response, self.initial_offset[0], self.initial_offset[1], self.encryption_options)
            if not self._download_complete:
                data_end = self.file_size
                if self.length is not None:
                    # Use the length unless it is over the end of the file
                    data_end = min(self.file_size, self.length + 1)
                self._iter_downloader = _AsyncChunkDownloader(
                    service=self.service,
                    total_size=self.download_size,
                    chunk_size=self.config.max_chunk_get_size,
                    current_progress=self.first_get_size,
                    start_range=self.initial_range[1] + 1,  # start where the first download ended
                    end_range=data_end,
                    stream=None,
                    parallel=False,
                    validate_content=self.validate_content,
                    encryption_options=self.encryption_options,
                    use_location=self.location_mode,
                    **self.request_options)
                self._iter_chunks = self._iter_downloader.get_chunk_offsets()
        elif self._download_complete:
            raise StopAsyncIteration("Download complete")
        else:
            try:
                chunk = next(self._iter_chunks)
            except StopIteration:
                raise StopAsyncIteration("DownloadComplete")
            self._current_content = await self._iter_downloader.yield_chunk(chunk)

        return self._current_content

    async def setup(self, extra_properties=None):
        if self.response:
            raise ValueError("Download stream already initialized.")
        self.response = await self._initial_request()
        self.properties = self.response.properties

        # Set the content length to the download size instead of the size of
        # the last range
        self.properties.size = self.download_size

        # Overwrite the content range to the user requested range
        self.properties.content_range = 'bytes {0}-{1}/{2}'.format(self.offset, self.length, self.file_size)

        # Set additional properties according to download type
        if extra_properties:
            for prop, value in extra_properties.items():
                setattr(self.properties, prop, value)

        # Overwrite the content MD5 as it is the MD5 for the last range instead
        # of the stored MD5
        # TODO: Set to the stored MD5 when the service returns this
        self.properties.content_md5 = None

    async def _initial_request(self):
        range_header, range_validation = validate_and_format_range_headers(
            self.initial_range[0],
            self.initial_range[1],
            start_range_required=False,
            end_range_required=False,
            check_content_md5=self.validate_content)

        try:
            location_mode, response = await self.service.download(
                range=range_header,
                range_get_content_md5=range_validation,
                validate_content=self.validate_content,
                data_stream_total=None,
                download_stream_current=0,
                **self.request_options)

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
                    _, response = await self.service.download(
                        validate_content=self.validate_content,
                        data_stream_total=0,
                        download_stream_current=0,
                        **self.request_options)
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
            if self.request_options.get('modified_access_conditions'):
                if not self.request_options['modified_access_conditions'].if_match:
                    self.request_options['modified_access_conditions'].if_match = response.properties.etag
        else:
            self._download_complete = True
        return response

    async def content_as_bytes(self, max_connections=1):
        """Download the contents of this file.

        This operation is blocking until all data is downloaded.

        :param int max_connections:
            The number of parallel connections with which to download.
        :rtype: bytes
        """
        stream = BytesIO()
        await self.download_to_stream(stream, max_connections=max_connections)
        return stream.getvalue()

    async def content_as_text(self, max_connections=1, encoding='UTF-8'):
        """Download the contents of this file, and decode as text.

        This operation is blocking until all data is downloaded.

        :param int max_connections:
            The number of parallel connections with which to download.
        :rtype: str
        """
        content = await self.content_as_bytes(max_connections=max_connections)
        return content.decode(encoding)

    async def download_to_stream(self, stream, max_connections=1):
        """Download the contents of this file to a stream.

        :param stream:
            The stream to download to. This can be an open file-handle,
            or any writable stream. The stream must be seekable if the download
            uses more than one parallel connection.
        :returns: The properties of the downloaded file.
        :rtype: Any
        """
        if self._iter_downloader:
            raise ValueError("Stream is currently being iterated.")

        # the stream must be seekable if parallel download is required
        parallel = max_connections > 1
        if parallel:
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
            content = await process_content(
                self.response, self.initial_offset[0], self.initial_offset[1], self.encryption_options)

        # Write the content to the user stream
        if content is not None:
            stream.write(content)
        if self._download_complete:
            return self.properties

        data_end = self.file_size
        if self.length is not None:
            # Use the length unless it is over the end of the file
            data_end = min(self.file_size, self.length + 1)

        downloader = _AsyncChunkDownloader(
            service=self.service,
            total_size=self.download_size,
            chunk_size=self.config.max_chunk_get_size,
            current_progress=self.first_get_size,
            start_range=self.initial_range[1] + 1,  # start where the first download ended
            end_range=data_end,
            stream=stream,
            parallel=parallel,
            validate_content=self.validate_content,
            encryption_options=self.encryption_options,
            use_location=self.location_mode,
            **self.request_options)

        dl_tasks = downloader.get_chunk_offsets()
        running_futures = [
            asyncio.ensure_future(downloader.process_chunk(d))
            for d in islice(dl_tasks, 0, max_connections)
        ]
        while running_futures:
            # Wait for some download to finish before adding a new one
            _done, running_futures = await asyncio.wait(
                running_futures, return_when=asyncio.FIRST_COMPLETED)
            try:
                next_chunk = next(dl_tasks)
            except StopIteration:
                break
            else:
                running_futures.add(asyncio.ensure_future(downloader.process_chunk(next_chunk)))

        if running_futures:
            # Wait for the remaining downloads to finish
            await asyncio.wait(running_futures)
        return self.properties
