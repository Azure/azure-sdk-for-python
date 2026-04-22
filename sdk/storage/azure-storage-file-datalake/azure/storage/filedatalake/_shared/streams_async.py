# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import sys
from io import BytesIO, IOBase
from typing import AsyncIterator

from .streams import (
    StructuredMessageConstants,
    StructuredMessageProperties,
    parse_message_header,
    parse_segment_header,
)
from .validation import calculate_crc64


class AsyncStructuredMessageDecoder(
    IOBase
):  # pylint: disable=too-many-instance-attributes

    message_version: int
    """The version of the structured message."""
    message_length: int
    """The total length of the structured message."""
    flags: StructuredMessageProperties
    """The properties included in the structured message."""
    num_segments: int
    """The number of message segments."""

    _inner_iterator: AsyncIterator[bytes]
    _buffer: bytes
    _message_offset: int
    _message_crc64: int
    _segment_number: int
    _segment_crc64: int
    _segment_content_length: int
    _segment_content_offset: int
    _block_size: int

    def __init__(
        self,
        inner_iterator: AsyncIterator[bytes],
        content_length: int,
        *,
        block_size: int = 4096,
    ) -> None:
        self.message_length = content_length
        # The stream should be at least long enough to hold minimum header length
        if self.message_length < StructuredMessageConstants.V1_HEADER_LENGTH:
            raise ValueError(
                "Content not long enough to contain a valid message header."
            )

        self._inner_iterator = inner_iterator
        self._buffer = b""
        self._message_offset = 0
        self._message_crc64 = 0

        self._segment_number = 0
        self._segment_crc64 = 0
        self._segment_content_length = 0
        self._segment_content_offset = 0
        self._block_size = block_size
        super().__init__()

    @property
    def content_length(self) -> int:
        return self.message_length

    @property
    def _segment_header_length(self) -> int:
        return StructuredMessageConstants.V1_SEGMENT_HEADER_LENGTH

    @property
    def _segment_footer_length(self) -> int:
        return (
            StructuredMessageConstants.CRC64_LENGTH
            if StructuredMessageProperties.CRC64 in self.flags
            else 0
        )

    @property
    def _message_footer_length(self) -> int:
        return (
            StructuredMessageConstants.CRC64_LENGTH
            if StructuredMessageProperties.CRC64 in self.flags
            else 0
        )

    @property
    def _end_of_segment_content(self) -> bool:
        return self._segment_content_offset == self._segment_content_length

    def readable(self) -> bool:
        return True

    def seekable(self) -> bool:
        return False

    def __aiter__(self):
        return self

    async def __anext__(self) -> bytes:
        data = await self.read(self._block_size)
        if not data:
            raise StopAsyncIteration
        return data

    async def read(self, size: int = -1) -> bytes:
        if self.closed:  # pylint: disable=using-constant-test
            raise ValueError("Stream is closed")

        if size == 0 or self._message_offset >= self.message_length:
            return b""
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
                    raise ValueError(
                        "First message segment was empty but more segments were detected."
                    )
                await self._read_message_footer()
                return b""

        count = 0
        content = BytesIO()
        while count < size and not (
            self._end_of_segment_content and self._message_offset == self.message_length
        ):
            if self._end_of_segment_content:
                await self._read_segment_header()

            segment_remaining = (
                self._segment_content_length - self._segment_content_offset
            )
            read_size = min(segment_remaining, size - count)

            segment_content = await self._read_from_inner(read_size)
            content.write(segment_content)

            # Update the running CRC64 for the segment and message
            if StructuredMessageProperties.CRC64 in self.flags:
                self._segment_crc64 = calculate_crc64(
                    segment_content, self._segment_crc64
                )
                self._message_crc64 = calculate_crc64(
                    segment_content, self._message_crc64
                )

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
        if (
            self._message_offset == self.message_length
            and self._segment_number != self.num_segments
        ):
            raise ValueError("Invalid structured message data detected.")

        return content.getvalue()

    async def _read_from_inner(self, size: int) -> bytes:
        while len(self._buffer) < size:
            try:
                chunk = await self._inner_iterator.__anext__()
            except StopAsyncIteration:
                break
            self._buffer += chunk

        if len(self._buffer) < size:
            raise ValueError(
                "Invalid structured message data detected. Stream content incomplete."
            )

        data = self._buffer[:size]
        self._buffer = self._buffer[size:]
        return data

    async def _read_message_header(self) -> None:
        header_data = await self._read_from_inner(
            StructuredMessageConstants.V1_HEADER_LENGTH
        )
        self.message_version, self.flags, self.num_segments = parse_message_header(
            header_data, self.message_length
        )
        self._message_offset += StructuredMessageConstants.V1_HEADER_LENGTH

    async def _read_message_footer(self) -> None:
        # Sanity check: There should only be self._message_footer_length (could be 0) bytes left to consume.
        # If not, it is likely the message header contained incorrect info.
        if self.message_length - self._message_offset != self._message_footer_length:
            raise ValueError("Invalid structured message data detected.")

        if StructuredMessageProperties.CRC64 in self.flags:
            message_crc = await self._read_from_inner(
                StructuredMessageConstants.CRC64_LENGTH
            )

            if self._message_crc64 != int.from_bytes(message_crc, "little"):
                raise ValueError(
                    "CRC64 mismatch detected in message trailer. "
                    "All data read should be considered invalid."
                )

        self._message_offset += self._message_footer_length

    async def _read_segment_header(self) -> None:
        header_data = await self._read_from_inner(self._segment_header_length)
        self._segment_number, self._segment_content_length = parse_segment_header(
            header_data, self._segment_number + 1
        )
        self._message_offset += self._segment_header_length

        self._segment_content_offset = 0
        self._segment_crc64 = 0

    async def _read_segment_footer(self) -> None:
        if StructuredMessageProperties.CRC64 in self.flags:
            segment_crc = await self._read_from_inner(
                StructuredMessageConstants.CRC64_LENGTH
            )

            if self._segment_crc64 != int.from_bytes(segment_crc, "little"):
                raise ValueError(
                    f"CRC64 mismatch detected in segment {self._segment_number}. "
                    f"All data read should be considered invalid."
                )

        self._message_offset += self._segment_footer_length
