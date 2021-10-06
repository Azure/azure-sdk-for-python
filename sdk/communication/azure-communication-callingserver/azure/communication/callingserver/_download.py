# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint: disable=invalid-overridden-method

import sys
import threading
from typing import Iterator
from io import BytesIO
from azure.core.exceptions import HttpResponseError
from azure.core.tracing.common import with_current_context
from .utils._utils import CallingServerUtils

class _ChunkDownloader(object):  # pylint: disable=too-many-instance-attributes
    def __init__(
        self,
        client=None,
        endpoint=None,
        total_size=None,
        chunk_size=None,
        current_progress=None,
        start_range=None,
        end_range=None,
        stream=None,
        parallel=None,
        **kwargs
    ):
        self.client = client
        self.endpoint = endpoint

        # Information on the download range/chunk size
        self.chunk_size = chunk_size
        self.total_size = total_size
        self.start_index = start_range
        self.end_index = end_range

        # The destination that we will write to
        self.stream = stream
        self.stream_lock = threading.Lock() if parallel else None
        self.progress_lock = threading.Lock() if parallel else None

        # For a parallel download, the stream is always seekable, so we note down the current position
        # in order to seek to the right place when out-of-order chunks come in
        self.stream_start = stream.tell() if parallel else None

        # Download progress so far
        self.progress_total = current_progress

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
        chunk_data = self._download_chunk(chunk_start, chunk_end - 1)
        length = chunk_end - chunk_start
        if length > 0:
            self._write_to_stream(chunk_data, chunk_start)
            self._update_progress(length)

    def yield_chunk(self, chunk_start):
        chunk_start, chunk_end = self._calculate_range(chunk_start)
        return self._download_chunk(chunk_start, chunk_end - 1)

    def _update_progress(self, length):
        if self.progress_lock:
            with self.progress_lock:  # pylint: disable=not-context-manager
                self.progress_total += length
        else:
            self.progress_total += length

    def _write_to_stream(self, chunk_data, chunk_start):
        if self.stream_lock:
            with self.stream_lock:  # pylint: disable=not-context-manager
                self.stream.seek(self.stream_start +
                                 (chunk_start - self.start_index))
                self.stream.write(chunk_data)
        else:
            self.stream.write(chunk_data)

    def _download_chunk(self, chunk_start, chunk_end):
        range_header = CallingServerUtils.validate_and_format_range_headers(
            chunk_start,
            chunk_end
        )

        response = self.client.download(
            content_url=self.endpoint,
            http_range=range_header,
            **self.request_options
        )

        #pylint: disable=protected-access
        return response.response.internal_response.content


class _ChunkIterator(object):
    """sync iterator for chunks in content download stream."""

    def __init__(self, size, content, downloader, chunk_size):
        self.size = size
        self._chunk_size = chunk_size
        self._current_content = content
        self._iter_downloader = downloader
        self._iter_chunks = None
        self._complete = (size == 0)

    def __len__(self):
        return self.size

    def __iter__(self):
        raise TypeError("stream must be iterated synchronously.")

    def __aiter__(self):
        return self

    def __anext__(self):
        """Iterate through responses."""
        if self._complete:
            raise StopIteration("Download complete")
        if not self._iter_downloader:
            # cut the data obtained from initial GET into chunks
            if len(self._current_content) > self._chunk_size:
                return self._get_chunk_data()
            self._complete = True
            return self._current_content

        if not self._iter_chunks:
            self._iter_chunks = self._iter_downloader.get_chunk_offsets()

        # initial GET result still has more than _chunk_size bytes of data
        if len(self._current_content) >= self._chunk_size:
            return self._get_chunk_data()

        try:
            chunk = next(self._iter_chunks)
            self._current_content += self._iter_downloader.yield_chunk(chunk)
        except StopIteration as ex:
            self._complete = True
            # it's likely that there some data left in self._current_content
            if self._current_content:
                return self._current_content
            raise StopIteration("Download complete") from ex

        return self._get_chunk_data()

    def _get_chunk_data(self):
        chunk_data = self._current_content[: self._chunk_size]
        self._current_content = self._current_content[self._chunk_size:]
        return chunk_data


class ContentStreamDownloader():  # pylint: disable=too-many-instance-attributes
    """A streaming object to download recording content.
    :ivar str endpoint:
        The url where the content is located.
    :ivar ~azure.communication.callingserver.ContentProperties properties:
        The properties of the content being downloaded. If only a range of the data is being
        downloaded, this will be reflected in the properties.
    :ivar int size:
        The size of the total data in the stream. This will be the byte range if speficied,
        otherwise the total size of the requested content.
    """

    def __init__(
        self,
        clients=None,
        config=None,
        start_range=None,
        end_range=None,
        endpoint=None,
        parallel_download_options=None,
        **kwargs
    ):
        self.endpoint = endpoint
        self.properties = None
        self.size = None

        self._clients = clients
        self._config = config
        self._start_range = start_range
        self._end_range = end_range
        self._max_concurrency = parallel_download_options.max_concurrency if parallel_download_options else 1
        self._request_options = kwargs
        self._download_complete = False
        self._current_content = None
        self._file_size = None
        self._non_empty_ranges = None
        self._response = None
        self._block_size = parallel_download_options.block_size if parallel_download_options else 4*1024*1024
        initial_request_start = self._start_range if self._start_range is not None else 0
        if self._end_range is not None and self._end_range - self._start_range < self._block_size:
            initial_request_end = self._end_range
        else:
            initial_request_end = initial_request_start + self._block_size - 1

        self._initial_range = (initial_request_start, initial_request_end)
        self._response = self._initial_request()
        if self.size == 0:
            self._current_content = b""
        else:
            self._current_content = self._response.response.internal_response.content  # pylint: disable=protected-access

    def _initial_request(self):
        range_header = CallingServerUtils.validate_and_format_range_headers(
            self._initial_range[0],
            self._initial_range[1])
        try:
            response = self._clients.download(
                content_url=self.endpoint,
                http_range=range_header,
                **self._request_options)
            # Parse the total file size and adjust the download size if ranges
            # were specified
            self._file_size = CallingServerUtils.parse_length_from_content_range(
                response.response.headers["Content-Range"])

            if self._end_range is not None:
                # Use the length unless it is over the end of the file
                self.size = min(self._file_size,
                                self._end_range - self._start_range + 1)
            elif self._start_range is not None:
                self.size = self._file_size - self._start_range
            else:
                self.size = self._file_size

        except HttpResponseError as error:

            if self._start_range is None and error.response.status_code == 416:
                # Get range will fail on an empty file. If the user did not
                # request a range, do a regular get request in order to get
                # any properties.
                response = self._clients.download(
                    content_url=self.endpoint,
                    **self._request_options)

                # Set the download size to empty
                self.size = 0
                self._file_size = 0
            else:
                raise

        # If the file is small, the download is complete at this point.
        # If file size is large, download the rest of the file in chunks.
        if int(response.response.headers["Content-Length"]) >= self.size:
            self._download_complete = True
        return response

    def chunks(self):
        # type: () -> Iterator[bytes]
        """Iterate over chunks in the download stream.
        :rtype: Iterator[bytes]
        """
        if self.size == 0 or self._download_complete:
            iter_downloader = None
        else:
            data_end = self._file_size
            if self._end_range is not None:
                # Use the length unless it is over the end of the file
                data_end = min(self._file_size, self._end_range + 1)
            iter_downloader = _ChunkDownloader(
                client=self._clients,
                endpoint=self.endpoint,
                total_size=self.size,
                chunk_size=self._config.max_chunk_get_size,
                current_progress=self._block_size,
                # Start where the first download ended
                start_range=self._initial_range[1] + 1,
                end_range=data_end,
                stream=None,
                parallel=False,
                **self._request_options)
        return _ChunkIterator(
            size=self.size,
            content=self._current_content,
            downloader=iter_downloader,
            chunk_size=self._config.max_chunk_get_size)

    def readall(self):
        """Download the contents.
        This operation is blocking until all data is downloaded.
        :rtype: bytes or str
        """
        stream = BytesIO()
        self.readinto(stream)
        return stream.getvalue()

    def readinto(self, stream):
        """Download the contents into a stream.
        :param stream:
            The stream to download to. This can be an open file-handle,
            or any writable stream. The stream must be seekable if the download
            uses more than one parallel connection.
        :returns: The number of bytes read.
        :rtype: int
        """
        # the stream must be seekable if parallel download is required
        parallel = self._max_concurrency > 1
        if parallel:
            error_message = "Target stream handle must be seekable."
            if sys.version_info >= (3,) and not stream.seekable():
                raise ValueError(error_message)

            try:
                stream.seek(stream.tell())
            except (NotImplementedError, AttributeError) as ex:
                raise ValueError(error_message) from ex

        # Write the content to the user stream
        stream.write(self._current_content)
        if self._download_complete:
            return self.size

        data_end = self._file_size
        if self._end_range is not None:
            # Use the length unless it is over the end of the file
            data_end = min(self._file_size, self._end_range + 1)

        downloader = _ChunkDownloader(
            client=self._clients,
            endpoint=self.endpoint,
            total_size=self.size,
            chunk_size=self._block_size,
            current_progress=self._block_size,
            # start where the first download ended
            start_range=self._initial_range[1] + 1,
            end_range=data_end,
            stream=stream,
            parallel=parallel,
            **self._request_options)

        if parallel:
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor(self._max_concurrency) as executor:
                list(executor.map(
                    with_current_context(downloader.process_chunk),
                    downloader.get_chunk_offsets()
                ))
        else:
            for chunk in downloader.get_chunk_offsets():
                downloader.process_chunk(chunk)

        return self.size
