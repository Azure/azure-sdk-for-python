# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import sys
import threading
from io import BytesIO

from azure.core.exceptions import HttpResponseError

from .models import ModifiedAccessConditions
from .request_handlers import validate_and_format_range_headers
from .response_handlers import process_storage_error, parse_length_from_content_range
from .encryption import decrypt_blob
from .downloads import process_range_and_offset


async def process_content(data, start_offset, end_offset, encryption):
    if data is None:
        raise ValueError("Response cannot be None.")
    content = b""
    async for chunk in data:
        content += chunk
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


class _AsyncChunkDownloader(object):

    def __init__(
            self, service=None,
            total_size=None,
            chunk_size=None,
            current_progress=None,
            start_range=None,
            end_range=None,
            stream=None,
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
            self._update_progress(length)

    async def yield_chunk(self, chunk_start):
        chunk_start, chunk_end = self._calculate_range(chunk_start)
        return await self._download_chunk(chunk_start, chunk_end)

    async def _update_progress(self, length):
        async with self.progress_lock:
            self.progress_total += length

    async def _write_to_stream(self, chunk_data, chunk_start):
        async with self.stream_lock:
            self.stream.seek(self.stream_start + (chunk_start - self.start_index))
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
