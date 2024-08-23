# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from __future__ import annotations

import inspect
import sys
from collections.abc import AsyncIterable, AsyncIterator
from io import BytesIO, IOBase, UnsupportedOperation
from typing import AnyStr, IO, Optional, Union

from .streams import StructuredMessageConstants, StructuredMessageProperties
from .validation import calculate_crc64


class AsyncIterStreamer(IOBase):
    """An async file-like wrapper over an async iterable."""

    def __init__(
            self, iterable: AsyncIterable[AnyStr],
            length: Optional[int] = None,
            encoding: str = "UTF-8",
            *,
            block_str: bool = False):
        self.iterable: Union[AsyncIterable[str], AsyncIterable[bytes]] = iterable
        self.iterator: Union[AsyncIterator[str], AsyncIterator[bytes]] = iterable.__aiter__()
        self.length = length
        self.encoding = encoding
        self.block_str = block_str

        self._leftover = bytearray()
        self._offset = 0

    def __len__(self):
        if self.length is not None:
            return self.length
        raise UnsupportedOperation()

    def __aiter__(self):
        return self.iterator

    def __anext__(self):
        return self.iterator.__anext__()

    def tell(self):
        return self._offset

    def readable(self):
        return True

    async def read(self, size: int = -1) -> bytes:
        if size < 0:
            size = sys.maxsize
        data = self._leftover
        count = len(self._leftover)
        try:
            while count < size:
                chunk = await self.iterator.__anext__()
                if isinstance(chunk, str):
                    if self.block_str:
                        raise TypeError("Iterable[str] is not supported.")
                    chunk = chunk.encode(self.encoding)
                data.extend(chunk)
                count += len(chunk)
        # This means count < size and what's leftover will be returned in this call.
        except StopAsyncIteration:
            self._leftover = bytearray()

        if count >= size:
            self._leftover = data[size:]

        ret = bytes(memoryview(data)[:size])
        self._offset += len(ret)
        return ret


class StructuredMessageDecodeStream:  # pylint: disable=too-many-instance-attributes

    message_version: int
    """The version of the structured message."""
    message_length: int
    """The total length of the structured message."""
    flags: StructuredMessageProperties
    """The properties included in the structured message."""
    num_segments: int
    """The number of message segments."""

    _inner_stream: IO[bytes]
    _message_offset: int
    _message_crc64: int
    _segment_number: int
    _segment_crc64: int
    _segment_content_length: int
    _segment_content_offset: int

    def __init__(self, inner_stream: IO[bytes], content_length: int) -> None:
        self.message_length = content_length
        # The stream should be at least long enough to hold minimum header length
        if self.message_length < StructuredMessageConstants.V1_HEADER_LENGTH:
            raise ValueError("Content not long enough to contain a valid message header.")

        self._inner_stream = inner_stream
        self._message_offset = 0
        self._message_crc64 = 0

        self._segment_number = 0
        self._segment_crc64 = 0
        self._segment_content_length = 0
        self._segment_content_offset = 0

    @property
    def _segment_header_length(self) -> int:
        return StructuredMessageConstants.V1_SEGMENT_HEADER_LENGTH

    @property
    def _segment_footer_length(self) -> int:
        return StructuredMessageConstants.CRC64_LENGTH if StructuredMessageProperties.CRC64 in self.flags else 0

    @property
    def _message_footer_length(self) -> int:
        return StructuredMessageConstants.CRC64_LENGTH if StructuredMessageProperties.CRC64 in self.flags else 0

    @property
    def _end_of_segment_content(self) -> bool:
        return self._segment_content_offset == self._segment_content_length

    async def read(self, size: int = -1) -> bytes:
        if size == 0:
            return b''
        if size < 0:
            size = sys.maxsize

        # On the first read, read message header and first segment header
        if self._message_offset == 0:
            await self._read_message_header()
            await self._read_segment_header()

            # Special case for 0 length content
            if self._end_of_segment_content:
                await self._read_segment_footer()
                if self.num_segments > 1:
                    raise ValueError("First message segment was empty but more segments were detected.")
                await self._read_message_footer()
                return b''

        count = 0
        content = BytesIO()
        while count < size and not (self._end_of_segment_content and self._message_offset == self.message_length):
            if self._end_of_segment_content:
                await self._read_segment_header()

            segment_remaining = self._segment_content_length - self._segment_content_offset
            read_size = min(segment_remaining, size - count)

            segment_content = await self._read_from_inner(read_size)
            content.write(segment_content)

            # Update the running CRC64 for the segment and message
            if StructuredMessageProperties.CRC64 in self.flags:
                self._segment_crc64 = calculate_crc64(segment_content, self._segment_crc64)
                self._message_crc64 = calculate_crc64(segment_content, self._message_crc64)

            self._segment_content_offset += read_size
            self._message_offset += read_size
            count += read_size

            if self._end_of_segment_content:
                await self._read_segment_footer()
                # If we are on the last segment, also read the message footer
                if self._segment_number == self.num_segments:
                    await self._read_message_footer()

        # One final check to ensure if we think we've reached the end of the stream
        # that the current segment number matches the total.
        if self._message_offset == self.message_length and self._segment_number != self.num_segments:
            raise ValueError("Invalid structured message data detected.")

        return content.getvalue()

    async def _read_from_inner(self, size: int) -> bytes:
        data = self._inner_stream.read(size)
        if inspect.isawaitable(data):
            data = await data
        if len(data) != size:
            raise ValueError("Invalid structured message data detected. Stream content incomplete.")
        return data

    async def _read_message_header(self) -> None:
        # The first byte should always be the message version
        self.message_version = int.from_bytes(await self._read_from_inner(1), 'little')

        if self.message_version == 1:
            message_length = int.from_bytes(await self._read_from_inner(8), 'little')
            if message_length != self.message_length:
                raise ValueError(f"Structured message length {message_length} "
                                 f"did not match content length {self.message_length}")

            self.flags = StructuredMessageProperties(int.from_bytes(await self._read_from_inner(2), 'little'))
            self.num_segments = int.from_bytes(await self._read_from_inner(2), 'little')

            self._message_offset += StructuredMessageConstants.V1_HEADER_LENGTH

        else:
            raise ValueError(f"The structured message version is not supported: {self.message_version}")

    async def _read_message_footer(self) -> None:
        # Sanity check: There should only be self._message_footer_length (could be 0) bytes left to consume.
        # If not, it is likely the message header contained incorrect info.
        if self.message_length - self._message_offset != self._message_footer_length:
            raise ValueError("Invalid structured message data detected.")

        if StructuredMessageProperties.CRC64 in self.flags:
            message_crc = await self._read_from_inner(StructuredMessageConstants.CRC64_LENGTH)

            if self._message_crc64 != int.from_bytes(message_crc, 'little'):
                raise ValueError("CRC64 mismatch detected in message trailer. "
                                 "All data read should be considered invalid.")

        self._message_offset += self._message_footer_length

    async def _read_segment_header(self) -> None:
        segment_number = int.from_bytes(await self._read_from_inner(2), 'little')
        if segment_number != self._segment_number + 1:
            raise ValueError(f"Structured message segment number invalid or out of order {segment_number}")
        self._segment_number = segment_number
        self._segment_content_length = int.from_bytes(await self._read_from_inner(8), 'little')
        self._message_offset += self._segment_header_length

        self._segment_content_offset = 0
        self._segment_crc64 = 0

    async def _read_segment_footer(self) -> None:
        if StructuredMessageProperties.CRC64 in self.flags:
            segment_crc = await self._read_from_inner(StructuredMessageConstants.CRC64_LENGTH)

            if self._segment_crc64 != int.from_bytes(segment_crc, 'little'):
                raise ValueError(f"CRC64 mismatch detected in segment {self._segment_number}. "
                                 f"All data read should be considered invalid.")

        self._message_offset += self._segment_footer_length
