# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
# pylint: disable=invalid-overridden-method

import asyncio
import sys
from typing import AsyncIterator
from io import BytesIO
from itertools import islice

from azure.core.exceptions import HttpResponseError
from .._download import _ChunkDownloader
from ..utils._utils import CallingServerUtils

class _AsyncChunkDownloader(_ChunkDownloader):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.stream_lock = asyncio.Lock() if kwargs.get('parallel') else None
        self.progress_lock = asyncio.Lock() if kwargs.get('parallel') else None

    async def process_chunk(self, chunk_start):
        chunk_start, chunk_end = self._calculate_range(chunk_start)
        chunk_data = await self._download_chunk(chunk_start, chunk_end - 1)
        length = chunk_end - chunk_start
        if length > 0:
            await self._write_to_stream(chunk_data, chunk_start)
            await self._update_progress(length)

    async def yield_chunk(self, chunk_start):
        chunk_start, chunk_end = self._calculate_range(chunk_start)
        return await self._download_chunk(chunk_start, chunk_end - 1)

    async def _update_progress(self, length):
        if self.progress_lock:
            async with self.progress_lock:  # pylint: disable=not-async-context-manager
                self.progress_total += length
        else:
            self.progress_total += length

    async def _write_to_stream(self, chunk_data, chunk_start):
        if self.stream_lock:
            async with self.stream_lock:  # pylint: disable=not-async-context-manager
                self.stream.seek(self.stream_start + (chunk_start - self.start_index))
                self.stream.write(chunk_data)
        else:
            self.stream.write(chunk_data)

    async def _download_chunk(self, chunk_start, chunk_end):
        range_header = CallingServerUtils.validate_and_format_range_headers(
            chunk_start,
            chunk_end
        )

        response = await self.client.download(
            content_url=self.endpoint,
            http_range=range_header,
            **self.request_options
        )

        #pylint: disable=protected-access
        return await self._response.response.internal_response.content.read()

class _AsyncChunkIterator(object):
    """Async iterator for chunks in content download stream."""

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
        raise TypeError("Async stream must be iterated asynchronously.")

    def __aiter__(self):
        return self

    async def __anext__(self):
        """Iterate through responses."""
        if self._complete:
            raise StopAsyncIteration("Download complete")
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
            self._current_content += await self._iter_downloader.yield_chunk(chunk)
        except StopIteration as ex:
            self._complete = True
            # it's likely that there some data left in self._current_content
            if self._current_content:
                return self._current_content
            raise StopAsyncIteration("Download complete") from ex

        return self._get_chunk_data()

    def _get_chunk_data(self):
        chunk_data = self._current_content[: self._chunk_size]
        self._current_content = self._current_content[self._chunk_size:]
        return chunk_data

class ContentStreamDownloader(): # pylint: disable=too-many-instance-attributes
    """A streaming object to download recording content.
    :ivar str endpoint:
        The url where the content is located.
    """
    def __init__(
        self,
        endpoint,
        clients,
        config,
        *,
        start_range=None,
        end_range=None,
        max_concurrency=1,
        block_size=4*1024*1024,
        **kwargs
    ):
        self.endpoint = endpoint
        self.properties = None
        self.size = None

        self._clients = clients
        self._config = config
        self._start_range = start_range
        self._end_range = end_range
        self._max_concurrency = max_concurrency
        self._request_options = kwargs
        self._download_complete = False
        self._current_content = None
        self._file_size = None
        self._non_empty_ranges = None
        self._response = None
        self._block_size = block_size
        initial_request_start = self._start_range if self._start_range is not None else 0
        if self._end_range is not None and self._end_range - self._start_range < self._block_size:
            initial_request_end = self._end_range
        else:
            initial_request_end = initial_request_start + self._block_size - 1

        self._initial_range = (initial_request_start, initial_request_end)

    async def _setup(self):
        self._response = await self._initial_request()
        if self.size == 0:
            self._current_content = b""
        else:
            self._current_content = await self._response.response.internal_response.content.read() #pylint: disable=protected-access

    async def _initial_request(self):
        http_range = CallingServerUtils.validate_and_format_range_headers(
            self._initial_range[0],
            self._initial_range[1])

        try:
            response = await self._clients.download(
                http_range=http_range,
                content_url=self.endpoint,
                **self._request_options)
            # Parse the total file size and adjust the download size if ranges
            # were specified
            self._file_size = CallingServerUtils.parse_length_from_content_range(
                response.response.headers["Content-Range"]
            )
            if self._end_range is not None:
                # Use the length unless it is over the end of the file
                self.size = min(self._file_size, self._end_range - self._start_range + 1)
            elif self._start_range is not None:
                self.size = self._file_size - self._start_range
            else:
                self.size = self._file_size

        except HttpResponseError as error:
            if self._start_range is None and error.response.status_code == 416:
                # Get range will fail on an empty file. If the user did not
                # request a range, do a regular get request in order to get
                # any properties.
                response = await self._clients.download(
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

    def chunks(self) -> AsyncIterator[bytes]:
        """Iterate over chunks in the download stream.
        :rtype: AsyncIterator[bytes]
        """
        if self.size == 0 or self._download_complete:
            iter_downloader = None
        else:
            data_end = self._file_size
            if self._end_range is not None:
                # Use the length unless it is over the end of the file
                data_end = min(self._file_size, self._end_range + 1)
            iter_downloader = _AsyncChunkDownloader(
                client=self._clients,
                endpoint=self.endpoint,
                total_size=self.size,
                chunk_size=self._config.max_chunk_get_size,
                current_progress=self._block_size,
                start_range=self._initial_range[1] + 1,  # Start where the first download ended
                end_range=data_end,
                stream=None,
                parallel=False,
                **self._request_options)
        return _AsyncChunkIterator(
            size=self.size,
            content=self._current_content,
            downloader=iter_downloader,
            chunk_size=self._config.max_chunk_get_size)

    async def readall(self):
        """Download the contents.
        This operation is blocking until all data is downloaded.
        :rtype: bytes or str
        """
        stream = BytesIO()
        await self.readinto(stream)
        return stream.getvalue()

    async def readinto(self, stream) -> int:
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
        # current_content = await self._current_content.read()
        stream.write(self._current_content)
        if self._download_complete:
            return self.size

        data_end = self._file_size
        if self._end_range is not None:
            # Use the length unless it is over the end of the file
            data_end = min(self._file_size, self._end_range + 1)

        downloader = _AsyncChunkDownloader(
            client=self._clients,
            endpoint=self.endpoint,
            total_size=self.size,
            chunk_size=self._block_size,
            current_progress=self._block_size,
            start_range=self._initial_range[1] + 1,  # start where the first download ended
            end_range=data_end,
            stream=stream,
            parallel=parallel,
            **self._request_options)

        dl_tasks = downloader.get_chunk_offsets()
        running_futures = [
            asyncio.ensure_future(downloader.process_chunk(d))
            for d in islice(dl_tasks, 0, self._max_concurrency)
        ]
        while running_futures:
            # Wait for some download to finish before adding a new one
            done, running_futures = await asyncio.wait(
                running_futures, return_when=asyncio.FIRST_COMPLETED)
            for task in done:
                task.result()
            try:
                next_chunk = next(dl_tasks)
            except StopIteration:
                break
            else:
                running_futures.add(asyncio.ensure_future(downloader.process_chunk(next_chunk)))

        if running_futures:
            # Wait for the remaining downloads to finish
            done, _ = await asyncio.wait(running_futures)
            for task in done:
                task.result()
        return self.size
